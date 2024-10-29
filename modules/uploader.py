from modules.bin import *
from pathlib import Path

class CsMyUCGooglePhotoUploaderSimple:
    def __init__(self):
        app_name = 'mideoToGPhoto'
        # Define the path to the Roaming folder for the app
        self.app_folder = Path.home() / "AppData" / "Roaming" / "mideoToGPhoto"
        # Create the directory if it doesn't already exist
        self.app_folder.mkdir(parents=True, exist_ok=True)
        self.config_file = self.app_folder / "config.json"
        self.load_config()
    def _start_browser(self, bool_headless = False):
        self.options = uc.ChromeOptions()
        self.options.unhandled_prompt_behavior = 'accept'
        self.options.add_argument("--no-sandbox")
        self.options.add_argument("--disable-dev-shm-usage")
        if bool_headless:
            self.options.add_argument('--headless')  # Enable headless mode
            self.options.add_argument('--disable-gpu')  # Disable GPU rendering
        self.options.add_argument("--disable-infobars")
        self.options.add_argument("--disable-extensions")
        # https://developer.chrome.com/docs/chromedriver/logging/performance-log
        self.options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
        # Enable Chrome DevTools Protocol
        caps = DesiredCapabilities.CHROME
        caps['goog:loggingPrefs'] = {'performance': 'ALL'}
        latest_user_agent = requests.get('http://headers.scrapeops.io/v1/user-agents?api_key=5f0dd055-a569-430e-a964-e49d53548856').json()
        self.options.add_argument(f"--user-agent={latest_user_agent['result'][0]}")
        user_data_dir = self.app_folder / 'userProfile'
        self.driver = cs_factory({
            CsMyDriverComponent:{},
            uc.Chrome: {}
        })(
            desired_capabilities=caps,
            user_data_dir=user_data_dir,
            options=self.options,
            use_subprocess=False
        )

        self.driver.maximize_window()            
        # List to store each response
    def _login(self):
        if not self.driver:self._start_browser(False) 
        login_url = 'https://photos.google.com/login'
        self.driver.get(login_url)
        _wait = self.driver._wait_element(By.XPATH, '//input[@type="text"]')
        self.driver.quit()
    def load_config(self):
        # Load the config data if the file exists
        if self.config_file.exists():
            with self.config_file.open("r") as file:
                self.config_data = json.load(file)
            print("Configuration loaded:", self.config_data)
        else:
            print("Configuration file not found, Please register first.")
            self.register_config()
    def register_config(self):
        self.config_data = {
            'mideo_folder' : input('please input mideo folder:'),
            'album_url' : input('please input album url')
        }
        
        # Write the config data as JSON
        with self.config_file.open("w") as file:
            json.dump(self.config_data, file, indent=4)

        print(f"Configuration saved to: {self.config_file}")
    def handler(self) -> None:
        pass
    def _upload_to_google_photo(self, bool_headless = False) -> str:
        self._start_browser(bool_headless)
        res = self.driver._get_response(self.config_data['album_url'])
        if res['status'] == 404:
            self._login()
        res = self.driver._get_response(self.config_data['album_url'])
        # Locate the input element by aria-label using XPath
        _add_photo_click = self.driver._wait_element(By.XPATH, '//button[@aria-label="新增相片"]').click()
        print("新增相片")
        # Interact with the input element
        _upload_click = self.driver._wait_element(By.XPATH, '//span[text()="從電腦中選取"]').click()
        print("從電腦中選取")
        _wait_file_input = self.driver.find_element(By.XPATH, '//input[@type="file"]')
        files_path = self._list_mkv_files(self.config_data['mideo_folder'])
        _wait_file_input.driver.send_keys(files_path)
        self.driver._wait_element(By.XPATH, f"//div[contains(text(), '你已備份')]")
        print('Upload succefully')
        self.driver.quit()
    def _list_mkv_files(self, mideo_folder) -> str:
        # Get all .mkv files in the folder
        mkv_files = [mideo_folder + '\\' + file for file in os.listdir(mideo_folder) if file.endswith('.mkv')]
        # Join the list of files into a single string separated by newline characters
        mkv_files_str = '\n'.join(mkv_files)
        return mkv_files_str

dic_my_driver_config = {
    uc.Chrome: None,
    CsMyDriverComponent: None
}

dic_uploaderSimple_config = {
    CsBasicComponent: None,
    CsMyUCGooglePhotoUploaderSimple: {}
}

