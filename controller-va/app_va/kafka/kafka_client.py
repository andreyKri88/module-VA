import json
import time
import asyncio
from typing import Dict, Any, Optional
from kafka import KafkaProducer
from kafka.errors import KafkaError
from app_va.kafka.kafka_models import (
    KafkaMessage,
    KafkaMessageType,
    VideoDetectionEventType,
    KafkaVideoDetectionEventMessage,
)
from app_va import log


class KafkaClient:
    def __init__(self, bootstrap_servers: str, group_id: str):
        self.bootstrap_servers = bootstrap_servers
        self.group_id = group_id
        self.producer: Optional[KafkaProducer] = None
        self._connect()

    def _connect(self):
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: json.dumps(
                    v, default=str, ensure_ascii=False
                ).encode("utf-8"),
                key_serializer=lambda k: k.encode("utf-8") if k else None,
                acks="all",
                retries=3,
                batch_size=16384,
                linger_ms=10,
                buffer_memory=33554432,
            )
            log.info(f"Connected to Kafka at {self.bootstrap_servers}")
        except Exception as e:
            log.error(f"Failed to connect to Kafka: {e}")
            raise

    def send_status_log_message(
        self, sender_module_id: int, messages: list, max_retries: int = 3
    ) -> bool:
        """Send status or log message to status-log topic with retry logic"""
        for attempt in range(max_retries):
            try:
                kafka_message = KafkaMessage(
                    type=(
                        KafkaMessageType.SAVE_STATUS
                        if messages[0].get("status") is not None
                        else KafkaMessageType.SAVE_LOG
                    ),
                    sender_module_id=sender_module_id,
                    payload=messages,
                )

                message_dict = {
                    "type": kafka_message.type.value,
                    "senderModuleId": kafka_message.sender_module_id,
                    "payload": kafka_message.payload,
                }

                future = self.producer.send(
                    "status-log", key=f"sender-{sender_module_id}", value=message_dict
                )

                # Block until message is sent or timeout
                record_metadata = future.get(timeout=10)

                log.info(
                    f"Status/Log message sent to topic 'status-log', partition {record_metadata.partition}, offset {record_metadata.offset}"
                )
                return True

            except KafkaError as e:
                log.warning(f"Kafka error on attempt {attempt + 1}/{max_retries}: {e}")
                if attempt == max_retries - 1:
                    log.error(
                        f"Failed to send status/log message after {max_retries} attempts: {e}"
                    )
                    return False
                # Wait before retry
                time.sleep(2**attempt)  # Exponential backoff
            except Exception as e:
                log.error(f"Unexpected error sending status/log message: {e}")
                return False

        return False

    def send_event_message(
        self, sender_module_id: int, event_data: Dict[str, Any], max_retries: int = 3
    ) -> bool:
        """Send ROI/LPR event to code-incident-33-event topic with retry logic"""
        for attempt in range(max_retries):
            try:
                # Determine event type from detector_type
                detector_type = event_data.get("detector_type", "").upper()
                if detector_type == "ROI":
                    event_type = VideoDetectionEventType.ROI
                elif detector_type == "LPR":
                    event_type = VideoDetectionEventType.LPR
                else:
                    log.warning(f"Unknown detector_type: {detector_type}")
                    return False

                # Extract common fields
                correlation_id = event_data.get("event_detector_uuid")
                device_id = event_data.get(
                    "archive_id"
                )  # Using archive_id as device_id
                date = event_data.get("event_time_begin")

                # Extract data payload
                data = event_data.get("data", {})

                # Build event-specific payload
                event_payload = {
                    "correlationId": correlation_id,
                    "eventType": event_type.value,
                    "deviceId": device_id,
                    "unitTypeId": None,  # Will be set based on camera mapping
                    "externalCodeEvent": None,  # Will be set based on event mapping
                    "date": date,
                    "imageToIncident": None,  # Will be set if image is available
                }

                # Add ROI-specific fields
                if event_type == VideoDetectionEventType.ROI:
                    event_payload.update(
                        {
                            "personFullName": None,
                            "personId": None,
                            "numberName": None,
                            "objectName": data.get("event_class", {}).get("name"),
                            "trackId": data.get("event_track_id"),
                            "comment": f"Event type: {data.get('event_type')}, Zone: {', '.join(data.get('linked_zone', []))}",
                        }
                    )

                # Add LPR-specific fields
                elif event_type == VideoDetectionEventType.LPR:
                    event_payload.update(
                        {
                            "personFullName": None,
                            "personId": None,
                            "numberName": data.get("event_number"),
                            "objectName": None,
                            "trackId": data.get("event_track_id"),
                            "comment": f"Number status: {data.get('event_number_status')}, Score: {data.get('event_score')}",
                        }
                    )

                kafka_message = KafkaMessage(
                    type=KafkaMessageType.SAVE_EVENT,
                    sender_module_id=sender_module_id,
                    payload=[event_payload],
                )

                message_dict = {
                    "type": kafka_message.type.value,
                    "senderModuleId": kafka_message.sender_module_id,
                    "payload": kafka_message.payload,
                }

                future = self.producer.send(
                    "code-incident-33-event",
                    key=f"event-{correlation_id}",
                    value=message_dict,
                )

                # Block until message is sent or timeout
                record_metadata = future.get(timeout=10)

                log.info(
                    f"Event message sent to topic 'code-incident-33-event', partition {record_metadata.partition}, offset {record_metadata.offset}"
                )
                return True

            except KafkaError as e:
                log.warning(f"Kafka error on attempt {attempt + 1}/{max_retries}: {e}")
                if attempt == max_retries - 1:
                    log.error(
                        f"Failed to send event message after {max_retries} attempts: {e}"
                    )
                    return False
                # Wait before retry
                time.sleep(2**attempt)  # Exponential backoff
            except Exception as e:
                log.error(f"Unexpected error sending event message: {e}")
                return False

        return False

    def close(self):
        """Close Kafka producer"""
        if self.producer:
            self.producer.flush()
            self.producer.close()
            log.info("Kafka producer closed")
