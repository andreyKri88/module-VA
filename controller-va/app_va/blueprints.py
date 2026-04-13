from flask import Blueprint, request, jsonify
from app_va import main_process, log

device_observer = Blueprint("device_observer", __name__)


@device_observer.route("/camera/get_all_cameras", methods=["GET"])
def get_all_cameras():
    """Get all cameras for a server"""
    try:
        serv_id = request.args.get("serv_id")
        if not serv_id:
            return (
                jsonify(
                    {"status": False, "description": "serv_id parameter is required"}
                ),
                400,
            )

        result = main_process.get_all_channels(serv_id)
        return jsonify(result)

    except Exception as e:
        log.error(f"Error in get_all_cameras: {e}")
        return jsonify({"status": False, "description": str(e)}), 500


@device_observer.route("/camera/get_api_cameras", methods=["GET"])
def get_api_cameras():
    """Get API cameras for a server"""
    try:
        serv_id = request.args.get("serv_id")
        if not serv_id:
            return (
                jsonify(
                    {"status": False, "description": "serv_id parameter is required"}
                ),
                400,
            )

        result = main_process.get_api_channels(serv_id)
        return jsonify(result)

    except Exception as e:
        log.error(f"Error in get_api_cameras: {e}")
        return jsonify({"status": False, "description": str(e)}), 500


@device_observer.route("/camera/handle_camera", methods=["POST"])
def handle_camera():
    """Handle camera status change"""
    try:
        data = request.get_json()
        if not data:
            return (
                jsonify({"status": False, "description": "JSON data is required"}),
                400,
            )

        serv_id = data.get("serv_id")
        cam_id = data.get("cam_id")
        status = data.get("status")

        if not all([serv_id, cam_id, status]):
            return (
                jsonify(
                    {
                        "status": False,
                        "description": "serv_id, cam_id, and status are required",
                    }
                ),
                400,
            )

        result = main_process.handle_camera(serv_id, cam_id, status)
        return jsonify(result)

    except Exception as e:
        log.error(f"Error in handle_camera: {e}")
        return jsonify({"status": False, "description": str(e)}), 500


@device_observer.route("/ping", methods=["GET"])
def ping():
    """Ping endpoint for health check and vendor server connection parameters"""
    try:
        # Get dynamic senderModuleId from ModuleIdService
        from app_va import main_process

        sender_id = 107  # Default fallback

        if hasattr(main_process, "module_id_service"):
            sender_id = main_process.module_id_service.get_sender_module_id()

        # Return vendor server connection parameters only
        return jsonify(
            {
                "status": True,
                "senderModuleId": sender_id,
                "vendor": "SentinelVA",
                "module": "Sentinel CONNECT",
                "version": "1.0.0",
                "vendor_server": {
                    "ip": main_process.initializer.server_api_addr,
                    "port": main_process.initializer.server_api_port,
                    "username": main_process.initializer.server_api_user,
                    "password": main_process.initializer.server_api_passw,
                },
            }
        )

    except Exception as e:
        log.error(f"Error in ping: {e}")
        return jsonify({"status": False, "description": str(e)}), 500


@device_observer.route("/status", methods=["GET"])
def status():
    """Get system status"""
    try:
        servers_status = []
        for serv_id, api_process in main_process.api_processes.items():
            controller = api_process.controller
            servers_status.append(
                {
                    "server_id": serv_id,
                    "server_name": (
                        controller.server.name if controller.server else "Unknown"
                    ),
                    "status": (
                        controller.server.status.value if controller.server else 0
                    ),
                    "cameras_count": len(controller.cameras),
                    "is_connected": api_process.is_connected,
                }
            )

        return jsonify(
            {
                "status": True,
                "servers": servers_status,
                "kafka_connected": main_process.kafka_client is not None,
                "websocket_connected": main_process.ws_client is not None
                and main_process.ws_client.is_running,
                "database_connected": False,  # No database in new architecture
            }
        )

    except Exception as e:
        log.error(f"Error in status: {e}")
        return jsonify({"status": False, "description": str(e)}), 500


# Backward compatibility endpoints
@device_observer.route("/api/lpr/save_event", methods=["POST"])
def lpr_save_event():
    """Backward compatibility endpoint for LPR save_event - redirects to Kafka"""
    try:
        data = request.get_json()
        if not data:
            return (
                jsonify({"status": False, "description": "JSON data is required"}),
                400,
            )

        # Convert old format to new event format
        event_data = {
            "detector_type": "LPR",
            "archive_id": data.get("device_id", 1),
            "event_time_begin": data.get("timestamp", ""),
            "event_detector_uuid": data.get("event_id", ""),
            "event_camera_name": data.get("camera_name", ""),
            "event_camera_uuid": data.get("camera_uuid", ""),
            "data": {
                "event_number": data.get("plate_number", ""),
                "event_track_id": data.get("track_id", ""),
                "event_score": data.get("confidence", 0.0),
                "event_number_status": data.get("plate_status", "unknown"),
            },
        }

        # Send to Kafka
        if main_process.message_producer:
            sender_id = main_process.module_id_service.get_sender_module_id()
            success = main_process.message_producer.send_lpr_event(
                sender_id, event_data
            )

            if success:
                return jsonify(
                    {"status": True, "description": "LPR event sent to Kafka"}
                )
            else:
                return (
                    jsonify(
                        {
                            "status": False,
                            "description": "Failed to send LPR event to Kafka",
                        }
                    ),
                    500,
                )
        else:
            return (
                jsonify(
                    {"status": False, "description": "Kafka producer not available"}
                ),
                500,
            )

    except Exception as e:
        log.error(f"Error in lpr_save_event: {e}")
        return jsonify({"status": False, "description": str(e)}), 500


@device_observer.route("/api/roi/save_event", methods=["POST"])
def roi_save_event():
    """Backward compatibility endpoint for ROI save_event - redirects to Kafka"""
    try:
        data = request.get_json()
        if not data:
            return (
                jsonify({"status": False, "description": "JSON data is required"}),
                400,
            )

        # Convert old format to new event format
        event_data = {
            "detector_type": "ROI",
            "archive_id": data.get("device_id", 1),
            "event_time_begin": data.get("timestamp", ""),
            "event_detector_uuid": data.get("event_id", ""),
            "event_camera_name": data.get("camera_name", ""),
            "event_camera_uuid": data.get("camera_uuid", ""),
            "data": {
                "event_class": {"name": data.get("object_type", "person")},
                "event_track_id": data.get("track_id", ""),
                "event_type": data.get("event_type", "detection"),
                "linked_zone": data.get("zones", []),
            },
        }

        # Send to Kafka
        if main_process.message_producer:
            sender_id = main_process.module_id_service.get_sender_module_id()
            success = main_process.message_producer.send_roi_event(
                sender_id, event_data
            )

            if success:
                return jsonify(
                    {"status": True, "description": "ROI event sent to Kafka"}
                )
            else:
                return (
                    jsonify(
                        {
                            "status": False,
                            "description": "Failed to send ROI event to Kafka",
                        }
                    ),
                    500,
                )
        else:
            return (
                jsonify(
                    {"status": False, "description": "Kafka producer not available"}
                ),
                500,
            )

    except Exception as e:
        log.error(f"Error in roi_save_event: {e}")
        return jsonify({"status": False, "description": str(e)}), 500


@device_observer.route("/api/modules/update_status", methods=["POST"])
def update_status():
    """Backward compatibility endpoint for update_status - redirects to Kafka"""
    try:
        data = request.get_json()
        if not data:
            return (
                jsonify({"status": False, "description": "JSON data is required"}),
                400,
            )

        device_id = data.get("device_id")
        unit_type_id = data.get("unit_type_id", 111)  # Default to device type
        status = data.get("status", 0)

        if not device_id:
            return (
                jsonify({"status": False, "description": "device_id is required"}),
                400,
            )

        # Send status update to Kafka
        if main_process.message_producer:
            sender_id = main_process.module_id_service.get_sender_module_id()
            success = main_process.message_producer.send_status_update(
                sender_module_id=sender_id,
                device_id=int(device_id),
                unit_type_id=int(unit_type_id),
                status=int(status),
            )

            if success:
                return jsonify(
                    {"status": True, "description": "Status update sent to Kafka"}
                )
            else:
                return (
                    jsonify(
                        {
                            "status": False,
                            "description": "Failed to send status update to Kafka",
                        }
                    ),
                    500,
                )
        else:
            return (
                jsonify(
                    {"status": False, "description": "Kafka producer not available"}
                ),
                500,
            )

    except Exception as e:
        log.error(f"Error in update_status: {e}")
        return jsonify({"status": False, "description": str(e)}), 500


@device_observer.route("/api/modules/save_log", methods=["POST"])
def save_log():
    """Backward compatibility endpoint for save_log - redirects to Kafka"""
    try:
        data = request.get_json()
        if not data:
            return (
                jsonify({"status": False, "description": "JSON data is required"}),
                400,
            )

        device_id = data.get("device_id")
        unit_type_id = data.get("unit_type_id", 111)  # Default to device type
        external_code_event = data.get("external_code_event", "SYSTEM_LOG")
        message = data.get("message", "")

        if not device_id:
            return (
                jsonify({"status": False, "description": "device_id is required"}),
                400,
            )

        # Send log message to Kafka
        if main_process.message_producer:
            sender_id = main_process.module_id_service.get_sender_module_id()
            success = main_process.message_producer.send_log_message(
                sender_module_id=sender_id,
                device_id=int(device_id),
                unit_type_id=int(unit_type_id),
                external_code_event=external_code_event,
                date=data.get("timestamp"),
                image_to_incident=data.get("image_path"),
            )

            if success:
                return jsonify(
                    {"status": True, "description": "Log message sent to Kafka"}
                )
            else:
                return (
                    jsonify(
                        {
                            "status": False,
                            "description": "Failed to send log message to Kafka",
                        }
                    ),
                    500,
                )
        else:
            return (
                jsonify(
                    {"status": False, "description": "Kafka producer not available"}
                ),
                500,
            )

    except Exception as e:
        log.error(f"Error in save_log: {e}")
        return jsonify({"status": False, "description": str(e)}), 500
