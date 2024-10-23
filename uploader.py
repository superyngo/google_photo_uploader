from modules.uploader import *

upload_config = {
  'no1' : 'C:/Users/user/Downloads/',
}

CsUCdriver = cs_factory(dic_uploader_config)
UCdriver = CsUCdriver()
UCdriver.google_uploader_handler(upload_config)
UCdriver.quit()

