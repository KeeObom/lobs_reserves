import streamlit as st
import pandas as pd
import os

# Initialize lists to store selected files
lob_files = []
reinsurance_files = []

# # Get the path to the Desktop directory
# desktop_path = os.path.expanduser("~/Desktop")

# # Create the "Dodo_results" folder on the Desktop
# results_folder = os.path.join(desktop_path, "Dodo_results")
# os.makedirs(results_folder, exist_ok=True)

# Create a Streamlit app
st.title("File Processor")

# Sidebar for file selection
st.sidebar.header("File Selection")

lob_files = st.sidebar.file_uploader("Upload Line of Business Files", accept_multiple_files=True, type=["xlsb"])
reinsurance_files = st.sidebar.file_uploader("Upload Reinsurance Files", accept_multiple_files=True, type=["xlsb"])

# Display selected files
st.sidebar.subheader("Selected Files:")
if lob_files:
    st.sidebar.write("Line of Business Files:")
    st.sidebar.write(lob_files)
if reinsurance_files:
    st.sidebar.write("Reinsurance Files:")
    st.sidebar.write(reinsurance_files)

# Main section
st.header("File Processing")

# Process the files
if st.button("Generate All"):
    if not lob_files and not reinsurance_files:
        st.error("Please upload Line of Business and Reinsurance files.")
    else:
        # Create a folder for generated sheet files
        results_folder = "Dodo_results"
        os.makedirs(results_folder, exist_ok=True)

        # Combine the lists of files
        all_files = lob_files + reinsurance_files

        # Define the sheet names you want to process
        group1_sheets = ["ACTUALS_FOR_VISUALIZATION", "ACTUARIAL_AOM_IMPACT", "CF_T1_PVFC_LIC_CLO","CF_T1_PVFC_LIC_INCEXP_LIC_INCR",
                       "CF_T1_PVFC_LIC_INCLAIM_LIC_INCR","CURVE_ID_PARAM","INITIALIZATION","MANDATORY_ACTUALS",
                       "MP_GOC","MP_GOC_SEG","OCI_OPTION_DERECOG", "CF_T1_PVFC_LIC_CLO_FADJ_PY",
                       "CF_T1_PVFC_LIC_OP", "CF_T1_PVFC_LIC_TEXPVAR_PY"]  # first group of sheets
        group2_sheets = ["CF_T1_PVFC_LIC_CLO_FADJ_PY", "CF_T1_PVFC_LIC_CLO_TADJ_PY",
                         "CF_T1_PVFC_LIC_DEREC","CF_T1_PVFC_LIC_EXPCLO_PY"]  # second group of sheets
        group3_sheets = ["CF_T1_PVFC_LIC_OP", "CF_T1_PVFC_LIC_OP_FADJ_PY","CF_T1_PVFC_LIC_OP_TADJ_PY"]  # third group of sheets
        group4_sheets = ["CF_T1_PVFC_LIC_TEXPVAR_PY", "CF_T1_PVFC_LIC_TASSCHG_PY",
                         "CF_T1_PVFC_LIC_FASSCHG_PY","CF_T1_PVFC_LIC_FEXPVAR_PY"]  # fourth group of sheets

        # Create a progress bar
        progress_bar = st.progress(0)

        # Process each sheet and save to the results folder
        total_sheets = group1_sheets + group2_sheets + group3_sheets + group4_sheets

        # Track the first sheet in groups 2, 3, and 4
        first_sheet_group2 = group2_sheets[0]
        first_sheet_group3 = group3_sheets[0]
        first_sheet_group4 = group4_sheets[0]

        for sheet_name in total_sheets:
            if sheet_name in group1_sheets:
                # Process each sheet in group 1 and save them with their original names
                merged_data = pd.DataFrame()
                for uploaded_file in all_files:
                    try:
                        df = pd.read_excel(uploaded_file, sheet_name=sheet_name, skiprows=8, engine='pyxlsb')
                        merged_data = pd.concat([merged_data, df], ignore_index=True)
                    except Exception as e:
                        st.error(f"Error reading {sheet_name} from {uploaded_file.name}: {e}")

                output_file = os.path.join(results_folder, f"{sheet_name}.csv")
                merged_data.to_csv(output_file, index=False)
                st.success(f"Processed {sheet_name}")

            elif sheet_name in group2_sheets:
                # For group 2, duplicate the first sheet in the group and save with the original names
                original_sheet_file = os.path.join(results_folder, f"{first_sheet_group2}.csv")
                output_file = os.path.join(results_folder, f"{sheet_name}.csv")
                with open(original_sheet_file, 'rb') as infile, open(output_file, 'wb') as outfile:
                    outfile.write(infile.read())
                st.success(f"Processed {sheet_name}")

            elif sheet_name in group3_sheets:
                # For group 3, duplicate the first sheet in the group and save with the original names
                original_sheet_file = os.path.join(results_folder, f"{first_sheet_group3}.csv")
                output_file = os.path.join(results_folder, f"{sheet_name}.csv")
                with open(original_sheet_file, 'rb') as infile, open(output_file, 'wb') as outfile:
                    outfile.write(infile.read())
                st.success(f"Processed {sheet_name}")

            elif sheet_name in group4_sheets:
                # For group 4, duplicate the first sheet in the group and save with the original names
                original_sheet_file = os.path.join(results_folder, f"{first_sheet_group4}.csv")
                output_file = os.path.join(results_folder, f"{sheet_name}.csv")
                with open(original_sheet_file, 'rb') as infile, open(output_file, 'wb') as outfile:
                    outfile.write(infile.read())
                st.success(f"Processed {sheet_name}")

            # Remove the "* MACRO_STEP_ID_DESCRIPTION" column from ACTUARIAL_AOM_IMPACT.csv
            if sheet_name == "ACTUARIAL_AOM_IMPACT":
                impact_file = os.path.join(results_folder, "ACTUARIAL_AOM_IMPACT.csv")
                if os.path.exists(impact_file):
                    impact_df = pd.read_csv(impact_file)
                    if "* MACRO_STEP_ID_DESCRIPTION" in impact_df.columns:
                        impact_df.drop("* MACRO_STEP_ID_DESCRIPTION", axis=1, inplace=True)
                        impact_df.to_csv(impact_file, index=False)

            # Update the progress bar
            progress_bar.progress((total_sheets.index(sheet_name) + 1) / len(total_sheets))

        st.success("All sheets processed successfully.")





# Clear selections
if st.button("Clear Selections"):
    lob_files = []
    reinsurance_files = st.sidebar.empty()
    st.success("Selections cleared.")
