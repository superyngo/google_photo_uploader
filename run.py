from modules.uploader import *


CsUCUploader = cs_factory(dic_uploader_config)
UCuploader = CsUCUploader()

menu = {
    'login': UCuploader.login,
    'register': UCuploader.register_config,
    'upload': UCuploader.upload_to_google_photo,
}
input = None

while True:
    task = input(f"tasks:\n {"\n ".join(menu.keys())}\n")
    if input != 'quit':
        menu(task)()
    else:
        break

