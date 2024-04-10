#!/usr/bin/env python
# coding: utf-8

# In[3]:


# Load libraries
import os
from pybis import Openbis
import json
import numpy as np

#%% Classes
class OpenBISDatabase:
    def __init__(self):
        self.session = None
        self.schema = {
            "spaces": [], 
            "property_types": [], 
            "object_types": [],
            "experiment_types": [],
            "vocabularies": [],
            "dataSetTypes": [],
        }
    
    @staticmethod
    def log_in(bisurl='openbis', bisuser='admin', bispasswd='changeit'):
        """Function to login to openBIS."""
        if Openbis(bisurl, verify_certificates=False).is_token_valid():
            session = Openbis(bisurl, verify_certificates=False)
        else:
            Openbis(bisurl, verify_certificates=False).login(bisuser, bispasswd, save_token=True)
            session = Openbis(bisurl, verify_certificates=False)
        return session

    def connect_to_openbis(self, bisurl: str, bisuser: str, bispasswd: str):
        """Function to connect to openBIS"""
        self.session = self.log_in(
            bisurl = bisurl, 
            bisuser = bisuser, 
            bispasswd = bispasswd
        )
    
    def extract_spaces(self):
        """Function to extract the spaces from openBIS"""
        spaces = self.session.get_spaces()

        for space in spaces:
            space_metadata = {
                "code": space.code, 
                "description": space.description
            }
            self.schema["spaces"].append(space_metadata)

    def extract_projects(self):
        """Function to extract the projects from openBIS"""
        for index, space in enumerate(self.schema["spaces"]):
            projects = self.session.get_projects(space = space["code"])
            self.schema["spaces"][index]["projects"] = []
            
            
            for project in projects:
                project_metadata = {
                    "code": project.code,
                    "description": project.description
                }
                self.schema["spaces"][index]["projects"].append(project_metadata)
    
    def extract_experiments(self):
        """Function to extract the experiments from openBIS"""
        for index_space, space in enumerate(self.schema["spaces"]):
            for index_project, project in enumerate(space["projects"]):
                experiments = self.session.get_experiments(
                    space = space["code"], 
                    project = project["code"]
                )
                self.schema["spaces"][index_space]["projects"][index_project]["experiments"] = []

                for experiment in experiments:
                    experiment_metadata = {
                        "code": experiment.code, 
                        "type": experiment.type.code,
                        "properties": experiment.props.all()
                    }
                    self.schema["spaces"][index_space]["projects"][index_project]["experiments"].append(experiment_metadata)
                    
    def extract_objects(self):
        """Function to extract the objects from openBIS"""
        for index_space, space in enumerate(self.schema["spaces"]):
            for index_project, project in enumerate(space["projects"]):
                for index_experiment, experiment in enumerate(project["experiments"]):
                    objects = self.session.get_samples(
                        space = space["code"], 
                        experiment = f"/{space['code']}/{project['code']}/{experiment['code']}"
                    )
                    self.schema["spaces"][index_space]["projects"][index_project]["experiments"][index_experiment]["objects"] = []
                    
                    for object in objects:
                        if object.registrator == "admin":
                            object = self.session.get_object(object.permId) #TODO: Correct this easy fix once the bug of getting parents from items from get_objects() is fixed
    
                            object_parents_identifiers = []
                            object_children_identifiers = []
                            object_datasets_metadata = []
    
                            for parent in object.get_parents():
                                object_parents_identifiers.append(parent.identifier)
                            
                            for child in object.get_children():
                                object_children_identifiers.append(child.identifier)
                            
                            #TODO: This thing does not work.........Connection error.
                            # object_datasets = object.get_datasets()
                            # for dataset in object_datasets:
                            #     dataset.data["dataStore"]["downloadUrl"] = 'https://openbis/'
                            #     dataset.download(destination = 'openBIS_datasets')
                            #     object_datasets_metadata.append({"type": dataset.type.code, "folderpath": f"openBIS_datasets/{dataset.code}"})
    
                            object_metadata = {
                                "code": object.code, 
                                "type": object.type.code,
                                "properties": object.props.all(),
                                "parents": object_parents_identifiers,
                                "children": object_children_identifiers,
                                # "datasets": object_datasets_metadata
                            }
                            self.schema["spaces"][index_space]["projects"][index_project]["experiments"][index_experiment]["objects"].append(object_metadata)
    
    def extract_property_types(self):
        """Function to extract the property types from openBIS"""
        for property_type in self.session.get_property_types():
            property_type_metadata = {
                "code": property_type.code,
                "label": property_type.label,
                "description": property_type.description,
                "dataType": property_type.dataType,
                "vocabulary": property_type.vocabulary,
                "metaData": property_type.metaData,
                "managedInternally": property_type.managedInternally
            }
            self.schema["property_types"].append(property_type_metadata)
    
    def extract_object_types(self):
        """Function to extract the object types from openBIS"""
        for object_type in self.session.get_object_types():
            object_properties = object_type.get_property_assignments().df
            object_properties_metadata = []

            for _, object_property in object_properties.iterrows():
                object_properties_metadata.append(
                    {
                    "section": object_property.section,
                    "mandatory": object_property.mandatory,
                    "prop": object_property.propertyType,
                    }
                )

            object_type_metadata = {
                "code": object_type.code,
                "description": object_type.description,
                "generatedCodePrefix": object_type.generatedCodePrefix,
                "autoGeneratedCode": object_type.autoGeneratedCode,
                "propertyAssignments": object_properties_metadata
            }
            self.schema["object_types"].append(object_type_metadata)
    
    def extract_experiment_types(self):
        """Function to extract the experiment types from openBIS"""
        for experiment_type in self.session.get_experiment_types():
            experiment_properties = experiment_type.get_property_assignments().df
            experiment_properties_metadata = []

            for _, experiment_property in experiment_properties.iterrows():
                experiment_properties_metadata.append(
                    {
                    "section": experiment_property.section,
                    "mandatory": experiment_property.mandatory,
                    "prop": experiment_property.propertyType,
                    }
                )

            experiment_type_metadata = {
                "code": experiment_type.code,
                "description": experiment_type.description,
                "propertyAssignments": experiment_properties_metadata,
            }
            self.schema["experiment_types"].append(experiment_type_metadata)

    def extract_vocabularies(self):
        """Function to extract the vocabularies from openBIS"""
        for vocabulary in self.session.get_vocabularies():
            
            terms_metadata = []
            terms = vocabulary.get_terms().df
            for _, term in terms.iterrows():
                terms_metadata.append(
                    {
                    "code": term.code,
                    "label": term.label,
                    "description": term.description,
                    }
                )

            vocabulary_metadata = {
                "code": vocabulary.code,
                "description": vocabulary.description,
                "terms": terms_metadata,
            }
            self.schema["vocabularies"].append(vocabulary_metadata)
    
    def extract_dataset_types(self):
        for dataset_type in self.session.get_dataset_types():
            dataset_type_properties = dataset_type.get_property_assignments().df
            dataset_type_properties_metadata = []

            for _, dataset_type_property in dataset_type_properties.iterrows():
                dataset_type_properties_metadata.append(
                    {
                    "section": dataset_type_property.section,
                    "mandatory": dataset_type_property.mandatory,
                    "prop": dataset_type_property.propertyType,
                    }
                )

            dataset_type_metadata = {
                "code": dataset_type.code,
                "description": dataset_type.description,
                "propertyAssignments": dataset_type_properties_metadata,
            }
            self.schema["dataSetTypes"].append(dataset_type_metadata)
    
    def extract_openbis_schema(self):
        self.extract_spaces()
        self.extract_projects()
        self.extract_experiments()
        self.extract_objects()
        self.extract_property_types()
        self.extract_object_types()
        self.extract_experiment_types()
        self.extract_vocabularies()
        self.extract_dataset_types()
    
    def export_schema_to_json(self, filename):
        with open(filename, 'w') as f:
            json.dump(self.schema, f, indent = 3)

    def import_schema_from_json(self, json_filename):
        with open(json_filename, 'r') as f:
            self.schema = json.load(f)

    def create_property_types(self):
        for openbis_property in self.schema["property_types"]:
            if "$" not in openbis_property:
                try:
                    self.session.new_property_type(**openbis_property).save()
                except ValueError as ve:
                    print(ve)
                    print(f"{openbis_property['code']} already exists.")
    
    def create_vocabularies(self):
        for openbis_vocabulary in self.schema["vocabularies"]:
            try:
                self.session.new_vocabulary(**openbis_vocabulary).save()
            except ValueError as ve:
                print(f"{openbis_vocabulary['code']} already exists.")
    
    def create_object_types(self):
        for openbis_object in self.schema["object_types"]:
            try:
                object_type = self.session.get_object_type(openbis_object["code"])
            except ValueError as ve:
                print(f"{openbis_object['code']} does not exist.")
                object_type = self.session.new_object_type(autoGeneratedCode=True, 
                                                           subcodeUnique=False,
                                                           listable=True,
                                                           showContainer=False,
                                                           showParents=True,
                                                           showParentMetadata=False,
                                                           code = openbis_object["code"],
                                                           generatedCodePrefix = openbis_object["generatedCodePrefix"])
                object_type.save()
                
            for property_type in openbis_object["propertyAssignments"]:
                try:
                    object_type.assign_property(self.session.get_property_type(code = property_type["prop"]))
                except ValueError as ve:
                    print(ve)

    def create_spaces(self):
        for index_space, space in enumerate(self.schema["spaces"]):
            available_spaces = self.session.get_spaces(code = space["code"])
            
            if len(available_spaces) == 0:
                new_space = self.session.new_space(
                    code = space["code"],
                    description = space["description"]
                )
                
                new_space.save()
    
    def create_projects(self):
        for index_space, space in enumerate(self.schema["spaces"]):
            for index_project, project in enumerate(space["projects"]):
                available_projects = self.session.get_projects(
                    space = space["code"],
                    code = project["code"]
                )
                
                if len(available_projects) == 0:
                    new_project = self.session.new_project(
                        code = project["code"],
                        space = space["code"],
                        description = project["description"]
                    )
                    
                    new_project.save()
    
    def create_experiments(self):
        experiment_type_available = openbis_database.session.get_experiment_types("EXPERIMENT")
        
        if not experiment_type_available:
            new_experiment_type = self.session.new_collection_type(
                code = "EXPERIMENT"
            )
            
            new_experiment_type.save()
            
            new_experiment_type.assign_property(
                prop = "$name",
                section = "General Information"
            )
            
        for index_space, space in enumerate(self.schema["spaces"]):
            for index_project, project in enumerate(space["projects"]):
                for index_experiment, experiment in enumerate(project['experiments']):
                    available_experiments = self.session.get_experiments(
                        space = space["code"], 
                        project = project["code"],
                        code = experiment["code"]
                    )
                    if len(available_experiments) == 0:
                        # This is needed because when exporting the JSON file, it assumes null whenever a default view is chosen.
                        if "$default_collection_view" in experiment["properties"]:
                            experiment["properties"]["$default_collection_view"] = "LIST_VIEW"
                        
                        experiment_type = experiment["type"]
                        
                        if experiment_type == "DEFAULT_EXPERIMENT":
                            experiment_type = "EXPERIMENT"
                        
                        new_experiment = self.session.new_experiment(
                            code = experiment["code"],
                            project = f"/{space['code']}/{project['code']}",
                            props = {"$name": experiment["properties"]["$name"]},
                            type = experiment_type
                        )
                        
                        new_experiment.save()
    
    def create_objects(self):
        return None
    
    def verify_if_object_exists(self, selected_object):
        database_objects = self.session.get_objects()
        
        for openbis_object in database_objects:
            if openbis_object.props.all() == selected_object["properties"]:
                return True
        
        return False

if __name__ == "__main__":
    #%% Save Database

    # Create OpenBISDatabase instance
    openbis_database = OpenBISDatabase()
    
    # Connect to openBIS
    openbis_database.connect_to_openbis("local.openbis.ch/openbis", "admin", "123456789")
    # openbis_database.connect_to_openbis("localhost:8443/openbis", "admin", "changeit")
    
    # Extract openBIS schema
    openbis_database.extract_openbis_schema()
    
    # Dump schema into JSON file
    filename = 'C:\\Users\\dafa\\Documents\\git\\metadata-spectroscopy\\openBIS_schema.json'
    openbis_database.export_schema_to_json(filename)
    
    #%% Load Database
    
    # Create OpenBISDatabase instance
    openbis_database = OpenBISDatabase()
    
    # Connect to openBIS
    openbis_database.connect_to_openbis("local.openbis.ch/openbis", "admin", "123456789")
    # openbis_database.connect_to_openbis("localhost:8443/openbis", "admin", "changeit")
    # Import JSON file
    json_filename = 'C:\\Users\\dafa\\Documents\\git\\metadata-spectroscopy\\openBIS_schema.json'
    openbis_database.import_schema_from_json(json_filename)
    
    # openbis_database.upload_database() -> At the end when all the others are done
    
    openbis_database.create_vocabularies()
    
    openbis_database.create_property_types()
    
    openbis_database.create_object_types()
    
    openbis_database.create_spaces()
    
    openbis_database.create_projects()
    
    openbis_database.create_experiments()
    
    # Create objects with no parents
    all_objects_codes_indexes = {}
    total_num_objects = 0
    for index_space, space in enumerate(openbis_database.schema["spaces"]):
        for index_project, project in enumerate(space["projects"]):
            for index_experiment, experiment in enumerate(project['experiments']):            
                for index_object, object in enumerate(experiment['objects']):
                    
                    object_exists = openbis_database.verify_if_object_exists(object)
                    
                    if object_exists == False:
                        
                        total_num_objects += 1
                        
                        if len(object["parents"]) == 0:
                            old_object_code = f"/{space['code']}/{project['code']}/{object['code']}"
                            
                            object_autoGeneratedCode = openbis_database.session.get_object_type(object["type"]).autoGeneratedCode
                            # Remove properties with no values
                            filtered_properties = {k: v for k, v in object["properties"].items() if v is not None}
                            
                            if object_autoGeneratedCode == False:
                                new_object = openbis_database.session.new_object(
                                    code = object["code"],
                                    type = object["type"],
                                    experiment = f"/{space['code']}/{project['code']}/{experiment['code']}",
                                    props = filtered_properties
                                )
                            else:
                                new_object = openbis_database.session.new_object(
                                    type = object["type"],
                                    experiment = f"/{space['code']}/{project['code']}/{experiment['code']}",
                                    props = filtered_properties
                                )
                            
                            try:
                                new_object.save()
                            except ValueError as ve:
                                print(f"Object {object['code']} already exists!")
                            
                            all_objects_codes_indexes[old_object_code] = f"{new_object.project.identifier}/{new_object.code}"
                            
    
    # Create objects with parents
    while len(all_objects_codes_indexes) < total_num_objects:
        # Iterate over the existent objects
        for index_space, space in enumerate(openbis_database.schema["spaces"]):
            for index_project, project in enumerate(space["projects"]):
                for index_experiment, experiment in enumerate(project['experiments']):
                        for index_object, object in enumerate(experiment['objects']):
                            
                            object_exists = openbis_database.verify_if_object_exists(object)
                            
                            if object_exists == False:
                            
                                if len(object["parents"]) > 0:
                                    
                                    old_object_code = f"/{space['code']}/{project['code']}/{object['code']}"
                                    parents_exist = True
                                    object_parents = []
                                    
                                    for index, parent in enumerate(object["parents"]):
                                        
                                        if parent in all_objects_codes_indexes:
                                            
                                            object_parents.append(all_objects_codes_indexes[parent])
                                        
                                            parent_created = openbis_database.session.get_objects(all_objects_codes_indexes[parent])
                                            
                                            if not parent_created:
                                                parents_exist = False
                                        
                                        else:
                                            parents_exist = False
                                    
                                    if parents_exist:
                                        
                                        object_autoGeneratedCode = openbis_database.session.get_object_type(object["type"]).autoGeneratedCode
                                        # Remove properties with no values
                                        filtered_properties = {k: v for k, v in object["properties"].items() if v is not None}
                                        
                                        if object_autoGeneratedCode == False:
                                            new_object = openbis_database.session.new_object(
                                                code = object["code"],
                                                type = object["type"],
                                                experiment = f"/{space['code']}/{project['code']}/{experiment['code']}",
                                                props = filtered_properties,
                                                parents = object_parents
                                            )
                                        else:
                                            new_object = openbis_database.session.new_object(
                                                type = object["type"],
                                                experiment = f"/{space['code']}/{project['code']}/{experiment['code']}",
                                                props = filtered_properties,
                                                parents = object_parents
                                            )
                                        
                                        try:
                                            new_object.save()
                                        except ValueError as ve:
                                            print(f"Object {object['code']} already exists!")
                                        
                                        all_objects_codes_indexes[old_object_code] = f"{new_object.project.identifier}/{new_object.code}"
    
    #TODO: Arrumar o codigo