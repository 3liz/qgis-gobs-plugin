# G-Obs presentation

[Old concept in French](./old_french_doc)

## Glossary

### Actor

**Person or legal person** belonging to one **actor category** and allowed to take on several roles in the observation/action loop. Actors can access services or not, according to their roles. Actors are responsible for the quality of the data they provide when feeding G-Obs.

It has a _name_, an _email address_, a _contact person_.

### Actor category

A **group of actors** sharing the same social status (ex: administrations, NGO, etc.)

### Spatial object

A **geo-referenced entity** characterized by a _type of geometry_ (point, line, polygon) and a _coordinate system_, and which coincides with a geometry at each time stamp.

* In the case of fixed spatial objects, the geometry remains unchanged (ex: village boundaries are fixed multi polygon)
* Otherwise it varies along time
    - ex 1: sand track = polyline varying along time
    - ex 2: ship = polygon moving along time.

### Spatial layer

A group of **spatial objects** produced by a given **actor** and sharing the same coordinate system.

It has a _code_, a _name_, a _description_.


### Protocol

**Observation or computation method** for scientific purpose. It can be a scientific protocol in the case of measures, instructions for investigators in the case of a survey, or a mathematical formula in the case of secondary data.

It has a _code_, a _name_, a _description_, and _bibliographic references_.


### Indicator

Abstraction of **data series** for decision-making purposes.

It may correspond to several data series obeying different protocols only if these protocols are close enough to keep the semantics of the indicator with respect to decision. For example, a more precise temperature sensor replaces an old one, with the same spatial granularity and acquisition frequencies.

It has a _label_, a _description_ ; it may be either monodimensonal (one value) or multidimensional (a vector of values)
it may be associated to an _icon_ and a _category_, for the benefit of external applications : in the case of the collection of observations through G-events, the icon will appear in the left/top/right panel according to the A/B/C category.


### Data series

**Set of observations/data** ruled by the **same protocol**, linked to the **same indicator** and the **same spatial layer**, and produced by the **same actor**.

It is possible to produce a data series by combining several data series; the protocol of the new series embeds the combination formula.


### Observation / Data

**Element of a data series** characterized by the **observation context** (spatial object, date) and the **observed values** for a set of dimensions in the case of a series attached to a multidimensional indicator.


### Indicator's dimensions

Indicators may be monodimensonal (one value) or multidimensional (a vector of values) ; for example, if we wish to record inside a single observation a quantity of men and a quantity of women, there are two dimensions: **nb of men** and **nb of women**.
Each dimension has a _label_ (ex: nb of women), a _type_ (ex: integer), a _unit_ (ex: person), an _alias_ (ex: population of women).


### Import dataset

**A physical set of observations** aimed at feeding a given series.

It has a _code_.

Its structure must match the structure of the target data series.


### Information service

**A representation usable by actors** for information or decision-making purposes. As a service, its access is administrated, i.e. : a user must have the propers rights to access a given service.

The information displayed results from requests upon one or several data series, possibly linked to distinct indicators. The representtaion is usually co-designed with the client of the service.


### Project

A **project** is defined by management purpose (example : Human Wildlife Conflicts mitigation) and is characterized by a group of indicators (example : presence of lions, presence of elephants, presence of crocodiles, presence of a crocodile barrier ...).
It is defined by a code, a label, a description.
It contains a list of spatial layers associated to the data series that will feed the indicators or supporting the display of the data.


### Project view

The data series associated to a **project** can be accessed within the whole geographical zone associated to the project, or only within subzones, depending on the user rights. The whole geographical zone, as well as the sub-zones, are called "project views".

A project view is a set of spatial objects (polygons).
Each project has at least one project view (the maximal spatial extent of the project), and possibly many partial project views.


### Software function

Part of a software in charge of a numeric transformation.


### Roles in the observation/action loop

An actor may play several roles, among:

* Data producer,
* information service producer,
* information service administrator,
* information service receiver/consumer.

According to these roles, an actor has access to **information services** and/or **software functions**.


## Examples

### Pluviometry collected on meteorological stations

Source data:

* **pluviometers**: sites equipped with pluviometers to measure rainfalls, defined by a code, a name and a position (point)
* **pluviometry**: hourly rainfall pluviometry in millimetre, obtained by measuring the height of water in the pluviometers every hour.

### Population of cities

Source data:

* **Cities of Brittany, France**: defined by a code, a name and a polygon
* **Population**: Number of inhabitants for city, obtained from annual census.
