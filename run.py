from modules.uploader import *

CsUCdriver = cs_factory(dic_uploaderSimple_config)
UCdriver = CsUCdriver()
UCdriver._login()
UCdriver._upload_to_google_photo()
UCdriver.quit()

