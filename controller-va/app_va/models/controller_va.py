from typing import Dict, Any, Optional
from app_va.models.server_va import ServerVA
from app_va import log


class ControllerVA:
    def __init__(
        self,
        shutdown_minutes: int,
        event_timer_delay: float,
        sentinel_address: str,
        sentinel_port: int,
        event_array_length_max: int,
        time_between_sending_events: float,
        events_locker,
    ):
        self.shutdown_minutes = shutdown_minutes
        self.event_timer_delay = event_timer_delay
        self.sentinel_address = sentinel_address
        self.sentinel_port = sentinel_port
        self.event_array_length_max = event_array_length_max
        self.time_between_sending_events = time_between_sending_events
        self.events_locker = events_locker

        # Server instance
        self.server: Optional[ServerVA] = None
        self.is_initialized: bool = False
        self.is_started: bool = False
        self.need_to_reload: bool = False

        # For backward compatibility
        self.id_server: Optional[str] = None
        self.cameras: Dict[str, Any] = {}
        self.lock_cameras = events_locker

    def get_server(self, raw_dict: Dict[str, Any]) -> bool:
        """Initialize server from configuration record"""
        try:
            self.server = ServerVA(
                shutdown_minutes=self.shutdown_minutes,
                event_timer_delay=self.event_timer_delay,
                sentinel_address=self.sentinel_address,
                sentinel_port=self.sentinel_port,
                event_list=[],
                event_array_length_max=self.event_array_length_max,
                time_between_sending_events=self.time_between_sending_events,
                events_locker=self.events_locker,
            )

            success = self.server.get_server(raw_dict)
            if success:
                self.id_server = self.server.id_server
                self.cameras = self.server.cameras
                self.is_initialized = True
                log.info(f"Controller initialized for server {self.id_server}")
            else:
                self.is_initialized = False

            return success

        except Exception as e:
            log.error(f"Failed to initialize controller: {e}")
            self.is_initialized = False
            return False

    def get_cameras(self, cameras_data: Dict[str, Dict[str, Any]]):
        """Initialize cameras from database data"""
        if self.server:
            self.server.get_cameras(cameras_data)
            self.cameras = self.server.cameras

    def get_list_cam(self) -> list:
        """Get list of cameras information"""
        if self.server:
            return self.server.get_list_cam()
        return []

    def stop_timer(self):
        """Stop any running timers"""
        # Implementation for stopping timers if needed
        pass

    def get_camera_mapping(self) -> Dict[str, Dict[str, Any]]:
        """Get camera UUID to device mapping for WebSocket events"""
        mapping = {}
        if self.server:
            with self.server.lock_cameras:
                for camera in self.server.cameras.values():
                    if camera.camera_uuid:
                        mapping[camera.camera_uuid] = {
                            "device_id": int(camera.id_device),
                            "unit_type_id": 111,  # ID_TYPE_UNIT_CAM
                            "server_id": self.id_server,
                            "camera_name": camera.name,
                        }
        return mapping
