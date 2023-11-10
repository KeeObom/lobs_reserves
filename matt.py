# !pip install pandas
# !pip install zipfile

import pandas as pd
import os
import shutil
from io import BytesIO
import zipfile

# Initialize lists to store selected files
lob_files = []
reinsurance_files = []

# Combine the lists of files
all_files = lob_files + reinsurance_files

# Define the sheet names you want to process
group1_sheets = ["ACTUALS_FOR_VISUALIZATION", "ACTUARIAL_AOM_IMPACT", "CF_T1_PVFC_LIC_CLO", "CF_T1_PVFC_LIC_INCEXP_LIC_INCR",
                  "CF_T1_PVFC_LIC_INCLAIM_LIC_INCR", "CURVE_ID_PARAM", "INITIALIZATION", "MANDATORY_ACTUALS",
                  "MP_GOC", "MP_GOC_SEG", "OCI_OPTION_DERECOG", "CF_T1_PVFC_LIC_CLO_FADJ_PY",
                  "CF_T1_PVFC_LIC_OP", "CF_T1_PVFC_LIC_TEXPVAR_PY"]  # first group of sheets
group2_sheets = ["CF_T1_PVFC_LIC_CLO_FADJ_PY", "CF_T1_PVFC_LIC_CLO_TADJ_PY",
                 "CF_T1_PVFC_LIC_DEREC", "CF_T1_PVFC_LIC_EXPCLO_PY"]  # second group of sheets
group3_sheets = ["CF_T1_PVFC_LIC_OP", "CF_T1_PVFC_LIC_OP_FADJ_PY", "CF_T1_PVFC_LIC_OP_TADJ_PY"]  # third group of sheets
group4_sheets = ["CF_T1_PVFC_LIC_TEXPVAR_PY", "CF_T1_PVFC_LIC_TASSCHG_PY",
                 "CF_T1_PVFC_LIC_FASSCHG_PY", "CF_T1_PVFC_LIC_FEXPVAR_PY"]  # fourth group of sheets

# Create a folder for generated sheet files
results_folder = "Dodo_results"
os.makedirs(results_folder, exist_ok=True)

# Initialize a list to store processed sheet DataFrames
processed_sheets = {}

# Process each sheet and save to the results folder
total_sheets = group1_sheets + group2_sheets + group3_sheets + group4_sheets

# Track the first sheet in groups 2, 3, and 4
first_sheet_group2 = group2_sheets[0]
first_sheet_group3 = group3_sheets[0]
first_sheet_group4 = group4_sheets[0]

for sheet_name in total_sheets:
    if sheet_name in group1_sheets:
        # Process each sheet in group 1 and save them to CSV
        merged_data = pd.DataFrame()
        for uploaded_file in all_files:
            try:
                df = pd.read_excel(uploaded_file, sheet_name=sheet_name, skiprows=8, engine='pyxlsb')
                merged_data = pd.concat([merged_data, df], ignore_index=True)
            except Exception as e:
                print(f"Error reading {sheet_name} from {uploaded_file.name}: {e}")

        # Save to CSV in the results folder
        csv_filename = os.path.join(results_folder, f"{sheet_name}.csv")
        merged_data.to_csv(csv_filename, index=False)
        processed_sheets[sheet_name] = csv_filename
        print(f"Processed {sheet_name}")

    elif sheet_name in group2_sheets:
        # For group 2, duplicate the first sheet in the group and save to CSV
        original_sheet = pd.read_csv(processed_sheets[first_sheet_group2])
        csv_filename = os.path.join(results_folder, f"{sheet_name}.csv")
        original_sheet.to_csv(csv_filename, index=False)
        processed_sheets[sheet_name] = csv_filename
        print(f"Processed {sheet_name}")

    elif sheet_name in group3_sheets:
        # For group 3, duplicate the first sheet in the group and save to CSV
        original_sheet = pd.read_csv(processed_sheets[first_sheet_group3])
        csv_filename = os.path.join(results_folder, f"{sheet_name}.csv")
        original_sheet.to_csv(csv_filename, index=False)
        processed_sheets[sheet_name] = csv_filename
        print(f"Processed {sheet_name}")

    elif sheet_name in group4_sheets:
        # For group 4, duplicate the first sheet in the group and save to CSV
        original_sheet = pd.read_csv(processed_sheets[first_sheet_group4])
        csv_filename = os.path.join(results_folder, f"{sheet_name}.csv")
        original_sheet.to_csv(csv_filename, index=False)
        processed_sheets[sheet_name] = csv_filename
        print(f"Processed {sheet_name}")

# Zip the CSV files
zip_filename = os.path.join(results_folder, "processed_sheets.zip")
with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for sheet_name, csv_filename in processed_sheets.items():
        zipf.write(csv_filename, arcname=f"{sheet_name}.csv")

print("All sheets processed successfully.")
print(f"CSV files saved in {results_folder}")
print(f"ZIP file saved in {zip_filename}")
