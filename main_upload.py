from modules.uploader import *


CsUCUploader = cs_factory(dic_uploader_config)
UCuploader = CsUCUploader()

# menu = {
#     'login': UCuploader.login,
#     'register': UCuploader.register_config,
#     'upload': UCuploader.upload_to_google_photo,
# }
# task = None

# while True:
#     task = input(f"action:\n {'\n '.join(menu.keys())}\n")
#     if input == 'quit':
#         break
#     menu[task]()

UCuploader.upload_to_google_photo()

import os
import glob
import time

def delete_mkv_files(directory):
    # Search for all .mkv files in the directory (including subdirectories)
    mkv_files = [os.path.join(directory, file) for file in os.listdir(directory)
                 if file.endswith('.mkv') and os.path.isfile(os.path.join(directory, file))]
    # Iterate through each .mkv file and delete it
    for file in mkv_files:
        try:
            os.remove(file)
            print(f"Deleted: {file}")
        except Exception as e:
            print(f"Error deleting {file}: {e}")

# Example usage:
directory_path = UCuploader.config_data['mideo_folder']  # Change this to your directory
time.sleep(60)
delete_mkv_files(directory_path)