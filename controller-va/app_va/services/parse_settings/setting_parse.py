from app_va.services.parse_settings.ini_class import IniClass
from app_va.services.parse_settings.setting_dict import SettingDict
from app_va import log


class SettingParse:
    def __init__(self):
        self.ini_class = IniClass()
        self.setting_dict = SettingDict()

        # Parse all settings
        self._parse_all_settings()

    def _parse_all_settings(self):
        # Server settings
        self.port_server = self.ini_class.get_setting(
            "ServerAPI", "port_server", type_cast=int
        )
        self.module_name = self.ini_class.get_setting("ServerAPI", "module_name")
        self.vendor_name = self.ini_class.get_setting("ServerAPI", "vendor_name")
        self.server_api_addr = self.ini_class.get_setting(
            "ServerAPI", "server_api_addr"
        )
        self.server_api_port = self.ini_class.get_setting(
            "ServerAPI", "server_api_port", type_cast=int
        )
        self.server_api_user = self.ini_class.get_setting(
            "ServerAPI", "server_api_user"
        )
        self.server_api_passw = self.ini_class.get_setting(
            "ServerAPI", "server_api_passw"
        )

        # Timer settings
        self.timer = self.ini_class.get_setting("ServerAPI", "timer", type_cast=int)
        self.event_timer_delay = self.ini_class.get_setting(
            "ServerAPI", "event_timer_delay", type_cast=float
        )
        self.event_array_length_max = self.ini_class.get_setting(
            "ServerAPI", "event_array_length_max", type_cast=int
        )
        self.time_between_sending_events = self.ini_class.get_setting(
            "ServerAPI", "time_between_sending_events", type_cast=float
        )

        # Kafka settings
        self.kafka_ip = self.ini_class.get_setting("Kafka", "kafka.ip")
        self.kafka_port = self.ini_class.get_setting(
            "Kafka", "kafka.port", type_cast=int
        )
        self.kafka_group_id = self.ini_class.get_setting("Kafka", "kafka.group-id")

        # WebSocket settings
        self.ws_url = self.ini_class.get_setting("WebSocket", "ws_url")

        # Events settings
        self.event_types = self._parse_event_types()

    def _parse_event_types(self):
        """Parse event_types from Events section"""
        try:
            events_str = self.ini_class.get_setting(
                "Events", "event_types", default="{}"
            )
            events_str = (
                str(events_str)
                .replace("{", "")
                .replace("}", "")
                .replace("'", "")
                .replace('"', "")
            )
            events_list = events_str.split(",")

            event_types = {}
            for event in events_list:
                if ":" in event:
                    key, value = event.split(":", 1)
                    event_types[key.strip()] = value.strip()

            return event_types
        except Exception as e:
            log.warning(f"Error parsing event_types: {e}")
            return {}
