# Deployment Instructions

## GitHub Repository Setup

### 1. Clone the Repository
```bash
git clone https://github.com/andreyKri88/module-VA.git
cd module-VA
```

### 2. Copy Project Files
```bash
# Copy all files from controller-va to the repository
cp -r /path/to/controller-va/* .
```

### 3. Initialize Git Repository
```bash
git init
git add .
git commit -m "Initial commit: Unified Video Analytics Controller"
```

### 4. Add Remote and Push
```bash
git remote add origin https://github.com/andreyKri88/module-VA.git
git branch -M main
git push -u origin main
```

## Project Structure
```
module-VA/
|-- README.md                    # Project documentation
|-- requirements.txt             # Python dependencies
|-- run_server.py               # Entry point
|-- settings.ini                # Configuration
|-- devices.json                # Device configuration
|-- Dockerfile                  # Docker configuration
|-- .gitignore                  # Git ignore rules
|-- app_va/                     # Main application
|   |-- __init__.py
|   |-- main_process.py         # Main process logic
|   |-- blueprints.py           # API endpoints
|   |-- services/               # Services
|   |   |-- module_id_service.py
|   |   |-- config_validator.py
|   |   |-- parse_settings/
|   |   |-- initialize_class.py
|   |-- models/                  # Data models
|   |-- kafka/                   # Kafka integration
|   |-- websocket/              # WebSocket integration
|   `-- api_process.py          # API processing
`-- DEPLOYMENT.md               # This file
```

## Docker Deployment

### Build and Run
```bash
# Build Docker image
docker build -t controller-va .

# Run container
docker run -d \
  --name controller-va \
  -p 600:600 \
  -v $(pwd)/settings.ini:/app/settings.ini \
  -v $(pwd)/devices.json:/app/devices.json \
  controller-va
```

### Docker Compose
```yaml
version: '3.8'
services:
  controller-va:
    build: .
    ports:
      - "600:600"
    volumes:
      - ./settings.ini:/app/settings.ini
      ./devices.json:/app/devices.json
    environment:
      - PYTHONPATH=/app
    depends_on:
      - kafka
      - redis

  kafka:
    image: confluentinc/cp-kafka:latest
    ports:
      - "9092:9092"
    environment:
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://localhost:9092
      KAFKA_ZOOKEEPER_CONNECT: localhost:2181

  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
```

## Environment Setup

### Prerequisites
- Python 3.8+
- Kafka broker
- WebSocket server (optional)

### Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Copy configuration files
cp settings.ini.example settings.ini
cp devices.json.example devices.json

# Edit configuration
nano settings.ini
nano devices.json
```

### Running the Application
```bash
# Development mode
python run_server.py

# Production mode (with Gunicorn)
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:600 run_server:app_run
```

## Configuration

### Settings.ini
```ini
[ServerAPI]
port_server=600
module_name=Sentinel CONNECT
vendor_name=SentinelVA
server_api_addr=127.0.0.1
server_api_port=3055
server_api_user=admin
server_api_passw=your_password
timer=30
event_timer_delay=10
event_array_length_max=3
time_between_sending_events=3

[Kafka]
kafka.ip=127.0.0.1
kafka.port=9092
kafka.group-id=sentinelVAModule

[WebSocket]
ws_url=wss://127.0.0.1:8080/api/events/ws_events

[Events]
event_types={"event": null}

[Devices]
# Device configuration will be loaded from external source or config file
```

### Devices.json
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

## API Endpoints

### Health Check
```bash
curl http://localhost:600/ping
```

### Device Management
```bash
# Get all cameras
curl http://localhost:600/camera/get_all_cameras?serv_id=1

# Handle camera status
curl -X POST http://localhost:600/camera/handle_camera \
  -H "Content-Type: application/json" \
  -d '{"serv_id": "1", "cam_id": "1", "status": "1"}'
```

### Backward Compatibility
```bash
# LPR events (legacy)
curl -X POST http://localhost:600/api/lpr/save_event \
  -H "Content-Type: application/json" \
  -d '{"device_id": 1, "plate_number": "ABC123"}'

# ROI events (legacy)
curl -X POST http://localhost:600/api/roi/save_event \
  -H "Content-Type: application/json" \
  -d '{"device_id": 1, "object_type": "person"}'
```

## Monitoring

### Logs
```bash
# View application logs
docker logs controller-va

# Follow logs in real-time
docker logs -f controller-va
```

### Health Monitoring
```bash
# Check system status
curl http://localhost:600/status

# Check Kafka connectivity
curl http://localhost:600/ping
```

## Troubleshooting

### Common Issues

1. **Kafka Connection Failed**
   - Check Kafka broker is running
   - Verify IP and port in settings.ini
   - Check network connectivity

2. **WebSocket Connection Failed**
   - Verify WebSocket URL is correct
   - Check firewall settings
   - Ensure WebSocket server is accessible

3. **Configuration Validation Failed**
   - Check devices.json format
   - Verify required fields are present
   - Check typeunit values (110 for servers, 111 for devices)

4. **Module ID Service Error**
   - Verify server_api_addr and server_api_port
   - Check external server accessibility
   - Review ping endpoint response

### Debug Mode
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python run_server.py
```

## Security Considerations

- Change default passwords in production
- Use HTTPS for WebSocket connections
- Implement proper authentication for API endpoints
- Regularly update dependencies
- Use environment variables for sensitive data
