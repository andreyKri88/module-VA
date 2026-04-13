from typing import Dict, Any, Optional
from app_va.models.enums import DeviceStatus
from app_va import log


class ServerVA:
    def __init__(
        self,
        shutdown_minutes: int,
        event_timer_delay: float,
        sentinel_address: str,
        sentinel_port: int,
        event_list: list,
        event_array_length_max: int,
        time_between_sending_events: float,
        events_locker,
    ):
        self.shutdown_minutes = shutdown_minutes
        self.event_timer_delay = event_timer_delay
        self.sentinel_address = sentinel_address
        self.sentinel_port = sentinel_port
        self.event_list = event_list
        self.event_array_length_max = event_array_length_max
        self.time_between_sending_events = time_between_sending_events
        self.events_locker = events_locker

        # Server properties
        self.id_server: Optional[str] = None
        self.ext_id: Optional[str] = None
        self.name: Optional[str] = None
        self.ip_address: Optional[str] = None
        self.port: Optional[int] = None
        self.status: DeviceStatus = DeviceStatus.OFFLINE
        self.is_initialized: bool = False
        self.is_started: bool = False
        self.need_to_reload: bool = False

        # Camera management
        self.cameras: Dict[str, "CameraVA"] = {}
        self.lock_cameras = events_locker

    def get_server(self, raw_dict: Dict[str, Any]) -> bool:
        """Initialize server from database record"""
        try:
            self.id_server = str(raw_dict.get("id_serv"))
            self.ext_id = raw_dict.get("ext_id")
            self.name = raw_dict.get("name")
            self.ip_address = raw_dict.get("ip_address")
            self.port = raw_dict.get("port")

            # Convert status to DeviceStatus enum
            status_value = raw_dict.get("status", 0)
            if status_value == 1:
                self.status = DeviceStatus.ONLINE
            else:
                self.status = DeviceStatus.OFFLINE

            self.is_initialized = True
            log.info(f"Server {self.id_server} ({self.name}) initialized successfully")
            return True

        except Exception as e:
            log.error(f"Failed to initialize server: {e}")
            self.is_initialized = False
            return False

    def get_cameras(self, cameras_data: Dict[str, Dict[str, Any]]):
        """Initialize cameras from configuration data"""
        try:
            with self.lock_cameras:
                self.cameras.clear()

                for cam_id, cam_data in cameras_data.items():
                    camera = CameraVA(
                        server_id=self.id_server,
                        events_list=self.event_list,
                        events_locker=self.events_locker,
                    )

                    if camera.get_camera(cam_data):
                        self.cameras[cam_id] = camera

                log.info(
                    f"Loaded {len(self.cameras)} cameras for server {self.id_server}"
                )

        except Exception as e:
            log.error(f"Failed to load cameras for server {self.id_server}: {e}")

    def get_list_cam(self) -> list:
        """Get list of cameras information"""
        cameras_list = []
        try:
            with self.lock_cameras:
                for camera in self.cameras.values():
                    cameras_list.append(
                        {
                            "id_device": camera.id_device,
                            "ext_id": camera.ext_id,
                            "name": camera.name,
                            "status": camera.status.value,
                            "camera_uuid": camera.camera_uuid,
                        }
                    )
        except Exception as e:
            log.error(f"Error getting camera list: {e}")

        return cameras_list

    def update_status(self, status: DeviceStatus) -> bool:
        """Update server status"""
        try:
            old_status = self.status
            self.status = status

            # Send status update to Kafka
            from app_va import main_process

            if hasattr(main_process, "message_producer"):
                success = main_process.message_producer.send_status_update(
                    sender_module_id=107,  # SENDER_MODULE_ID
                    device_id=int(self.id_server),
                    unit_type_id=110,  # ID_TYPE_UNIT_SRV
                    status=status.value,
                )

                if success:
                    log.info(
                        f"Server {self.id_server} status updated: {old_status.name} -> {status.name}"
                    )
                else:
                    log.error(
                        f"Failed to send status update for server {self.id_server}"
                    )

            return True

        except Exception as e:
            log.error(f"Error updating server status: {e}")
            return False
