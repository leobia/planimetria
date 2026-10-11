# Planimetria interattiva per Home Assistant: V1

Pacchetto di asset per una dashboard `picture-elements` su due piani, in stile
[Anton Frolov](https://antonfrolov.substack.com/p/i-hired-an-illustrator-to-draw-my):
basi giorno/notte e 10 luci indipendenti, una per ambiente, che si possono accendere insieme.

## Contenuto

```
home-assistant-v1/
├── anteprima.html                      preview interattiva (usa gli stessi file di HA)
├── manifest.json                       asset, livelli, coordinate, mapping entità (generato)
├── www/floorplan/                      → da copiare in /config/www/floorplan/
│   ├── trasparente.png                 1500×1049 vuoto, mostrato con luce spenta/unknown
│   ├── primo-piano/  base-giorno.png  base-notte.png
│   │                 luce-salotto  luce-ingresso  luce-cucina  luce-bagno  luce-studio (.png)
│   └── mansarda/     base-giorno.png  base-notte.png
│                     luce-studio  luce-pianerottolo  luce-camera  luce-bagno  luce-ripostiglio (.png)
├── home-assistant/
│   ├── packages/planimetria.yaml       helper notte + 10 interruttori demo + automazione alba/tramonto
│   ├── dashboard-planimetria-demo.yaml dashboard funzionante subito con gli helper demo
│   └── dashboard-planimetria-luci.yaml stessa dashboard con segnaposto light.*
├── strumenti/
│   ├── stanze.json                     SORGENTE UNICA: poligoni, hotspot, icone, entità
│   ├── genera_overlay.py               rigenera i 10 overlay PNG
│   ├── genera_integrazione.py          rigenera manifest, anteprima e YAML
│   └── anteprima.template.html         template della preview
└── provenienza/                        prompt usati per generare le basi giorno/notte
```

Tutte le immagini sono 1500 × 1049, sulla stessa tela delle illustrazioni
`../illustrazione-nuova/0*-v2.png`, senza ritagli né spostamenti.

## Come sono fatti gli asset

| Livello | File | Note |
|---|---|---|
| 1. Base giorno | `base-giorno.png` | luci spente, luce diurna neutra (generata dal modello di immagini, vedi `provenienza/`) |
| 2. Base notte | `base-notte.png` | luci spente, ambiente notturno leggibile; sopra la base giorno quando `input_boolean.planimetria_notte` è `on` |
| 3. Luci | `luce-*.png` | RGBA a tutta tela, fusione normale; opacità 0.6 di giorno, 1.0 di notte |
| 4. Comandi | icone `state-icon` | unici elementi cliccabili, sugli hotspot del manifest |

Le basi giorno/notte prodotte nella sessione precedente sono state verificate: registrazione a offset (0,0)
rispetto agli originali e nessuna differenza di arredo visibile. Sono state mantenute.

Gli overlay AI della sessione precedente sono stati scartati (due erano larghi 1499 px e la luce non
era confinata alla stanza) e poi eliminati. I 10 overlay attuali sono
**deterministici** (`genera_overlay.py`):

- la stanza "accesa" è ricavata dall'illustrazione originale, già illuminata in modo caldo, con alone ~2800 K
  centrato sull'hotspot. Nessun pixel viene ridisegnato o spostato: geometria, mobili e pareti restano identici;
- il confine è il poligono della stanza in `stanze.json`, sfumato di 5 px. I poligoni non si sovrappongono
  (mappa di etichette): ogni luce illumina solo la propria stanza;
- non si aggiungono lampade: è un'illuminazione ambientale.

Ambiguità risolte: in mansarda l'armadio alto in alto a sinistra nel box del bagno appartiene al bagno;
le pareti esterne bianche del box bagno restano spente. Al primo piano l'armadio alto a destra del corridoio
appartiene allo studio, le porte del corridoio all'ingresso.

## Anteprima

`anteprima.html` carica le immagini con percorsi relativi, quindi va aperta via HTTP:

```bash
python -m http.server 8765 --directory output/home-assistant-v1
```

Poi apri http://localhost:8765/anteprima.html. Puoi scegliere il piano, passare da giorno a notte e
accendere più stanze dalle icone, dai poligoni (opzione "Mostra zone cliccabili") o dagli interruttori.
"Mostra entity_id luci" visualizza i segnaposto `light.*`.

## Installazione in Home Assistant

1. **Immagini**: copia `www/floorplan/` in `/config/www/floorplan/`. Se la cartella `www` non esisteva,
   riavvia Home Assistant: viene servita come `/local/floorplan/…`.
2. **Pacchetto**: copia `home-assistant/packages/planimetria.yaml` in `/config/packages/` e abilita i pacchetti
   in `configuration.yaml`:
   ```yaml
   homeassistant:
     packages: !include_dir_named packages
   ```
   Il pacchetto crea `input_boolean.planimetria_notte`, 10 interruttori `input_boolean.planimetria_*` di prova
   e due automazioni (notte al tramonto, giorno all'alba). La sintassi `triggers:`/`actions:` richiede
   Home Assistant 2024.10 o successivo. Riavvia o ricarica gli helper e le automazioni.
3. **Dashboard**: Impostazioni → Dashboard → Aggiungi dashboard → "Nuova dashboard da zero", poi
   ⋮ → Modifica → ⋮ → Editor di configurazione grezza, e incolla `home-assistant/dashboard-planimetria-demo.yaml`.
   In alternativa, in modalità YAML:
   ```yaml
   lovelace:
     dashboards:
       planimetria:
         mode: yaml
         title: Planimetria
         icon: mdi:floor-plan
         filename: dashboards/planimetria.yaml
   ```
   e copia il file YAML in `/config/dashboards/planimetria.yaml`.
   Ottieni due viste (Primo piano, Mansarda); ciascuna ha l'interruttore "Modalità notte" sopra la planimetria.

Tocca un'icona per accendere o spegnere; tieni premuto per aprire la finestra dell'entità.
Gli stati `unknown`/`unavailable` mostrano `trasparente.png`: nessuna luce, l'icona segnala lo stato.

Nessuna dipendenza HACS: card-mod e Browser Mod non servono per la V1.

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

Servono Python 3, Pillow e numpy (nel `.venv` del repository):

```bash
.venv/Scripts/python output/home-assistant-v1/strumenti/genera_overlay.py
```

```bash
.venv/Scripts/python output/home-assistant-v1/strumenti/genera_integrazione.py
```

Dopo aver modificato le immagini, incrementa `VERSION` in `genera_integrazione.py`: cambia il parametro `?v=`
degli URL e forza il browser a ricaricarle.

## Fuori dalla V1

TV, monitor ed elettrodomestici; vista combinata dei due piani (servono scontorni e card-mod);
animazioni WebP; popup Browser Mod.
