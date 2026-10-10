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
- Camera da letto ricostruita da due foto: letto matrimoniale bianco, due comodini con lampade, armadi bianchi a muro, mobile TV in legno, sedia, poltroncina bianca, ventilatore e sgabello azzurro. Falda con travi e lucernario nascosta all'apertura. Porta del bagno in legno mantenuta in posizione.
- Bagno superiore con WC, bidet, lavabo su piano piastrellato, doccia, specchio e accessori; pavimento blu e rivestimento bianco con fasce blu. Ripostiglio con scaffali e scatole, mantenendo libero l'accesso. Falde nascoste all'apertura.
- Accesso alla camera con porta in legno e condizionatore sopra. Bagno e ripostiglio hanno muri e falde che scendono verso destra nella planimetria, lato TV e ripostiglio, da circa 250 a 180 cm; quote stimate.

## Rigenerazione

Il file `.sh3d` corrente contiene anche modifiche manuali, incluse le due scrivanie. Non rigenerarlo con `build_project.py`: lo script descrive la ricostruzione iniziale e non incorpora tutte le modifiche successive. `update_studio.py` applica soltanto l'armadio a muro e la porta in legno al progetto corrente, preservando gli altri elementi.

`ingresso_su.py` aggiorna soltanto gli arredi e il pavimento dell'ingresso superiore nel progetto corrente. Conserva porte, scala e altri ambienti.

`camera_letto.py` aggiorna la camera e la sua falda sul progetto corrente, preservando gli altri ambienti e le posizioni delle porte.

`bagno_ripostiglio.py` arreda bagno superiore e ripostiglio sul progetto corrente senza modificare gli altri ambienti o le posizioni delle porte. Sanitari, decorazioni e oggetti sono semplificati.

`finish_upper_floor.py` applica le rifiniture finali: porta e climatizzatore della camera, altezze decrescenti di bagno e ripostiglio. Va eseguito dopo gli script dei singoli ambienti se questi vengono riutilizzati.

`build_project.py` genera il file `.sh3d` e un'anteprima usando Python e Pillow. `studio_su.py` contiene la ricostruzione dello studio superiore:

```sh
python -m pip install Pillow
python build_project.py
```

Lo script sovrascrive il progetto principale. Eventuali modifiche fatte direttamente in Sweet Home 3D vanno riportate nello script prima di rigenerare, altrimenti saranno perse.

L'XML intermedio e l'anteprima sono file generati esclusi da Git. Il progetto `.sh3d` contiene i modelli necessari e viene versionato insieme allo script.
