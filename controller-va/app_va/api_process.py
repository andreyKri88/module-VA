from app_va.models.enums import DeviceStatus
from app_va import log


class ApiProcess:
    def __init__(self, controller):
        self.controller = controller
        self.is_connected = False

    def connect(self) -> bool:
        """Connect to server/device API"""
        try:
            # Simulate connection logic
            # In real implementation, this would connect to actual device APIs
            self.is_connected = True
            self.controller.is_started = True
            
            # Send initial status to Kafka
            if hasattr(self.controller, 'server') and self.controller.server:
                self.controller.server.update_status(DeviceStatus.ONLINE)
            
            log.info(f"API process connected for server {self.controller.id_server}")
            return True
            
        except Exception as e:
            log.error(f"Failed to connect API process: {e}")
            self.is_connected = False
            self.controller.is_started = False
            return False

    def disconnect(self) -> bool:
        """Disconnect from server/device API"""
        try:
            self.is_connected = False
            self.controller.is_started = False
            
            # Send offline status to Kafka
            if hasattr(self.controller, 'server') and self.controller.server:
                self.controller.server.update_status(DeviceStatus.OFFLINE)
            
            log.info(f"API process disconnected for server {self.controller.id_server}")
            return True
            
        except Exception as e:
            log.error(f"Failed to disconnect API process: {e}")
            return False

    def handle_cam(self, camera_id: str, status: str) -> list:
        """Handle camera status change"""
        try:
            # Convert status string to DeviceStatus enum
            if status.lower() in ('1', 'true', 'on', 'online'):
                new_status = DeviceStatus.ONLINE
            elif status.lower() in ('0', 'false', 'off', 'offline'):
                new_status = DeviceStatus.OFFLINE
            else:
                return [False, f"Invalid status: {status}"]

            # Find camera by external ID
            camera = None
            for cam in self.controller.cameras.values():
                if cam.ext_id == camera_id:
                    camera = cam
                    break

            if not camera:
                return [False, f"Camera with ext_id {camera_id} not found"]

            # Update camera status
            success = camera.update_status(new_status)
            
            if success:
                return [True, f"Camera {camera.name} status updated to {new_status.name}"]
            else:
                return [False, f"Failed to update camera status"]
                
        except Exception as e:
            log.error(f"Error handling camera: {e}")
            return [False, f"Error: {str(e)}"]

    def get_list_cam(self) -> list:
        """Get list of cameras with their status"""
        try:
            return self.controller.get_list_cam()
        except Exception as e:
            log.error(f"Error getting camera list: {e}")
            return []
