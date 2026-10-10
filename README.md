# Planimetria su due livelli

Progetto Sweet Home 3D ricostruito da una planimetria abbozzata e dalle foto degli ingressi e della scala.

Aprire `Planimetria_due_livelli.sh3d` in Sweet Home 3D. Questo è il file principale: gli aggiornamenti vengono salvati sempre nello stesso file.

## Stato attuale

- Due livelli con muri, ambienti, porte e finestre.
- Piano inferiore di circa 90 m² interni; dimensioni e altezze stimate.
- Scala aperta con pedate in legno, curva a ventaglio, struttura e ringhiera nere.
- Vano scala e parapetto con cancelletto al piano superiore.
- Lucernari indicati in pianta; falde del tetto ancora da definire.
- Studio superiore arredato dalle due fotografie: scrivania e PC, sedia da ufficio, letto blu, armadi sottotetto, cyclette, cassettiera, libreria, sedia in legno, tiragraffi, pesi e climatizzatore. Gli oggetti sono rappresentazioni semplificate.
- Falda dello studio con rivestimento e travi in legno, lucernario con tenda scura e pavimento a piastrelle diagonali. Le altezze sono stimate. Il gruppo della falda può essere nascosto per vedere gli arredi dall'alto; è disponibile una vista salvata dalla porta.
- Arredamento degli altri ambienti da aggiungere a partire dalle fotografie.
- Ingresso superiore arredato dalla fotografia: armadio bianco, tavolino con monitor, mensola e quadro, tenda azzurra, radiatore e lettiera coperta. Cestino centrale escluso. Pavimento a piastrelle diagonali.

## Rigenerazione

Il file `.sh3d` corrente contiene anche modifiche manuali, incluse le due scrivanie. Non rigenerarlo con `build_project.py`: lo script descrive la ricostruzione iniziale e non incorpora tutte le modifiche successive. `update_studio.py` applica soltanto l'armadio a muro e la porta in legno al progetto corrente, preservando gli altri elementi.

`ingresso_su.py` aggiorna soltanto gli arredi e il pavimento dell'ingresso superiore nel progetto corrente. Conserva porte, scala e altri ambienti.

`build_project.py` genera il file `.sh3d` e un'anteprima usando Python e Pillow. `studio_su.py` contiene la ricostruzione dello studio superiore:

```sh
python -m pip install Pillow
python build_project.py
```

Lo script sovrascrive il progetto principale. Eventuali modifiche fatte direttamente in Sweet Home 3D vanno riportate nello script prima di rigenerare, altrimenti saranno perse.

L'XML intermedio e l'anteprima sono file generati esclusi da Git. Il progetto `.sh3d` contiene i modelli necessari e viene versionato insieme allo script.
