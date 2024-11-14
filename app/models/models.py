from dataclasses import dataclass, field
from typing import Dict, Optional, List
from app.utils.timestamp import *
from selenium.webdriver.common.by import By
from app.utils.common import STR_DOWNLOADS_FOLDER_PATH, STR_DOWNLOADS_TIMESTAMP_FOLDER_PATH

class CsBasicComponent:
    def __getattr__(self, name):
        raise AttributeError(f"'{self.__class__.__name__}' '{name}' was not set")


class MyDataclass:
    def __init__(self, **kwargs) -> None:
        for key, value in kwargs.items():
            if key in self.__slots__:
                setattr(self, key, value)
            else:
                raise AttributeError(f"'{key}' is not a valid attribute for {self.__class__.__name__}")
    def __getattr__(self, name):
        if name in self.__slots__:
            raise AttributeError(f"'{name}' was not set during initialization")
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")


@dataclass()
class CsMSGReport:
    name: str
    prefix: Optional[str] = None
    postfix: Optional[str] = None
    set_report: Dict[str, str] = field(default_factory=dict)
    set_report_attribute: Dict[str, List[str]] = field(default_factory=dict)
    handle_check_online: bool = True
    show_report: bool = True
    filename: str = ""
    filename_extension: str = "xlsx"
    old_path: str = ""
    new_name: str = ""
    new_path: str = ""

    def __post_init__(self):
        self.filename = self.name
        match self.name:
            case 'RS4183MA4L':
                self.prefix = self.prefix if self.prefix else STR_THIS_MONTH_PREFIX
                self.set_report = self.set_report if self.set_report else {
                            'ddlSys':'MASIS',
                            'ddlCSys':'MASISIV',
                        }
                self.set_report_attribute = self.set_report_attribute if self.set_report_attribute else {
                        'ddlOrg':['fn_driver_select_change_value', By.ID, '5']
                    }
            case "RS0101RA4L_NE":
                self.prefix = self.prefix if self.prefix else STR_DATESTAMP
                self.set_report = self.set_report if self.set_report else {
                            'ddlSys':'MASIS',
                            'ddlCSys':'MASISMSH',
                        }
                self.set_report_attribute = self.set_report_attribute if self.set_report_attribute else {
                        "ddlOrg":['fn_driver_select_change_value', By.ID, 'M33'],
                        "txtSDate":['fn_driver_input_send_keys', By.ID, STR_START_DATE]
                    }
            case 'RS4212RA4L':
                self.prefix = self.prefix if self.prefix else STR_DATESTAMP
                self.set_report = self.set_report if self.set_report else {
                            'ddlSys':'MASIS',
                            'ddlCSys':'MASISIV',
                        }
                if not self.postfix is None: self.set_report_attribute = self.set_report_attribute if self.set_report_attribute else {
                        'txtWhNo':['fn_driver_input_send_keys', By.ID, self.postfix]
                    }
            case 'RS4153RA4L':
                self.prefix = self.prefix if self.prefix else STR_DATESTAMP
                self.postfix = self.postfix if self.postfix else "all"
                self.set_report = self.set_report if self.set_report else {
                            'ddlSys':'MASIS',
                            'ddlCSys':'MASISIV',
                        }
                self.set_report_attribute = self.set_report_attribute if self.set_report_attribute else {
                        'ddlWhNo1':['fn_driver_select_change_value', By.ID, '50502'],
                        'ddlWhNo2':['fn_driver_select_change_value', By.ID, '50503'],
                        'ddlWhNo3':['fn_driver_select_change_value', By.ID, '59521'],
                        'ddlWhNo4':['fn_driver_select_change_value', By.ID, '59531'],
                    }
            case 'RS4182M':
                self.prefix = self.prefix if self.prefix else STR_THIS_MONTH_PREFIX
                self.set_report = self.set_report if self.set_report else {
                            'ddlSys':'MASIS',
                            'ddlCSys':'MASISIV',
                        }
            case 'RS0472MA4L':
                self.prefix = self.prefix if self.prefix else STR_THIS_MONTH_PREFIX
                self.set_report = self.set_report if self.set_report else {
                            'ddlSys':'MASIS',
                            'ddlCSys':'MASISMSH',
                        }
                self.set_report_attribute = self.set_report_attribute if self.set_report_attribute else {
                        "ddlSOrg":['fn_driver_select_change_value', By.ID, '5']
                    }
            case 'RS1563MA4L':
                self.prefix = self.prefix if self.prefix else STR_THIS_MONTH_PREFIX
                self.set_report = self.set_report if self.set_report else {
                            'ddlSys':'MASIS',
                            'ddlCSys':'MASISIC',
                        }
                self.set_report_attribute = self.set_report_attribute if self.set_report_attribute else {
                        'ddlShowDetail':['fn_driver_select_change_value', By.ID, '']
                    }
            case 'RSahdinqRA4L':
                self.prefix = self.prefix if self.prefix else STR_THIS_MONTH_PREFIX
                self.set_report = self.set_report if self.set_report else {
                            'ddlSys':'MASIS',
                            'ddlCSys':'MASISLP',
                        }
                self.set_report_attribute = self.set_report_attribute if self.set_report_attribute else {
                        'txtCtId':['fn_driver_input_send_keys', By.ID, self.prefix]
                    }
            case 'RS5203A':
                self.prefix = self.prefix if self.prefix else STR_DATESTAMP
                self.postfix = self.postfix if self.postfix else "all"
                self.set_report = self.set_report if self.set_report else {
                            'ddlSys':'MASIS',
                            'ddlCSys':'MASISASIS',
                        }
                self.set_report_attribute = self.set_report_attribute if self.set_report_attribute else {
                        'txtMaxPrice':['fn_driver_input_send_keys', By.ID, '9999999'],
                        'txtEDate':['fn_driver_input_send_keys', By.ID, datetime.datetime.strptime(self.prefix, '%Y%m%d').strftime('%Y/%m/%d')],
                        'ddlSOrg':['fn_driver_select_change_value', By.ID, ''],
                        'chkSelect':['fn_driver_click', By.ID],
                    }
                self.filename += STR_DATESTAMP
                self.filename_extension = 'xls'
                self.show_report = False
            case 'RS4107RA4L':
                self.prefix = self.prefix if self.prefix else STR_FIRST_DAY_OF_THIS_YEAR + "_" + STR_DATESTAMP
                self.postfix = self.postfix if self.postfix else "行通"
                self.set_report = self.set_report if self.set_report else {
                            'ddlSys':'MASIS',
                            'ddlCSys':'MASISIV',
                        }
                self.set_report_attribute = self.set_report_attribute if self.set_report_attribute else {
                        'ddlOrg':['fn_driver_select_change_value', By.ID, 'M33'],
                        'txtSDate':['fn_driver_input_send_keys', By.ID, datetime.date(DAT_TODAY.year, 1, 1).strftime("%Y/%m/%d")],
                    }
            case "_":
                self.prefix = self.prefix if self.prefix else STR_DATESTAMP
        self.old_path = f"{STR_DOWNLOADS_FOLDER_PATH}\\{self.filename}.{self.filename_extension}"
        self.new_name = f"{self.prefix}_{self.filename}_{self.postfix}.{self.filename_extension}" if bool(self.postfix) else f"{self.prefix}_{self.filename}.{self.filename_extension}"
        self.new_path = f"{STR_DOWNLOADS_TIMESTAMP_FOLDER_PATH}\\{self.new_name}"


