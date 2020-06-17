# CHANGELOG

### 0.3.0 - 17/06/2020

* Remove spatial layer data - new algorithm to proceed spatial layer data deletion
* Remove series data - new algorithm to proceed observation data deletion
* QGIS gobs_manager project - change SCR and map extent
* Get observation data - Add option to also get the corresponding geometry
* Publish on Github: https://github.com/3liz/qgis-gobs-plugin
* Add translation to Transifex: https://www.transifex.com/3liz-1/g-obs/dashboard/

### 0.2.11 - 05/06/2020

* Import scripts - Fix bugs related to old use of self.tr instead of tr

### 0.2.10 - 28/05/2020

* Import spatial layer - Fix bug with points & linestrings

### 0.2.9 - 27/05/2020

* Import observation data - Explicitly convert source value to target format and remove useless spaces from source data
* Import spatial layer - Check geometry types compatibility between QGIS layer and target spatial layer
* Demo data - fix encoding for subdistricts layer
* Continuous integration & test - many fixes and improvements

### 0.2.8 - 05/05/2020

* Import spatial layer data - Use ST_Buffer(geom, 0) to remove invalid geometries
* Import spatial layer data - Fix bug when opening form
* Documentation - Describe each algorithms usage and parameters.
* Documenation - Add 2 button to see Concepts and Database schema

### 0.2.7 - 12/03/2020
 
* Rename name, title, label, code fields into normalized code label
* Import observation data - Adapt alg inputs based on the indicator caracteristics

### 0.2.6 - 06/03/2020

* Create db structure - Fix bug when adding test data
* Move comments in specific SQL script file

### 0.2.5 - 24/02/2020

* Database - Update installation scripts & documentation
* QGIS - Fix bug with indicator type values (remove default value)
* Import observation - add constraint to override data only if not yet validated
* Feedback - Use reportError instead of pushInfo when needed
* Import observation - Remove useless series id in the end of series combobox
* Get series data - Fix bug giving wrong vector dimensions && remove useless series id in combo boxes
