import streamlit as st
import pandas as pd
import os
import zipfile
from github import Github

# Retrieve the GitHub personal access token
github_access_token = st.secrets["github"]["access_token"]

# Initialize lists to store selected files
lob_files = []
reinsurance_files = []

# Define your GitHub repository credentials
github_username = 'KeeObom'
github_token = github_access_token
repository_name = 'lobs_reserves'

# Initialize a GitHub instance with your credentials
g = Github(github_username, github_token)

# Specify the target repository
repo = g.get_repo(f"{github_username}/{repository_name}")

# Create a Streamlit app
st.title("LOB & Reinsurance File Processor")

# Sidebar for file selection
st.sidebar.header("File Selection")

lob_files = st.sidebar.file_uploader("Upload Line of Business Files", accept_multiple_files=True, type=["xlsx", "xlsb"])
reinsurance_files = st.sidebar.file_uploader("Upload Reinsurance Files", accept_multiple_files=True, type=["xlsx", "xlsb"])

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
                         "CF_T1_PVFC_LIC_OP", "CF_T1_PVFC_LIC_TEXPVAR_PY"]
        group2_sheets = ["CF_T1_PVFC_LIC_CLO_FADJ_PY", "CF_T1_PVFC_LIC_CLO_TADJ_PY",
                         "CF_T1_PVFC_LIC_DEREC","CF_T1_PVFC_LIC_EXPCLO_PY"]
        group3_sheets = ["CF_T1_PVFC_LIC_OP", "CF_T1_PVFC_LIC_OP_FADJ_PY","CF_T1_PVFC_LIC_OP_TADJ_PY"]
        group4_sheets = ["CF_T1_PVFC_LIC_TEXPVAR_PY", "CF_T1_PVFC_LIC_TASSCHG_PY",
                         "CF_T1_PVFC_LIC_FASSCHG_PY","CF_T1_PVFC_LIC_FEXPVAR_PY"]

        # Create a progress bar
        progress_bar = st.progress(0)

        # Initialize a list to store processed sheet DataFrames
        processed_sheets = {}

        # Process each sheet and save to the results folder
        total_sheets = group1_sheets + group2_sheets + group3_sheets + group4_sheets

        # Define the ZIP file name on GitHub
        zip_file_name = "Dodo_results/processed_sheets.zip"

        for sheet_name in total_sheets:
            merged_data = pd.DataFrame()

            for uploaded_file in all_files:
                try:
                    file_extension = os.path.splitext(uploaded_file.name)[-1].lower()
                    if file_extension == ".xlsx":
                        if sheet_name in pd.ExcelFile(uploaded_file).sheet_names:
                            df = pd.read_excel(uploaded_file, sheet_name=sheet_name, skiprows=8)
                        else:
                            continue
                    elif file_extension == ".xlsb":
                        if sheet_name in pd.ExcelFile(uploaded_file).sheet_names:
                            df = pd.read_excel(uploaded_file, sheet_name=sheet_name, skiprows=8, engine='pyxlsb')
                        else:
                            continue
                    else:
                        st.warning(f"Unsupported file format for {uploaded_file.name}. Only xlsx and xlsb files are supported.")
                        continue

                    merged_data = pd.concat([merged_data, df], ignore_index=True)
                except Exception as e:
                    st.error(f"Error reading {sheet_name} from {uploaded_file.name}: {e}")

            # Fill blank spaces or NaN with 0
            merged_data = merged_data.fillna(0)

            processed_sheets[sheet_name] = merged_data
            st.success(f"Processed {sheet_name}")

            # Update the progress bar
            progress_bar.progress((total_sheets.index(sheet_name) + 1) / len(total_sheets))

        # Remove the "* MACRO_STEP_ID_DESCRIPTION" column from ACTUARIAL_AOM_IMPACT.csv
        if "ACTUARIAL_AOM_IMPACT" in processed_sheets:
            if "* MACRO_STEP_ID_DESCRIPTION" in processed_sheets["ACTUARIAL_AOM_IMPACT"].columns:
                processed_sheets["ACTUARIAL_AOM_IMPACT"] = processed_sheets["ACTUARIAL_AOM_IMPACT"].drop(columns="* MACRO_STEP_ID_DESCRIPTION")

        st.success("All sheets processed successfully.")

        # Generate and save the ZIP file on your local machine
        with zipfile.ZipFile("processed_sheets.zip", 'w', zipfile.ZIP_DEFLATED) as zipf:
            for sheet_name, df in processed_sheets.items():
                csv_data = df.to_csv(index=False)
                zipf.writestr(f"{sheet_name}.csv", csv_data.encode())

        # Read the content of the generated ZIP file
        with open("processed_sheets.zip", 'rb') as zip_file:
            zip_file_content = zip_file.read()

        # Upload the generated ZIP file to your GitHub repository
        zip_contents = None
        try:
            zip_contents = repo.get_contents(zip_file_name)
        except Exception as e:
            pass

        if zip_contents:
            repo.update_file(zip_file_name, f"Update {zip_file_name}", zip_file_content, zip_contents.sha, branch="main")
        else:
            repo.create_file(zip_file_name, f"Create {zip_file_name}", zip_file_content, branch="main")

        # Add a link to the GitHub processed_sheets.zip file
        processed_sheets_link = f"[Download Processed Sheets.zip](https://github.com/{github_username}/{repository_name}/blob/main/{zip_file_name})"
        st.markdown(processed_sheets_link)

        # Download the ZIP file to system
        st.download_button(
            label="Download to System",
            data=zip_file_content,
            file_name="processed_sheets.zip",
            key="download_button"
        )

# Clear selections
if st.button("Clear Selections"):
    lob_files = st.sidebar.empty()
    reinsurance_files = st.sidebar.empty()
    st.success("Selections cleared.")
