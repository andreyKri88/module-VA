import requests
import time
from typing import Optional
from app_va import log


class ModuleIdService:
    def __init__(self, server_api_addr: str, server_api_port: int):
        self.server_api_addr = server_api_addr
        self.server_api_port = server_api_port
        self.cached_sender_module_id: Optional[int] = None
        self.last_ping_time: float = 0
        self.ping_interval: int = 300  # 5 minutes
        self.ping_timeout: int = 10

    def get_sender_module_id(self) -> int:
        """Get senderModuleId from external server via ping"""
        current_time = time.time()
        
        # Return cached value if still valid
        if (self.cached_sender_module_id and 
            current_time - self.last_ping_time < self.ping_interval):
            return self.cached_sender_module_id
        
        # Fetch new value from server
        try:
            sender_id = self._fetch_sender_module_id()
            if sender_id:
                self.cached_sender_module_id = sender_id
                self.last_ping_time = current_time
                log.info(f"Received senderModuleId: {sender_id} from server")
                return sender_id
            else:
                log.warning("Failed to get senderModuleId from server, using default")
                return 107  # Default value
        except Exception as e:
            log.error(f"Error fetching senderModuleId: {e}")
            return self.cached_sender_module_id or 107

    def _fetch_sender_module_id(self) -> Optional[int]:
        """Fetch senderModuleId from external server"""
        try:
            # Try to ping external server to get senderModuleId
            ping_url = f"http://{self.server_api_addr}:{self.server_api_port}/ping"
            
            response = requests.get(ping_url, timeout=self.ping_timeout)
            
            if response.status_code == 200:
                data = response.json()
                sender_id = data.get('senderModuleId')
                if sender_id and isinstance(sender_id, int):
                    return sender_id
                else:
                    log.warning(f"Invalid senderModuleId in response: {data}")
                    return None
            else:
                log.warning(f"Ping request failed with status {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            log.warning(f"Network error during ping: {e}")
            return None
        except Exception as e:
            log.error(f"Unexpected error during ping: {e}")
            return None

    def force_refresh(self) -> bool:
        """Force refresh of senderModuleId"""
        self.last_ping_time = 0  # Reset cache time
        try:
            sender_id = self.get_sender_module_id()
            return sender_id is not None
        except Exception:
            return False

    def get_cached_id(self) -> Optional[int]:
        """Get cached senderModuleId without refresh"""
        return self.cached_sender_module_id
