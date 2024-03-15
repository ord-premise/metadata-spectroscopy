# D2.1 - Metadata schema to store and access microscopy data
Common metadata schema to store and access microscopy data from simulations and experiments in a single platform.

## Authors
- Fabio Lopes
- Carlo Pignedoli

## Goal
* "Metadata_Schema_for_openBIS.xlsx" defines the information needed to map the objects used to define experiments and simulations within the electronic lab notebook (ELN). It contains seven datasheets:
    - The "Metadata Schema" contains the objects together with their parameters. It comprises ten columns:
            - "Metadata": The name of the object/property (metadata);
            - "Unit": The unit used on the respective metadata;
            - "Input": Who introduces the value oof the respective metadata;
            - "Description": A small description of the respective metadata;
            - "Ontology": The name of the respective metadata in the used semantic schema;
            - "openBIS" The name of respetive metadata in the openBIS software;
            - "openBIS datatype": The datatype of the respetive metadata inside openBIS;
            - "Comments": Some comments to the respetive metadata;
            - "is Parameter already created?": To verify whether the respective metadata is already present in the "openBIS - parameters" datasheet;
            - "is Entity already created?": To verify whether the respective metadata is already present in the "Ontology - definition" datasheet;
            - "does Entity already contains an IRI?": To verify whether the entity used in the respective metadata already contains an IRI in the "Ontology - definition" datasheet;
        - The "Metadata Updates" contains some tasks that should be performed to improve the "Metadata Schema";
        - The "Ontology - definition" contains the IRI links to the different ontologies. It comprises three columns:
            - "Entity": The name given to the respective metadata;
            - "IRI": The link to the ontology that defines the respective metadata;
            - "Type": The datatype of the respective metadata.
        - The "openBIS - parameters" contains the definitions necessary to create the property types inside openBIS. It comprises seven columns:
            - "Code": Code of the property type inside openBIS;
            - "Label": Label of the property type inside openBIS;
            - "Description": Description of the property type inside openBIS;
            - "DataType": Datatype of the property type inside openBIS;
            - "managedInternally": Whether the property type is managed internally in openBIS;
            - "Vocabulary": Vocabulary of the property type inside openBIS, in the case, the property is a CONTROLLEDVOCABULARY datatype;
            - "Metadata": Type of widget used in the case of property types that are MULTILINE_VARCHAR or XML.
        - The "openBIS - vocabulary" contains the vocabularies used in openBIS. It comprises two columns:
            - "Vocabulary": The code of the vocabulary inside openBIS;
            - "Description": Description of the respective vocabulary inside openBIS.
        - The "openBIS - vocabulary terms" contains the terms used in vocabularies in openBIS. It comprises four columns:
            - "Vocabulary": The code of the vocabulary inside openBIS;
            - "Term code": The code of the term inside openBIS;
            - "Term label": The label of the term inside openBIS;
            - "Term description": The description of the term inside openBIS;
        - The "Legend" contains a column with colors and a column with the legend of the colors. These colors are used in the file while developing it.

* "Metadata_Experiment_Objects.xlsx" defines an example of a publication. It contains all the objects and relations between those needed for defining a publication. It contains a datasheet named "Experiment" where all the relations between the different objects are defined and several other datasheets where the objects are described.
* "convert_excel_to_jsonld.py" is used to convert information contained in the previous two Excel files into JSON-LD file format.
* "selected_object_schema.json" is an example of an JSON-LD file obtained from converting the information available in the Excel files. This JSON-LD can be explored in the [JSON-LD Playground](https://json-ld.org/playground/). One just needs to copy its content into the textbox displayed in the playground and click on the "Visualized" tab below it.

## Achievement
This repository contains all the files needed for creating the provenance of experiments and simulations in the context of microscopy.

## External links
List here any relevant tools used in preparing this deliverable that are not maintained by PREMISE.

## Acknowledgements
The [PREMISE](https://ord-premise.github.io/) project is supported by the [Open Research Data Program](https://ethrat.ch/en/eth-domain/open-research-data/) of the ETH Board.

![image](https://github.com/ord-premise/metadata-batteries/assets/45081142/74640b5c-ee94-41e1-9acd-fa47da866fe8)

![image](https://github.com/ord-premise/metadata-batteries/assets/45081142/d282c4d9-feb3-47dc-b5d4-c616151518be)

