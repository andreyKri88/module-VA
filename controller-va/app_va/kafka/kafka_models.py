from enum import Enum
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime


class KafkaMessageType(Enum):
    SAVE_STATUS = "SAVE_STATUS"
    SAVE_LOG = "SAVE_LOG"
    SAVE_EVENT = "SAVE_EVENT"


class VideoDetectionEventType(Enum):
    ROI = "ROI"
    LPR = "LPR"


@dataclass
class KafkaVideoDetectionEventMessage:
    correlation_id: Optional[str] = None
    id: Optional[int] = None
    unit_type_id: Optional[int] = None
    external_code_event: Optional[str] = None
    status: Optional[int] = None
    children_status: Optional[int] = None
    card_number: Optional[str] = None
    economic_body: Optional[str] = None
    date: Optional[str] = None
    image_to_incident: Optional[str] = None
    
    # Event specific fields
    event_type: Optional[VideoDetectionEventType] = None
    device_id: Optional[int] = None
    person_full_name: Optional[str] = None
    person_id: Optional[str] = None
    number_name: Optional[str] = None
    object_name: Optional[str] = None
    track_id: Optional[str] = None
    comment: Optional[str] = None


@dataclass
class KafkaMessage:
    type: KafkaMessageType
    sender_module_id: int
    payload: List[KafkaVideoDetectionEventMessage]
