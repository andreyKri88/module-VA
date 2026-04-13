# Controller VA - Unified Video Analytics Controller

## Overview

Controller VA - this is a unified system that combines the functionality of both controller-lpr and controller-roi-master into a single project. It provides integration with Kafka for message processing and WebSocket for real-time event handling, operating completely without database dependencies.

## Features

- **Unified Controller**: Combines LPR (License Plate Recognition) and ROI (Region of Interest) functionality
- **Kafka Integration**: Sends status updates, logs, and events to Kafka topics
- **WebSocket Support**: Subscribes to real-time events from video analytics servers
- **Database-Free Architecture**: No database dependencies - configuration loaded from JSON files
- **REST API**: HTTP endpoints for device management and status monitoring

## Configuration

### Settings.ini

The main configuration file `settings.ini` contains the following sections:

```ini
[ServerAPI]
port_server=600
module_name=Sentinel CONNECT
vendor_name=SentinelVA
server_api_addr=127.0.0.1
server_api_port=3055
server_api_user=admin
server_api_passw=1e6e282c1eabcd366f4248e3d5173c97
timer=3
event_timer_delay=10
event_array_length_max=3
time_between_sending_events=3

[Kafka]
kafka.ip=127.0.0.1
kafka.port=9092
kafka.group-id=sentinelVAModule

[WebSocket]
ws_url=wss://127.0.0.1:600/api/events/ws_events

[Devices]
# Device configuration will be loaded from external source or config file
# Format: device_uuid=device_id,unit_type_id
```

### Device Configuration

Device configuration is loaded from `devices.json` file. This file contains server and camera definitions without requiring a database:

```json
{
  "servers": {
    "1": {
      "id_serv": "1",
      "ext_id": "server_001",
      "name": "VA Server 1",
      "ip_address": "127.0.0.1",
      "port": 600,
      "status": 1,
      "id_type_unit": "110"
    }
  },
  "cameras": {
    "1": {
      "1": {
        "id_device": "1",
        "ext_id": "camera_001",
        "name": "VA Camera 1",
        "camera_uuid": "675a1fb7-f926-4972-8957-c64f715a4015",
        "ip_address": "127.0.0.1",
        "port": 8080,
        "status": 1,
        "id_type_unit": "111",
        "id_serv": "1"
      }
    }
  }
}
```

## Architecture

### Updated Constants

- **Id_vendor**: 69
- **typeunit server**: 110 (replaces 54, 95)
- **typeunit device**: 111 (replaces 55, 96)
- **senderModuleId**: 107

### Kafka Topics

1. **status-log**: For device status updates and log messages
2. **code-incident-33-event**: For ROI and LPR events

### WebSocket Events

The system subscribes to `wss://ip:port/api/events/ws_events` and processes events based on `detector_type`:

- **ROI Events**: Person detection, zone violations
- **LPR Events**: License plate recognition

## API Endpoints

### Device Management

- `GET /camera/get_all_cameras?serv_id={id}` - Get all cameras for a server
- `GET /camera/get_api_cameras?serv_id={id}` - Get API cameras for a server
- `POST /camera/handle_camera` - Handle camera status change

### System Endpoints

- `GET /ping` - Health check and senderModuleId
- `GET /status` - System status overview

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure `settings.ini` with your database and Kafka settings

3. Run the application:
```bash
python run_server.py
```

## Docker Deployment

```bash
docker build -t controller-va .
docker run -p 600:600 controller-va
```

## Event Processing

### ROI Event Example
```json
{
    "detector_type": "ROI",
    "event_camera_uuid": "camera-uuid",
    "event_time_begin": "2025-08-05T08:22:52.000000Z",
    "data": {
        "event_class": {"name": "person"},
        "event_track_id": "track-id",
        "event_type": "exit"
    }
}
```

### LPR Event Example
```json
{
    "detector_type": "LPR",
    "event_camera_uuid": "camera-uuid",
    "event_time_begin": "2025-08-05T08:32:28.000000Z",
    "data": {
        "event_number": "176TX7",
        "event_track_id": "track-id",
        "event_score": 0.892912
    }
}
```

## Migration Notes

This unified controller replaces:
- `controller-lpr` (port 596, typeunit 95/96)
- `controller-roi-master` (port 593, typeunit 54/55)

All existing functionality has been consolidated with the new typeunit mapping:
- Old server types (54, 95) -> New server type (110)
- Old device types (55, 96) -> New device type (111)

## Logging

The application uses structured logging with both console and file output. Logs are stored in the `logs/` directory with rotation to prevent disk space issues.
