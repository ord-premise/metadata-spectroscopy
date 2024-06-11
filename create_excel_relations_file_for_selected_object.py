# -*- coding: utf-8 -*-
"""
Created on Wed Apr 10 10:43:54 2024

@author: dafa
"""

#%% Import libraries
import numpy as np
import pandas as pd
import json
import re
from pybis import Openbis

#%% Functions

def is_nan(var):
    """Function to verify whether it is a NaN."""
    return var != var

def remove_digits_from_string(string):
    return ''.join([i for i in string if not i.isdigit()])

def log_in(bisurl='openbis', bisuser='admin', bispasswd='changeit'):
    """Function to login to openBIS."""
    if Openbis(bisurl, verify_certificates=False).is_token_valid():
        session = Openbis(bisurl, verify_certificates=False)
    else:
        Openbis(bisurl, verify_certificates=False).login(bisuser, bispasswd, save_token=True)
        session = Openbis(bisurl, verify_certificates=False)
    return session

def get_object_provenance(session, object_id, objects, relations): 
    
    eln_object = session.get_object(object_id)
    
    object_type = eln_object.type.code
    
    eln_object_props = eln_object.props.all()
    
    #TODO: This is just for retro-compability. Should be removed after correction
    correction_dictionary = {"emin-ev": "emin-j",
                             "emax-ev": "emax-j",
                             "de-ev": "de-j",
                             "fwhm-ev": "fwhm-j",
                             "extrap-plane-angst": "extrap-plane-m",
                             "constant-height-angst": "constant-height-m",
                             "constant-current": "constant-current-elect-m3",
                             "duration-min": "duration-s",
                             "pressure-mbar": "pressure-Pa",
                             "energy-kv": "discharge-voltage-V",
                             "temperature-celsius": "temperature-K",
                             "current-ma": "current-A",
                             "diameter-mm": "diameter-m",
                             "height-mm": "height-m",
                             "oscillation-control-amplitude-pgain-vnm": "oscillation-control-amplitude-pgain-vm",
                             "oscillation-control-amplitude-igain-vnmsec": "oscillation-control-amplitude-igain-vmsec",
                             "scan-dx-ang": "scan-dx-m",
                             "scan-zmin-ang": "scan-zmin-m",
                             "scan-zmax-ang": "scan-zmax-m",
                             "afm-amplitude-ang": "afm-amplitude-m",
                             "afm-cantilever-f0": "resonance-frequency-hz",
                             "force-convergence-threshold-bohrhartree": "force-convergence-threshold-m-J"}
    
    reversed_correction_dictionary = dict(zip(correction_dictionary.values(),correction_dictionary.keys()))

    skip_properties = ["simulated", "simulation-method", "manufacturer-website", "simulation-type"]
    # Until here.
    
    # Convert openBIS property names into ontology ids
    for prop in eln_object.props.all():
        #TODO: This is just for retro-compability. Should be removed after correction
        if prop in correction_dictionary:
            prop = correction_dictionary[prop]
            
        if prop in skip_properties:
            eln_object_props.pop(prop)
            continue
        # Until here.
        
        print(prop)
        prop_ontology = schema_metadata["Ontology"][schema_metadata["openBIS"].str.lower() == prop.lower()].iloc[0]
        
        #TODO: This is just for retro-compability. Should be removed after correction
        if prop in reversed_correction_dictionary:
            prop = reversed_correction_dictionary[prop]
        # Until here.
        
        eln_object_props[prop_ontology] = eln_object_props.pop(prop)
    
    # Save object properties into the specified class dictionary
    eln_object_code = remove_digits_from_string(eln_object.code)
    object_code_ontology = schema_metadata["Ontology"][schema_metadata["openBIS"] == eln_object_code].iloc[0]
    
    if object_code_ontology not in objects:
        objects[object_code_ontology] = {eln_object.code: eln_object_props}
    else:
        objects[object_code_ontology][eln_object.code] = eln_object_props
    
    # Run it through the parents up until the last one
    for parent in eln_object.parents:
        eln_parent_object = session.get_object(parent)
        
        get_object_provenance(session, eln_parent_object.permId, objects, relations)
    
    # If the object contains at least one parent, save the relation
    if len(eln_object.parents) > 0:
        eln_object_parents = [parent.split("/")[-1] for parent in eln_object.parents]
        relations[eln_object.code] = eln_object_parents
    
    return relations, objects
 
#%% Load excel datasheets
root_path = "C:\\Users\\dafa\\Documents\\git\\metadata-spectroscopy"
metadata_openbis_schema_filename = f"{root_path}\\Metadata_Schema_for_openBIS.xlsx"

# Get objects metadata schema
schema_metadata = pd.read_excel(metadata_openbis_schema_filename, sheet_name = "Metadata Schema")
# Get information concerning the ontologised parameters
schema_ontology = pd.read_excel(metadata_openbis_schema_filename, sheet_name = "Ontology - definition")

#%% Get ontology entity for every parameter code
object_code_ontology_map = {}
for _, row in schema_metadata.iterrows():
    parameter_code = row["openBIS"]
    if is_nan(parameter_code) == False and is_nan(row["Ontology"]) == False and is_nan(row["Unit"]):
        object_code_ontology_map[parameter_code] = row["Ontology"]
   
#%% Data Processing

if __name__ == "__main__":
    session = log_in("https://local.openbis.ch/openbis", "admin", "123456789")
    
    selected_object_id = "20240424150511678-271"
    
    relations, objects = get_object_provenance(session, selected_object_id, {}, {})
    
    with pd.ExcelWriter('Metadata_Experiment_Objects.xlsx') as writer:
        for object_class in objects:
            objects_df = pd.DataFrame.from_dict(objects[object_class], orient = "index")
            objects_df = objects_df.reset_index()
            objects_df = objects_df.rename(columns={'index': 'ID'})
            
            objects_df.to_excel(writer, sheet_name = object_class, index = False)
        
        triple_relations = []
        for object_code in relations:
            for parent_object_code in relations[object_code]:
                triple_relations.append([object_code, "hasPart", parent_object_code])
        
        relations_df = pd.DataFrame(triple_relations, columns = ["Object 1", "Relation", "Object 2"])
        relations_df.to_excel(writer, sheet_name = "Relations", index = False)
        