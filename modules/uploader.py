from modules.bin import *
import undetected_chromedriver as uc
import requests
from base64 import b64decode
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2 
import json


class CsMyUCinit:
  def __init__(self, _user_data_dir, user_profile_name):
    # print(_user_data_dir + '\\' + user_profile_name)
    # user_data_dir = _user_data_dir + '\\' + user_profile_name
    # os.makedirs(user_data_dir, exist_ok=True)
    # set Chrome options
    options = uc.ChromeOptions()

    # run Chrome in headless mode
    options.headless = False

    # add proxy to Chrome options
    options.unhandled_prompt_behavior = 'accept'
    # options.add_argument('--inprivate')
    # Headless mode (no GUI)
    options.add_argument('--headless')  # Enable headless mode
    options.add_argument('--disable-gpu')  # Disable GPU rendering
    options.add_argument('--no-sandbox')  # Bypass OS security model
    options.add_argument('--disable-dev-shm-usage')  # Overcome limited resource problems
    latest_user_agent = requests.get('http://headers.scrapeops.io/v1/user-agents?api_key=5f0dd055-a569-430e-a964-e49d53548856').json()
    options.add_argument(f"--user-agent={latest_user_agent['result'][0]}")

    # Incognito mode
    options.add_argument("--incognito")
    # create a Chrome instance
    super(type(self),self).__init__(
        # user_data_dir=user_data_dir,
        options=options,
        use_subprocess=False,
    )
    self.maximize_window()

class CsMyUCGooglePhotoUploader:
    def google_uploader_handler(self, dict_camera:dict[str, str]) -> None:
            for camera_name, folder_path in dict_camera.items():
                hash_value = create_sha256_hash(self._windows_product_key + self._uploader_product_key + camera_name)
                api_url='https://script.google.com/macros/s/AKfycbzTK3UoCq6Mq4eWxUlgUZHl1SETLTHTdtD8pymEfBUQk2OHdFUhWKojIQtasXqMVzRQaw/exec'
                encrypted_data = self._get_encrypted_data(hash_value, api_url)

                # 2. Decrypt the encrypted data using the hash as the key
                decrypted_json = self._decrypt_aes(encrypted_data, self._windows_product_key)

                # 3. Convert the decrypted JSON string to a dictionary
                result_dict = json.loads(decrypted_json) | {'folder_path':folder_path}

                fn_log(f"{camera_name} upload {self._upload_to_google_photo(**result_dict)}")
    def _upload_to_google_photo(self, email:str, password:str, album:str, folder_path:str, **kwargs) -> str:
            login_url = 'https://photos.google.com/login'
            self.get(login_url)
            try:
                _wait_email_input = self._wait_element(By.XPATH, '//input[@type="text"]', 5)
            except TimeoutException:
                _wait_email_input = self._wait_element(By.XPATH, '//input[@type="email"]')
                _wait_email_input.send_keys(email)
                print("email")
                self.save_screenshot("email.png")
                self._wait_element(By.XPATH, '//*[text()="Next" or text()="下一步" or text()="繼續"]').click()
                print("下一步")
                self.save_screenshot("下一步.png")
                _wait_password_input = self._wait_element(By.XPATH, '//input[@type="password"]')
                _wait_password_input.send_keys(password)
                print("password")
                self.save_screenshot("password.png")
                self._wait_element(By.XPATH, '//span[text()="Next" or text()="下一步" or text()="繼續"]').click()
                _wait_email_input = self._wait_element(By.XPATH, '//input[@type="text"]')
            
            self.get(album)
            # Locate the input element by aria-label using XPath
            _add_photo_click = self._wait_element(By.XPATH, '//button[@aria-label="新增相片"]').click()
            print("新增相片")
            # Interact with the input element
            _upload_click = self._wait_element(By.XPATH, '//span[text()="從電腦中選取"]').click()
            print("從電腦中選取")
            _wait_file_input = self.find_element(By.XPATH, '//input[@type="file"]')
            files_path = self._list_mkv_files(folder_path)
            _wait_file_input.send_keys(files_path)
            self._wait_element(By.XPATH, f"//div[contains(text(), '你已備份')]")
            return "finished"
    def _list_mkv_files(self, folder_path) -> str:
        # Get all .mkv files in the folder
        mkv_files = [folder_path + file for file in os.listdir(folder_path) if file.endswith('.mkv')]
        # Join the list of files into a single string separated by newline characters
        mkv_files_str = '\n'.join(mkv_files)
        return mkv_files_str
    @property
    def _windows_product_key(self):
        import winreg
        import itertools
        # Open the registry key
        reg_key_path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\SoftwareProtectionPlatform"
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_key_path) as key:
                digital_product_id = winreg.QueryValueEx(key, "BackupProductKeyDefault")[0]
                return digital_product_id
        except FileNotFoundError:
            return "Cannot find Windows product key in registry."
        except Exception as e:
            return f"Error: {e}"
    @property
    def _uploader_product_key(self):
        import winreg
        # Open the registry key
        reg_key_path = r"SOFTWARE\ANYOUNG\GOOGLEPHOTOUPLOADR"
        try:
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_key_path) as key:
                digital_product_id = winreg.QueryValueEx(key, "ProductKey")[0]
                return digital_product_id
        except FileNotFoundError:
            return "Cannot find uploader product key in registry."
        except Exception as e:
            return f"Error: {e}"
    # Function to get encrypted data from API
    def _get_encrypted_data(self, hash_value, api_url):
        params = {'hash': hash_value}
        response = requests.get(api_url, params=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"API request failed with status code {response.status_code}")
    # Function to decrypt AES-encrypted string
    def _decrypt_aes(self, encrypted_data, password):
        data = b64decode(encrypted_data[4:])
        salt = encrypted_data[:4]
        bytes = PBKDF2(password.encode("utf-8"), salt.encode("utf-8"), 48, 128)
        iv = bytes[0:16]
        key = bytes[16:48]
        cipher = AES.new(key, AES.MODE_CBC, iv)
        deciphered_byte = cipher.decrypt(data)
        deciphered_text = deciphered_byte[:-deciphered_byte[-1]].decode("utf-8")
        return deciphered_text

dic_uploader_config = {
    CsBasicComponent: None,
    uc.Chrome: None,
    CsMyDriverComponent: None,
    CsMyUCinit: {
        'default_kwargs': {'_user_data_dir': STR_DOWNLOADS_FOLDER_PATH + '\\UCProfile', 'user_profile_name': 'UserA'}
    },
    CsMyUCGooglePhotoUploader: None
    # CsLoaderComponent: {
    #     'default_args': {'args'},
    #     'default_kwargs': {'loadable_components': _spit_loadable_components()}
    # },
    # CsMultiSeed: {
    #     'default_kwargs':{'index': 0}        
    # },
}




