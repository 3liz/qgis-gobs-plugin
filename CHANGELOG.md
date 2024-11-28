# Changelog

## Unreleased

## 6.3.1 - 2024-11-28

### Changed

* Change minimum QGIS version to 3.28
* Unit tests - Use version QGIS 3.34 instead of 3.28

### Fixed

* SQL - upgrade script to 6.3.0: remove useless INSERT

## 6.3.0 - 2024-11-27

### Changed

* QGIS Administration project
  * Prevent from editing some tables (`actor_category`, `observation`, etc.)
  * Remove the `actor` child attribute table in the `actor_category` form
  * Remove some layers from Lizmap attribute table configuration
  * Reorder attribute layers & editable layers
* Database
  * Remove the useless `application` table
  * Remove the NOT NULL constraint on the `actor.a_login` column
  * Observation & protocol - Add a trigger function which prevents from editing an observation older than the protocol duration

  ### Fixed

* Import spatial layer data alg: remove unneeded `int` cast

## 6.2.0 - 2024-05-06

* QGIS Administration project
  * Move back PostgreSQL connection to sslmode=prefer
  * Set the file type of the target file to QGIS project
  * Add a Lizmap Web Client configuration file
  * Do not allow special chars on the indicators dimension code values
* Import observation data - change titles of the algorithm input values `Source data & Field containing the spatial object id`
* Observation & protocol - Add a trigger function which prevents from editing an observation older than the protocol duration
* Test - Docker : change QGIS version to 3.28

## 6.1.0 - 2023-07-25

* Database structure - Improve the tables project and project_view
* Import observation data - Allow negative values for integer and real

## 6.0.2 - 2023-04-27

* Import observation data - Fix missing table prefix
* Administration QGIS project - user sslmode=prefer instead of disable

## 6.0.1 - 2023-04-04

* Version check - Get the available migrations from the database
  version instead of from the plugin version
* Migration - Fix a bug preventing to upgrade do 6.0.0 from old databases

## 6.0.0 - 2023-03-27

* Indicator - Move the dimensions characteristics into a new dedicated table

## 5.2.2 - 2023-03-06

* Re-enable all languages in the plugin

## 5.2.1 - 2023-03-02

* Improved the message about the database version and if migrations are available
* Temporary disabling translations, this version is only available in English

## 5.2.0 - 2023-02-24

* G-Obs right panel
    - Show the buttons "Create database structure"
      and "Upgrade database structure" only when the project variable
      `gobs_is_admin` has the value `yes` in the project properties.
    - Display the plugin version and the database structure version
      at the top of the panel and add messages depending on these versions.
* Temporary disabling translations, this version is only available in English

## 5.1.0 - 2022-10-07

* Get aggregated data
  * Fix wrong use of aggregate functions on incompatible data types
  * Add `count`, `count_distinct` and `string_agg` aggregates
* Database
  * Add project and project_view tables
  * Add new table `gobs.application`
  * Update documentation
* Admin QGIS project:
  * upgrade project to 3.16
  * use SSL prefer mode for PostgreSQL connection
* Get observation data - Add 2 columns `observation_start` & `observation_end`
  with the start and end timestamp of the observation, formatted in respect of the indicator
  specified date format
* Create database structure - New option to add observation and spatial object data
* Code style - Fix Python PEP8 issues
* Tests - Add new SQL file containing observation and spatial_object data
* Docs - Update concepts and admin guide WIP
* CI & tests -Use docker compose plugin instead of docker-compose


## 5.0.1 - 2021-05-31

* Fix some migrations about the API in QGIS 3.16

## 5.0.0 - 2021-04-07

* Add button in the help menu to open the online webpage https://docs.3liz.org/qgis-gobs-plugin
* Raise the QGIS minimum version to 3.16
* Update the documentation website with MkDocs

## 0.4.3 - 2021-04-07

* Actor - Add a new "a_login" column with unique constraint
* Administration - Update QGIS admin project template
* Docs - Update Schemaspy

## 0.4.2 - 2021-03-15

* Import observations - specify the series spatial layer id to match spatial objects: fix some bugs if spatial objects shared the same codes for different spatial layers.
* Import - Spatial layer: add new SQL functions to check related observations
* Admin - Update the QGIS administration project template with the new document layer
* Doc - Update Schemaspy database documentation

## 0.4.1 - 2020-12-02

Admin - Update administration project template
Docs - Update admin guide
Docs - Add Processing documentation
Docs - Update SchemaSpy database structure documentation: https://docs.3liz.org/qgis-gobs-plugin/database/
Docs - Database doc generation: improve compatibility with PG13
Fix some packaging issues about Transifex

## 0.4.0 - 2020-12-02

* Database structure - Add needed tables and fields for G-Event API:
   - indicator: category, created_at and updated_at
   - observation: end timestamp, uid, created_at and updated_at
   - spatial object: start and end of validity dates, uid, created_at and updated_at
   - new table document to store indicator documents
   - new table deleted_data_log to store indicator documents
   - new trigger to calculate created_at and updated_at, and auto-change validity date for spatial objects
* Import - Observation data: manage new field end date (manual or from field)
* Import - Spatial layer objects: allow multiple versions with validity dates
* Test data - Add tracks data & update pluviometers and cities data
* Tests - Add test for the import spatial layer data algorithm
* Docs - Update database documentation
* Continuous Integration - Move from CI to GitHub actions
* Makefile - Add sql command to export & reformat SQL install scripts
* Docs - Improve administration guide

## 0.3.1 - 2020-08-12

* Documentation - Publish documentation to https://3liz.github.io/qgis-gobs-plugin/ (installation, concepts, admin guide, user guide & database)
* Algorithms - New algorithm to create a database local interface for admins as a QGIS project
* Active PostgreSQL connection - Use a QGIS project variable instead of a QGIS global variable to store the connection name used
* Dock - Reorganize buttons, display the chosen database connection on top
* Dock - Replace helps buttons by single online help button

## 0.3.0 - 2020-06-17

* Remove spatial layer data - new algorithm to proceed spatial layer data deletion
* Remove series data - new algorithm to proceed observation data deletion
* QGIS gobs_manager project - change SCR and map extent
* Get observation data - Add option to also get the corresponding geometry
* Publish on GitHub: https://github.com/3liz/qgis-gobs-plugin

## 0.2.11 - 2020-06-05

* Import scripts - Fix bugs related to old use of `self.tr` instead of `tr`

## 0.2.10 - 2020-05-28

* Import spatial layer - Fix bug with points & linestrings

## 0.2.9 - 2020-05-27

* Import observation data - Explicitly convert source value to target format and remove useless spaces from source data
* Import spatial layer - Check geometry types compatibility between QGIS layer and target spatial layer
* Demo data - fix encoding for sub-districts layer
* Continuous integration & test - many fixes and improvements

## 0.2.8 - 2020-05-05

* Import spatial layer data - Use ST_Buffer(geom, 0) to remove invalid geometries
* Import spatial layer data - Fix bug when opening form
* Documentation - Describe each algorithm usage and parameters.
* Documentation - Add 2 button to see Concepts and Database schema

## 0.2.7 - 2020-03-12

* Rename name, title, label, code fields into normalized code label
* Import observation data - Adapt alg inputs based on the indicator characteristics

## 0.2.6 - 2020-03-06

* Create db structure - Fix bug when adding test data
* Move comments in specific SQL script file

## 0.2.5 - 2020-02-24

* Database - Update installation scripts & documentation
* QGIS - Fix bug with indicator type values (remove default value)
* Import observation - add constraint to override data only if not yet validated
* Feedback - Use reportError instead of pushInfo when needed
* Import observation - Remove useless series id in the end of series combobox
* Get series data - Fix bug giving wrong vector dimensions && remove useless series id in combo boxes
