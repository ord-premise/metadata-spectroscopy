# -*- coding: utf-8 -*-
"""
Created on Tue Apr 30 14:14:49 2024

@author: dafa
"""

import pandas as pd

#%%Functions

def is_nan(var):
    """Function to verify whether it is a NaN."""
    return var != var

#%% Processing data

filename = "Metadata_Schema_for_ELN_corrected.xlsx"

file_ontology = pd.read_excel(filename, sheet_name = "Ontology")
file_molecules = pd.read_excel(filename, sheet_name = "Molecule")

object_properties = file_molecules[file_molecules["Metadata"]=="Ontology"].values[0][2:] # First two are not ontologised
object_properties_units = file_molecules[file_molecules["Metadata"]=="Unit"].values[0][2:] # First two are not ontologised

object_properties_values_start_index = file_molecules[file_molecules["Metadata"]=="Values"].index.item()
object_properties_values = file_molecules.iloc[object_properties_values_start_index:,2:].values

# Objects
all_objects_dict = {"@graph": [], "@context": {}}

# Iterate over each property
for instance_index, instance_properties_values in enumerate(object_properties_values):
    
    # Initialize an empty dictionary
    result = {}
    
    for index, prop in enumerate(object_properties):
        # Split the property by the dash
        levels = prop.split('-')
        current = result
        
        # Iterate over each level
        for level in levels[:-1]:
            # If the level doesn't exist, create an empty dictionary for it
            if level not in current:
                current[level] = {}
                
            # Move to the next level
            current = current[level]
            
            property_mapping_iri = file_ontology[file_ontology["Entity/Property"]==level]["IRI"].item()
            property_mapping_type = file_ontology[file_ontology["Entity/Property"]==level]["Type"].item()
            
            if property_mapping_type == "id":
                property_mapping_type = "@id"
            
            all_objects_dict["@context"][level] = {"@id": property_mapping_iri, "@type": property_mapping_type}
        
        # Assign the value to the last level key
        unit = object_properties_units[index]
        level = levels[-1]
        
        if is_nan(instance_properties_values[index]) == False:
            if unit == "NoUnit":
                current[level] = instance_properties_values[index]
            else:
                current[level] = {"value": instance_properties_values[index], "unit": unit}
            
            property_mapping_iri = file_ontology[file_ontology["Entity/Property"]==level]["IRI"].item()
            property_mapping_type = file_ontology[file_ontology["Entity/Property"]==level]["Type"].item()
            
            if property_mapping_type == "id":
                property_mapping_type = "@id"
            
            all_objects_dict["@context"][level] = {"@id": property_mapping_iri, "@type": property_mapping_type}
    
    all_objects_dict["@graph"].append(current)
            

