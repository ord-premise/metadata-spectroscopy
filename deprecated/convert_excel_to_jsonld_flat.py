# -*- coding: utf-8 -*-
"""
Created on Tue Apr  9 15:30:22 2024

@author: dafa
"""

#%% Import libraries
import numpy as np
import pandas as pd
import json
import re

#%% Functions

def is_nan(var):
    """Function to verify whether it is a NaN."""
    return var != var

def remove_digits_from_string(string):
    return ''.join([i for i in string if not i.isdigit()])

def match_pattern(pattern, input_string):
    """
    Verify whether the input_string follows the given pattern

    Parameters
    ----------
    pattern : TYPE
        DESCRIPTION.
    input_string : TYPE
        DESCRIPTION.

    Returns
    -------
    bool
        DESCRIPTION.

    """
    if re.match(pattern, input_string):
        return True
    else:
        return False

def compute_flat_jsonld_graph(all_relations, selected_object_code, jsonld_graph, jsonld_context):
    
    # Get selected object relations
    selected_object_relations = all_relations.loc[selected_object_code]
    
    # Get selected object category
    selected_object_class = object_code_ontology_map[remove_digits_from_string(selected_object_code)]
    
    # Get selected object metadata, convert ID to @id and specify the @type
    selected_object_metadata = all_objects_metadata[selected_object_class][all_objects_metadata[selected_object_class]["ID"] == selected_object_code].to_dict("records")[0]
    selected_object_metadata["@id"] = selected_object_metadata.pop("ID")
    selected_object_metadata["@type"] = selected_object_class
    
    for parameter in selected_object_metadata:
        
        internal_jsonld_variable = "@" == parameter[0] # JSON-LD already knows what this type of parameters is.
        
        if internal_jsonld_variable == False:
            
            # Select the ontology of the current parameter
            parameter_ontology = schema_ontology[schema_ontology["Entity"]==parameter]
            
            # Get the datatype of the parameter
            # print(parameter)
            # print(parameter_ontology)
            # print(selected_object_code)
            parameter_ontology_type = parameter_ontology["Type"].item()
            
            # Convert the datatype according to JSON-LD context standards
            if parameter_ontology_type == "id":
                parameter_ontology_type = "@id"
            else:
                parameter_ontology_type = f"xsd:{parameter_ontology_type}"
            
            # Save the parameter information into the JSON-LD context
            jsonld_context[parameter] = {"@id": parameter_ontology["IRI"].item(), "@type": parameter_ontology_type}
            
            # In the case the parameter contains a NaN value, assign null to it. Otherwise it gives an error in the JSON-LD Playground
            if is_nan(selected_object_metadata[parameter]):
                selected_object_metadata[parameter] = "null"
    
    if np.count_nonzero(selected_object_relations): # If there are no more relations, close the function
        
        for index, relation in enumerate(selected_object_relations):
            
            if relation == "hasPart": # Only do this if there is a relation between the objects in the matrix
                
                # Get parent object code
                new_selected_object_code = selected_object_relations.index[index]
                
                # Get the category of the parent object
                relation_object_class = object_code_ontology_map[remove_digits_from_string(new_selected_object_code)]
                
                # Get the ontology information about the category
                object_ontology = schema_ontology[schema_ontology["Entity"]==relation_object_class]
                
                # Assign the object ontology to the JSON-LD context
                jsonld_context[relation_object_class] = {"@id": object_ontology["IRI"].item(), "@type": "@id"}
                
                # Convert the category to lowercase 
                relation_object_class_lower = relation_object_class.lower()
                
                # Save the lowercase category name in the JSON-LD context
                jsonld_context[relation_object_class_lower] = {"@id": object_ontology["IRI"].item(), "@type": "@id"}
                
                # If there are no objects of the current category in the selected object, create a dictionary with the first
                if relation_object_class_lower not in selected_object_metadata:
                    selected_object_metadata[relation_object_class_lower] = {"@id": f"#{new_selected_object_code}"} # The # was added because of RO-Crate standards. It can be removed if not needed
                
                # If there is at least one object of the current category already in the selected object, convert the dictionary into a list of objects
                elif type(selected_object_metadata[relation_object_class_lower]) == dict:
                    first_relation_object = selected_object_metadata[relation_object_class_lower]
                    list_relation_objects = [first_relation_object, {"@id": f"#{new_selected_object_code}"}]
                    selected_object_metadata[relation_object_class_lower] = list_relation_objects
                
                # If it is already a list, append one more parent
                else:
                    selected_object_metadata[relation_object_class_lower].append({"@id": f"#{new_selected_object_code}"})
                
                # Run recursively
                compute_flat_jsonld_graph(all_relations, new_selected_object_code, jsonld_graph, jsonld_context)
    
    # If the selected object was not already created in the @graph, create it. This is needed to not generate redundant data
    object_already_created = False
    for object_metadata in jsonld_graph:
        if object_metadata["@id"] == selected_object_metadata["@id"]:
            object_already_created = True
    
    if object_already_created == False:
        jsonld_graph.append(selected_object_metadata)
    
    return jsonld_graph, jsonld_context


#%% Load excel datasheets
root_path = "C:\\Users\\dafa\\Documents\\git\\metadata-spectroscopy"
metadata_openbis_schema_filename = f"{root_path}\\Metadata_Schema_for_openBIS.xlsx"
metadata_experiment_filename = f"{root_path}\\Metadata_Experiment_Objects.xlsx"

# Get objects metadata schema
schema_metadata = pd.read_excel(metadata_openbis_schema_filename, sheet_name = "Metadata Schema")
# Get information concerning the ontologised parameters
schema_ontology = pd.read_excel(metadata_openbis_schema_filename, sheet_name = "Ontology - definition")

# Open the experiment example metadata Excel file
experiment_objects_excel = pd.ExcelFile(metadata_experiment_filename)
# Get all the datasheet names inside the Excel file
experiment_objects_excel_sheets_names = experiment_objects_excel.sheet_names

# Get the experiment example metadata from the Excel file
experiment_metadata = experiment_objects_excel.parse("Relations")
# There are some objects that have more than one parent. In those cases the left column
# only has the code of object on the first relation and then it is empty for all the following ones.
# Therefore, this functions fill the rows with the first code.
experiment_metadata = experiment_metadata.fillna(method = "ffill")

#%% Get ontology entity for every parameter code
object_code_ontology_map = {}
for _, row in schema_metadata.iterrows():
    parameter_code = row["openBIS"]
    if is_nan(parameter_code) == False and is_nan(row["Ontology"]) == False and is_nan(row["Unit"]):
        object_code_ontology_map[parameter_code] = row["Ontology"]

#%% Process Excel datasheets
all_objects_metadata = {}

# Obtain metadata from all the objects from the multiple datasheets inside the Excel file
for sheet_name in experiment_objects_excel_sheets_names:
    if sheet_name != "Experiment":
        # One has to add here all the parameters that should not be read using default setup
        objects_metadata = experiment_objects_excel.parse(sheet_name, dtype={'Work phone': str})
        
        # Convert timestamp objects into strings
        for col_name, col in objects_metadata.items():
            if col.dtype == "datetime64[ns]":
                objects_metadata[col_name] = objects_metadata[col_name].astype(str)
                objects_metadata[col_name] = objects_metadata[col_name].str.replace(" ", "T")
        
        # Save the objects according to the type
        all_objects_metadata[sheet_name] = objects_metadata

# Close the Excel object
experiment_objects_excel.close()

# Generate matrix containing all the parent-child relations for all objects
all_unique_objects_ids = pd.unique(experiment_metadata[['Object 1', 'Object 2']].values.ravel('K'))
all_objects_relations = pd.DataFrame(0, index = all_unique_objects_ids, columns = all_unique_objects_ids)
for idx, object_1_id in enumerate(experiment_metadata["Object 1"]):
    relation_id = experiment_metadata["Relation"][idx]
    object_2_id = experiment_metadata["Object 2"][idx]
    all_objects_relations.loc[object_1_id, object_2_id] = relation_id

#%% Generate dictionary that is going to be used to generate the JSON-LD file

selected_object_code = "PUBL1"
all_objects_relations_dict = {}
jsonld_graph = []
jsonld_context = {"xsd": "http://www.w3.org/2001/XMLSchema#"}
#TODO: Generate JSON-LD context. It is giving an error at the moment
all_objects_relations_dict["@graph"], all_objects_relations_dict["@context"] = compute_flat_jsonld_graph(all_objects_relations, selected_object_code, jsonld_graph, jsonld_context)

#%% Export to JSON-LD
jsonld_object = json.dumps(all_objects_relations_dict, indent=4)
 
# Writing to sample.json
with open(f"{root_path}\\selected_object_schema.json", "w") as outfile:
    outfile.write(jsonld_object)

"""
Tasks:
    3 - Link the parameters to the units (meters, Volts, Amperes, etc.)
    4 - Link the description given in the Excel file
    5 - Replace openBIS ID by hasPart or other relation in JSON-LD file
"""


