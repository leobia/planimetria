"""Genera manifest, anteprima HTML e YAML Home Assistant da strumenti/stanze.json.

Vista unica: i due piani composti sulla tela "casa" (vedi genera_casa.py).
Produce, nella cartella output/home-assistant-v1:
  manifest.json
  anteprima.html
  home-assistant/dashboard-planimetria-demo.yaml   (helper input_boolean del pacchetto demo)
  home-assistant/dashboard-planimetria-luci.yaml   (segnaposto light.* da sostituire)
  home-assistant/packages/planimetria.yaml          (helper giorno/notte, luci demo, automazione)

Uso:  python genera_integrazione.py   (dopo genera_overlay.py e genera_casa.py)
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOCAL = "/local/floorplan"
VERSION = 3            # incrementare per forzare il refresh della cache del browser
NIGHT_FILTER = "brightness(45%) saturate(70%)"


def pct(v, total):
    return f"{v / total * 100:.2f}%"


def load():
    return json.loads((ROOT / "strumenti" / "stanze.json").read_text(encoding="utf-8"))


def cat_center(cfg):
    g = cfg["gatta"]
    ox, oy = cfg["casa"]["offsets"][g["floor"]]
    return [g["center"][0] + ox, g["center"][1] + oy]


def house_rooms(cfg):
    """Stanze di tutti i piani con coordinate riportate sulla tela casa."""
    rooms = []
    for floor in cfg["floors"]:
        ox, oy = cfg["casa"]["offsets"][floor["id"]]
        for r in floor["rooms"]:
            rooms.append(dict(
                r,
                floor=floor["id"],
                floor_label=floor["label"],
                polygon=[[x + ox, y + oy] for x, y in r["polygon"]],
                hotspot=[r["hotspot"][0] + ox, r["hotspot"][1] + oy],
                overlay=f"casa/luce-{r['id'].replace('_', '-')}.png",
            ))
    return rooms


# ---------------------------------------------------------------- manifest
def build_manifest(cfg):
    w, h = cfg["casa"]["size"]
    rooms = []
    for z, r in enumerate(house_rooms(cfg)):
        xs = [p[0] for p in r["polygon"]]
        ys = [p[1] for p in r["polygon"]]
        rooms.append({
            "id": r["id"],
            "label": r["label"],
            "floor": r["floor"],
            "icon": r["icon"],
            "overlay": f"www/floorplan/{r['overlay']}",
            "overlay_url": f"{LOCAL}/{r['overlay']}",
            "z_index": 10 + z,
            "polygon_px": r["polygon"],
            "polygon_pct": [[round(x / w * 100, 3), round(y / h * 100, 3)] for x, y in r["polygon"]],
            "bbox_px": [min(xs), min(ys), max(xs), max(ys)],
            "hotspot_px": r["hotspot"],
            "hotspot_pct": [round(r["hotspot"][0] / w * 100, 2), round(r["hotspot"][1] / h * 100, 2)],
            "entity_demo": r["entity_demo"],
            "entity_light": r["entity_light"],
            "states": {"on": "overlay visibile", "off": "trasparente",
                       "unknown/unavailable": "trasparente (icona di stato segnala il problema)"},
            "tap_action": "toggle",
            "hold_action": "more-info",
        })
    g = cfg["gatta"]
    return {
        "version": VERSION,
        "generated_by": "strumenti/genera_integrazione.py da strumenti/stanze.json",
        "canvas": {"width": w, "height": h},
        "layers": [
            "1 base giorno della casa (immagine della card)",
            "2 base notte (sopra la base giorno quando night_entity = on)",
            "3 overlay luce, uno per stanza, a tutta tela, non cliccabili",
            "4 gattina (SVG animato), scurita di notte se la luce della sua stanza e' spenta",
            "5 widget meteo in alto a sinistra",
            "6 icone di stato cliccabili sugli hotspot",
        ],
        "lighting": {
            "method": "overlay RGBA a tutta tela, fusione normale; stanza accesa ricavata dall'illustrazione originale + alone caldo ~2800 K",
            "opacity_giorno": cfg["opacity"]["giorno"],
            "opacity_notte": cfg["opacity"]["notte"],
            "night_entity": cfg["night_entity"],
            "fallback": "unknown/unavailable: overlay nascosto (trasparente.png)",
        },
        "base": {"giorno": "www/floorplan/casa/base-giorno.png", "notte": "www/floorplan/casa/base-notte.png"},
        "transparent": "www/floorplan/casa/trasparente.png",
        "floors_layout": {
            fid: {"offset_px": cfg["casa"]["offsets"][fid],
                  "source_illustration": next(f["source"] for f in cfg["floors"] if f["id"] == fid)}
            for fid in cfg["casa"]["order"]
        },
        "cat": {
            "file": f"www/floorplan/{g['file']}",
            "center_px": cat_center(cfg),
            "width_px": g["width"],
            "center_pct": [round(cat_center(cfg)[0] / w * 100, 2), round(cat_center(cfg)[1] / h * 100, 2)],
            "room": g["room"],
            "night_filter_when_room_off": NIGHT_FILTER,
        },
        "weather": dict(cfg["meteo"], elements=[
            {k: e[k] for k in ("kind", "x", "y", "what")} for e in weather_layout(cfg)]),
        "rooms": rooms,
    }


# ---------------------------------------------------------------- YAML Home Assistant
FULL_STYLE = ["top: 50%", "left: 50%", "width: 100%", "pointer-events: none"]


def yaml_style(lines, indent, extra=()):
    pad = " " * indent
    out = [f"{pad}style:"]
    for s in list(lines) + list(extra):
        k, v = s.split(": ", 1)
        out.append(f'{pad}  {k}: "{v}"' if "%" in v else f"{pad}  {k}: {v}")
    return out


def picture_elements(cfg, entity_key):
    w, h = cfg["casa"]["size"]
    night = cfg["night_entity"]
    rooms = house_rooms(cfg)
    g = cfg["gatta"]
    cat_room = next(r for r in rooms if r["id"] == g["room"])
    v = f"?v={VERSION}"
    cx, cy = cat_center(cfg)
    cat_style = [f"top: {pct(cy, h)}", f"left: {pct(cx, w)}",
                 f"width: {pct(g['width'], w)}", "pointer-events: none"]
    L = [
        "type: picture-elements",
        f"image: {LOCAL}/casa/base-giorno.png{v}",
        "elements:",
    ]

    def overlays(opacity, indent):
        pad = " " * indent
        out = []
        for r in rooms:
            out += [
                f"{pad}- type: image",
                f"{pad}  entity: {r[entity_key]}",
                f"{pad}  image: {LOCAL}/casa/trasparente.png{v}",
                f"{pad}  state_image:",
                f'{pad}    "on": {LOCAL}/{r["overlay"]}{v}',
                f"{pad}  tap_action:",
                f"{pad}    action: none",
            ]
            out += yaml_style(FULL_STYLE, indent + 2, [f"opacity: {opacity}"])
        return out

    for state, label in (("off", "giorno"), ("on", "notte")):
        L += [
            f"  # ---- {label}",
            "  - type: conditional",
            "    conditions:",
            "      - condition: state",
            f"        entity: {night}",
            f'        state: "{state}"',
            "    elements:",
        ]
        if state == "on":
            L += [
                "      - type: image",
                f"        image: {LOCAL}/casa/base-notte.png{v}",
                "        tap_action:",
                "          action: none",
            ]
            L += yaml_style(FULL_STYLE, 8)
        L += overlays(cfg["opacity"][label], 6)
        L += [
            f"      # gattina ({g['room']})",
            "      - type: image",
            f"        image: {LOCAL}/{g['file']}{v}",
        ]
        if state == "on":
            L += [
                f"        entity: {cat_room[entity_key]}",
                "        state_filter:",
                f'          "off": {NIGHT_FILTER}',
                f'          "unavailable": {NIGHT_FILTER}',
                f'          "unknown": {NIGHT_FILTER}',
            ]
        L += ["        tap_action:", "          action: none"]
        L += yaml_style(cat_style, 8)

    L.append("  # ---- meteo")
    L += weather_elements(cfg)
    L.append("  # ---- comandi (sopra a tutto)")
    for r in rooms:
        x, y = r["hotspot"]
        L += [
            "  - type: state-icon",
            f"    entity: {r[entity_key]}",
            f"    icon: {r['icon']}",
            f"    title: {r['label']} ({r['floor_label'].lower()})",
            "    tap_action:",
            "      action: toggle",
            "    hold_action:",
            "      action: more-info",
        ]
        L += yaml_style([f"top: {pct(y, h)}", f"left: {pct(x, w)}"], 4, [
            "--mdc-icon-size: 26px",
            "background: rgba(20, 20, 24, 0.55)",
            "border-radius: 50%",
            "padding: 3px",
        ])
    return L


WEATHER_TEXT = ["color: rgba(244, 240, 233, 0.96)", "text-shadow: 0 1px 4px rgba(0, 0, 0, 0.7)",
                "white-space: nowrap", "transform: translate(0, -50%)"]


def weather_layout(cfg):
    """Elementi del widget meteo: (tipo, x, y, contenuto) in pixel della tela casa."""
    m = cfg["meteo"]
    ax, ay = m["anchor"]
    return [
        {"kind": "condition", "x": ax + 50, "y": ay + 55, "what": m["entity"]},
        {"kind": "big", "x": ax + 110, "y": ay + 55, "what": "temperature"},
        {"kind": "icon", "x": ax + 124, "y": ay + 128, "what": "mdi:white-balance-sunny"},
        {"kind": "small", "x": ax + 146, "y": ay + 128, "what": "max"},
        {"kind": "icon", "x": ax + 284, "y": ay + 128, "what": "mdi:weather-night"},
        {"kind": "small", "x": ax + 306, "y": ay + 128, "what": "min"},
        {"kind": "icon", "x": ax + 124, "y": ay + 176, "what": "mdi:water-percent"},
        {"kind": "small", "x": ax + 146, "y": ay + 176, "what": "humidity"},
        {"kind": "icon", "x": ax + 284, "y": ay + 176, "what": "mdi:weather-windy"},
        {"kind": "small", "x": ax + 306, "y": ay + 176, "what": "wind_speed"},
    ]


def weather_elements(cfg):
    w, h = cfg["casa"]["size"]
    m = cfg["meteo"]
    L = []
    for e in weather_layout(cfg):
        pos = [f"top: {pct(e['y'], h)}", f"left: {pct(e['x'], w)}"]
        if e["kind"] == "condition":
            L += ["  - type: state-icon", f"    entity: {m['entity']}", "    state_color: false",
                  "    tap_action:", "      action: more-info"]
            L += yaml_style(pos, 4, ["--mdc-icon-size: clamp(34px, 4.4vw, 84px)",
                                     "color: rgba(244, 240, 233, 0.96)"])
        elif e["kind"] == "icon":
            L += ["  - type: icon", f"    icon: {e['what']}", "    tap_action:", "      action: none"]
            L += yaml_style(pos, 4, ["--mdc-icon-size: clamp(13px, 1.45vw, 26px)",
                                     "color: rgba(244, 240, 233, 0.8)", "pointer-events: none"])
        else:
            size = "clamp(24px, 3.5vw, 66px)" if e["kind"] == "big" else "clamp(12px, 1.45vw, 26px)"
            if e["what"] in ("max", "min"):
                L += ["  - type: state-label", f"    entity: {m['sensor_' + e['what']]}"]
            else:
                unit = {"temperature": " °C", "humidity": "%", "wind_speed": " km/h"}[e["what"]]
                L += ["  - type: state-label", f"    entity: {m['entity']}", f"    attribute: {e['what']}",
                      f'    suffix: "{unit}"']
            L += ["    tap_action:", "      action: more-info"]
            L += yaml_style(pos, 4, WEATHER_TEXT + [f"font-size: {size}",
                                                    "font-weight: " + ("500" if e["kind"] == "big" else "400")])
    return L


def dashboard(cfg, entity_key, title_note):
    pe = picture_elements(cfg, entity_key)
    L = [
        "# Generato da strumenti/genera_integrazione.py: non modificare a mano,",
        "# modificare strumenti/stanze.json e rigenerare.",
        f"# {title_note}",
        "title: Planimetria",
        "views:",
        "  - title: Casa",
        "    path: casa",
        "    icon: mdi:home",
        "    type: panel",
        "    cards:",
        "      - type: vertical-stack",
        "        cards:",
        "          - type: entities",
        "            entities:",
        f"              - entity: {cfg['night_entity']}",
        "                name: Modalità notte",
        "          - " + pe[0],
    ]
    L += ["            " + s for s in pe[1:]]
    return "\n".join(L) + "\n"


def package(cfg):
    L = [
        "# Pacchetto Home Assistant per la planimetria interattiva.",
        "# Generato da strumenti/genera_integrazione.py.",
        "# Copiare in /config/packages/ e abilitare i pacchetti in configuration.yaml:",
        "#   homeassistant:",
        "#     packages: !include_dir_named packages",
        "",
        "input_boolean:",
        "  planimetria_notte:",
        "    name: Planimetria modalità notte",
        "    icon: mdi:weather-night",
        "  # Interruttori dimostrativi: sostituiti dalle luci reali in dashboard-planimetria-luci.yaml",
    ]
    for floor in cfg["floors"]:
        for r in floor["rooms"]:
            L += [
                f"  {r['entity_demo'].split('.', 1)[1]}:",
                f"    name: Demo luce {r['label'].lower()} ({floor['label'].lower()})",
                f"    icon: {r['icon']}",
            ]
    m = cfg["meteo"]
    L += [
        "",
        "# Massima e minima di oggi per il widget meteo (le previsioni non sono piu' attributi dell'entita').",
        "template:",
        "  - triggers:",
        "      - trigger: time_pattern",
        '        minutes: "/30"',
        "      - trigger: homeassistant",
        "        event: start",
        "    actions:",
        "      - action: weather.get_forecasts",
        "        target:",
        f"          entity_id: {m['entity']}",
        "        data:",
        "          type: daily",
        "        response_variable: previsioni",
        "    sensor:",
    ]
    for key, label, field in (("max", "massima", "temperature"), ("min", "minima", "templow")):
        L += [
            f"      - name: Planimetria meteo {label}",
            f"        unique_id: planimetria_meteo_{label}",
            '        unit_of_measurement: "°C"',
            "        device_class: temperature",
            f"        state: \"{{{{ previsioni['{m['entity']}'].forecast[0].{field} | round(1) }}}}\"",
        ]
    L += [
        "",
        "automation:",
        "  - id: planimetria_notte_al_tramonto",
        "    alias: Planimetria - notte al tramonto",
        "    triggers:",
        "      - trigger: sun",
        "        event: sunset",
        "    actions:",
        "      - action: input_boolean.turn_on",
        "        target:",
        f"          entity_id: {cfg['night_entity']}",
        "  - id: planimetria_giorno_all_alba",
        "    alias: Planimetria - giorno all'alba",
        "    triggers:",
        "      - trigger: sun",
        "        event: sunrise",
        "    actions:",
        "      - action: input_boolean.turn_off",
        "        target:",
        f"          entity_id: {cfg['night_entity']}",
    ]
    return "\n".join(L) + "\n"


# ---------------------------------------------------------------- anteprima HTML
def preview(manifest, cfg):
    data = {
        "canvas": manifest["canvas"],
        "opacity": cfg["opacity"],
        "base": manifest["base"],
        "nightFilter": NIGHT_FILTER,
        "cat": manifest["cat"],
        "weather": manifest["weather"],
        "floors": [{"id": fid, "label": next(f["label"] for f in cfg["floors"] if f["id"] == fid)}
                   for fid in reversed(cfg["casa"]["order"])],
        "rooms": [
            {k: r[k] for k in ("id", "label", "floor", "icon", "overlay", "polygon_px", "hotspot_px",
                               "entity_demo", "entity_light")}
            for r in manifest["rooms"]
        ],
    }
    tpl = (ROOT / "strumenti" / "anteprima.template.html").read_text(encoding="utf-8")
    return tpl.replace("/*__DATA__*/null", json.dumps(data, ensure_ascii=False))


def main():
    cfg = load()
    manifest = build_manifest(cfg)
    (ROOT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    ha = ROOT / "home-assistant"
    (ha / "packages").mkdir(parents=True, exist_ok=True)
    (ha / "dashboard-planimetria-demo.yaml").write_text(
        dashboard(cfg, "entity_demo", "Versione DEMO: usa gli input_boolean del pacchetto packages/planimetria.yaml."),
        encoding="utf-8")
    (ha / "dashboard-planimetria-luci.yaml").write_text(
        dashboard(cfg, "entity_light", "Versione LUCI: gli entity_id light.* sono SEGNAPOSTO, aggiornarli in stanze.json (entity_light)."),
        encoding="utf-8")
    (ha / "packages" / "planimetria.yaml").write_text(package(cfg), encoding="utf-8")
    (ROOT / "anteprima.html").write_text(preview(manifest, cfg), encoding="utf-8")
    for p in ["manifest.json", "anteprima.html", "home-assistant/dashboard-planimetria-demo.yaml",
              "home-assistant/dashboard-planimetria-luci.yaml", "home-assistant/packages/planimetria.yaml"]:
        print("scritto", p)


if __name__ == "__main__":
    main()
