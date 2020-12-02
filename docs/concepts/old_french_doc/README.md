---
Title: G-Obs plugin - Main concepts
Favicon: ../icon.png
Sibling: yes
...

[TOC]

# Documentation

## Introduction

Le projet s'appelle **G-Obs**.

## Dictionnaire des concepts

### Entité spatiale

Un objet défini par une géométrie et un identifiant unique. La géométrie peut être variable dans le temps (ex: Piste). Elle est caractérisée par son type (Point, ligne, polygone, etc.), son système de coordonnées de référence.

### Couche spatiale

Un regroupement d'entités spatiales conceptuellement ou techniquement homogène, caractérisé par un nom et une source

### Observation

Une donnée caractérisée par un nom d'observable, une entité spatiale, une date, une ou des valeurs, une source ou le code du jeu de données qui la contient.

### Valeurs observées

Nous appelons valeurs les dimensions du vecteur qui porte les données d'observations.

Par exemple, si on souhaite enregistrer dans un vecteur la population des hommes et la population des femmes, le vecteur contiendra 2 valeurs "population_homme" et "population_femme". Dans la plupart des cas simples, le vecteur ne contiendra qu'une seule valeur (ex: "pluviometrie").

Chaque valeur est caractérisée par un nom (ex: "pluviometrie", un type (ex: "integer"), une unité (ex: "mm"), un alias (ex: "Pluviométrie journalière")

### Protocole

Méthode de recueil d'une série d'observations en vue d'une exploitation scientifique. Il est caractérisé un code, un nom, une description, des références bibliographiques.

### Référence bibliographique

Document caractérisé par un type, un nom, une description, une URL

### Série d'observations

Un ensemble d'observations obéissant au même protocole. Si le protocole évolue, on doit créer une nouvelle série d'observations, qui se rattache au nouveau protocole. On garde ainsi un historique qui est important pour la validation scientifique.

Chaque série est caractérisée par une source (acteur) et attachée à une couche spatiale. Si la couche spatiale évolue (ex: Communes fusionnées, ou pluviomètre rajouté ou déplacé), il faut créer une nouvelle couche spatiale et une nouvelle série liée.

* Exemple des banquettes en Tunisie: on crée une couche spatiale par an
* Exemple de suvi de déplacement de moutons: chaque mouton a un code unique et est référencé par un ou plusieurs objets spatiaux. Son vrai identifiant est le couple so_unique_id et geom. Pour suivre l'évolution du déplacement de chaque mouton, on a donc plusieurs observations caractérisées chacune par un objet spatial différent.
Si on avait d'autres données que la position GPS disponibles, on pourrait les ajouter dans la valeur de l'observation, par exemple le rythme cardiaque pour l'observation.
Dans ce cas d'objets mobiles (ou de géométries variables telles que des zonages), il n'est pas utile de créer une nouvelle série à chaque ajout ou modification de géométrie dans la couche spatiale.

### Jeu de données

Un ensemble physique d'observations appartenant à la même série. En pratique, le terme est utilisé pour présenter un paquet de données présenté à un gestionnaire de données. Il est caractérisé par un code, une source. Cela peut être sous la forme d'un fichier excel par exemple.

Au moment de l'import, le gestionnaire de donnée va devoir choisir le jeu de données à importer (fichier tableur, CSV, etc.) et le rattacher à une série existante ou à créer.

Les jeux de données source ne seront pas enregistrés ni conservés dans le système d'information après import et conversion en observations.

### Acteur

Un organisme ou une personne capable de produire des observations (source), d'agir dans un territoire, de signer une charte dans le cadre d'une action collective. Il fournit les jeux de données au gestionnaire de données qui pourra les transformer en observations.

Il peut aussi valider les observations après avoir eu accès aux observations sous forme de services informationnels (cartes Lizmap).

Il est caractérisé par un nom, un email, une personne contact, une catégorie

### Catégorie d'acteurs

Regroupement d'acteurs ayant les mêmes besoins en information. Ces catégories (ou "groupes") sont utilisées par G-Obs pour déterminer les services informationels à disposition de l'acteur.

### Gestionnaire de données

Il récolte et centralise les jeux de données fournis par les acteurs. C'est lui qui importe les données dans le système.

### Indicateur

Un regroupement de données d'observation dans un but d'aide à la décision.
Il est caractérisé par un nom, une définition, un type d'entité spatiale, une granularité et une fréquence temporelle.

L'indicateur peut regrouper une seule série d'observations. Il peut aussi être utilisé pour regrouper plusieurs séries obéissant à des protocoles différents mais suffisamment voisins pour ne pas changer la sémantique de l'indicateur. Par exemple, on a remplacé un capteur de température par un nouveau système plus précis, mais on a conservé les fréquences d'acquisition, les sites de mesure, etc.

L'indicateur permet aussi de rassembler des données observées sur des sites ou des terrains différents.

Si on souhaite utiliser des données de plusieurs séries pour les combiner et créer une nouvelle donnée, on devra passer par la création d'un nouvelle série de données dont le nouveau protocole contiendra la formule de calcul. C'est l'acteur source qui fera ce travail de création de la nouvelle série.


### Chemins d'accès

Pour faciliter la navigation et le choix parmi les indicateurs, on rattache à chaque indicateur un ou plusieurs chemins d'accès. Un chemin se caractérise par une suite ordonnée de mots-clés précisant progressivement la thématique puis l'indicateur.

Par exemple, pour accéder à l'indicateur "Pluviométrie", deux chemins sont possibles

* Environnement / Changement climatique / Pluviométrie
* Gestion de l'eau / Pluviométrie

On formalise le stockage des chemins d'accès via un graphe orienté en évitant les boucles.

C'est le gestionnaire de données qui a la maîtrise totale sur le graphe, car il est responsable de la création des indicateurs.

### Service informationnel

Un service de présentation d'indicateurs qui répond aux besoins et aux préférences d'une catégorie d'acteur en vue d'une aide à la décision. Par exemple des graphiques, des cartes thématiques.

Par exemple, un projet QGIS publié vers une carte Web peut être ici le sujet de la gestion des droits.

Un outil d'importation est aussi un service informationnel, car il répond aux besoins d'administration des données, et doit être restreint à des groupes d'utilisateurs.

La construction d'un service informationnel (par exemple un projet QGIS) est aussi un service informationnel, à destination des géomaticiens.

## Modèle physique des données

[Voir la documentation de la base](https://docs.3liz.org/qgis-gobs-plugin/database/relationships.html)


## Scénarios d'utilisation

On décrit dans ce chapitre les étapes essentielles à la publication de services informationnels. Chaque étape peut être conduite par des personnes différentes selon leur rôle dans la mise en oeuvre.

### Administration des données

Cette étape doit être réalisée avant l'import, en amont, pour préparer l'accueil des données. C'est le rôle de l'administrateur de données. Elle consiste à nourrir le modèle de données:

* Description des acteurs, catégories d'acteurs
* Description des protocoles
* Description séries d'observations
* Description des indicateurs
* Description des couches spatiales

Voir MCD ci-dessus.

### Gestion des données

C'est le rôle du gestionnaire de données. Cette étape consiste à:

* choisir les jeux de données à importer (feuille Excel, fichier CSV, etc.) et les couches spatiales de référence.
* rattacher ces données à la série d'observations et à un acteur (fournisseur du jeu de données). Si la série n'existe pas, il faut faire appel à l'administrateur pour la créer ainsi que les données liées (protocole, acteur, etc.)
* transférer des données spatiales d'une ou plusieurs couches (référentiels spatiaux sur lesquels se rattachent les données d'observation). Le transfert consiste à envoyer les données vers le serveur de base de données.
* importer les données d'observation en précisant le lien à la couche spatiale. Il devra aussi valider le lien entre les composantes de la source (champs) et les composantes de la cible (dimensions du vecteur). Par exemple, dans le jeu de données à importer, il dispose de 2 champs f_pop et h_pop, qu'il devra relier aux dimensions population_homme et population_femme de la valeur de l'indicateur.

Un journal d'import est automatiquement rempli à chaqe import d'un jeu de données. Il est caractérisé par une date, un acteur, une série d'observations et un statut de validation: import en attente de validation / import validé. Chaque observation est rattachée à un code d'import.

Lors de l'import, le gestionnaire (ou l'outil) doit vérifier que toutes les données du jeu de données ont une correspondance aux objets spatiaux de la couche spatiale définie. Si non, l'import est invalidé.

Lors de la création de cet import, un message est envoyé à l'acteur, avec un lien vers un service informationnel qui lui permet de visualiser les données importées (l'outil choisit la première carte accessible). Il se connecte en tant qu'acteur dans l'application de visualisation (Lizmap). Il peut alors appliquer un filtre sur les données pour ne voir que les données de l'import à valider.

Après vérification, il peut valider l'import via un élément d'interface.

Les données non validées ne sont visibles que pour certains groupes d'utilisateurs (acteurs fournisseurs de données, gestionnaires et administrateurs). Les autres utilisateurs ne voient que les données validées.

Le gestionnaire de données peut ajouter des données. Il peut réimporter un jeu de donnée amélioré par l'acteur, ce qui écrase les données non validées. On s'appuie sur l'objet spatial, le vecteur, la date et la série d'observation pour gérer cette contrainte d'unicité de chaque observation (identifiant). L'outil gère automatiquement les différents cas:

* Si l'observation existe déjà et a été validée : pas d'écrasement.
* Si l'observaton n'existe pas, elle est ajoutée, a le statut par défaut (non validée)
* Si l'observation existe et qu'elle n'est pas validée, elle est écrasée par la nouvelle.
* Pour pouvoir supprimer des données, il faut permettre de gérer un champ "a supprimer" ou une valeur "delete" ou "-1" qui permet de supprimer les données d'observation de manière contrôlée. Ajouter les UUID des observatoins supprmées dans une table de log.
Le gestionnaire des données peut facilement connaître les données importées dans la base non validées, et ainsi contacter si besoin ou supprimer les données après accord.

### Création d'un service informationnel

Cela correspond par exemple à la création d'un projet QGIS, et à sa publication dans Lizmap.

Toutes les sources des séries d'observations utilisées dans le projet QGIS sont visibles par les utilisateurs à qui on a donné le droit (outil de gestion des groupes d'utilisateurs)


## Outils et traitements

### Administration des données

Il s'agit:

* de créer le vocabulaire, de lister les acteurs, les protocoles, le catalogue de couches, les séries d'observations et indicateurs, pour un observatoire.
* de gérer les droits d'accès selon les catégories d'utilisateurs

On utilise les capacités de QGIS à produire des outils de saisie riches via des formulaires. Les relations entre couches permettent de lier les données entre elles.

### Gestion des données

Il s'agit d'importer les données d'observation dans le système à partir des jeux de données fournis par les acteurs. On passe des données source aux indicateurs, via un travail de consolidation et d'homogénéisation de la donnée.

Liste:

* Voir la liste des couches spatiales
* Voir les relations entre les couches et les indicateurs (comment est faite la jointure)
* Import d'une couche spatiale
* Import d'un jeu de données
* Tableau de bord qui permet de chercher les observations (voir Extraction des données ci-dessous)

Notes:

* Ce n'est pas au gestionnaire de données de faire la jointure spatiale entre couche spatiale et indicateur, car elle a été pensée en amont et décrite par l'administrateur de données. Le gestionnaire doit simplement alimenter les indicateurs.
* Le gestionnaire peut voir l'ensemble des données décrites par l'administrateur, sans pouvoir les modifier. Cela lui permet de connaître les listes d'acteur, d'indicateur, de couches spatiales, etc.


### Exploration des données

Il s'agit d'avoir un état de la connaissance des données du système.

On permet à l'administrateur, au gestionnaire de récupérer des informations sur les indicateurs correspondant aux filtres de recherche suivants:

* temporel : dans un intervalle de date (ou par exemple "le mois dernier")
* spatial : dans un rectangle d'emprise ou dans une couche de type polygone
* indicateur(s)
* acteur(s) source

Une fois le ou les filtres spécifié, on lance la recherche. Les résultats sont affichés sous la forme d'un tableau présentant une ligne par indicateur

* le nom de l'indicateur
* la couche spatiale
* les acteurs source
* le nombre total d'observations
* les dates minimum et maximum des observations
* la date de dernier import
* les chemins d'accès
* les services informationnels qui référencent l'indicateur (lien direct vers la carte)
* un bouton pour charger la couche spatiale
* un bouton pour charger les données dans l'outil de visualisation

### Représentation des données

Il s'agit de récupérer les informations depuis le système dans un format exploitable par les outils bureautique et géomatiques ( Tableur, QGIS et Lizmap ), afin de créer des modèles de représentation au pilotage de l'action collective: cartes, graphiques, tableaux, etc.

Le géomaticien peut récupérer les données converties au format SIG ou tableur via un outil qui présente les filtres de recherche suivants:

* choix de l'indicateur
* filtre spatial : dans un rectangle d'emprise ou dans une couche vectorielle de type polygone présente dans QGIS
* filtre temporel : dans un intervalle de date (ou par exemple "le mois dernier")

Il lance la recherche, qui lui présente un tableau synthétique sur les données filtrée de l'indicateur (équivalent à l'explorateur décrit au chapitre précédent)

* le nom de l'indicateur
* la couche spatiale
* les acteurs source
* le nombre total d'observations
* les dates minimum et maximum des observations
* la date de dernier import
* les chemins d'accès
* les services informationnels qui référencent l'indicateur (lien direct vers la carte)
* un bouton pour charger la couche spatiale
* un bouton pour charger les données

Les options suivantes sont présentées pour faciliter le chargement des données:

* charger les données brutes : cela ajoute dans QGIS une couche non spatiale contenant les données de l'indicateur avec le champ de jointure. Une relation est automatiquement créée dans le projet QGIS entre la couche spatiale chargée précédemment et les données brutes.

* charger les données d'indicateur aggrégées par un à plusieurs critères:

  - à l'unité temporelle : minute, heure, journée, mois, année (par exemple, 36 lignes avec la somme des hauteurs d'eau par mois entre 2016 et 2018)
  - à l'unité temporelle unique. Par exemple, la moyenne des hauteurs d'eau tombées pour chacun des 12 mois, toutes années confondues
  - à l'objet spatial de la couche de référence. Par exemple, une ligne par pluviomètre avec la somme des hauteurs d'eau
  - choix de la fonction de calcul : décompte, somme, moyenne, minimum, maximum, médiane

Les couches résultantes sont générées par l'outil, en se basant sur des requêtes SQL. Les données sont donc affichées dynamiquement, sans avoir besoin de les rafraîchir à chaque nouvel import.

Chaque requête est représentée comme une couche stockée dans QGIS, qui pourra êre publié comme un service informationnel avec des droits différents que les droits de la donnée brute.

Le géomaticien doit lier le projet QGIS qui porte les modes de représentations au service informationnel présent dans le système (créé en amont par l'administrateur de données).


### Publication des SI

Il s'agit de proposer un accès web aux services informationnels qui peuvent intégrer plusieurs modèles de représentation pour différents indicateurs.


## Interfaces

###  Lizmap

#### Page d'accueil

Points importants:

* Une interface qui s'adapte aux écrans de différentes tailes ("responsive design")
* Chaque service informationnel est comme une petite application qui délivre de l'information (un à plusieurs indicateurs). On propose l'analogie avec la liste des applications présente sur un smartphone.
* La page d'accueil présente une liste des services informationnels, représentés par une image. Un clic sur cette image lance l'affichage de la carte.
* La présentation de cette liste est paramétrable, avec un choix de l'ordre des présentations des services informationnels:

  - mise à jour de la donnée la plus récente en premier
  - ordre alphabétique
  - affichage des nouveaux services informationnels en premier

L'utilisateur peut filtrer les services informationnels affichés via les chemins d'accès. Pour cela, on lui présente un outil de recherche avec une autocomplétion, qui lui permet de parcourir les mots-clé des chemins d'accès.

    [ champ de recherche ] [ paramètre de tri ]
    **1ER NOEUD SELECTIONNE**
    **FILS DU 1ER NOEUD SELECTIONNE**
    *Petit fils A sélectionnable*
    *Petit fils B sélectionnable* -> idem
    *Petit fils C sélectionnable* -> idem

    Affichage filtré des services informationnels
    [ SI 1 ] [ SI 2 ] [ SI 3 ] [ SI 4 ]
    [ SI 5 ] [ SI 6 ] [ SI 7 ] [ SI 8 ]
    [ SI 9 ] [ SI10 ] [ SI11 ] [ SI12 ]
    [ SI13 ] [ SI14 ] ...


A l'arrivée sur la page d'accueil:

* l'utilisateur voit le champ de filtre vide, avec la mention "Taper votre recherche". On active l'autocomplétion.
* Sous le champ de filtre, on présente les premiers noeuds fils (mots-clés). Par exemple:

    Eau
    Qualité
    Gouvernance

Lorsque l'utilisateur clique sur un des fils, celui-ci passe en mode "sélectionné" (par exemple en gras avec un fond de couleur). Sur sélection de ce mot-clé, on présente directement en dessous les fils directs, en mode "sélectionnable" (par exemple en italique et avec un fond clair)

Le champs de filtre présente via une autocomplétion l'ensemble des fils directs du dernier noeud sélectionné. A l'arrivée, on peut donc chercher directement un fils éloigné.

On pourra adapter la disposition des noeuds sélectionnés en mode horizontal (fils d'ariane) pour les écrans larges, et en mode vertical avec les mots-clé empilés sur les petits écrans.

TODO

* renommer le series.fk_id_actor en series.fk_id_actor_observer
* ajouter un champ import.fk_id_actor_import pour préciser quel acteur a importé le jeu de données (gestionnaire de donnée par exemple)

