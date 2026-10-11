# Planimetria interattiva per Home Assistant: V1

Pacchetto di asset per una dashboard `picture-elements`, in stile
[Anton Frolov](https://antonfrolov.substack.com/p/i-hired-an-illustrator-to-draw-my):
tutta la casa in un'unica immagine (mansarda sopra il primo piano, vista "esplosa"), basi giorno/notte,
10 luci indipendenti che si possono accendere insieme, un widget meteo in alto a sinistra e una gattina
tigrata grigia che dorme in camera.

## Contenuto

```
home-assistant-v1/
├── anteprima.html                      preview interattiva (usa gli stessi file di HA)
├── manifest.json                       asset, livelli, coordinate, mapping entità (generato)
├── www/floorplan/casa/                 → da copiare in /config/www/floorplan/casa/
│   ├── base-giorno.png  base-notte.png tela unica 1630×1440
│   ├── luce-<stanza>.png               10 overlay: salotto ingresso cucina bagno-giu studio-giu
│   │                                   studio-su pianerottolo camera bagno-su ripostiglio
│   ├── gatta.svg                       gattina tigrata grigia, respiro animato
│   └── trasparente.png                 1630×1440 vuoto, mostrato con luce spenta/unknown
├── livelli/                            asset intermedi per piano (1500×1049), sorgente della tela unica
│   ├── primo-piano/                    base-giorno, base-notte, luce-*.png
│   └── mansarda/                       base-giorno, base-notte, luce-*.png
├── home-assistant/
│   ├── packages/planimetria.yaml       helper notte + 10 interruttori demo + automazioni alba/tramonto
│   ├── dashboard-planimetria-demo.yaml dashboard funzionante subito con gli helper demo
│   └── dashboard-planimetria-luci.yaml stessa dashboard con segnaposto light.*
├── strumenti/
│   ├── stanze.json                     SORGENTE UNICA: poligoni, hotspot, icone, entità, layout casa, gattina, meteo
│   ├── genera_overlay.py               1. overlay per piano → livelli/
│   ├── genera_casa.py                  2. composizione della tela unica → www/floorplan/casa/
│   ├── genera_integrazione.py          3. manifest, anteprima e YAML
│   └── anteprima.template.html         template della preview
└── provenienza/                        prompt usati per generare le basi giorno/notte per piano
```

## Come sono fatti gli asset

| Livello | File | Note |
|---|---|---|
| 1. Base giorno | `casa/base-giorno.png` | luci spente, luce diurna neutra |
| 2. Base notte | `casa/base-notte.png` | luci spente, ambiente notturno leggibile; sopra la base giorno quando `input_boolean.planimetria_notte` è `on` |
| 3. Luci | `casa/luce-*.png` | RGBA a tutta tela, fusione normale; opacità 0.6 di giorno, 1.0 di notte |
| 4. Gattina | `casa/gatta.svg` | sul letto della camera; di notte si scurisce se la luce della camera è spenta |
| 5. Meteo | elementi `state-icon`/`state-label` | `weather.forecast_casa`: condizione, temperatura, massima/minima di oggi (sensori template del pacchetto), umidità, vento |
| 6. Comandi | icone `state-icon` | unici elementi cliccabili, sugli hotspot del manifest |

**Per piano** (`livelli/`): le basi giorno/notte sono state generate con il modello di immagini (prompt in
`provenienza/`) e verificate: allineate al pixel alle illustrazioni `../illustrazione-nuova/0*-v2.png`, arredo
invariato. Gli overlay luce sono **deterministici** (`genera_overlay.py`):

- la stanza "accesa" è ricavata dall'illustrazione originale, già illuminata in modo caldo, con alone ~2800 K
  centrato sull'hotspot. Nessun pixel viene ridisegnato o spostato: geometria, mobili e pareti restano identici;
- il confine è il poligono della stanza in `stanze.json`, sfumato di 5 px. I poligoni non si sovrappongono
  (mappa di etichette): ogni luce illumina solo la propria stanza;
- non si aggiungono lampade: è un'illuminazione ambientale.

**Tela unica** (`genera_casa.py`): ogni piano viene ritagliato dallo sfondo (casa + ombra portata, bordo morbido)
e posato sulla tela 1630×1440 agli offset di `stanze.json → casa` (primo piano `(150, 454)`, mansarda `(-10, -66)`:
la mansarda sta sopra, spostata di 160 px a sinistra). La mansarda sta davanti; gli overlay del primo piano sono
mascherati dove la mansarda li coprirebbe. Le coordinate delle stanze restano per piano in `stanze.json`
e vengono traslate automaticamente.

Ambiguità risolte: in mansarda l'armadio alto in alto a sinistra nel box del bagno appartiene al bagno;
le pareti esterne bianche del box bagno restano spente. Al primo piano l'armadio alto a destra del corridoio
appartiene allo studio, le porte del corridoio all'ingresso.

## Anteprima

`anteprima.html` carica le immagini con percorsi relativi, quindi va aperta via HTTP:

```bash
python -m http.server 8765 --directory output/home-assistant-v1
```

Poi apri http://localhost:8765/anteprima.html. Puoi passare da giorno a notte e accendere più stanze dalle
icone, dai poligoni (opzione "Mostra zone cliccabili") o dagli interruttori, raggruppati per piano.
"Mostra entity_id luci" visualizza i segnaposto `light.*`.

## Installazione in Home Assistant

1. **Immagini**: copia `www/floorplan/casa/` in `/config/www/floorplan/casa/`. Se la cartella `www` non esisteva,
   riavvia Home Assistant: viene servita come `/local/floorplan/…`.
2. **Pacchetto**: copia `home-assistant/packages/planimetria.yaml` in `/config/packages/` e abilita i pacchetti
   in `configuration.yaml`:
   ```yaml
   homeassistant:
     packages: !include_dir_named packages
   ```
   Il pacchetto crea `input_boolean.planimetria_notte`, 10 interruttori `input_boolean.planimetria_*` di prova
   due automazioni (notte al tramonto, giorno all'alba) e due sensori template con massima e minima di oggi
   (`weather.get_forecasts` ogni 30 minuti) per il widget meteo. La sintassi `triggers:`/`actions:` richiede
   Home Assistant 2024.10 o successivo. Riavvia o ricarica gli helper e le automazioni.
3. **Dashboard** in modalità YAML. Il nome della dashboard deve contenere un trattino:
   ```yaml
   lovelace:
     dashboards:
       planimetria-casa:
         mode: yaml
         title: Planimetria
         icon: mdi:floor-plan
         show_in_sidebar: true
         filename: dashboards/planimetria.yaml
   ```
   e copia `home-assistant/dashboard-planimetria-demo.yaml` in `/config/dashboards/planimetria.yaml`.
   In alternativa: Impostazioni → Dashboard → Aggiungi dashboard → "Nuova dashboard da zero", poi
   ⋮ → Modifica → ⋮ → Editor di configurazione grezza, e incolla il file.
   Ottieni una vista unica (`/planimetria-casa/casa`) con l'interruttore "Modalità notte" sopra la casa.
   Le modifiche successive al file della dashboard si vedono ricaricando la pagina, senza riavvio.

Tocca un'icona per accendere o spegnere; tieni premuto per aprire la finestra dell'entità.
Gli stati `unknown`/`unavailable` mostrano `trasparente.png`: nessuna luce, l'icona segnala lo stato.

Nessuna dipendenza HACS: card-mod e Browser Mod non servono.

### Installazione attuale

Raspberry `192.168.1.10`, Home Assistant Container: configurazione in
`/home/lbianco/dev/home-assisstant/config`, dashboard su http://192.168.1.10:8123/planimetria-casa/casa.
Il repository git della Raspberry traccia `config/packages/*.yaml` e `config/dashboards/*.yaml`;
le immagini in `www/` restano escluse (sono qui).

## Collegare le luci reali

1. In `strumenti/stanze.json` sostituisci i segnaposto `entity_light` (`light.salotto`, `light.ingresso`, …)
   con gli `entity_id` reali. Vanno bene anche `switch.*` e gruppi: lo stato atteso è `on`/`off`.
2. Rigenera:
   ```bash
   .venv/Scripts/python output/home-assistant-v1/strumenti/genera_integrazione.py
   ```
3. Usa `home-assistant/dashboard-planimetria-luci.yaml` al posto della versione demo. Gli interruttori demo del
   pacchetto si possono rimuovere: `input_boolean.planimetria_notte` e le automazioni servono ancora.

Per abbinare giorno/notte a `sun.sun` senza helper, sostituisci nei blocchi `conditional` la condizione
su `input_boolean.planimetria_notte` con `entity: sun.sun`, `state: below_horizon` / `above_horizon`.

## Rigenerare gli asset

Servono Python 3, Pillow e numpy (nel `.venv` del repository). In ordine:

```bash
.venv/Scripts/python output/home-assistant-v1/strumenti/genera_overlay.py
```

```bash
.venv/Scripts/python output/home-assistant-v1/strumenti/genera_casa.py
```

```bash
.venv/Scripts/python output/home-assistant-v1/strumenti/genera_integrazione.py
```

Per spostare o ingrandire la gattina (`gatta.center`/`gatta.width`, coordinate del suo piano) o il meteo
(`meteo.anchor`) basta cambiare `stanze.json` e rieseguire solo l'ultimo script. Dopo aver modificato le immagini, incrementa `VERSION` in
`genera_integrazione.py`: cambia il parametro `?v=` degli URL e forza il browser a ricaricarle.

## Fuori dalla V1

TV, monitor ed elettrodomestici; animazioni WebP; popup Browser Mod.
