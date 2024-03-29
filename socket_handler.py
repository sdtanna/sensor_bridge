import logging
import json
import socketio
import numpy as np
import threading
import time


class socketHandeler():
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.logger.info("SocketIO initialized")
        self.sio_url = 'https://websocket-playground-9faa6ad4da71.herokuapp.com'
        self.sio = socketio.Client(reconnection=True, reconnection_attempts=0, reconnection_delay=1)
        self.connected = False
        self.sio.on('disconnect', self.disconnect)
        self.sio.on('reconnect', self.reconnect)    
 
    def init_socketIO(self):
        """ Connect to Socket.IO server """
        try:
            self.sio.connect(self.sio_url)
            self.connected = True
            self.logger.info(f"Connected to Socket.IO server at {self.sio_url}")
            self.start_heartbeat(interval=5)  # Start sending heartbeats every 5 seconds

        except Exception as e:
            self.logger.info(f"Failed to connect to Socket.IO: {e}")
    
    def disconnect(self):
        self.connected = False
        self.logger.info("Disconnected from Socket.IO server")
        self.logger.info("Attempting to reconnect...")

    def reconnect(self):
        self.connected = True
        self.logger.info("Reconnected to Socket.IO server")
    
    def convert_numpy_to_list(self, data):
        """ Convert all numpy arrays in the data to lists for JSON serialization """
        if isinstance(data, np.ndarray):
            return data.tolist()
        elif isinstance(data, dict):
            return {k: self.convert_numpy_to_list(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [self.convert_numpy_to_list(v) for v in data]
        else:
            return data

    def send_data_to_websocket(self, event, data):
        """ Send data to WebSocket server """
        if self.sio:
            try:
                self.sio.emit(event, data)
                self.logger.debug("Data sent to Socket.IO server")
            except Exception as e:

                self.logger.error(f"Error sending data to Socket.IO: {e}")

    def start_heartbeat(self, interval=5):
        """Start sending heartbeat messages at the given interval in seconds."""
        def heartbeat():
            while self.connected:
                try:
                    self.sio.emit('heartbeat', {'ping': '1'})
                    self.logger.debug("Heartbeat sent")
                except Exception as e:
                    self.logger.error(f"Failed to send heartbeat: {e}")
                    self.connected = False  # Assume disconnected and trigger reconnection logic
                time.sleep(interval)
                
        # Start the heartbeat in a separate thread to prevent blocking
        threading.Thread(target=heartbeat, daemon=True).start()
