from typing import Dict, Any, Optional
from app_va.models.enums import DeviceStatus
from app_va import log


class CameraVA:
    def __init__(self, server_id: str, events_list: list, events_locker):
        self.server_id = server_id
        self.events_list = events_list
        self.events_locker = events_locker

        # Camera properties
        self.id_device: Optional[str] = None
        self.ext_id: Optional[str] = None
        self.name: Optional[str] = None
        self.camera_uuid: Optional[str] = None
        self.ip_address: Optional[str] = None
        self.port: Optional[int] = None
        self.status: DeviceStatus = DeviceStatus.OFFLINE
        self.is_initialized: bool = False

        # Additional properties
        self.description: Optional[str] = None
        self.location: Optional[str] = None

    def get_camera(self, raw_dict: Dict[str, Any]) -> bool:
        """Initialize camera from database record"""
        try:
            self.id_device = str(raw_dict.get("id_device"))
            self.ext_id = raw_dict.get("ext_id")
            self.name = raw_dict.get("name")
            self.camera_uuid = raw_dict.get(
                "camera_uuid"
            )  # UUID for WebSocket event mapping
            self.ip_address = raw_dict.get("ip_address")
            self.port = raw_dict.get("port")
            self.description = raw_dict.get("description")
            self.location = raw_dict.get("location")

            # Convert status to DeviceStatus enum
            status_value = raw_dict.get("status", 0)
            if status_value == 1:
                self.status = DeviceStatus.ONLINE
            else:
                self.status = DeviceStatus.OFFLINE

            self.is_initialized = True
            log.debug(f"Camera {self.id_device} ({self.name}) initialized successfully")
            return True

        except Exception as e:
            log.error(f"Failed to initialize camera: {e}")
            self.is_initialized = False
            return False

    def update_status(self, status: DeviceStatus) -> bool:
        """Update camera status and send to Kafka"""
        try:
            old_status = self.status
            self.status = status

            # Send status update to Kafka
            from app_va import main_process

            if hasattr(main_process, "message_producer"):
                success = main_process.message_producer.send_status_update(
                    sender_module_id=107,  # SENDER_MODULE_ID
                    device_id=int(self.id_device),
                    unit_type_id=111,  # ID_TYPE_UNIT_CAM
                    status=status.value,
                )

                if success:
                    log.info(
                        f"Camera {self.id_device} status updated: {old_status.name} -> {status.name}"
                    )
                else:
                    log.error(
                        f"Failed to send status update for camera {self.id_device}"
                    )

            return True

        except Exception as e:
            log.error(f"Error updating camera status: {e}")
            return False

    def send_log_message(self, message: str, external_code_event: str = None) -> bool:
        """Send log message to Kafka"""
        try:
            from app_va import main_process

            if hasattr(main_process, "message_producer"):
                success = main_process.message_producer.send_log_message(
                    sender_module_id=107,  # SENDER_MODULE_ID
                    device_id=int(self.id_device),
                    unit_type_id=111,  # ID_TYPE_UNIT_CAM
                    external_code_event=external_code_event or "CAMERA_LOG",
                    card_number=None,
                    economic_body=None,
                    date=None,
                    image_to_incident=None,
                )

                if success:
                    log.info(f"Log message sent for camera {self.id_device}: {message}")
                else:
                    log.error(f"Failed to send log message for camera {self.id_device}")

                return success

            return False

        except Exception as e:
            log.error(f"Error sending log message: {e}")
            return False
