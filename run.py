from modules.uploader import *

CsUCUploader = cs_factory(dic_uploader_config)
UCuploader = CsUCUploader()
UCuploader.login()
UCuploader.upload_to_google_photo(True)
UCuploader.upload_to_google_photo()
UCuploader.quit()

