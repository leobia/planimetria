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
VERSION = 2            # incrementare per forzare il refresh della cache del browser
NIGHT_FILTER = "brightness(45%) saturate(70%)"


def pct(v, total):
    return f"{v / total * 100:.2f}%"


def load():
    return json.loads((ROOT / "strumenti" / "stanze.json").read_text(encoding="utf-8"))


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
            "5 icone di stato cliccabili sugli hotspot",
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
            "center_px": g["center"],
            "width_px": g["width"],
            "center_pct": [round(g["center"][0] / w * 100, 2), round(g["center"][1] / h * 100, 2)],
            "room": g["room"],
            "night_filter_when_room_off": NIGHT_FILTER,
        },
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
    cat_style = [f"top: {pct(g['center'][1], h)}", f"left: {pct(g['center'][0], w)}",
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
