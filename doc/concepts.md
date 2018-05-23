# Documentation

## Dictionnaire des concepts

### Entité spatiale

Un objet défini par une géométrie et un identifiant unique. La géométrie peut être variable dans le temps (ex: Piste). Elle est caractérisée par son type (Point, ligne, polygone, etc.), son système de coordonnées de référence.

### Couche spatiale

Un regroupement d'entités spatiales conceptuellement ou techniquement homogène, caractérisé par un nom et une source

### Observation

Une donnée caractérisée par un nom d'observable, une entité spatiale, une date, une ou des valeurs, une source ou le code du jeu de données qui la contient.

### Valeurs observées

Nous appelons valeurs les dimensions du vecteur qui porte les données d'observations.

Par exemple, si on souhaite enregistrer dans un vecteur la population des hommes et la population des femmes, le vecteur contiendra 2 valeurs "population_homme" et "population_femme". Dans la plupart des cas simples, le vecteur ne contiendra qu'une seule valeur (ex: "pluviometrie"). Chaque valeur est caractérisée par un nom (ex: "pluviometrie", un type (ex: "integer"), une unité (ex: "mm"), un alias (ex: "Pluviométrie journalière")

### Protocole

Méthode de recueil d'une série d'observations en vue d'une exploitation scientifique. Il est caractérisé un code, un nom, une description, des références bibliographiques.

### Série d'observations

Un ensemble d'observations obéissant au même protocole. Si le protocole évolue, on doit créer une nouvelle série d'observations, qui se rattache au nouveau protocole. On garde ainsi un historique qui est important pour la validation scientifique.

### Jeu de données

Un ensemble d'observations conceptuellement homogène ou techniquement cohérent. En pratique, le terme est utilisé pour présenter un paquet de données présenté à un utilisateur. Il est caractérisé par un code, une source.

### Acteur

Un organisme ou une personne capable de produire des observations (source), d'agir dans un territoire, de signer une charte dans le cadre d'une action collective.

### Catégorie d'acteurs

Regroupement d'acteurs ayant les mêmes besoins en information.

### Indicateur

Un regroupement de données d'observation dans un but d'aide à la décision. Il est caractérisé par un nom, une définition, un type d'entité spatiale, une granularité et une fréquence temporelle. Soit une série d'observations, soit une formule de calcul portant sur une ou plusieurs séries d'observations et de couches spatiales. Une personne morale est choisie en tant que gestionnaire responsable.

Il peut être utilisé par exemple pour rassembler deux séries d'observations obéissant à 2 protocoles différents mais proches du point de vue de l'exploitation en vue de décider et d'agir. Par exemple, on a remplacé un capteur de température par un nouveau système plus précis, mais on a conservé les fréquences d'acquisition, les sites de mesure, etc. L'indicateur permet aussi de rassembler des données observées sur des sites ou des terrains différents.

### Chemins d'accès

Pour faciliter la navigation et le choix parmi les indicateurs, on rattache à chaque indicateur un ou plusieurs chemins d'accès. Un chemin se caractérise par une suite ordonnée de mots-clés précisant progressivement la thématique puis l'indicateur.

Par exemple, pour accéder à l'indicateur "Pluviométrie", deux chemins sont possibles

* Environnement / Changement climatique / Pluviométrie
* Gestion de l'eau / Pluviométrie

### Service informationnel

Un service de présentation d'indicateurs qui répond aux besoins et aux préférences d'une catégorie d'acteur en vue d'une aide à la décision. Par exemple des graphiques, des cartes thématiques. Est candidat pour une implémentation en tant ue projet QGIS. Un projet QGIS peut être ici le sujet de la gestion des droits.

## Modèle conceptuel de données

![](media/modele_conceptuel.png)
