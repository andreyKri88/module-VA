from app_va.services.parse_settings.setting_parse import SettingParse


class InitializeClass:
    def __init__(self):
        self.settings = SettingParse()

        # Server settings
        self.module_name = self.settings.module_name
        self.vendor_name = self.settings.vendor_name
        self.server_api_addr = self.settings.server_api_addr
        self.server_api_port = self.settings.server_api_port

        # Timer settings
        self.shutdown_minutes = self.settings.timer
        self.event_timer_delay = self.settings.event_timer_delay
        self.event_array_length_max = self.settings.event_array_length_max
        self.time_between_sending_events = self.settings.time_between_sending_events

        # Kafka settings
        self.kafka_ip = self.settings.kafka_ip
        self.kafka_port = self.settings.kafka_port
        self.kafka_group_id = self.settings.kafka_group_id

        # WebSocket settings
        self.ws_url = self.settings.ws_url
