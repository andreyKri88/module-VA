from threading import Thread, RLock
import time
import gc
import json
from typing import Dict
from pathlib import Path
from app_va import ID_TYPE_UNIT_CAM, ID_TYPE_UNIT_SRV, log
from app_va.services import InitializeClass, ModuleIdService, ConfigValidator
from app_va.models import ControllerVA
from app_va.api_process import ApiProcess
from app_va.models.scheduler import ScheduleWorker
from app_va.kafka import KafkaClient, MessageProducer
from app_va.websocket import WebSocketClient, EventProcessor


class MainProcess:
    def __init__(self, init_instance: InitializeClass):
        self.initializer: InitializeClass = init_instance
        self.schedule_worker: ScheduleWorker = ScheduleWorker(
            api_addr=self.initializer.server_api_addr,
            api_port=self.initializer.server_api_port,
        )

        self.api_processes: Dict[str, ApiProcess] = {}
        self.raw_servers: dict = {}
        self.raw_cameras: dict = {}
        self.events_list: list = []

        self.events_locker: RLock = RLock()
        self.sentinel_update_thread = Thread(
            target=self.__update_sentinel_data, daemon=True, name="updateThread"
        )
        self.sentinel_update_thread.start()
        self.schedule_keeper = Thread(
            target=self.schedule_thread, daemon=True, name="schedule_keeper"
        )

        # Initialize Kafka client
        self.kafka_client: KafkaClient = None
        self.message_producer: MessageProducer = None
        self._init_kafka()

        # Initialize WebSocket client
        self.ws_client: WebSocketClient = None
        self.event_processor: EventProcessor = None
        self._init_websocket()

        # Initialize ModuleIdService for dynamic senderModuleId
        self.module_id_service = ModuleIdService(
            server_api_addr=self.initializer.server_api_addr,
            server_api_port=self.initializer.server_api_port,
        )

        # Initialize ConfigValidator
        self.config_validator = ConfigValidator()

        # Load device configuration from file or external source
        self._load_device_configuration()

    def _load_device_configuration(self):
        """Load device configuration from JSON file or external source"""
        try:
            # Try to load from devices.json file
            config_file = Path("devices.json")
            if config_file.exists():
                with open(config_file, "r", encoding="utf-8") as f:
                    config = json.load(f)
                    self.raw_servers = config.get("servers", {})
                    self.raw_cameras = config.get("cameras", {})

                # Validate configuration
                if self.config_validator.validate_device_config(config):
                    log.info(
                        f"Loaded and validated device configuration from {config_file}"
                    )
                else:
                    log.error(
                        f"Device configuration validation failed for {config_file}"
                    )
                    report = self.config_validator.get_validation_report()
                    log.error(f"Validation errors: {report['errors']}")
                    # Fall back to default configuration if validation fails
                    self._create_default_device_config()
                    log.info(
                        "Falling back to default configuration due to validation errors"
                    )
            else:
                # Create default configuration
                self._create_default_device_config()
                log.info("Created default device configuration")
        except Exception as e:
            log.error(f"Error loading device configuration: {e}")
            self._create_default_device_config()

    def _create_default_device_config(self):
        """Create default device configuration"""
        # Default server configuration
        self.raw_servers = {
            "1": {
                "id_serv": "1",
                "ext_id": "server_001",
                "name": "VA Server 1",
                "ip_address": "127.0.0.1",
                "port": 600,
                "status": 1,
                "id_type_unit": ID_TYPE_UNIT_SRV,
            }
        }

        # Default camera configuration
        self.raw_cameras = {
            "1": {
                "1": {
                    "id_device": "1",
                    "ext_id": "camera_001",
                    "name": "VA Camera 1",
                    "camera_uuid": "675a1fb7-f926-4972-8957-c64f715a4015",
                    "ip_address": "127.0.0.1",
                    "port": 8080,
                    "status": 1,
                    "id_type_unit": ID_TYPE_UNIT_CAM,
                    "id_serv": "1",
                }
            }
        }

    def _init_kafka(self):
        """Initialize Kafka client and message producer"""
        try:
            # Use Kafka parameters from settings file
            kafka_servers = f"{self.initializer.kafka_ip}:{self.initializer.kafka_port}"

            self.kafka_client = KafkaClient(
                bootstrap_servers=kafka_servers,
                group_id=self.initializer.kafka_group_id,
            )
            self.message_producer = MessageProducer(self.kafka_client)
            log.info(f"Kafka client initialized with servers: {kafka_servers}")
        except Exception as e:
            log.error(f"Failed to initialize Kafka client: {e}")

    def _init_websocket(self):
        """Initialize WebSocket client and event processor"""
        try:
            # Create event processor with empty camera mapping (will be updated later)
            self.event_processor = EventProcessor(
                message_producer=self.message_producer, camera_mapping={}
            )

            # Create WebSocket client
            self.ws_client = WebSocketClient(
                ws_url=self.initializer.ws_url,
                event_processor=self.event_processor.process_event,
            )

            # Start WebSocket client
            self.ws_client.start()
            log.info("WebSocket client initialized successfully")
        except Exception as e:
            log.error(f"Failed to initialize WebSocket client: {e}")

    def schedule_thread(self) -> None:
        self.schedule_worker.main_work()

    def __create_server_process(self, raw_dict: dict) -> None:
        this_controller: ControllerVA = ControllerVA(
            shutdown_minutes=self.initializer.shutdown_minutes,
            event_timer_delay=self.initializer.event_timer_delay,
            sentinel_address=self.initializer.server_api_addr,
            sentinel_port=self.initializer.server_api_port,
            event_array_length_max=self.initializer.event_array_length_max,
            time_between_sending_events=self.initializer.time_between_sending_events,
            events_locker=self.events_locker,
        )
        this_controller.get_server(raw_dict=raw_dict)

        if this_controller.id_server in self.raw_cameras:
            this_controller.get_cameras(self.raw_cameras[this_controller.id_server])

        self.api_processes[this_controller.id_server] = ApiProcess(
            controller=this_controller
        )

        if this_controller.is_initialized:
            log.info(f"<server_id>[{this_controller.id_server}] initialized")
            self.api_processes[this_controller.id_server].connect()
            if this_controller.is_started:
                log.info(
                    f"<server_id>[{this_controller.id_server}] successfully connected"
                )
        else:
            log.warning(
                f"<server_id>[{this_controller.id_server}] has not been initialized"
            )

        # Update camera mapping for WebSocket events
        self._update_camera_mapping()

    def __remove_server_process(self, id_server: str) -> None:
        if id_server in self.api_processes:
            this_process = self.api_processes[id_server]
            this_process.disconnect()

            if not this_process.controller.is_started:
                self.api_processes[id_server].controller.stop_timer()
                del self.api_processes[id_server]

        try:
            assert id_server not in self.api_processes
            log.warning(f"<server_id>[{id_server}] disconnected")
        except AssertionError:
            log.warning(f"error while removing server <id server>[{id_server}]")

        # Update camera mapping
        self._update_camera_mapping()

    def __verify_server_process(self, id_server, raw_dict: dict):
        this_controller = self.api_processes[id_server].controller
        this_controller.get_server(raw_dict=raw_dict)

        if this_controller.id_server in self.raw_cameras:
            with this_controller.lock_cameras:
                this_controller.get_cameras(self.raw_cameras[this_controller.id_server])

        if this_controller.need_to_reload:
            self.__remove_server_process(id_server=id_server)
            self.__create_server_process(raw_dict=raw_dict)
        else:
            self.api_processes[id_server].connect()

        # Update camera mapping
        self._update_camera_mapping()

    def _update_camera_mapping(self):
        """Update camera mapping for WebSocket event processor"""
        if self.event_processor:
            camera_mapping = {}
            for api_process in self.api_processes.values():
                if api_process.controller and api_process.controller.server:
                    server_mapping = api_process.controller.get_camera_mapping()
                    camera_mapping.update(server_mapping)

            self.event_processor.update_camera_mapping(camera_mapping)
            log.info(f"Camera mapping updated: {len(camera_mapping)} cameras")

    def __update_data(self):
        self.__load_n_handle_servers()
        self.__load_n_handle_cameras()

        removed_servers = {
            key: self.api_processes[key]
            for key in self.api_processes.keys() - self.raw_servers.keys()
        }
        if len(removed_servers) > 0:
            for id_server in removed_servers:
                self.__remove_server_process(id_server=id_server)

        for id_serv in self.raw_servers.keys():
            if id_serv not in self.api_processes.keys():
                self.__create_server_process(raw_dict=self.raw_servers[id_serv])
            else:
                self.__verify_server_process(
                    id_server=id_serv, raw_dict=self.raw_servers[id_serv]
                )
        _ = gc.collect()

    def __update_sentinel_data(self) -> None:
        # Start the update loop immediately since we don't have database connection dependency
        iter_count: int = 0
        while True:
            if not self.schedule_keeper.is_alive():
                self.schedule_keeper.start()

            self.__update_data()
            iter_count = iter_count + 1
            if iter_count >= 2:
                self.__server_up_time()
                iter_count = 0
            time.sleep(20)

    def __server_up_time(self) -> None:
        if len(self.raw_servers):
            str_ids: str = ",".join(self.raw_servers.keys())
            # Send server up time via Kafka instead of database
            if self.message_producer:
                for server_id in self.raw_servers.keys():
                    sender_id = self.module_id_service.get_sender_module_id()
                    success = self.message_producer.send_status_update(
                        sender_module_id=sender_id,
                        device_id=int(server_id),
                        unit_type_id=110,  # ID_TYPE_UNIT_SRV
                        status=1,  # Online status
                    )
                    if success:
                        log.info(
                            f"Server up time sent to Kafka for [{server_id}] with senderId [{sender_id}]"
                        )
                    else:
                        log.warning(f"Failed to send server up time for [{server_id}]")

    def __single_up_time(self, id_server: str) -> None:
        # Send single server up time via Kafka instead of database
        if self.message_producer:
            sender_id = self.module_id_service.get_sender_module_id()
            success = self.message_producer.send_status_update(
                sender_module_id=sender_id,
                device_id=int(id_server),
                unit_type_id=110,  # ID_TYPE_UNIT_SRV
                status=1,  # Online status
            )
            if success:
                log.info(
                    f"Server up time sent to Kafka for [{id_server}] with senderId [{sender_id}]"
                )
            else:
                log.warning(f"Failed to send server up time for [{id_server}]")

    def __load_n_handle_servers(self) -> None:
        # Servers are loaded from configuration file, no database access needed
        log.debug(f"Loaded {len(self.raw_servers)} servers from configuration")

    def __load_n_handle_cameras(self) -> None:
        # Cameras are loaded from configuration file, no database access needed
        log.debug(f"Loaded {len(self.raw_cameras)} cameras from configuration")

    def get_all_channels(self, serv_id: str) -> dict:
        this_devices: dict = {}

        if serv_id not in self.api_processes.keys():
            this_devices["status"] = False
            this_devices["serv_id"] = serv_id
            this_devices["devices"] = []
            this_devices["description"] = "invalid serv_id"
        else:
            this_devices["status"] = True
            this_devices["serv_id"] = int(serv_id)
            this_devices["devices"] = self.api_processes[
                serv_id
            ].controller.get_list_cam()

        return this_devices

    def get_api_channels(self, serv_id: str) -> dict:
        this_devices: dict = {}

        if serv_id not in self.api_processes.keys():
            this_devices["status"] = False
            this_devices["serv_id"] = serv_id
            this_devices["devices"] = []
            this_devices["description"] = "invalid serv_id"
        else:
            this_devices["status"] = True
            this_devices["serv_id"] = int(serv_id)
            this_devices["devices"] = self.api_processes[serv_id].get_list_cam()

        return this_devices

    def handle_camera(self, serv_id: str, cam_id: str, status: str) -> dict:
        response: dict = {}

        if serv_id is None or cam_id is None or status is None:
            response["status"] = False
            response["description"] = "invalid params"
        elif serv_id not in self.api_processes.keys():
            response["status"] = False
            response["description"] = "invalid server_id"
        else:
            this_server: ApiProcess = self.api_processes[serv_id]

            if cam_id not in this_server.controller.cameras:
                response["status"] = False
                response["description"] = "invalid device_id"
            else:
                device_id_api = this_server.controller.cameras[cam_id].ext_id
                resp: list = this_server.handle_cam(
                    camera_id=device_id_api, status=status
                )
                response["status"] = resp[0]
                response["server_id"] = int(serv_id)
                response["device_id"] = int(cam_id)
                response["description"] = resp[1]

        return response

    def shutdown(self):
        """Graceful shutdown of all components"""
        try:
            log.info("Shutting down MainProcess...")

            # Stop WebSocket client
            if self.ws_client:
                self.ws_client.stop()

            # Close Kafka client
            if self.kafka_client:
                self.kafka_client.close()

            log.info("MainProcess shutdown completed")
        except Exception as e:
            log.error(f"Error during shutdown: {e}")
