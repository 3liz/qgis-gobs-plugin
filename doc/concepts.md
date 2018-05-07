## Dictionnaire des concepts

### Entité spatiale

Un objet défini par une géométrie et un identifiant unique. La géométrie peut être variable dans le temps (ex: Piste). Elle est caractérisée par son type (Point, ligne, polygone, etc.), son système de coordonnées de référence.

### Couche spatiale

Un regroupement d'entités spatiales conceptuellement ou techniquement homogène, caractérisé par un nom et une source

### Observation

Une donnée caractérisée par un nom d'observable, une entité spatiale, une date, une ou des valeurs, une source ou le code du jeu de données qui la contient.

### Clés et valeurs

Comment appeler le ou les items d'un vecteur. Je propose clé (concept clé-valeur ou key-value en anglais). Par exemple, si on souhaite enregistrer dans un vecteur la population des hommes et la population des femmes, le vecteur contiendrait 2 clés "population_homme" et "population_femme" avec les valeurs respectives. Dans la plupart des cas simple, le vecteur ne contiendra qu'une seule clé (ex: "pluviometrie"). Chaque clé est caractérisée par un nom (ex: "pluviometrie", un type (ex: "integer"), une unité (ex: "mm"), un alias (ex: "Pluviométrie journalière")

### Protocole

Méthode de recueil d'une série d'observations en vue d'une exploitation scientifique. Il est caractérisé un code, un nom, une description, des références bibliographiques.

### Série d'observations

Un ensemble d'observations obéissant au même protocole.

### Jeu de données

Un ensemble d'observations conceptuellement homogène ou techniquement cohérent. En pratique, le terme est utilisé pour présenter un paquet de données présenté à un utilisateur. Il est caractérisé par un code, une source.

### Acteur

Un organisme ou une personne capable de produire des observations (source), d'agir dans un territoire, de signer une charte dans le cadre d'une action collective.

### Catégorie d'acteurs

Regroupement d'acteurs ayant les mêmes besoins en information.

### Indicateur

Un regroupement de données d'observation dans un but d'aide à la décision. Il est caractérisé par un nom, une définition, un type d'entité spatiale, une granularité et une fréquence temporelle. Soit une série d'observations, soit une formule de calcul portant sur une ou plusieurs séries d'observations et de couches spatiales. Une personne morale est choisie en tant que gestionnaire responsable.

### Service informationnel

Un service de présentation d'indicateurs qui répond aux besoins et aux préférences d'une catégorie d'acteur en vue d'une aide à la décision. Par exemple des graphiques, des cartes thématiques. Est candidat pour une implémentation en tant ue projet QGIS. Un projet QGIS peut être ici le sujet de la gestion des droits.

## Modèle conceptuel de données

![](media/modele_conceptuel.png)
