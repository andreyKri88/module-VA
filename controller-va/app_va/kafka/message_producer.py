from app_va.kafka.kafka_client import KafkaClient
from app_va import log


class MessageProducer:
    def __init__(self, kafka_client: KafkaClient):
        self.kafka_client = kafka_client
    
    def send_status_update(self, sender_module_id: int, device_id: int, unit_type_id: int, 
                          status: int, children_status: int = None, 
                          external_code_event: str = None, card_number: str = None,
                          economic_body: str = None, date: str = None) -> bool:
        """Send status update message"""
        try:
            message = {
                'id': device_id,
                'unitTypeId': unit_type_id,
                'externalCodeEvent': external_code_event,
                'status': status,
                'childrenStatus': children_status,
                'cardNumber': card_number,
                'economicBody': economic_body,
                'date': date,
                'imageToIncident': None
            }
            
            return self.kafka_client.send_status_log_message(sender_module_id, [message])
            
        except Exception as e:
            log.error(f"Failed to send status update: {e}")
            return False
    
    def send_log_message(self, sender_module_id: int, device_id: int, unit_type_id: int,
                        external_code_event: str, card_number: str = None,
                        economic_body: str = None, date: str = None,
                        image_to_incident: str = None) -> bool:
        """Send log message"""
        try:
            message = {
                'id': device_id,
                'unitTypeId': unit_type_id,
                'externalCodeEvent': external_code_event,
                'status': None,
                'childrenStatus': None,
                'cardNumber': card_number,
                'economicBody': economic_body,
                'date': date,
                'imageToIncident': image_to_incident
            }
            
            return self.kafka_client.send_status_log_message(sender_module_id, [message])
            
        except Exception as e:
            log.error(f"Failed to send log message: {e}")
            return False
    
    def send_roi_event(self, sender_module_id: int, event_data: dict) -> bool:
        """Send ROI event"""
        return self.kafka_client.send_event_message(sender_module_id, event_data)
    
    def send_lpr_event(self, sender_module_id: int, event_data: dict) -> bool:
        """Send LPR event"""
        return self.kafka_client.send_event_message(sender_module_id, event_data)
