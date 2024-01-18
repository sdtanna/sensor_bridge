import logging
import json
import socketio
import numpy as np


class socketHandeler():
    def __init__(self):
        self.sio_url = 'https://websocket-playground-9faa6ad4da71.herokuapp.com'
        self.sio = socketio.Client(reconnection=True, reconnection_attempts=5, reconnection_delay=1)
        self.connected = False
        self.sio.on('disconnect', self.disconnect)
        self.sio.on('reconnect', self.reconnect)
        self.logger = logging.getLogger(__name__)
        self.logger.info("SocketIO initialized")


        
    def init_socketIO(self):
        """ Connect to Socket.IO server """
        try:
            self.sio.connect(self.sio_url)
            self.connected = True
            self.logger.info(f"Connected to Socket.IO server at {self.sio_url}")
        except Exception as e:
            self.logger.info(f"Failed to connect to Socket.IO: {e}")
    
    def disconnect(self):
        self.connected = False
        self.logger.info("Disconnected from Socket.IO server")

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
                self.logger.info("Data sent to Socket.IO server")
            except Exception as e:

                self.logger.info(f"Error sending data to Socket.IO: {e}")
