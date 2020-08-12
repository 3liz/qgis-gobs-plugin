---
Title: G-Obs plugin - Admin guide
Favicon: ../icon.png
Sibling: yes
...

[TOC]


## Introduction

The **administrator** is in charge of describing the different data stored in the G-Obs database:

* actors,
* spatial layers,
* protocols,
* indicators,
* series of data.

See the (documentation on these concepts)(../concepts/).

To go on, you must first have installed and configured the G-Obs plugin for QGIS Desktop. See the doc [G-Obs installation and configuration](../installation/)

## Create your database local interface

This algorithm will create a **new QGIS project file** for G-Obs administration purpose.

The generated QGIS project must then be opened by the administrator to create the needed metadata by using QGIS editing capabilities (actors, spatial layers information, indicators, etc.)

Parameters:

* `PostgreSQL connection to G-Obs database`: name of the database connection you would like to use for the new QGIS project.
* `QGIS project file to create`: choose the output file destination.

![Create administration project](../media/gobs_create_database_local_interface.jpg)

## Edit the database metadata

The **administration project** created beforehand will allow the administrator to **create, modify and delete metadata** in the G-Obs database. As an administrator, you must open this project with QGIS.

Be sure you have a working connection between your computer and the database server.

Once opened, the QGIS project is configured to allow the administrator to edit the data. In the QGIS **Layers** panel, you will see the following layers:

![G-Obs administration layers](../media/gobs_administration_layers.jpg)

These layers represent the G-Obs PostgreSQL tables which are in charge of storing the metadata and data. In QGIS, you can edit the table data by toggling the **editing mode** for each layer:

* Select the layer in the panel by clicking on it: the layer is highlighted in blue
* Right-click on the layer name and select `Toggle Editing`

Before going on, please **toggle editing** for all the following layers:

* actor_category
* actor
* spatial_layer
* indicator
* protocol
* series

We will illustrate the administration task with an example, by editing these layers in the same order as above. Please refer to the (documentation on G-Obs concepts)(../concepts/) to understand the procedure.

### actor_category

Example content:

| id | ac_label             | ac_description |
|----|----------------------|----------------|
| 1  | Public organizations |                |
| 2  | Research centers     |                |



### actor

Example content

| id                                 | a_label          | a_description                                                                                                                                               | a_email        | id_category |
|------------------------------------|------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------|-------------|
| 1                                  | IGN              | French national geographical institute.                                                                                                                     | contact@ign.fr | 1           |
| 3                                  | DREAL Bretagne   | Direction régionale de l'environnement, de l'aménagement et du logement, région Bretagne.                                                                   | email@dreal.fr | 1           |
| 2                                  | CIRAD            | "The French agricultural research and international cooperation organization working for the sustainable development of tropical and Mediterranean regions. |                |             |
|                                    |                  |                                                                                                                                                             |                |             |
| https://www.cirad.fr/en/home-page" | contact@cirad.fr | 2                                                                                                                                                           |                |             |


### spatial_layer

Example content

| id | sl_code         | sl_label                    | sl_description                                       | sl_creation_date | fk_id_actor | sl_geometry_type |
|----|-----------------|-----------------------------|------------------------------------------------------|------------------|-------------|------------------|
| 1  | pluviometers    | Pluviometers                | Sites equiped with pluviometers to measure rainfalls | 2019-06-26       | 2           | point            |
| 2  | brittany-cities | Cities of Brittany , France | Cities of Brittany, France                           | 2019-07-05       | 2           | multipolygon     |


### indicator

Example content

| id | id_code     | id_label            | id_description                            | id_date_format | id_value_code | id_value_name | id_value_type | id_value_unit | id_paths                                                                |
|----|-------------|---------------------|-------------------------------------------|----------------|---------------|---------------|---------------|---------------|-------------------------------------------------------------------------|
| 1  | pluviometry | Hourly pluviometry  | Hourly rainfall pluviometry in millimetre | hour           | pluviometry   | Pluviometry   | real          | mm            | Environment / Water / Data \| Physical and chemical conditions / Water  |
| 2  | population  | Population          | Number of inhabitants for city            | year           | population    | Population    | integer       | people        | Socio-eco / Demography / Population                                     |


### protocol

Example content

| id | pr_code           | pr_label    | pr_description                              |
|----|-------------------|-------------|---------------------------------------------|
| 1  | cirad-pluviometry | Pluviometry | Measure of rainfall in mm                   |
| 2  | cirad-population  | Population  | Number of inhabitants obtained from census. |

### series

Example content

| id | fk_id_protocol | fk_id_actor | fk_id_indicator | fk_id_spatial_layer |
|----|----------------|-------------|-----------------|---------------------|
| 1  | 1              | 2           | 1               | 1                   |
| 2  | 2              | 2           | 2               | 2                   |


