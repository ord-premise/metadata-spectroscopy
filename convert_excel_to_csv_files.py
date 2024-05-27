# -*- coding: utf-8 -*-
"""
Created on Wed Apr 10 15:27:26 2024

@author: dafa
"""

import pandas as pd
import os

root_path = "metadata-spectroscopy"

metadata_openbis_schema_filename = "Metadata_Schema_for_openBIS.xlsx"

# Open the metadata schema Excel file
metadata_schema_excel = pd.ExcelFile(metadata_openbis_schema_filename)

# Get all the datasheet names inside the Excel file
metadata_schema_excel_sheets_names = metadata_schema_excel.sheet_names

metadata_csv_files_foldername = "Metadata_Files"

if os.path.isdir(metadata_csv_files_foldername) == False:
    os.mkdir(metadata_csv_files_foldername)

for sheet_name in metadata_schema_excel_sheets_names:
    sheet_dataframe = metadata_schema_excel.parse(sheet_name)
    sheet_dataframe.to_csv(f"{metadata_csv_files_foldername}/{sheet_name}.csv", index = False)