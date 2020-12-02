---
Title: G-Obs plugin - Main concepts
Favicon: ../icon.png
Index: yes
...

[TOC]

## G-Obs presentation

todo

## Glossary

### Actor

**Person or legal person** belonging to one **actor category** and allowed to take on several roles in the observation/action loop.

It has a **name**, an **email address**, a **contact person**.

### Actor category

A **group of actors** sharing the **same social status** (ex: administrations, NGO, etc.)

### Spatial object

A **geo-referenced entity** characterized by a **type of geometry** (point, line, polygon) and a **coordinate system**, and which coincides with a geometry at each time stamp.

* In the case of fixed spatial objects, the geometry remains unchanged (ex: village boundaries are fixed multi polygon)
* Otherwise it varies along time
    - ex 1: sand track = polyline varying along time
    - ex 2: ship = polygon moving along time.

### Spatial layer

A group of **spatial objects** produced by a **given actor** and sharing the same coordinate system.

It has a **code**, a **name**, a **description**.

### Protocol

**Observation method** for scientific purpose.

It has a **code**, a **name**, a **description**, and **bibliographic references**.

### Indicator

**Abstraction of observation series** for decision-making purposes.

It has a **name**, a **definition**, a **type of geometry**, a **granularity** and a **frequency**.

It may correspond to several series obeying different protocols only if these protocols are close enough to keep the semantics of the indicator with respect to decision. For example, a more precise temperature sensor replaces an old one, with the same spatial granularity and acquisition frequencies.

### Data series

**Set of observations** ruled by the **same protocol**, linked to the **same indicator** and the **same spatial layer**, and produced by the **same actor**.

It is possible to produce a data series by combining several data series: the protocol of the new series embeds the combination formula.

### Observation / Data

**Element of a series** characterized by the observation **context** (spatial object, date) and the **observed values** for a set of observation dimensions.

### Observation dimensions

For example, if we wish to record inside a single observation a quantity of men and a quantity of women, there are two dimensions: **nb of men** and **nb of women**.

Each dimension has a **label** (ex: nb of women), a **type** (ex: integer), a **unit** (ex: person), an **alias** (ex: population of women).

### Import dataset

**A physical set of observations** aimed at feeding a given series.

It has a **code**.

Its structure must match the structure of the target data series.

### Informational service

**A representation usable by actors** for information or decision-making purposes.

It **aggregates and transforms** heterogeneous data series.

It is the role of the informational service **administrator** to administrate information services.

### Software function

Part of a software in charge of a **numeric transformation**.

### Roles in the observation/action loop

An actor may play several roles, among:

* Data producer,
* informational service producer,
* informational service administrator,
* informational service receiver/consumer.

According to these roles, an actor has **access to informational services** and/or **software functions**.


## Examples

### Pluviometry collected on meteorological stations

Source data:

* **pluviometers**: sites equiped with pluviometers to measure rainfalls, defined by a code, a name and a position (point)
* **pluviometry**: hourly rainfall pluviometry in millimetre, obtained by measuring the height of water in the pluviometers every hour.

### Population of cities

Source data:

* **Cities of Brittany, France**: defined by a code, a name and a polygon
* **Population**: Number of inhabitants for city, obtained from annual census.
