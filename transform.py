import streamlit as st
import pandas as pd
import os
import zipfile
from github import Github
import tempfile

# Retrieve the GitHub personal access token
github_access_token = st.secrets["github"]["access_token"]

# GitHub credentials and repository details
github_username = 'KeeObom'
repository_name = 'lobs_reserves'
github_token = github_access_token
repo_path = f"{github_username}/{repository_name}"

# Initialize GitHub client
g = Github(github_token)
repo = g.get_repo(repo_path)

# Streamlit App
def main():
    st.title("LOB & Reinsurance File Processor V2")

    # File upload section
    st.sidebar.header("File Selection")
    lob_files = st.sidebar.file_uploader("Upload Line of Business Files", accept_multiple_files=True, type=["xlsx", "xlsb"])
    reinsurance_files = st.sidebar.file_uploader("Upload Reinsurance Files", accept_multiple_files=True, type=["xlsx", "xlsb"])

    st.sidebar.subheader("Selected Files")
    if lob_files:
        st.sidebar.write("LOB Files:", [f.name for f in lob_files])
    if reinsurance_files:
        st.sidebar.write("Reinsurance Files:", [f.name for f in reinsurance_files])

    # Sheet groups
    group1_sheets = ["ACTUALS_FOR_VISUALIZATION", "ACTUARIAL_AOM_IMPACT", "CF_T1_PVFC_LIC_CLO",
                     "CF_T1_PVFC_LIC_INCEXP_LIC_INCR", "CF_T1_PVFC_LIC_INCLAIM_LIC_INCR", "CURVE_ID_PARAM",
                     "INITIALIZATION", "MANDATORY_ACTUALS", "MP_GOC", "MP_GOC_SEG", "OCI_OPTION_DERECOG",
                     "CF_T1_PVFC_LIC_CLO_FADJ_PY", "CF_T1_PVFC_LIC_OP", "CF_T1_PVFC_LIC_TEXPVAR_PY"]
    group2_sheets = ["CF_T1_PVFC_LIC_CLO_FADJ_PY", "CF_T1_PVFC_LIC_CLO_TADJ_PY", "CF_T1_PVFC_LIC_DEREC",
                     "CF_T1_PVFC_LIC_EXPCLO_PY"]
    group3_sheets = ["CF_T1_PVFC_LIC_OP", "CF_T1_PVFC_LIC_OP_FADJ_PY", "CF_T1_PVFC_LIC_OP_TADJ_PY"]
    group4_sheets = ["CF_T1_PVFC_LIC_TEXPVAR_PY", "CF_T1_PVFC_LIC_TASSCHG_PY", "CF_T1_PVFC_LIC_FASSCHG_PY",
                     "CF_T1_PVFC_LIC_FEXPVAR_PY"]

    all_files = lob_files + reinsurance_files
    total_sheets = group1_sheets + group2_sheets + group3_sheets + group4_sheets

    if st.button("Generate All"):
        if not all_files:
            st.error("Please upload at least one file.")
            return

        processed_sheets = {}
        progress = st.progress(0)

        for i, sheet in enumerate(total_sheets):
            merged_df = pd.DataFrame()

            for file in all_files:
                try:
                    ext = os.path.splitext(file.name)[-1].lower()
                    excel_file = pd.ExcelFile(file, engine='pyxlsb' if ext == '.xlsb' else None)
                    if sheet not in excel_file.sheet_names:
                        continue
                    df = pd.read_excel(excel_file, sheet_name=sheet, skiprows=8)

                    # Normalize numeric columns conditionally
                    for col in df.columns[1:]:
                        numeric_like = df[col].apply(
                            lambda x: isinstance(x, (int, float)) or str(x).replace('.', '', 1).isdigit()
                        )
                        if numeric_like.mean() > 0.9:
                            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

                    merged_df = pd.concat([merged_df, df], ignore_index=True)

                except Exception as e:
                    st.error(f"Error reading {sheet} from {file.name}: {e}")

            # Specific column cleanup
            if sheet == "ACTUARIAL_AOM_IMPACT" and "* MACRO_STEP_ID_DESCRIPTION" in merged_df.columns:
                merged_df = merged_df.drop(columns="* MACRO_STEP_ID_DESCRIPTION")

            processed_sheets[sheet] = merged_df
            st.success(f"Processed {sheet}")
            progress.progress((i + 1) / len(total_sheets))

        # Create ZIP in memory
        zip_buffer = tempfile.NamedTemporaryFile(delete=False, suffix=".zip")
        with zipfile.ZipFile(zip_buffer.name, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for sheet, df in processed_sheets.items():
                zipf.writestr(f"{sheet}.csv", df.to_csv(index=False))

        zip_buffer.seek(0)
        zip_path = zip_buffer.name

        # Upload to GitHub
        github_file_path = "Dodo_results/processed_sheets.zip"
        try:
            contents = repo.get_contents(github_file_path)
            repo.update_file(github_file_path, f"Update {github_file_path}", zip_buffer.read(), contents.sha, branch="main")
        except:
            zip_buffer.seek(0)
            repo.create_file(github_file_path, f"Create {github_file_path}", zip_buffer.read(), branch="main")

        # Download buttons
        zip_buffer.seek(0)
        st.success("All sheets processed and ZIP file created.")
        st.markdown(f"[Download from GitHub](https://github.com/{github_username}/{repository_name}/blob/main/{github_file_path})")
        st.download_button("Download Processed Sheets", zip_buffer.read(), file_name="processed_sheets.zip")

        st.info("Please click the button above to save your file.")

if __name__ == "__main__":
    main()


# #Second Trial, some string columns were being changed to zero
# import streamlit as st
# import pandas as pd
# import os
# import zipfile
# from github import Github
# import tempfile

# # Retrieve the GitHub personal access token
# github_access_token = st.secrets["github"]["access_token"]

# # GitHub credentials and repository details
# github_username = 'KeeObom'
# repository_name = 'lobs_reserves'
# github_token = github_access_token
# repo_path = f"{github_username}/{repository_name}"

# # Initialize GitHub client
# g = Github(github_token)
# repo = g.get_repo(repo_path)

# # Streamlit App
# def main():
#     st.title("LOB & Reinsurance File Processor V2")

#     # File upload section
#     st.sidebar.header("File Selection")
#     lob_files = st.sidebar.file_uploader("Upload Line of Business Files", accept_multiple_files=True, type=["xlsx", "xlsb"])
#     reinsurance_files = st.sidebar.file_uploader("Upload Reinsurance Files", accept_multiple_files=True, type=["xlsx", "xlsb"])

#     st.sidebar.subheader("Selected Files")
#     if lob_files:
#         st.sidebar.write("LOB Files:", [f.name for f in lob_files])
#     if reinsurance_files:
#         st.sidebar.write("Reinsurance Files:", [f.name for f in reinsurance_files])

#     # Sheet groups
#     group1_sheets = ["ACTUALS_FOR_VISUALIZATION", "ACTUARIAL_AOM_IMPACT", "CF_T1_PVFC_LIC_CLO",
#                      "CF_T1_PVFC_LIC_INCEXP_LIC_INCR", "CF_T1_PVFC_LIC_INCLAIM_LIC_INCR", "CURVE_ID_PARAM",
#                      "INITIALIZATION", "MANDATORY_ACTUALS", "MP_GOC", "MP_GOC_SEG", "OCI_OPTION_DERECOG",
#                      "CF_T1_PVFC_LIC_CLO_FADJ_PY", "CF_T1_PVFC_LIC_OP", "CF_T1_PVFC_LIC_TEXPVAR_PY"]
#     group2_sheets = ["CF_T1_PVFC_LIC_CLO_FADJ_PY", "CF_T1_PVFC_LIC_CLO_TADJ_PY", "CF_T1_PVFC_LIC_DEREC",
#                      "CF_T1_PVFC_LIC_EXPCLO_PY"]
#     group3_sheets = ["CF_T1_PVFC_LIC_OP", "CF_T1_PVFC_LIC_OP_FADJ_PY", "CF_T1_PVFC_LIC_OP_TADJ_PY"]
#     group4_sheets = ["CF_T1_PVFC_LIC_TEXPVAR_PY", "CF_T1_PVFC_LIC_TASSCHG_PY", "CF_T1_PVFC_LIC_FASSCHG_PY",
#                      "CF_T1_PVFC_LIC_FEXPVAR_PY"]

#     all_files = lob_files + reinsurance_files
#     total_sheets = group1_sheets + group2_sheets + group3_sheets + group4_sheets

#     if st.button("Generate All"):
#         if not all_files:
#             st.error("Please upload at least one file.")
#             return

#         processed_sheets = {}
#         progress = st.progress(0)

#         for i, sheet in enumerate(total_sheets):
#             merged_df = pd.DataFrame()

#             for file in all_files:
#                 try:
#                     ext = os.path.splitext(file.name)[-1].lower()
#                     excel_file = pd.ExcelFile(file, engine='pyxlsb' if ext == '.xlsb' else None)
#                     if sheet not in excel_file.sheet_names:
#                         continue
#                     df = pd.read_excel(excel_file, sheet_name=sheet, skiprows=8)

#                     # Normalize numeric columns
#                     for col in df.columns[1:]:
#                         df[col] = pd.to_numeric(df[col], errors='coerce')
#                     df.iloc[:, 1:] = df.iloc[:, 1:].fillna(0)

#                     merged_df = pd.concat([merged_df, df], ignore_index=True)

#                 except Exception as e:
#                     st.error(f"Error reading {sheet} from {file.name}: {e}")

#             # Specific column cleanup
#             if sheet == "ACTUARIAL_AOM_IMPACT" and "* MACRO_STEP_ID_DESCRIPTION" in merged_df.columns:
#                 merged_df = merged_df.drop(columns="* MACRO_STEP_ID_DESCRIPTION")

#             processed_sheets[sheet] = merged_df
#             st.success(f"Processed {sheet}")
#             progress.progress((i + 1) / len(total_sheets))

#         # Create ZIP in memory
#         zip_buffer = tempfile.NamedTemporaryFile(delete=False, suffix=".zip")
#         with zipfile.ZipFile(zip_buffer.name, 'w', zipfile.ZIP_DEFLATED) as zipf:
#             for sheet, df in processed_sheets.items():
#                 zipf.writestr(f"{sheet}.csv", df.to_csv(index=False))

#         zip_buffer.seek(0)
#         zip_path = zip_buffer.name

#         # Upload to GitHub
#         github_file_path = "Dodo_results/processed_sheets.zip"
#         try:
#             contents = repo.get_contents(github_file_path)
#             repo.update_file(github_file_path, f"Update {github_file_path}", zip_buffer.read(), contents.sha, branch="main")
#         except:
#             zip_buffer.seek(0)
#             repo.create_file(github_file_path, f"Create {github_file_path}", zip_buffer.read(), branch="main")

#         # Download buttons
#         zip_buffer.seek(0)
#         st.success("All sheets processed and ZIP file created.")
#         st.markdown(f"[Download from GitHub](https://github.com/{github_username}/{repository_name}/blob/main/{github_file_path})")
#         st.download_button("Download Processed Sheets", zip_buffer.read(), file_name="processed_sheets.zip")

#         # Auto-download (Note: Streamlit does not support true auto-download, browser permissions block it)
#         st.info("Please click the button above to save your file.")

# if __name__ == "__main__":
#     main()

## Original code working for months
# import streamlit as st
# import pandas as pd
# import os
# import zipfile
# from github import Github

# # Retrieve the GitHub personal access token
# github_access_token = st.secrets["github"]["access_token"]

# # Initialize lists to store selected files
# lob_files = []
# reinsurance_files = []

# # Define your GitHub repository credentials
# github_username = 'KeeObom'
# github_token = github_access_token
# repository_name = 'lobs_reserves'

# # Initialize a GitHub instance with your credentials
# g = Github(github_username, github_token)

# # Specify the target repository
# repo = g.get_repo(f"{github_username}/{repository_name}")

# # Create a Streamlit app
# st.title("LOB & Reinsurance File Processor V2")

# # Sidebar for file selection
# st.sidebar.header("File Selection")

# lob_files = st.sidebar.file_uploader("Upload Line of Business Files", accept_multiple_files=True, type=["xlsx", "xlsb"])
# reinsurance_files = st.sidebar.file_uploader("Upload Reinsurance Files", accept_multiple_files=True, type=["xlsx", "xlsb"])

# # Display selected files
# st.sidebar.subheader("Selected Files:")
# if lob_files:
#     st.sidebar.write("Line of Business Files:")
#     st.sidebar.write(lob_files)
# if reinsurance_files:
#     st.sidebar.write("Reinsurance Files:")
#     st.sidebar.write(reinsurance_files)

# # Main section
# st.header("File Processing")

# # Process the files
# if st.button("Generate All"):
#     if not lob_files and not reinsurance_files:
#         st.error("Please upload Line of Business and Reinsurance files.")
#     else:
#         # Create a folder for generated sheet files
#         results_folder = "Dodo_results"
#         os.makedirs(results_folder, exist_ok=True)

#         # Combine the lists of files
#         all_files = lob_files + reinsurance_files

#         # Define the sheet names you want to process
#         group1_sheets = ["ACTUALS_FOR_VISUALIZATION", "ACTUARIAL_AOM_IMPACT", "CF_T1_PVFC_LIC_CLO","CF_T1_PVFC_LIC_INCEXP_LIC_INCR",
#                          "CF_T1_PVFC_LIC_INCLAIM_LIC_INCR","CURVE_ID_PARAM","INITIALIZATION","MANDATORY_ACTUALS",
#                          "MP_GOC","MP_GOC_SEG","OCI_OPTION_DERECOG", "CF_T1_PVFC_LIC_CLO_FADJ_PY",
#                          "CF_T1_PVFC_LIC_OP", "CF_T1_PVFC_LIC_TEXPVAR_PY"]
#         group2_sheets = ["CF_T1_PVFC_LIC_CLO_FADJ_PY", "CF_T1_PVFC_LIC_CLO_TADJ_PY",
#                          "CF_T1_PVFC_LIC_DEREC","CF_T1_PVFC_LIC_EXPCLO_PY"]
#         group3_sheets = ["CF_T1_PVFC_LIC_OP", "CF_T1_PVFC_LIC_OP_FADJ_PY","CF_T1_PVFC_LIC_OP_TADJ_PY"]
#         group4_sheets = ["CF_T1_PVFC_LIC_TEXPVAR_PY", "CF_T1_PVFC_LIC_TASSCHG_PY",
#                          "CF_T1_PVFC_LIC_FASSCHG_PY","CF_T1_PVFC_LIC_FEXPVAR_PY"]

#         # Create a progress bar
#         progress_bar = st.progress(0)

#         # Initialize a list to store processed sheet DataFrames
#         processed_sheets = {}

#         # Process each sheet and save to the results folder
#         total_sheets = group1_sheets + group2_sheets + group3_sheets + group4_sheets

#         # Define the ZIP file name on GitHub
#         zip_file_name = "Dodo_results/processed_sheets.zip"

#         for sheet_name in total_sheets:
#             merged_data = pd.DataFrame()

#             for uploaded_file in all_files:
#                 try:
#                     file_extension = os.path.splitext(uploaded_file.name)[-1].lower()
#                     if file_extension == ".xlsx":
#                         if sheet_name in pd.ExcelFile(uploaded_file).sheet_names:
#                             df = pd.read_excel(uploaded_file, sheet_name=sheet_name, skiprows=8)
#                         else:
#                             continue
#                     elif file_extension == ".xlsb":
#                         if sheet_name in pd.ExcelFile(uploaded_file).sheet_names:
#                             df = pd.read_excel(uploaded_file, sheet_name=sheet_name, skiprows=8, engine='pyxlsb')
#                         else:
#                             continue
#                     else:
#                         st.warning(f"Unsupported file format for {uploaded_file.name}. Only xlsx and xlsb files are supported.")
#                         continue

#                     merged_data = pd.concat([merged_data, df], ignore_index=True)
#                 except Exception as e:
#                     st.error(f"Error reading {sheet_name} from {uploaded_file.name}: {e}")

#             # Fill blank spaces or NaN with 0
#             merged_data = merged_data.fillna(0)

#             processed_sheets[sheet_name] = merged_data
#             st.success(f"Processed {sheet_name}")

#             # Update the progress bar
#             progress_bar.progress((total_sheets.index(sheet_name) + 1) / len(total_sheets))

#         # Remove the "* MACRO_STEP_ID_DESCRIPTION" column from ACTUARIAL_AOM_IMPACT.csv
#         if "ACTUARIAL_AOM_IMPACT" in processed_sheets:
#             if "* MACRO_STEP_ID_DESCRIPTION" in processed_sheets["ACTUARIAL_AOM_IMPACT"].columns:
#                 processed_sheets["ACTUARIAL_AOM_IMPACT"] = processed_sheets["ACTUARIAL_AOM_IMPACT"].drop(columns="* MACRO_STEP_ID_DESCRIPTION")

#         st.success("All sheets processed successfully.")

#         # Generate and save the ZIP file on your local machine
#         with zipfile.ZipFile("processed_sheets.zip", 'w', zipfile.ZIP_DEFLATED) as zipf:
#             for sheet_name, df in processed_sheets.items():
#                 csv_data = df.to_csv(index=False)
#                 zipf.writestr(f"{sheet_name}.csv", csv_data.encode())

#         # Read the content of the generated ZIP file
#         with open("processed_sheets.zip", 'rb') as zip_file:
#             zip_file_content = zip_file.read()

#         # Upload the generated ZIP file to your GitHub repository
#         zip_contents = None
#         try:
#             zip_contents = repo.get_contents(zip_file_name)
#         except Exception as e:
#             pass

#         if zip_contents:
#             repo.update_file(zip_file_name, f"Update {zip_file_name}", zip_file_content, zip_contents.sha, branch="main")
#         else:
#             repo.create_file(zip_file_name, f"Create {zip_file_name}", zip_file_content, branch="main")

#         # Add a link to the GitHub processed_sheets.zip file
#         processed_sheets_link = f"[Download Processed Sheets.zip](https://github.com/{github_username}/{repository_name}/blob/main/{zip_file_name})"
#         st.markdown(processed_sheets_link)

#         # Download the ZIP file to system
#         st.download_button(
#             label="Download to System",
#             data=zip_file_content,
#             file_name="processed_sheets.zip",
#             key="download_button"
#         )

# # Clear selections
# if st.button("Clear Selections"):
#     lob_files = st.sidebar.empty()
#     reinsurance_files = st.sidebar.empty()
#     st.success("Selections cleared.")
