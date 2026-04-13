import asyncio
import json
import websockets
import threading
from typing import Callable, Optional
from websockets.exceptions import ConnectionClosed, WebSocketException
from app_va import log


class WebSocketClient:
    def __init__(self, ws_url: str, event_processor: Callable):
        self.ws_url = ws_url
        self.event_processor = event_processor
        self.websocket: Optional[websockets.WebSocketServerProtocol] = None
        self.is_running = False
        self.reconnect_interval = 5  # seconds
        self.thread: Optional[threading.Thread] = None
    
    def start(self):
        """Start WebSocket client in a separate thread"""
        if self.is_running:
            log.warning("WebSocket client is already running")
            return
        
        self.is_running = True
        self.thread = threading.Thread(target=self._run_client, daemon=True)
        self.thread.start()
        log.info(f"WebSocket client started for {self.ws_url}")
    
    def stop(self):
        """Stop WebSocket client"""
        self.is_running = False
        if self.websocket:
            asyncio.run_coroutine_threadsafe(self.websocket.close(), self.loop)
        if self.thread:
            self.thread.join(timeout=5)
        log.info("WebSocket client stopped")
    
    def _run_client(self):
        """Run WebSocket client with event loop"""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        
        try:
            self.loop.run_until_complete(self._connect_and_listen())
        except Exception as e:
            log.error(f"WebSocket client error: {e}")
        finally:
            self.loop.close()
    
    async def _connect_and_listen(self):
        """Connect to WebSocket and listen for messages"""
        while self.is_running:
            try:
                log.info(f"Connecting to WebSocket: {self.ws_url}")
                
                async with websockets.connect(
                    self.ws_url,
                    ping_interval=20,
                    ping_timeout=10,
                    close_timeout=10
                ) as websocket:
                    self.websocket = websocket
                    log.info("WebSocket connected successfully")
                    
                    async for message in websocket:
                        if not self.is_running:
                            break
                        
                        try:
                            await self._process_message(message)
                        except Exception as e:
                            log.error(f"Error processing WebSocket message: {e}")
                            continue
                        
            except ConnectionClosed as e:
                log.warning(f"WebSocket connection closed: {e}")
            except WebSocketException as e:
                log.error(f"WebSocket error: {e}")
            except Exception as e:
                log.error(f"Unexpected WebSocket error: {e}")
            
            if self.is_running:
                log.info(f"Reconnecting in {self.reconnect_interval} seconds...")
                await asyncio.sleep(self.reconnect_interval)
    
    async def _process_message(self, message: str):
        """Process incoming WebSocket message"""
        try:
            event_data = json.loads(message)
            
            # Validate message structure
            if not isinstance(event_data, dict):
                log.warning(f"Invalid message format: {message}")
                return
            
            # Check if it's an event message
            if 'detector_type' not in event_data:
                log.debug(f"Non-event message received: {event_data}")
                return
            
            # Process event in thread pool to avoid blocking WebSocket
            await asyncio.get_event_loop().run_in_executor(
                None, self.event_processor, event_data
            )
            
        except json.JSONDecodeError as e:
            log.error(f"Failed to parse JSON message: {e}")
        except Exception as e:
            log.error(f"Error processing message: {e}")
