# 20241014
from modules.timestamp import *
import time, re, ast, os
import threading
from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.common.exceptions import UnexpectedAlertPresentException, NoSuchElementException, TimeoutException, NoAlertPresentException, JavascriptException
from typing import TypedDict, Any, Callable
from types import MethodType
import hashlib

os.environ['HTTPS_PROXY'] = ''
os.environ['HTTP_PROXY'] = ''
import sqlite3
LOCK = threading.Lock()

# URL and Path
STR_DOWNLOADS_FOLDER_PATH = os.path.join(os.path.expanduser('~'), 'Downloads')
STR_DOWNLOADS_TIMESTAMP_FOLDER_PATH = f"{STR_DOWNLOADS_FOLDER_PATH}\\{STR_DATESTAMP}"
os.makedirs(STR_DOWNLOADS_TIMESTAMP_FOLDER_PATH, exist_ok=True)
DB_PATH = r'D:\Users\user\OneDrive - Chunghwa Telecom Co., Ltd\Work\99_共享檔案\三駐點\存控\存控.db'

def fn_log(str_log:str, str_filename:str = "") -> None:
    # Get the current date and time
    current_time = datetime.datetime.now()
    # Format the timestamp as a readable string
    timestamp = current_time.strftime("%Y-%m-%d %H:%M:%S")
    # Define the log message with the timestamp
    log_message = f"{timestamp} - {str_log}\n"
    # Open the log file in append mode ('a')
    if str_filename == "":
        str_filename = f"{STR_DATESTAMP}_log.txt"
    with open(f"{STR_DOWNLOADS_TIMESTAMP_FOLDER_PATH}\\{str_filename}", 'a') as log_file:
        # Write the log message to the file
        log_file.write(log_message)
    print(log_message)

def sanitize_string(value):
    # Remove non-printable and non-ASCII characters, except for common Chinese characters and punctuation
    if isinstance(value, str):
        return re.sub(r'[^\x20-\x7E\u4E00-\u9FFF\u3000-\u303F]', '', value)
    return value

def split_list(input_list:list, num:int=1):
    # Create a list of empty lists
    result = [[] for _ in range(num)]
    # Iterate through the input list and distribute elements into sublists
    for i, val in enumerate(input_list):
        result[i % num].append(val)
    return result

def split_to_dict(source:any, num:int=1) -> dict[int, any]:
    def _list(_list, num:int=1)->dict[int, any]:
        if len(_list) < num:
            num=len(_list)
        # Create a dictionary with empty lists for each key
        result = {i: [] for i in range(num)}
        # Iterate through the input list and distribute elements into the sublists
        for i, val in enumerate(_list):
            result[i % num].append(val)
        return result
    if isinstance(source, (list,tuple)):
        return _list(source, num)
    if isinstance(source, dict):
        return {k: dict(v) for k, v in _list(source.items(), num).items()}
    raise TypeError("source must be type list, tuple or dictionary")

def create_lst_of(n:int, element={'index': None, 'driver': None, 'list': []}):
    return [element for _ in range(n)]

def multithreading(source:any, call_def:Callable, threads:int=1, args:list=[], kwargs:dict={}):
    with ThreadPoolExecutor(max_workers=threads) as executor:
        match source:
            case None:
                futures = [
                    executor.submit(call_def, *args, index=index, **kwargs)  
                    for index in list(range(threads))
                ]
            case list() | tuple() | dict():
                futures = [
                    executor.submit(call_def, *args, source=splitted_source, index=index, **kwargs)  
                    for index, splitted_source in split_to_dict(source, threads).items()
                ]
            case _:
                futures = [
                    executor.submit(call_def, *args, source=source, index=index, **kwargs) 
                    for index in list(range(threads))
                ] 
        for future in futures:
            future.result()

def convert_roc_to_western(roc_date: str = "") -> str:
    if roc_date == "":
        return ""
    # Step 1: Eliminate all non-numeric characters except "/" and "-"
    cleaned_date = re.sub(r'[^\d/-]', '', roc_date)
    # Step 2: Extract the first 3 characters (ROC year) and convert to Western year
    roc_year = int(cleaned_date[:3])
    western_year = str(roc_year + 1911)
    # Step 3: Combine Western year with the remaining part of the ROC date string
    western_date = western_year + cleaned_date[3:]
    return western_date

def create_sha256_hash(data):
    # Create a SHA-256 hash object
    sha256_hash = hashlib.sha256()
    
    # Encode the input data to bytes (if it's a string) and update the hash object
    sha256_hash.update(data.encode('utf-8'))
    
    # Get the hexadecimal representation of the hash
    return sha256_hash.hexdigest()

class DatabaseManager:
    def __init__(self, db_name):
        self._db_name = db_name
        self._conn = None
        self._cursor = None

    @property
    def sqlite(self):
        if self._cursor is None:
            raise ConnectionError("Database is not connected. Call sqlite.setter with 'connect' first.")
        return self._cursor

    @sqlite.setter
    def sqlite(self, action="connect"):
        try:
            if action == "connect":
                if self._conn is None:
                    self._conn = sqlite3.connect(self._db_name)
                    self._cursor = self._conn.cursor()
                else:
                    print("Database is already connected.")
            elif action == "close":
                if self._conn is not None:
                    self._conn.close()
                    self._conn = None
                    self._cursor = None
                else:
                    print("Database is already closed.")
            else:
                raise ValueError("Invalid action. Use 'connect' or 'close'.")
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            self._conn = None
            self._cursor = None
            raise

    def execute_query(self, query, parameters=None):
        try:
            if self._cursor is None:
                raise ConnectionError("Database is not connected. Call sqlite.setter with 'connect' first.")
            
            if parameters:
                self._cursor.execute(query, parameters)
            else:
                self._cursor.execute(query)
            
            self._conn.commit()
            return self._cursor.fetchall()
        except sqlite3.Error as e:
            print(f"An error occurred while executing the query: {e}")
            self._conn.rollback()
            raise

    def execute_many(self, query, parameters):
        try:
            if self._cursor is None:
                raise ConnectionError("Database is not connected. Call sqlite.setter with 'connect' first.")
            
            self._cursor.executemany(query, parameters)
            self._conn.commit()
            return self._cursor.rowcount
        except sqlite3.Error as e:
            print(f"An error occurred while executing the batch query: {e}")
            self._conn.rollback()
            raise
    def write_db(self, dbname:str, columns:list[str], records:list[list]):
        insert_replace_sql = f'''
        INSERT OR REPLACE INTO {dbname} (
            {','.join(columns)}
        ) VALUES ({",".join(["?"] * len(columns))})
        '''
        try:
            if self._cursor is None:
                raise ConnectionError("Database is not connected. Call sqlite.setter with 'connect' first.")
            
            self._cursor.executemany(insert_replace_sql, records)
            self._conn.commit()
            return self._cursor.rowcount
        except sqlite3.Error as e:
            print(f"An error occurred while executing the batch query: {e}")
            self._conn.rollback()
            raise
    def __enter__(self):
        self.sqlite = "connect"
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.sqlite = "close"

class CsMyClass:
    def __init__(self, **kwargs) -> None:
        dic_default_values = {} # if default needed
        for key, value in kwargs.items():
            if key in self.__slots__:
                setattr(self, key, dic_default_values.get(key, value))
            else:
                raise AttributeError(f"'{key}' is not a valid attribute for {self.__class__.__name__}")
    def __getattr__(self, name):
        if name in self.__slots__:
            raise AttributeError(f"'{name}' was not set during initialization")
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")

class CsBasicComponent:
    def __getattr__(self, name):
        raise AttributeError(f"'{self.__class__.__name__}' '{name}' was not set")

class CsMyDriverComponent:
    def _select_change_value(self, By_locator: str, locator: str, new_value: str) -> None:
        _select_element = WebDriverWait(self, 20).until(EC.element_to_be_clickable((By_locator, locator)))
        _select_element = Select(_select_element)  # Create a Select instance
        _select_element.select_by_value(new_value)
    def _input_send_keys(self, By_locator: str, locator: str, new_value: str) -> None:
        _input_element = WebDriverWait(self, 20).until(EC.element_to_be_clickable((By_locator, locator)))
        _input_element.clear()
        _input_element.send_keys(new_value)
    def _wait_element(self, By_locator: str, locator: str, time: int = 1000):
        try:
            return WebDriverWait(self, time).until(EC.element_to_be_clickable((By_locator, locator)))
        except UnexpectedAlertPresentException:
            try:
                self.switch_to.alert.accept()
            except NoAlertPresentException:
                pass
            return WebDriverWait(self, time).until(EC.presence_of_element_located((By_locator, locator)))
    def _try_extract_element_value(self, element, error_return = "") -> str:
        try:
            match element.tag_name:
                case 'input' | 'textarea':
                    if element.get_attribute('type') == 'checkbox':
                        return element.get_attribute('checked')
                    return element.get_attribute('value')
                case 'select':
                    return Select(element).first_selected_option.text
                case _:
                    return element.text
        except NoSuchElementException:
            return error_return

class CsMyEdgeDriverInit:
    def __init__(self, user_data_dir):
        import logging
        Service = webdriver.EdgeService
        Options = webdriver.EdgeOptions
        # Suppress selenium and webdriver_manager logs
        logging.getLogger('selenium').setLevel(logging.WARNING)
        logging.getLogger('urllib3').setLevel(logging.WARNING)
        logging.getLogger('webdriver_manager').setLevel(logging.WARNING)
        # Set up paths
        user_data_dir = os.path.abspath(user_data_dir)
        log_path = os.path.abspath("./logs/edge_driver.log")

        # Create directories if they don't exist
        os.makedirs(user_data_dir, exist_ok=True)
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        edge_bin = './bin/msedgedriver.exe'
        service_args=[
                    #   '--log-level=ALL',
                    #   '--append-log',
                    #   '--readable-timestamp',
                    '--disable-build-check',
                    ]
        service = Service(executable_path=edge_bin, service_args=service_args)
        options = Options()
        options.unhandled_prompt_behavior = 'accept'
        options.add_argument('--inprivate')
        # options.add_argument(f"user-data-dir={user_data_dir}")
        options.add_argument("--disable-notifications")
        options.add_argument("--log-level=3")
        super(type(self),self).__init__(service=service, options=options)
        self.int_main_window_handle = self.current_window_handle

class CsLoaderComponent:
    def __init__(self, *args, loadable_components: dict):
        self._loadable_components = loadable_components
        self._loaded_components = set()
        if args: self.load_components(*args)
    def load_components(self, *args) -> None:
        if 'ALL' in args:
            args = set(self._loadable_components) - {'_loader_init_remove'}
        for task in args:
            if task in self._loaded_components:
                fn_log(f"{task} has already been loaded so skip")
                continue
            if task in set(self._loadable_components) - {'_loader_init_remove'}:
                for key, value in self._loadable_components[task].items():
                    match key:
                        case '__init__component':
                            MethodType(value, self)()
                        case '__remove__component':
                            pass
                        case _:
                            setattr(self, key, MethodType(value, self) if callable(value) else value)
            else:
                raise AttributeError(f"'{task}' is not a valid task for {self.__class__.__name__}, try {list(self._loadable_components.keys())} or 'ALL' ")
            if self._loadable_components.get('_loader_init_remove'): MethodType(self._loadable_components['_loader_init_remove']['__init__loader'], self)(task)
            self._loaded_components.add(task)
            fn_log(f"{task} loaded successfully")
        return None
    def remove_components(self, *args) -> None:
        if 'ALL' in args:
            args = set(self._loadable_components) - {'_loader_init_remove'}
        for task in args:
            if task in self._loaded_components:
                for key,value in self._loadable_components[task].items():
                    match key:
                        case '__init__component':
                            pass
                        case '__remove__component':
                            MethodType(value, self)()
                        case _:
                            if hasattr(self, key): delattr(self, key)
                if self._loadable_components.get('_loader_init_remove'): MethodType(self._loadable_components['_loader_init_remove']['__remove__loader'], self)(task)
                self._loaded_components.remove(task)
                fn_log(f"{task} removed successfully")
            else:
                raise AttributeError(f"'{task}' components is not loaded or component {task} doesn't exists")
        return None

class CsMultiSeed:
    def __init__(self, index):
        self._index = index
    def _close_instance(self):
        self.close() # depends on the instance
        self.quit()
class CsMultiManager:
    def __init__(self, *args, threads, subclass, **kwargs) -> None: 
        for key, value in {'instances':{}, 'sources':{}, 'threads': 0, 'subclass': subclass, 'args': set(args), 'kwargs': kwargs}.items():
            setattr(self, '_' + key, value)
        # init instances
        self.threads = threads
    def _init_instances(self) -> None:
        def _init_instance(*args, index, **kwargs):
            if index in self._instances:
                fn_log(f"{index} instance already exists so pass")
                return
            fn_log(f"start initializing {index} instance")
            self._instances.update({index: self._subclass(*args, index=index, **kwargs)})
        multithreading(
            source = None,
            call_def = _init_instance,
            threads = self._threads,
            args = self._args,
            kwargs = self._kwargs
        )
    def _call_instances(self, handler:str, threads:int=None) -> Callable:
        if threads is None: threads = self._threads 
        if threads <= 0: raise ValueError('threads must be positive integer( >0 )')
        def _def_wrapper(*args, source:any=None, threads:int=threads, **kwargs):
            match threads:
                case _ if threads <= 0: raise ValueError('threads must be positive integer( >0 )')
                case _ if threads > self._threads: self.threads = threads
                case _: pass
            # split source into self._sources
            if isinstance(source,(list, tuple, dict)):
                self._sources.clear()
                multithreading(
                    source = source,
                    call_def = lambda source, index: self._sources.update({index: source}),
                    threads = threads,
                )
            # execute instances def
            multithreading(
                source = source,
                call_def = lambda *args, index, **kwargs: getattr(self._instances[index], handler)(*args, **kwargs),
                threads = threads,
                args = args,
                kwargs = kwargs
            )
        return _def_wrapper
    @property # Getter
    def threads(self) -> int:
        return self._threads
    @threads.setter # Setter
    def threads(self, threads: int) -> None:
        if not isinstance(threads, int) or threads < 0: raise TypeError(f"threads must > 0")
        match threads:
            case self._threads:
                fn_log(f"current threads {threads} unchanged")
            case _ if threads > self._threads:
                self._threads = threads
                self._init_instances()
            case _ if threads < self._threads:
                for i in range(threads, self._threads):
                    self._instances[i]._close_instance() 
                    self._instances.pop(i)
                self._threads = threads
class CsMultiLoaderEntry:
    def __init__(self):
        if self.threads == 0: self.threads = 1
        self._instances_loadable_components = self._instances[0]._loadable_components
        for task in self._args:
            for handler in self._instances_loadable_components[task]:
                if not task.startswith("_"):
                    setattr(self, handler, self._call_instances(handler=handler))
    def load_instances_components(self, *args, threads:int=None) -> None:
        if 'ALL' in args:
            args = set(self._instances_loadable_components)
        for task in args:
            if task in self._args:
                fn_log(f"{task} has already been loaded so skip")
                continue
            if task in self._instances_loadable_components:
                # load component to instances
                self._call_instances(handler='load_components')(task)
                # set handler entrance for multi_manager
                for handler in self._instances_loadable_components[task]:
                    if not task.startswith("_"):
                        setattr(self, handler, self._call_instances(handler=handler, threads=threads))
            else:
                raise AttributeError(f"'{task}' is not a valid task for {self.__class__.__name__}, try {set(self._instances_loadable_components)} or 'ALL' ")
            self._args.add(task)
            fn_log(f"{task} entry loaded successfully")
    def remove_instances_components(self, *args) -> None:
        if 'ALL' in args: args = set(self._args)
        for task in args:
            if task in self._args:
                # remove component for instances
                self._call_instances('remove_components')(task)
                for key in self._instances_loadable_components[task]:
                    if 'handler' in key and hasattr(self, key):
                        delattr(self, key)
                self._args.remove(task)
                fn_log(f"{task} entry removed successfully")
            else:
                raise AttributeError(f"'{task}' components is not loaded or component {task} doesn't exists")
    def crawling_main(self, task, source=None, threads=None, **kwargs):
        fn_log(f"Start {task}, total source count : {len(source)}")
        
        # load task
        if task not in self._args: self.load_instances_components(task, threads=threads)
        
        # execute
        getattr(self, task + '_handler')(source = source, **kwargs)

def cs_factory(dic_cs: dict):
    # create class skelton
    class _Cs(*dic_cs):
        __slots__ = {slot for base in dic_cs if hasattr(base, '__slots__') for slot in getattr(base, '__slots__')}
        def __init__(self, *args, **kwargs):
        # set attributes
            for Cs, config in dic_cs.items():
                if config is None: continue
                default_args, default_kwargs = config.get('default_args', set()), config.get('default_kwargs', {})
                _args = default_args - {'args', 'kwargs'} | set(args) if 'args' in default_args else default_args - {'kwargs'}
                _kwargs = default_kwargs | kwargs if 'kwargs' in default_args else {key: kwargs.get(key, value) for key, value in default_kwargs.items()}
                Cs.__init__(self, *_args, **_kwargs)
    return _Cs


