from flask import Flask
from app_va.services import InitializeClass, Logs
from fidlet_text import FIGLET_TEXT

initializer: InitializeClass = InitializeClass()
module_name: str = initializer.module_name
vendor_name: str = initializer.vendor_name


class Constants:
    FIO_DEG = "Sentinel CONNECT (SentinelVA)"
    RELEASE = "release from: 2025-04-13"
    VERSION = "version: 1.0.0"
    UPPER_BOUNDER = ">" * len(FIO_DEG) if len(FIO_DEG) > len(RELEASE) else ">" * len(RELEASE)
    LOWER_BOUNDER = "<" * len(FIO_DEG)


log = Logs(f"{vendor_name}").logger

current_ver: str = "current version: [1.0.0]"
bounders: str = "*" * len(current_ver)

# Обновленные константы согласно требованиям
ID_VENDOR = "69"
ID_TYPE_UNIT_SRV = "110"  # server
ID_TYPE_UNIT_CAM = "111"  # device
SENDER_MODULE_ID = 107

FIO_DEG = f"{module_name} ({vendor_name})"
EVENT_TIMER: float = 10.0

from app_va.main_process import MainProcess  # noqa

app_run = Flask(__name__)
app_run.config["JSON_SORT_KEYS"] = False

print(FIGLET_TEXT)
print(
    f"{Constants.UPPER_BOUNDER}\n"
    f"{Constants.FIO_DEG}\n"
    f"{Constants.VERSION}\n"
    f"{Constants.RELEASE}\n"
    f"{Constants.LOWER_BOUNDER}"
)
log.info(Constants.UPPER_BOUNDER)
log.info(Constants.FIO_DEG)
log.info(Constants.VERSION)
log.info(Constants.RELEASE)
log.info(Constants.LOWER_BOUNDER)


main_process = MainProcess(init_instance=initializer)

from app_va.blueprints import device_observer  # noqa

app_run.register_blueprint(device_observer)
