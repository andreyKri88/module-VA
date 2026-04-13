from typing import Dict, Any


class SettingDict:
    def __init__(self):
        self.settings: Dict[str, Any] = {}
    
    def get_setting(self, key: str, default=None):
        return self.settings.get(key, default)
    
    def set_setting(self, key: str, value: Any):
        self.settings[key] = value
    
    def update_settings(self, new_settings: Dict[str, Any]):
        self.settings.update(new_settings)
