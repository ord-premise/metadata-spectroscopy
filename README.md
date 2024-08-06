# D2.1 - Metadata schema to store and access microscopy data
Common metadata schema to store and access microscopy data from simulations and experiments in a single platform.

## Authors
- Fabio Lopes
- Carlo Pignedoli

## Goal
* `schema\spmlink_model.yaml` defines the maps the objects and their properties needed to define experiments and simulations within the electronic lab notebook (ELN). It contains classes, types, slots, and enums:
    - Classes define objects and complex properties. Each class contains the CURIEs (compact uniform resource identifiers), a small description, some annotations needed for openBIS, and some slots (properties). There are some classes such as PiezoConfigurationSettings that are not objects, but properties that contain other properties. Classes also contain the object Container which is needed for [LinkML](https://linkml.io/linkml/) validation purposes.
    - Types define custom datatypes. Each type contains a description, a base datatype, a pattern, and an URI.
    - Slots define object properties. Each slot contains a description, a range (data that are allowed in that slot), a CURIE, and some annotations needed for openBIS. It can also contains pattern, and whether it is an array (multivalued).
    - Enums define list of values that can be used in some slots. Each enum contains a description, some annotations needed for openBIS, and allowed values (permissible_values).
The schema can be converted to other file formats such as [JSON-Schema](https://json-schema.org/) and [RDF](https://www.w3.org/RDF/) using [LinkML](https://linkml.io/linkml/) tools.

* `data\collections_config.json` contains metadata needed to setup collections inside openBIS.
* `data\small_example.yaml` contains a small example of data that can be validated or converted to other file format, e.g. [JSON-LD](https://json-ld.org/) using [LinkML](https://linkml.io/linkml/) tools.
* `src\setup_openbis_using_linkml.py` is a Python script that uses `schema\spmlink_model.yaml` and `data\collections_config.json` to create all properties, vocabularies, object types, spaces, projects, and collections necessary to start storing data in openBIS.
* `deprecated` contains deprecated files that were important to reach the current state.

## Achievement
This repository contains all the files needed for creating the provenance of experiments and simulations in the context of microscopy.

## External links
- https://www.ebi.ac.uk/ols4/
- https://www.w3.org/TR/json-ld11/
- https://github.com/emmo-repo/

## Acknowledgements
The [PREMISE](https://ord-premise.github.io/) project is supported by the [Open Research Data Program](https://ethrat.ch/en/eth-domain/open-research-data/) of the ETH Board.

![image](https://github.com/ord-premise/metadata-batteries/assets/45081142/74640b5c-ee94-41e1-9acd-fa47da866fe8)

![image](https://github.com/ord-premise/metadata-batteries/assets/45081142/d282c4d9-feb3-47dc-b5d4-c616151518be)

