from enum import Enum


class DeviceStatus(Enum):
    ONLINE = 1
    OFFLINE = 0
    ERROR = -1
    MAINTENANCE = 2


class EventType(Enum):
    ROI_DETECTION = "ROI_DETECTION"
    LPR_DETECTION = "LPR_DETECTION"
    DEVICE_STATUS_CHANGE = "DEVICE_STATUS_CHANGE"
    SYSTEM_LOG = "SYSTEM_LOG"
