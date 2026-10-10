# Planimetria su due livelli

Progetto Sweet Home 3D ricostruito da una planimetria abbozzata e dalle foto degli ingressi e della scala.

Aprire `Planimetria_due_livelli.sh3d` in Sweet Home 3D. Questo è il file principale: gli aggiornamenti vengono salvati sempre nello stesso file.

## Stato attuale

- Due livelli con muri, ambienti, porte e finestre.
- Piano inferiore di circa 90 m² interni; dimensioni e altezze stimate.
- Scala aperta con pedate in legno, curva a ventaglio, struttura e ringhiera nere.
- Vano scala e parapetto con cancelletto al piano superiore.
- Lucernari indicati in pianta; falde del tetto ancora da definire.
- Arredamento degli ambienti da aggiungere a partire dalle fotografie.

## Rigenerazione

`build_project.py` genera il file `.sh3d` e un'anteprima usando Python e Pillow:

```sh
python -m pip install Pillow
python build_project.py
```

Lo script sovrascrive il progetto principale. Eventuali modifiche fatte direttamente in Sweet Home 3D vanno riportate nello script prima di rigenerare, altrimenti saranno perse.

L'XML intermedio e l'anteprima sono file generati esclusi da Git. Il progetto `.sh3d` contiene i modelli necessari e viene versionato insieme allo script.
