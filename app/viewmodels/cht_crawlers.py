
from app.utils.my_driver import *
from app.utils.composer import *
from app.models.models import CsBasicComponent
from selenium.webdriver.common.by import By
import time, ast
from app.services.db_manager import DatabaseManager
from app.config import DB_PATH
from app.models.models import CsMSGReport

def _spit_cht_crawlers_loadable_components() -> dict[str, dict[str, Any]]:
    def MSG() -> dict[str, Any]:
        def MSG_handler(self, source:list[dict], handle_check_online: bool=True, **kwargs) -> None:
            _BASE_URL = 'https://msgrpt.cht.com.tw/RsView12/RsPortal.aspx'
            self.get(_BASE_URL)
            # Login to sharepoint
            if handle_check_online and self._helper_driver is None:
                self._helper_driver = self.__class__('sharepoint')
            # main fetch and uploading
            for report in source:
                report = CsMSGReport(**report)
                # check if exited online
                if handle_check_online and self._helper_driver.sharepoint_check_online(report):
                    fn_log(f"{self._index}:{report.new_name} already uploaded!")
                    continue
                # fetch
                fn_log(f"{self._index}: Start fetching {report.prefix} {report.name} {report.postfix if report.postfix else ""}")
                fn_log(f"{self._index}: Fetching {report.new_name} {self._MSG_query(report = report)}!!")
                while not os.path.exists(report.old_path):
                    time.sleep(3)
                # Rename and move
                try:
                    os.rename(report.old_path, report.new_path)
                except:
                    os.remove(report.old_path)
                    fn_log(f"{report.new_path} already exists")
                # upload
                if handle_check_online:
                    fn_log(f"{self._index}: Start uploading {report.new_path}, please wait for uploading.")
                    fn_log(f"{self._index}: Upload {report.new_path} {self._helper_driver.sharepoint_upload(report)}!!")
        def _MSG_query(self, report: CsMSGReport) -> str:
                try:
                    # choose report
                    for id, value in report.set_report.items():
                        self._select_change_value(By.ID, id, value)
                    self._select_change_value(By.ID, 'ddlReport', report.name)
                    # wait for iframe
                    self.switch_to.frame(self._wait_element(By.ID, "iframe"))
                    # set report attribute
                    for id, value in report.set_report_attribute.items():
                        match value[0]:
                            case 'fn_driver_select_change_value':
                                self._select_change_value(value[1], id, value[2])
                                pass
                            case 'fn_driver_input_send_keys':
                                self._input_send_keys(value[1], id, value[2])
                            case 'fn_driver_click':
                                self._wait_element(value[1], id).click()
                            case _:
                                print('Missing procedure definition')
                                pass
                    # fetch report
                    _int_current_windows_handles = len(self.window_handles)
                    self._wait_element(By.ID, "btnQuery").click()
                    str_report_handle:str|None = None
                    # check if direct download
                    if report.show_report:
                        while len(self.window_handles) == _int_current_windows_handles:
                            time.sleep(1)
                        str_report_handle = self.window_handles[-1]
                        self.switch_to.window(str_report_handle)
                        # wait report
                        self._wait_element(By.XPATH, f"//div[contains(text(), {report.name})]")
                        # time.sleep(3)
                        # download and wait
                        self._wait_element(By.ID, 'ReportViewer1_ctl05_ctl04_ctl00_Button', condition=EC.element_to_be_clickable).click()
                        # time.sleep(1)
                        try:
                            self._wait_element(By.XPATH, '//a[@title="Excel"]', 3, condition=EC.element_to_be_clickable).click()
                            # time.sleep(1)
                        except TimeoutException:
                            self._wait_element(By.ID, 'ReportViewer1_ctl05_ctl04_ctl00_Button', condition=EC.element_to_be_clickable).click()
                            # time.sleep(1)
                            self._wait_element(By.XPATH, '//a[@title="Excel"]', condition=EC.element_to_be_clickable).click()
                            # time.sleep(1)
                    # Wait for download
                    while not os.path.exists(report.old_path):
                        time.sleep(2)
                    time.sleep(1)
                    fn_log(f"{self._index}:{report.old_path} downloaded!!")
                    # switch to main
                    if report.show_report:
                        self.switch_to.window(str_report_handle)
                        self.close()
                        self.switch_to.window(self.int_main_window_handle)
                    # Switch back to the default content frame
                    self.switch_to.default_content()
                    return "succeeded"
                except Exception as e:
                    return f"failed with {e}"
        return vars()
        def __init__component(self) -> None:
            print('MSG component equipped!!')
    def MASIS_InvQry() -> dict[str, Any]:
        def MASIS_InvQry_handler(self, source: list[str], **kwargs) -> None:
            _BASE_URL = 'https://masis.cht.com.tw/IV_Net/IvQry/Inv/InvQry.aspx'
            _task_name = 'MASIS_InvQry'
            self.get(_BASE_URL)
            # main
            fn_log(f"{self._index}: total {len(source)} warehouses inventory to be fetched")
            for txtWhno in source:     
                lst_data = []   
                fn_log(f"{self._index}: start fetching {txtWhno} inventory")
                # Input contract ID
                lst_data = self._MASIS_InvQry_query(txtWhno = txtWhno)
                with DatabaseManager(DB_PATH) as db:
                    # DELETE operation
                    db.execute_query(f"DELETE FROM {_task_name} WHERE 庫號 = '{txtWhno}'")
                    if len(lst_data) == 0:
                        fn_log(f"{self._index}:{txtWhno} has no inventory")
                        continue
                    fn_log(f"{self._index}:{txtWhno} inventory fetched")
                    # Prepare the SQL query
                    lst_sql_columns = ['項次', '庫號', '材料編號', '名稱', '料別', '呆料', '最高庫存', '實際庫存', '可用庫存', '待收數', '待退數', '待調出數', '待撥入數', '待發數', '安全存量', '上月結存數', '上月單價', '累退數', '累調出數', '累撥入數', '累領數', '料位', '管料員']
                    db.write_db(dbname=_task_name, columns=lst_sql_columns, records=lst_data)
                fn_log(f"{self._index}:{txtWhno} inventory {len(lst_data)} records saved")
        def _MASIS_InvQry_query(self, txtWhno: str) -> list:
            self._input_send_keys(By.ID, 'ContentPlaceHolder1_txtWhno', txtWhno)
            self._wait_element(By.ID, 'ContentPlaceHolder1_btnQry').click()
            time.sleep(1) # Adjust the delay as needed
            # Wait rendering
            try:
                str_pages_info = self._wait_element(By.ID, 'ContentPlaceHolder1_lbGvCount', 2).text
                int_total_pages = int(re.findall(r'共(.*?)頁', str_pages_info)[0])
                # Extract table headers
                lst_data = self._MASIS_InvQry_extract_table_html(int_total_pages = int_total_pages)
                self.refresh()
                return lst_data
            except TimeoutException:
                return []
        def _MASIS_InvQry_extract_table_html(self, int_total_pages: int) -> list:
            lst_data = []
            # initialize paging
            for page in range(1, int_total_pages + 1):
                try:
                    # Wait for up to 1 second for the element to be present
                    self._wait_element(By.XPATH, f"//span[text()='{str(page)}']", 1)
                except TimeoutException:
                    try:
                        # If the element is not found within the timeout click it
                        self._wait_element(By.XPATH, f"//a[text()='{str(page)}']", 1).click()
                        self._wait_element(By.XPATH, f"//span[text()='{str(page)}']")
                    except TimeoutException:
                        self._wait_element(By.XPATH, f"//a[text()='...']", 1).click()
                        self._wait_element(By.XPATH, f"//span[text()='{str(page)}']")
                # get table
                table = self._wait_element(By.ID, "ContentPlaceHolder1_gv0")
                html = table.get_attribute("innerHTML")
                _result = re.sub(r'<tr(.*?)</tr>', '', html, flags=re.DOTALL, count=1)
                _result = re.sub(r'<a(.*?)>|</a>|<input(.*?)>|<tr class="pgr"(.*)</tr>|\.000', '', _result, flags=re.DOTALL)
                _result = re.sub(r'<tbody>|<tr.*?>', '[', _result)
                _result = re.sub(r'</tbody>|</tr>', ']', _result)
                _result = re.sub(r'<td(.*?)>|</td>', "'", _result, flags=re.DOTALL)
                _result = _result.replace(r"''", "','")
                _result = re.sub(r'\n|\t|\s|\r', '', _result, flags=re.DOTALL)
                _result = _result.replace(r'][', '],[')
                # Convert the string to a list
                _result = self. _MASIS_InvQry_process_data(ast.literal_eval(_result))
                lst_data += _result
            return lst_data
        def _MASIS_InvQry_process_data(self, data):
            for item in data:
                # Split the third element
                third_element = item[2]
                if '(' in third_element:
                    split_elem = third_element.split('(', 1)
                    item[2] = split_elem[0]
                    item.insert(3, '(' + split_elem[1])
                # Remove the first and last letter of the fourth element (now the element at index 3)
                if len(item[3]) > 2:  # Ensure the element is long enough
                    item[3] = item[3][1:-1]
            return data
        return vars()
    def EPIS_contract_info_items() -> dict[str, Any]:
        def EPIS_contract_info_items_handler(self, source: list[str], **kwargs):
            EPIS_contract_info_task_name, EPIS_contract_items_task_name = 'EPIS_contract_info', 'EPIS_contract_items'
            int_total = len(source)
            int_finished_count = 0
            DIC_COLUMNS_NAMES_CONTRACT_ITEMS = {
                12: [['id', '契約編號', '材料編號', '名稱', '單位', '明細來源', 'IT類別', '規格', '數量', '單價', '小計', '備註'], '一般'],
                13: [['id', '契約編號', '材料編號', '名稱', '單位', '明細來源', 'IT類別', '規格', '數量', '單價', '小計', '小計調整', '備註'], '一般'],
                15: [['id', '契約編號', '材料編號', '名稱', '單位', '明細來源', 'IT類別', '規格', '數量', '幣別', '外幣單價', '單價', '外幣小計', '小計', '備註'], '外幣'],
                20: [['id', '契約編號', '材料編號', '名稱', '單位', '明細來源', 'IT類別', '規格', '數量', '單價', '小計', '備註', '查型錄', '優惠計算說明', '查證方式', '查證金額', '查證結果', '契約類別', '來源契約編號', '共同供應契約資訊'], '共契']
            }
            for contract in source:
                int_finished_count += 1
                # fetch info
                lst_info_data = []
                try:
                    fn_log(f"{self._index}: Start fetching {contract} info.")
                    lst_info_data = [contract] + self._EPIS_contract_info_query(contract = contract)
                    fn_log(f"{self._index}: Fetching {contract} info succeed, proceed to fetch items.")
                except TimeoutException:
                    fn_log(f"{self._index}:{contract} has no info data. {int_finished_count} of {int_total} finished")
                    continue
                # fetch items
                lst_items_data = []
                lst_items_sql_columns = []
                str_type = ''
                try:
                    fn_log(f"{self._index}: Start fetching {contract} items.")
                    lst_items_data = self._EPIS_contract_items_query(contract = contract)
                    # sample out corresponding columns and type
                    lst_items_sql_columns, str_type = DIC_COLUMNS_NAMES_CONTRACT_ITEMS[len(lst_items_data[0])]
                    fn_log(f"{self._index}:{contract} items fetched. {int_finished_count} of {int_total} finished")
                except UnexpectedAlertPresentException:
                    pass
                except TimeoutException:
                    fn_log(f"{self._index}:{contract} has no items data. {int_finished_count} of {int_total} finished")
                with DatabaseManager(DB_PATH) as db:
                    # Write contract info
                    lst_info_sql_columns = ['契約編號', '契約幣別', '契約金額_外幣', '台銀賣出匯率日期', '台銀即期賣出匯率', '國際貿易條件', '約定履約日期', '決標資訊', '免收履約保證金', '履約保證金繳納方式', '履約保證金額', '履約保證有效期限', '免收保固保證金', '保固保證金繳納方式', '保固保證金額', '保固保證有效期限', '保固期限', '已全部請款完畢', '契約是否變更', '最後契約變更日期', '契約備註', '契約狀態']
                    db.write_db(dbname=EPIS_contract_info_task_name, columns=lst_info_sql_columns, records=[lst_info_data])
                    # DELETE operation
                    db.execute_query(f"DELETE FROM {EPIS_contract_items_task_name} WHERE 契約編號 = '{contract}'")
                    if lst_items_data:
                        # Write Types
                        db.execute_query(f"INSERT OR REPLACE INTO EPIS_contract_type (契約編號, 契約類別) VALUES ('{contract}', '{str_type}')")
                        # Write contract items
                        db.write_db(dbname=EPIS_contract_items_task_name, columns=lst_items_sql_columns, records=lst_items_data)
                fn_log(f"{self._index}:{contract} info saved to {EPIS_contract_info_task_name}!")
                fn_log(f"{self._index}:{contract} items saved to {EPIS_contract_items_task_name}!")
        # EPIS_contract_info
        def _EPIS_contract_info_query(self, contract: str) -> list:
            BASE_URL = 'https://epis.cht.com.tw/epis100/Pages/GContract/Contract.aspx?f=G_ContractEdit&cid='
            self.get(BASE_URL + contract)
            _wait = self._wait_element(By.XPATH, f"//span[contains(text(), '契約編號：{contract}')]")
            try:
                # extract info
                return self._EPIS_contract_info_extract_table_html()
            except TimeoutException:
                raise TimeoutException
        def _EPIS_contract_info_extract_table_html(self) -> list:
            str_契約幣別 = self._try_extract_th_next_element_value_by_text('契約幣別')
            str_契約金額_外幣 = self._try_extract_th_next_element_value_by_text('契約金額(外幣)')
            str_台銀賣出匯率日期 = convert_roc_to_western(self._try_extract_th_next_element_value_by_text('台銀賣出匯率日期'))
            str_台銀即期賣出匯率 = self._try_extract_th_next_element_value_by_text('台銀即期賣出匯率')
            str_國際貿易條件 = self._try_extract_th_next_element_value_by_text('國際貿易條件')
            str_約定履約日期 = self._try_extract_th_next_element_value_by_text('約定履約日期')
            str_決標資訊 = self._try_extract_th_next_element_value_by_text('決標資訊')
            str_免收履約保證金 = self._try_extract_th_next_element_value_by_text('履約保證金')
            str_履約保證金繳納方式 = self._try_extract_th_next_element_value_by_text('履約保證金繳納方式')
            str_履約保證金額 = self._try_extract_th_next_element_value_by_text('履約保證金額')
            str_履約保證有效期限 = convert_roc_to_western(self._try_extract_th_next_element_value_by_text('履約保證有效期限'))
            str_免收保固保證金 = self._try_extract_th_next_element_value_by_text('保固保證金')
            str_保固保證金繳納方式 = self._try_extract_th_next_element_value_by_text('保固保證金繳納方式')
            str_保固保證金額 = self._try_extract_th_next_element_value_by_text('保固保證金額')
            str_保固保證有效期限 = convert_roc_to_western(self._try_extract_th_next_element_value_by_text('保固保證有效期限'))
            str_保固期限 = convert_roc_to_western(self._try_extract_th_next_element_value_by_text('保固期限'))
            str_已全部請款完畢 = self._try_extract_th_next_element_value_by_text('已全部請款完畢')
            str_契約是否變更 = self._try_extract_th_next_element_value_by_text('契約是否變更')
            str_最後契約變更日期 = convert_roc_to_western(self._try_extract_th_next_element_value_by_text('最後契約變更日期'))
            str_契約備註 = self._try_extract_th_next_element_value_by_text('契約備註')
            str_契約狀態 = self._try_extract_th_next_element_value_by_text('契約狀態')
            return [
                str_契約幣別, str_契約金額_外幣, str_台銀賣出匯率日期, str_台銀即期賣出匯率, str_國際貿易條件,
                str_約定履約日期, str_決標資訊, str_免收履約保證金, str_履約保證金繳納方式, str_履約保證金額,
                str_履約保證有效期限, str_免收保固保證金, str_保固保證金繳納方式, str_保固保證金額, str_保固保證有效期限,
                str_保固期限, str_已全部請款完畢, str_契約是否變更, str_最後契約變更日期, str_契約備註, str_契約狀態
            ]
        # EPIS_contract_items
        def _EPIS_contract_items_query(self, contract: str) -> list:
            try:
                BASE_URL = 'https://epis.cht.com.tw/epis100/Pages/GContract/ContractItem.aspx?f=G_ContractItem&cid='
                self.get(BASE_URL + contract)
            except UnexpectedAlertPresentException:
                time.sleep(1)
                try:
                    _input = self._wait_element(By.NAME, 'ctl00$ContentPlaceHolder1$ButtonList_Notice$ctl00', 1)
                    _input.click()
                except:
                    pass
                pass
            try:
                # Wait rendering
                str_pages_info = self._wait_element(By.CLASS_NAME, 'prev', 1).text
                int_total_pages = int(re.findall(r'/(.*?)頁', str_pages_info)[0])
                # Extract table headers
                lst_data = self._EPIS_contract_items_extract_table_html(int_total_pages = int_total_pages)
                # to save to excel eliminate below line
                lst_data = [[contract + "_" + sublist[0], contract] + sublist for sublist in lst_data]
                return lst_data
            except TimeoutException:
                raise TimeoutException
        def _EPIS_contract_items_extract_table_html(self, int_total_pages: int) -> list:
            lst_data = []
            check_currency = self._try_currency()
            # initialize paging
            try:
                for page in range(1, int_total_pages + 1):
                    # jump to page 1
                    if page == 1:
                        pass
                    else:
                        self.execute_script(f"__doPostBack('ctl00$ContentPlaceHolder1$SortGridView_Items','Page${str(page)}')")
                    # get table
                    table = self._wait_element(By.ID, "ctl00_ContentPlaceHolder1_SortGridView_Items")
                    html = table.get_attribute("innerHTML")
                    _result = re.sub(r'<tr(.*?)</tr>', '', html, flags=re.DOTALL, count=1)
                    _result = re.sub(r'<td class="func">(.*?)disabled="disabled">(.*?)<\/td>|<span class="prefix">(.*?)</span>| title=""|">有', '', _result, flags=re.DOTALL)
                    _result = re.sub(r' class="detail" data-detail="', '>', _result)
                    _result = re.sub(r'<tbody>|<tr.*?>', '[', _result)
                    _result = re.sub(r'</tbody>|</tr>', ']', _result)
                    _result = re.sub("\'", "\\'", _result, flags=re.DOTALL)
                    _result = re.sub(r'<td class="link">.*?href="|"\starget=.*?</td>', "'", _result, flags=re.DOTALL)
                    _result = re.sub(r'<td.*?<span>|</span></td>', "'", _result, flags=re.DOTALL)
                    _result = _result.replace(r'../..', 'https://epis.cht.com.tw/epis100')
                    _result = _result.replace(r"''", "','")
                    _result = re.sub(r'\n|\t|&nbsp;|<br>|amp;|\r', '', _result)
                    _result = _result.replace(r'][', '],[')
                    if isinstance(check_currency, str) and bool(check_currency):
                        currency_pattern = f"'({check_currency})([\\d,.]+)','([\\d,.]+)','{check_currency} ([\\d,.]+)\\(([\\d,.]+)元\\)'"
                        _result = re.sub(currency_pattern, 
                            lambda match: f"'{match.group(1)}','{match.group(2)}','{match.group(3)}','{match.group(4)}','{match.group(5)}'",
                                        _result)
                    # Convert the string to a list
                    _result = ast.literal_eval(_result)
                    lst_data += _result
                return lst_data
            except TimeoutException:
                raise TimeoutException
        return vars()
    def MASIS_barcode() -> dict[str, Any]:
        def MASIS_barcode_handler(self, source: dict[str, list[Any]], **kwargs) -> None:
            _task_name = 'MASIS_barcode'
            STR_MASIS_BARCODE_URL = 'https://masis.cht.com.tw/IV_Net/IvQry/Inv/BarcodeQry.aspx'
            self.get(STR_MASIS_BARCODE_URL)
            int_total_lots = sum(len(value) for value in source.values())
            int_finished_count = 0
            # main
            for key in source.keys():        
                # Input contract ID
                self._input_send_keys(By.ID, 'ContentPlaceHolder1_txtCtId', key)
                for Lot in source.get(key, []):
                    lst_data = []
                    # zfill every lot
                    zfill_lot = Lot.zfill(3) if type(Lot) == str else str(Lot).zfill(3)
                    int_finished_count += 1
                    # Check if file already existed
                    # if os.path.isfile(f"{STR_DOWNLOADS_TIMESTAMP_FOLDER_PATH}\\{key}_{zfill_lot}.xlsx"):
                    #     fn_log(f"{STR_DOWNLOADS_TIMESTAMP_FOLDER_PATH}\\{key}_{zfill_lot} already existed!!")
                    #     continue
                    try:
                        fn_log(f"{self._index}: Fetching {key} {zfill_lot} data")
                        lst_data: list[list[str]] = [[key , zfill_lot] + lst for lst in self._MASIS_barcode_query_lot(zfill_lot)]
                        fn_log(f"{self._index}:{key} {zfill_lot} barcode fetched")
                        with DatabaseManager(DB_PATH) as db:
                            # Prepare the SQL query
                            lst_sql_columns = ['契約編號', '批次', '材料編號', '棧板序號', '箱號', 'EAN號碼', '序號', '廠商自編序號', 'MAC位址', '所在庫號', '狀態', '最近領料庫號', '最近領料單號']
                            db.write_db(dbname=_task_name, columns=lst_sql_columns, records=lst_data)
                        fn_log(f"{self._index}:{key} {zfill_lot} {len(lst_data)} barcode saved to db {_task_name}, {int_finished_count} of {int_total_lots} finished")
                    except UnexpectedAlertPresentException:
                        fn_log(f"{self._index}:{key} {zfill_lot} has no barcode. {int_finished_count} of {int_total_lots} finished")
                        continue
        def _MASIS_barcode_query_lot(self, zfill_lot: str) -> list[list[str]]:
            # Input Lot No.
            self._input_send_keys(By.ID, 'ContentPlaceHolder1_txtLotNo', zfill_lot)
            # Query
            try:
                self._wait_element(By.ID,'ContentPlaceHolder1_btnQry').click()
                time.sleep(1) # Adjust the delay as needed
                _check_alert = self.current_url
            except UnexpectedAlertPresentException:
                raise UnexpectedAlertPresentException
            # Wait rendering
            str_pages_info = self._wait_element(By.ID, 'ContentPlaceHolder1_lbGvCount').text
            int_total_pages = int(re.findall(r'共(.*?)頁', str_pages_info)[0])
            # Extract table data
            lst_data = self._MASIS_barcode_extract_table_html(int_total_pages)
            return lst_data
        def _MASIS_barcode_extract_table_html(self, int_total_pages: int) -> list[list[str]]:
            lst_data = []
            # initialize paging
            for page in range(1, int_total_pages + 1):
                if int_total_pages == 1:
                    pass
                elif page == 1:
                    try:
                        # Wait for up to 1 second for the element to be present
                        self._wait_element(By.XPATH, "//span[text()='1']", 1)
                    except TimeoutException:
                        # If the element is not found within the timeout, jump to page 1
                        self.execute_script(f"__doPostBack('ctl00$ContentPlaceHolder1$gv','Page$1')")
                else:
                    self.execute_script(f"__doPostBack('ctl00$ContentPlaceHolder1$gv','Page${str(page)}')")
                # get table
                table = self._wait_element(By.ID, "ContentPlaceHolder1_gv")
                html = table.get_attribute("innerHTML")
                pattern = re.compile(r'<tr class="pgr">(?:.*?<tr>.*?</tr>)*.*?</tr>', re.DOTALL)
                _result = re.sub(pattern, '', html)
                _result = re.sub(r'<tr>.*?</tr>', '', _result, count=1, flags=re.DOTALL)
                _result = re.sub(r'<tbody>|<tr>', '[', _result)
                _result = re.sub(r'</tbody>|</tr>', ']', _result)
                _result = re.sub('<[^>]+>', '"', _result)
                _result = _result.replace(r'""', '","') 
                _result = _result.replace(r'][', '],[') 
                _result = re.sub(r'\n|\t|&nbsp;', '', _result)
                # Convert the string to a list
                _result = ast.literal_eval(_result)
                lst_data += _result
            return lst_data
        return vars()
        def useless():
            # Save the DataFrame to a excel file
            # df = pd.DataFrame(lst_data)
            # df.columns = ['契約編號', '批次', '材料編號', '棧板序號', '箱號', 'EAN號碼', '序號', '廠商自編序號', 'MAC位址', '所在庫號', '狀態', '最近領料庫號', '最近領料單號']
            # df.to_excel(f'{STR_DOWNLOADS_TIMESTAMP_FOLDER_PATH}\\{key}_{zfill_lot}.xlsx', index=False)
            # fn_log(f"{key}_{zfill_lot}.xlsx saved!! {int_finished_count} of {int_total_lots} finished")
            pass
    def MASIS_item_detail() -> dict[str, Any]:
        def MASIS_item_detail_handler(self, source: list[str], **kwargs):
            _task_name = 'MASIS_item_detail'
            _BASE_URL = 'https://masis.cht.com.tw/masis/NM/Mano/ManoMtn.aspx?t=m'
            self.get(_BASE_URL)
            int_total_lots = len(source)
            int_finished_count = 0
            # main
            lst_result_items_detail = []
            for item in source:        
                int_finished_count += 1
                try:
                    fn_log(f"{self._index}: Fetching {item} details")
                    lst_item_detail = self.MASIS_item_detail_query_item(item)
                    lst_result_items_detail.append([item] +  lst_item_detail)
                    fn_log(f"{self._index}: Fetching {item} succeeded, {int_finished_count} of {int_total_lots} finished!!")
                except UnexpectedAlertPresentException:
                    fn_log(f"{self._index}:{item} doesn't exist. {int_finished_count} of {int_total_lots} queried.")
                    continue
            if len(lst_result_items_detail) == 0:
                fn_log(f"{self._index}: items has no data")
                return
            fn_log(f"{self._index}:{len(lst_result_items_detail)} items data fetched")
            with DatabaseManager(DB_PATH) as db:
                lst_sql_columns = ['材料編號', '材料名稱', '材料分類1', '材料分類2', '材料分類3', '計量單位', '追蹤週期', '導入條碼', 'EAN', '管理人員', '建檔日期', '異動日期', 'CPE', '掃碼', '歸屬機構']
                db.write_db(dbname=_task_name, columns=lst_sql_columns , records=lst_result_items_detail)
                fn_log(f"{self._index}:{len(lst_result_items_detail)} items data saved to db {_task_name}")
        def MASIS_item_detail_query_item(self, item)->list:
            # Input item NO
            self._input_send_keys(By.NAME, 'ctl00$ContentPlaceHolder1$txtMano', item)
            # Query
            self._wait_element(By.NAME,'ctl00$ContentPlaceHolder1$btnQry').click()
            # Wait rendering
            str_材料名稱 = self._wait_element(By.ID, 'ContentPlaceHolder1_txtMaName').get_attribute("value")
            str_材料分類1 = self._wait_element(By.ID, 'ContentPlaceHolder1_DDL1').get_attribute("value")
            str_材料分類2 = self._wait_element(By.ID, 'ContentPlaceHolder1_DDL2').get_attribute("value")
            str_材料分類3 = self._wait_element(By.ID, 'ContentPlaceHolder1_DDL3').get_attribute("value")
            str_計量單位 = self._wait_element(By.NAME, 'ctl00$ContentPlaceHolder1$MaUnitCtrl$ctl00').get_attribute("value")
            str_追蹤週期 = self._wait_element(By.ID, 'ContentPlaceHolder1_ddlTrace').get_attribute("value")
            str_導入條碼 = self._wait_element(By.ID, 'ContentPlaceHolder1_ddlImportReasons').get_attribute("value")
            str_EAN = self._wait_element(By.ID, 'ContentPlaceHolder1_lbEAN').text
            str_EAN.replace(";","")
            str_管理人員 = self._wait_element(By.ID, 'ContentPlaceHolder1_lbController').text
            str_建檔日期 = self._wait_element(By.ID, 'ContentPlaceHolder1_lbCrDt').text
            str_異動日期 = self._wait_element(By.ID, 'ContentPlaceHolder1_lbUpDt').text
            bool_CPE = True if self._wait_element(By.ID, 'ContentPlaceHolder1_RbCpeY').get_attribute('checked') else False
            bool_掃碼 = True if self._wait_element(By.ID, 'ContentPlaceHolder1_rbBarcodeY').get_attribute('checked') else False
            str_歸屬機構 = self._try_wait_extract_element_value(By.NAME, 'ctl00$ContentPlaceHolder1$OrgCtrl$ctl00')
            self.back()
            return [str_材料名稱, str_材料分類1, str_材料分類2, str_材料分類3, str_計量單位, str_追蹤週期, str_導入條碼, str_EAN, str_管理人員, str_建檔日期, str_異動日期, bool_CPE, bool_掃碼, str_歸屬機構]
        return vars()
        def useless(self):
            # Save the DataFrame to a excel file
            # df = pd.DataFrame(lst_result_items_detail)
            # df.columns = ['材料編號', '材料名稱', '材料分類1', '材料分類2', '材料分類3','計量單位', '追蹤週期', '導入條碼', 'EAN', '管理人員', '建檔日期', '異動日期']
            # df.to_excel(f'{STR_DOWNLOADS_TIMESTAMP_FOLDER_PATH}\\item_detail/{STR_DATESTAMP}_items.xlsx', index=False)
            pass
    def EPIS_contract_batch() -> dict[str, Any]:
        def EPIS_contract_batch_handler(self, source: list[str], **kwargs) -> None:
            int_total = len(source)
            int_finished_count = 0
            for contract in source:
                dict_contract_batches = None
                int_finished_count += 1
                try:
                    fn_log(f"{self._index}: Start fetching {contract} batch.")
                    dict_contract_batches = self._EPIS_contract_batch_query_contract(contract)
                except TimeoutException:
                    fn_log(f"{self._index}:{contract} has no data. {int_finished_count} of {int_total} finished")
                    continue
                if len(dict_contract_batches['data']['info']) == 0:
                    fn_log(f"{self._index}:{contract} has no data. {int_finished_count} of {int_total} finished")
                    continue
                if  dict_contract_batches['postfix'] == '外幣' and len(dict_contract_batches['data']['info'][0]) != 14:
                    dict_contract_batches['postfix'] = '類型有誤'
                # Save Contract Batch
                self._EPIS_contract_batch_save_db(dict_contract_batches)
                fn_log(f"{self._index}:{contract} batches data saved!! {int_finished_count} of {int_total} finished")
            fn_log(f"{self._index}: contract batches finished!")
            return
        def _EPIS_contract_batch_query_contract(self, contract: str):
            BASE_URL = 'https://epis.cht.com.tw/epis100/Pages/GContract/_Menu.aspx?f=G_ContractMenu&cid='
            self.get(BASE_URL + contract)
            try:
                _wait = self._wait_element(By.ID, 'ctl00_ContentPlaceHolder1_TablePContractInfos_FormView_Content',5)
                # get batches
                _li_elements = self._wait_element(By.TAG_NAME, "ul").find_elements(By.TAG_NAME, "li")
                _lst_batches = [li.get_attribute('title') for li in _li_elements]
                lst_batches = [batch.split()[1] for batch in _lst_batches]
                # Extract batch details
                dic_batches_data = {
                    'contract': contract,
                    'temp_batch': "",
                    'data': {
                        'info': [],
                        '點收單': [],
                        '收料單': [],
                        '請款單': []
                    },
                    'check_currency': self._try_currency(),
                    'postfix': '外幣' if self._try_currency() else '一般',
                }
                int_total_batches, int_fetched_batch = len(lst_batches), 0
                for batch in lst_batches:
                    dic_batches_data['temp_batch'] = batch
                    self._EPIS_contract_batch_query_batch(dic_batches_data)
                    int_fetched_batch += 1
                    fn_log(f"{self._index}:{contract}({batch}) {int_fetched_batch} / {int_total_batches} batch(es) fetched")
                return dic_batches_data
            except TimeoutException:
                raise TimeoutException
        def _EPIS_contract_batch_query_batch(self, dic_batches_data: dict) -> None:
            _table, S_mark, _物品點收單_html, _收料單_html, _請款單_html, _batch_info_html = None, None, None, None, None, None
            contract, batch = dic_batches_data['contract'], dic_batches_data['temp_batch']
            BATCH_BASE_URL = f"https://epis.cht.com.tw/epis100/Pages/GContract/_Menu.aspx?f=G_PerformMenu&cid={contract}&pid={batch}"
            self.get(BATCH_BASE_URL)
            data = dic_batches_data['data']
            _wait = self._wait_element(By.XPATH, f"//span[contains(text(), '履約批次：{batch}')]")
            try:
                _table = self.find_element(By.ID, 'ctl00_ContentPlaceHolder1_TablePContractBatchInfos_FormView_Content')
                S_mark = ''
            except NoSuchElementException:
                _table = self.find_element(By.ID, 'ctl00_ContentPlaceHolder1_TablePContractBatchInfos_S_FormView_Content')
                S_mark = 'S_'
            _do = self._EPIS_contract_batch_query_batch_lists(dic_batches_data, S_mark)
            # batch info
            _batch_info_html = _table.get_attribute("innerHTML")
            lst_batch_info = self._EPIS_contract_batch_extract_batch_info(_batch_info_html, dic_batches_data['check_currency'])
            data['info'] += [[contract + "_" + batch] + [contract] + [batch] + lst_batch_info]
        def _EPIS_contract_batch_query_batch_lists(self, dic_batches_data, S_mark) -> None:
            _物品點收單_html, _收料單_html, _請款單_html = None, None, None
            contract, batch, data = dic_batches_data['contract'], dic_batches_data['temp_batch'], dic_batches_data['data']
            # 物品點收單
            _物品點收單_html = self.find_element(By.ID, f'ctl00_ContentPlaceHolder1_TableBatchInfos_{S_mark}SortGridView_ItemCheck').get_attribute('innerHTML')
            str_物品點收單 = ','.join(re.findall(r'<span>(\w{8})</span>',_物品點收單_html))
            if str_物品點收單:
                data['點收單'] += self._EPIS_contract_batch_extract_lists(_物品點收單_html, contract, batch)
            # MASIS收料單 不一定有element所以要if not S_mark
            if not S_mark:
                _收料單_html = self.find_element(By.ID, r'ctl00_ContentPlaceHolder1_TableBatchInfos_SortGridView_MasisReceive').get_attribute('innerHTML')
                str_收料單 = ','.join(re.findall(r'<span>(\w{7})</span>',_收料單_html))
            else:
                str_收料單 = ''
            if str_收料單:
                _lst = self._EPIS_contract_batch_extract_lists(_收料單_html, contract, batch)
                data['收料單'] += [[
                    convert_roc_to_western(item) if i == 5 and item else item
                    for i, item in enumerate(j)] for j in _lst
                ]
            # 請款單
            _請款單_html = self.find_element(By.ID, f'ctl00_ContentPlaceHolder1_TableBatchInfos_{S_mark}SortGridView_ApplyPay').get_attribute('innerHTML')
            str_請款單 = ','.join(re.findall(r'<span>(\w{8})</span>',_請款單_html))
            if str_請款單:
                data['請款單'] += self._EPIS_contract_batch_extract_lists(_請款單_html, contract, batch)
        def _EPIS_contract_batch_extract_batch_info(_self, html: str, check_currency) -> list:
            # basic info
            _html = re.sub(r'[\n,元]', '', html)
            if isinstance(check_currency, str) and bool(check_currency):
                pattern1 = rf'AutoLabel_BatchDatesInfo">(.*?)／(.*?)</span>.*?AutoLabel_TotalAmount">{check_currency}(.*)<br>進口匯率：(.*?)\((.*?)\).*?AutoLabel_ItemTotalAmount">{check_currency}*?(.*?)</span>'
                pattern2 = rf'.*?器材款FCA：{check_currency}(.*?)<br>.*?未稅金額\)：(.*?)<br>.*?未稅金額\)：(.*?)<br>.*?換算比例：(.*?)<br>'
                group1 = re.search(pattern1, _html).groups()
                group2 = ('', '', '', '') if re.search(pattern2, _html) is None else re.search(pattern2, _html).groups()
                _result = group1 + group2 + (re.sub(r'\\', '',check_currency),)
            else: 
                pattern = r'AutoLabel_BatchDatesInfo">(.*?)／(.*?)</span>.*?AutoLabel_TotalAmount">(.*?)</span>.*?AutoLabel_ItemTotalAmount">(.*?)</span>'
                _result = re.search(pattern, _html).groups()
            converted_result = tuple(
                convert_roc_to_western(item) if isinstance(item, str) and item.count('/') == 2 else item
                for item in _result
            )
            return list(converted_result)
        def _EPIS_contract_batch_extract_lists(_self, html: str, contract: str, batch: str) -> list[list[str]]:
            a = re.sub(r'[\n\t]|<thead>.*?</thead>|<tfoot>.*?</tfoot>|<div.*?>|</div>|元', '', html, flags=re.DOTALL)
            b = re.sub(r'<tbody>|<tr.*?>','[',a)
            c = re.sub(r'</tbody>|</tr>',']',b)
            d = re.sub(r'<td><span.*?>|</span></td>|<td.*?<a\s|"\sid.*?</td>','"',c)
            e = re.sub(r'<span.*?>|</span>', '', d)
            f = re.sub(r'href=.*?aspx&amp;','https://epis.cht.com.tw/apy/apayc.aspx?',e)
            g = re.sub(r'""','","',f)
            h = re.sub(r'\]\[','],[',g)
            i = ast.literal_eval(h)
            lst_inserted_batch = [[contract] + [batch] + sublist for sublist in i]
            return lst_inserted_batch
        _dic_EPIS_contract_batch_db_names = {
            '一般': ['EPIS_contract_batch', ['id', '契約編號', '批次', '約定履約日期', '履約日期', '"履約金額(含稅)"', '履約明細金額總計']],
            '外幣': ['EPIS_contract_batch', ['id', '契約編號', '批次', '約定履約日期', '履約日期', '"履約金額(含稅)"', '進口匯率', '匯率日期', '履約明細金額總計', '器材款FCA', '交貨總金額', '成本分析表總價', '換算比例', '幣別']],
            '類型有誤': None,
            '點收單': ['EPIS_contract_batch_Pick', ['契約編號', '批次', '點收單號', '代建物品增加單', '收貨單位', '點收員工']],
            '收料單': ['EPIS_contract_batch_RS2901RA4L', ['契約編號', '批次', '庫號', '庫名', '收料單號', '到料日期']],
            '請款單': ['EPIS_contract_batch_RSapay', ['契約編號', '批次', '往請款作業', '請款單號', '類別', '狀態']]
        }
        def  _EPIS_contract_batch_save_db(self, dict_contract_batches: dict) -> None:
            data, postfix, contract = dict_contract_batches['data'], dict_contract_batches['postfix'], dict_contract_batches['contract']
            for key, value in data.items():
                if value:
                    [tablename, lst_sql_columns] = self._dic_EPIS_contract_batch_db_names[postfix] if key == 'info' else self._dic_EPIS_contract_batch_db_names[key]
                    with DatabaseManager(DB_PATH) as db:
                        # Prepare the SQL query
                        insert_replace_sql = f'''
                        INSERT OR REPLACE INTO {tablename} (
                            {','.join(lst_sql_columns)}
                        ) VALUES ({",".join(["?"] * len(lst_sql_columns))})
                        '''
                        # DELETE operation
                        db.execute_query(f"DELETE FROM {tablename} WHERE 契約編號 = '{contract}'")
                        # Iterate over the list and execute the query for each record
                        db.execute_many(insert_replace_sql , value)
                        fn_log(f"{self._index}: {contract} {key} saved to db {tablename}")
        return vars()
    def sharepoint() -> dict[str, Any]:
        _sharepoint_base_url = 'https://cht365.sharepoint.com/sites/msteams_e919c5/Shared Documents/General/存控/0_DB/'
        def sharepoint_check_online(self, source: CsMSGReport, **kwargs) ->bool:
            self.get(f"{self._sharepoint_base_url}{source.name}/")
            try:
                self._wait_element(By.XPATH, f"//button[contains(text(), '{source.new_name}')]",2)
                return True
            except:
                return False
        def sharepoint_upload(self, source: CsMSGReport, index: int = 0) -> str:
            try:
                # Clicking buttons
                self.find_element(By.CSS_SELECTOR, "button[name='上傳']").click()
                self.find_element(By.CSS_SELECTOR, "button[name='檔案']").click()
                # Waiting for 5 seconds
                time.sleep(5)
                # Sending file path to input
                file_input = self.find_element(By.CSS_SELECTOR, "input[data-automationid='commandFileInput']")
                file_input.send_keys(source.new_path)
                # Waiting for upload to complete
                self._wait_element(By.XPATH, f"//button[contains(text(), '{source.new_name}')]")
                return "succeeded"
            except Exception as e:
                return f"failed with {e}"
        def __init__component(self) -> None:
            self.get(self._sharepoint_base_url)
            self._wait_element(By.XPATH, '//span[text()="供三採購駐點"]')
        return vars()
    def google() -> dict[str, Any]:
        def google_handler(self):
            self.get('https://google.com')
        def __init__component(self, *args, **kwargs):
            self.get('https://google.com')
        return vars()
    def _loader_init_remove() -> dict[str, Any]:
        def __init__loader(self, task) -> None:
            if task not in ['sharepoint', 'google']: self.login_cht()
        def __remove__loader(self, task) -> None:
            if self._helper_driver:
                self._helper_driver.close()
        return vars()
    return {key: func() for key, func in vars().items()}

class CsChtCrawlerComponent:
    def login_cht(self) -> object:
        if not self._login_cht:
            fn_log('Please login to CHT')
            OTP_LOGIN_URL = 'https://am.cht.com.tw/NIASLogin/faces/CHTOTP?origin_url=https%3A%2F%2Feip.cht.com.tw%2Findex.jsp'
            self.get(OTP_LOGIN_URL)
            self._wait_element(By.ID, 'orientation')
            self.switch_to.window(self.window_handles[-1])
            self.close()
            self.switch_to.window(self.window_handles[0])
            self._login_cht = True
        return self
    def _try_currency(self):
        try:
            _str: str = self.find_element(By.XPATH, "//span[contains(text(), 'US$') or contains(text(), '€')]").text
            _pattern = r'US\$|€'
            match: str = re.search(_pattern, _str).group()
            if match == '€':
                return match
            return 'US\\$'
        except Exception:
            return False
    def _try_extract_th_next_element_value_by_text(self, str_text:str, error_return = "") -> str:
        try:
            element = self.find_element(By.XPATH,  f"//th[contains(text(), '{str_text}')]")
            try:
                target_element = element.find_element(By.XPATH, 'following-sibling::*[1]/*[1]/*[1]')
                if target_element.tag_name == 'input': return self._try_extract_element_value(target_element)
                else: raise NoSuchElementException
            except NoSuchElementException: 
                target_element = element.find_element(By.XPATH, 'following-sibling::*[1]/*[1]')
                return self._try_extract_element_value(target_element)
        except NoSuchElementException:
            return error_return
    def __init__(self):
        self._helper_driver = None
        self._login_cht = False
# class factory



dic_cs_cht_crawler_config = {
    CsBasicComponent: None,
    webdriver.Edge: None,
    CsMyDriverComponent: None,
    CsMyEdgeDriverInit: {
        'default_args': ["./profiles/userA"]
    },
    CsChtCrawlerComponent: {},
    CsLoaderComponent: {
        'all_args': True,
        'default_kwargs': {'loadable_components': _spit_cht_crawlers_loadable_components()}
    },
    CsMultiSeed: {
        'default_kwargs':{'index': 0}        
    },
}

dic_cs_cht_multi_crawler_config = {
    CsMultiManager: {
        'all_args': True,
        'all_kwargs': True,
        'default_kwargs': {
            'threads': 1,
            'subclass': cs_factory(dic_cs_cht_crawler_config),
        }
    },
    CsMultiLoaderEntry: {}
}

CsMultiCHTCrawler = cs_factory(dic_cs_cht_multi_crawler_config)

CsCHTCrawler = cs_factory(dic_cs_cht_crawler_config)