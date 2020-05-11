## Import des données

### Création d'un acteur, source de la donnée

- code
- nom
- description
- site internet
- email

### Import des entités spatiales et définition d'une couche spatiale (si besoin)

#### Création

- nom
- code
- source (todo: préciser le concept : acteur ou autre, ex IGN, OpenStreetMap)
- couche vectorielle QGIS source
- champ d'identifiant unique (ex: Code INSEE d'une commune)
- champ d'étiquette (ex: Nom de la commune)
- type de géométrie (Point, Linestring, Polygon, MultiPoint, MultiLinestring, MultiPolygon)
- srid de la couche source (ex: 2154, pour permettre la conversion)


#### Mise à jour

- nom
- ajouter ou écraser
- couche vectorielle QGIS source
- champ d'identifiant unique (ex: Code INSEE d'une commune)
- champ d'étiquette (ex: Nom de la commune)
- type de géométrie (Point, Linestring, Polygon, MultiPoint, MultiLinestring, MultiPolygon)
- srid de la couche source (ex: 2154, pour permettre la conversion)


### Import des observations

#### Définition du protocole

- code
- nom
- description
- références bibliographiques
- acteur (= auteur, responsable du protocole) ?

#### Import des observations

- protocole
- couche QGIS source (spatiale ou non spatiale)
- couche spatiale support
- champ contenant l'identifiant de l'objet spatial dans la couche spatiale (correspondant au champ d'identifiant unique renseigné dans la couche spatiale, ex: Code INSEE)
- champ contenant l'information temporelle (date)
- format de date à stocker (résolution temporelle : seconde, heure, jour, mois, année)

- champ(s) contenant les valeurs à stocker
- nom souhaité pour chaque clé (ex: pluviometrie) ['population_homme', 'population_femme']
- type de valeur pour chacun de ces champs (Ex: entier, réel, texte, booléan, etc.) ['integer', 'integer']
- unité de chaque clé (Ex: mm, °C, etc.) ['','']
- alias souhaité pour chaque clé (Ex: Pluviométrie) ['Population (hommes)', 'Population (femmes)']



## Récupération des données


## Calculs sur les données


## TODO

Cas de figure exotique : une couche de lac (2 lacs A et B) dont la géométrie évolue au cours du temps (par ex une géométrie différente par année). 2 possibilités:

* stocker l'ensemble des géométries dans spatial_object et stocker dans data un lien dont le vecteur contient le code du lac {"code": "A"} et d_timestamp permet de connaître l'année.

* stocker le centroide de A et B dans spatial_object et stocker dans data autant de lignes que de couple géométrie/année. Les clés étant ["geometrie", "année"]
