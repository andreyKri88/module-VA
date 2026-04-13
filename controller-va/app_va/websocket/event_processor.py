from typing import Dict, Any
from app_va.kafka.message_producer import MessageProducer
from app_va import log, SENDER_MODULE_ID


class EventProcessor:
    def __init__(self, message_producer: MessageProducer, camera_mapping: Dict[str, Dict]):
        self.message_producer = message_producer
        self.camera_mapping = camera_mapping  # Maps camera_uuid to device info
    
    def process_event(self, event_data: Dict[str, Any]) -> bool:
        """Process incoming WebSocket event and send to Kafka"""
        try:
            detector_type = event_data.get('detector_type', '').upper()
            camera_uuid = event_data.get('event_camera_uuid')
            
            if not camera_uuid:
                log.warning("Event missing camera_uuid")
                return False
            
            # Get device info from mapping
            device_info = self.camera_mapping.get(camera_uuid)
            if not device_info:
                log.warning(f"Camera {camera_uuid} not found in device mapping")
                return False
            
            # Add device mapping info to event
            event_data['device_id'] = device_info.get('device_id')
            event_data['unit_type_id'] = device_info.get('unit_type_id')
            
            # Send event based on detector type
            if detector_type == 'ROI':
                return self._process_roi_event(event_data)
            elif detector_type == 'LPR':
                return self._process_lpr_event(event_data)
            else:
                log.warning(f"Unknown detector type: {detector_type}")
                return False
                
        except Exception as e:
            log.error(f"Error processing event: {e}")
            return False
    
    def _process_roi_event(self, event_data: Dict[str, Any]) -> bool:
        """Process ROI event"""
        try:
            log.info(f"Processing ROI event: {event_data.get('event_detector_uuid')}")
            
            # Send ROI event to Kafka
            success = self.message_producer.send_roi_event(SENDER_MODULE_ID, event_data)
            
            if success:
                log.info("ROI event sent to Kafka successfully")
            else:
                log.error("Failed to send ROI event to Kafka")
            
            return success
            
        except Exception as e:
            log.error(f"Error processing ROI event: {e}")
            return False
    
    def _process_lpr_event(self, event_data: Dict[str, Any]) -> bool:
        """Process LPR event"""
        try:
            log.info(f"Processing LPR event: {event_data.get('event_detector_uuid')}")
            
            # Send LPR event to Kafka
            success = self.message_producer.send_lpr_event(SENDER_MODULE_ID, event_data)
            
            if success:
                log.info("LPR event sent to Kafka successfully")
            else:
                log.error("Failed to send LPR event to Kafka")
            
            return success
            
        except Exception as e:
            log.error(f"Error processing LPR event: {e}")
            return False
    
    def update_camera_mapping(self, camera_mapping: Dict[str, Dict]):
        """Update camera mapping"""
        self.camera_mapping = camera_mapping
        log.info(f"Camera mapping updated with {len(camera_mapping)} cameras")
