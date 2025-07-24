import os
import zipfile
import shutil

source_folder = r"C:\Users\msmit\Downloads\Portal theme"
destination_folder = r"C:\Source\aura_portal\Aura.Portal\wwwroot\css"
source_file_name = "aura-portal-2025.css"
destination_file_name = "aura-portal.css"

# Find the first zip file in the source folder
for file_name in os.listdir(source_folder):
    if file_name.endswith('.zip'):
        zip_file_path = os.path.join(source_folder, file_name)
        print(f"Found zip file: {zip_file_path}")
        break
else:
    print("No zip file found in the source folder.")
    exit()

# Open the zip file and navigate to the specified path
with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
    css_file_path = f"aura-portal-2025/dist/css/{source_file_name}"
    if css_file_path in zip_ref.namelist():
        print(f"File found: {css_file_path}")
        # Extract the file to the destination folder
        zip_ref.extract(css_file_path, destination_folder)
        # Rename the extracted file to the desired name
        extracted_file_path = os.path.join(destination_folder, css_file_path)
        final_destination_path = os.path.join(destination_folder, destination_file_name)
        if os.path.exists(final_destination_path):
            os.remove(final_destination_path)
        os.rename(extracted_file_path, final_destination_path)
        print(f"File copied to: {final_destination_path}")
    else:
        print(f"No file found at {css_file_path}")
        exit()