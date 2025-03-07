import os
import shutil

# Define the source base directory and the destination directory
source_base_dir = './.data/train/images'
destination_dir = './dataset/images/train'

# Folders to copy
folders_to_copy = ['glide', 'loose', 'none', 'slab']

# Ensure the destination directory exists
os.makedirs(destination_dir, exist_ok=True)

# Iterate through each folder and copy files
for folder in folders_to_copy:
    folder_path = os.path.join(source_base_dir, folder)
    if os.path.exists(folder_path):
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            if os.path.isfile(file_path):  # Ensure it's a file
                shutil.copy(file_path, destination_dir)
                print(f"Copied {file_path} to {destination_dir}")
    else:
        print(f"Folder {folder_path} does not exist!")

print("All files copied successfully!")
