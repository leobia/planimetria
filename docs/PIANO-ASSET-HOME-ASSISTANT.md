# Piano degli asset per Home Assistant

Ricerca e verifica locale: 11 ottobre 2026. Documento di progetto; non è ancora un pacchetto installabile.

## Riferimento verificato

[Articolo di Anton Frolov](https://antonfrolov.substack.com/p/i-hired-an-illustrator-to-draw-my).
L'autore usa picture-elements, livelli trasparenti, dispositivi statici/animati WebP e varianti giorno/notte. Richiede esportazioni sulla stessa tela, senza ritagliare ogni oggetto. Un helper seleziona giorno/notte. Riutilizza gli elementi con file YAML; per la vista combinata usa vertical-stack e card-mod. Browser Mod serve al suo popup personalizzato; kiosk e HDMI riguardano la visualizzazione TV. Nell'articolo non è collegato un repository completo della dashboard: il frammento YAML pubblicato è illustrativo, non un pacchetto pronto da installare.

## Materiale disponibile

- `output/illustrazione-nuova/01-primo-piano-v2.png`
- `output/illustrazione-nuova/02-mansarda-v2.png`

Entrambi: 1500 × 1049 pixel, RGB senza canale alpha, sfondo scuro incorporato. Sono illustrazioni appiattite: arredi, dispositivi e illuminazione non sono livelli separati. Nella ricerca dei file non sono emersi master PSD/KRA/ORA né configurazioni YAML Home Assistant.

Le immagini possono già servire come fondali per comandi e letture. Per una casa che cambia visivamente servono gli asset descritti sotto. Non abbiamo ancora un inventario delle entità reali di Home Assistant: i dispositivi rappresentati non implicano che siano integrati o controllabili.

## Architettura proposta per questo progetto

Due viste, una per piano, come prima consegna; vista complessiva opzionale successiva. Congelare camera, geometria, dimensioni e coordinate delle v2.

Composizione: base → illuminazione → stati dei dispositivi → indicatori → aree interattive.

La base deve avere uno stato dichiarato: luce ambientale diurna o notturna, luci comandabili spente, schermi spenti. Una base notturna deve restare leggibile. Alcune lampade nelle v2 sembrano già luminose: va normalizzato lo stato iniziale.

Non rigenerare l'intero piano per ciascuna combinazione. Creare livelli indipendenti: due luci accese contemporaneamente devono comporsi senza cancellarsi a vicenda. Un ritaglio opaco di stanza può coprire gli effetti di altri dispositivi; usare trasparenza, maschere e ordine dei livelli verificati.

## Inventario da produrre

| Artefatto | Quantità iniziale | Priorità |
|---|---:|---|
| Master modificabile per piano con maschere e livelli | 2 | Alta |
| Base giorno a luci comandabili spente | 2 | Alta |
| Base notte a luci comandabili spente | 2 | Alta per giorno/notte |
| Maschere delle zone illuminate | Una per zona/circuito indipendente | Alta |
| Overlay luce accesa: sorgente, alone e superfici illuminate | Uno per circuito; variante giorno/notte se necessaria | Alta |
| Stato TV/monitor acceso | Uno per schermo integrato scelto | Media |
| Effetto ventilatore/climatizzatore attivo | Uno per dispositivo scelto, eventualmente animato | Media |
| Finestre, porte o tapparelle in stati alternativi | Solo quelle monitorate che si vogliono visualizzare | Opzionale |
| Robot/elettrodomestici in attività | Solo dispositivi integrati scelti | Opzionale |
| Scontorni dei piani e composizione comune | 2 scontorni più layout | Solo vista combinata |

Non è necessario animare una luce stabile. Temperature, umidità, consumi e avvisi possono essere testo/icone: non richiedono illustrazioni.

Per oggetti che cambiano sagoma o posizione (porte, robot, pale), ricostruire anche lo sfondo prima coperto: sovrapporre la nuova immagine all'oggetto originale produrrebbe un doppione. Per uno schermo, invece, può bastare un livello limitato alla superficie del display.

Convenzione proposta: tutti gli overlay di un piano su tela trasparente 1500 × 1049, senza crop automatico e senza spostamenti. PNG per gli statici; WebP per le animazioni, da provare sul browser di destinazione. Un master unico per entrambi i piani non è indispensabile per le viste separate; per la composizione complessiva occorre fissare scala e trasformazione di ogni piano e dei suoi livelli.

## Contratto con il progetto Home Assistant

Preparare un manifest JSON/YAML con: identificativo asset, piano, dimensioni, file, ordine di sovrapposizione, zona cliccabile, entità o segnaposto, stati previsti, varianti di illuminazione, azione al tocco e fallback per unknown/unavailable.

Separare livelli visivi a tutta tela dalle zone cliccabili: la trasparenza di un'immagine non garantisce che i clic attraversino il suo rettangolo. I livelli puramente decorativi non devono intercettare gli input; le aree interattive vanno collocate sopra.

Il pacchetto finale dovrebbe contenere:

1. Asset esportati in `www/floorplan/`, suddivisi per piano.
2. Manifest degli asset e tabella di associazione alle entità reali.
3. File degli elementi e dashboard YAML di esempio, con segnaposto espliciti finché mancano gli entity_id.
4. Helper/automazione giorno-notte, se adottati.
5. Istruzioni di installazione e anteprime delle combinazioni principali.

La documentazione ufficiale descrive [picture-elements e stati](https://www.home-assistant.io/dashboards/picture-elements/), [dashboard YAML](https://www.home-assistant.io/dashboards/dashboards/) e [inclusione di file](https://www.home-assistant.io/docs/configuration/splitting_configuration/). Per l'hosting, `/config/www/floorplan/` è raggiungibile come `/local/floorplan/`; la prima creazione di www richiede un riavvio: [HTTP hosting](https://www.home-assistant.io/integrations/http/#hosting-files).

Dipendenze opzionali: [card-mod](https://github.com/thomasloven/lovelace-card-mod) per layout CSS elaborati e [Browser Mod](https://github.com/thomasloven/hass-browser_mod) per popup personalizzati. Non necessari per la prima versione a due viste.

## Sequenza consigliata

1. Inventario per stanza: luci/circuiti, dispositivi, stati osservabili e azioni desiderate.
2. Prova completa sul salotto: base giorno/notte, una luce, TV accesa e aree di tocco.
3. Verificare allineamento, bordi, luce+TV simultanee, fallback, leggibilità e clic.
4. Estendere agli altri ambienti, poi introdurre animazioni dove utili.
5. Collegare e collaudare sul progetto Home Assistant reale; solo dopo completare vista complessiva e modalità TV.

Il numero finale degli asset dipende dai circuiti indipendenti e dagli stati effettivamente disponibili. Evitare una stima basata soltanto sul numero delle stanze.

## Stato (11 ottobre 2026)

La V1 è pronta in `output/home-assistant-v1/`: vista unica della casa (due piani sulla stessa tela), basi giorno/notte, 10 overlay luce deterministici, gattina,
manifest, anteprima HTML, pacchetto e dashboard YAML (demo e segnaposto `light.*`).
Installazione e rigenerazione: `output/home-assistant-v1/README.md`.
