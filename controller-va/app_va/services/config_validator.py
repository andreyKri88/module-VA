from typing import Dict, Any, List, Optional
from app_va import log
import uuid


class ConfigValidator:
    def __init__(self):
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def validate_device_config(self, config: Dict[str, Any]) -> bool:
        """Validate complete device configuration"""
        self.errors.clear()
        self.warnings.clear()
        
        is_valid = True
        
        # Validate servers
        servers = config.get('servers', {})
        if not servers:
            self.errors.append("No servers defined in configuration")
            is_valid = False
        else:
            is_valid &= self._validate_servers(servers)
        
        # Validate cameras
        cameras = config.get('cameras', {})
        if not cameras:
            self.warnings.append("No cameras defined in configuration")
        else:
            is_valid &= self._validate_cameras(cameras, servers)
        
        # Log validation results
        if self.errors:
            log.error(f"Configuration validation errors: {self.errors}")
        if self.warnings:
            log.warning(f"Configuration validation warnings: {self.warnings}")
        
        if is_valid:
            log.info("Device configuration validation passed")
        
        return is_valid

    def _validate_servers(self, servers: Dict[str, Any]) -> bool:
        """Validate server configuration"""
        is_valid = True
        
        for server_id, server_config in servers.items():
            if not isinstance(server_config, dict):
                self.errors.append(f"Server {server_id} configuration must be a dictionary")
                is_valid = False
                continue
            
            # Required fields
            required_fields = ['id_serv', 'ext_id', 'name', 'ip_address', 'port', 'id_type_unit']
            for field in required_fields:
                if field not in server_config:
                    self.errors.append(f"Server {server_id} missing required field: {field}")
                    is_valid = False
            
            # Validate typeunit
            if 'id_type_unit' in server_config:
                type_unit = str(server_config['id_type_unit'])
                if type_unit not in ['110']:  # Server typeunit
                    self.errors.append(f"Server {server_id} has invalid id_type_unit: {type_unit}, should be 110")
                    is_valid = False
            
            # Validate port
            if 'port' in server_config:
                port = server_config['port']
                if not isinstance(port, int) or port < 1 or port > 65535:
                    self.errors.append(f"Server {server_id} has invalid port: {port}")
                    is_valid = False
            
            # Validate IP address (basic check)
            if 'ip_address' in server_config:
                ip = server_config['ip_address']
                if not isinstance(ip, str) or not self._is_valid_ip(ip):
                    self.warnings.append(f"Server {server_id} has potentially invalid IP address: {ip}")
        
        return is_valid

    def _validate_cameras(self, cameras: Dict[str, Any], servers: Dict[str, Any]) -> bool:
        """Validate camera configuration"""
        is_valid = True
        
        for server_id, server_cameras in cameras.items():
            if server_id not in servers:
                self.errors.append(f"Cameras defined for non-existent server: {server_id}")
                is_valid = False
                continue
            
            if not isinstance(server_cameras, dict):
                self.errors.append(f"Cameras for server {server_id} must be a dictionary")
                is_valid = False
                continue
            
            for camera_id, camera_config in server_cameras.items():
                if not isinstance(camera_config, dict):
                    self.errors.append(f"Camera {camera_id} in server {server_id} configuration must be a dictionary")
                    is_valid = False
                    continue
                
                # Required fields
                required_fields = ['id_device', 'ext_id', 'name', 'id_type_unit', 'id_serv']
                for field in required_fields:
                    if field not in camera_config:
                        self.errors.append(f"Camera {camera_id} in server {server_id} missing required field: {field}")
                        is_valid = False
                
                # Validate typeunit
                if 'id_type_unit' in camera_config:
                    type_unit = str(camera_config['id_type_unit'])
                    if type_unit not in ['111']:  # Device typeunit
                        self.errors.append(f"Camera {camera_id} in server {server_id} has invalid id_type_unit: {type_unit}, should be 111")
                        is_valid = False
                
                # Validate server reference
                if 'id_serv' in camera_config:
                    camera_server_id = str(camera_config['id_serv'])
                    if camera_server_id != server_id:
                        self.errors.append(f"Camera {camera_id} references server {camera_server_id} but is defined under server {server_id}")
                        is_valid = False
                
                # Validate camera_uuid if present
                if 'camera_uuid' in camera_config:
                    uuid_str = camera_config['camera_uuid']
                    if not isinstance(uuid_str, str) or not self._is_valid_uuid(uuid_str):
                        self.warnings.append(f"Camera {camera_id} in server {server_id} has potentially invalid UUID: {uuid_str}")
        
        return is_valid

    def _is_valid_ip(self, ip: str) -> bool:
        """Basic IP address validation"""
        try:
            parts = ip.split('.')
            if len(parts) != 4:
                return False
            for part in parts:
                if not part.isdigit() or int(part) < 0 or int(part) > 255:
                    return False
            return True
        except:
            return False

    def _is_valid_uuid(self, uuid_str: str) -> bool:
        """Validate UUID format"""
        try:
            uuid.UUID(uuid_str)
            return True
        except ValueError:
            return False

    def get_validation_report(self) -> Dict[str, Any]:
        """Get validation report"""
        return {
            'is_valid': len(self.errors) == 0,
            'errors': self.errors.copy(),
            'warnings': self.warnings.copy(),
            'error_count': len(self.errors),
            'warning_count': len(self.warnings)
        }
