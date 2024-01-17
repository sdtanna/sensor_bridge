import numpy as np
from parser import uartParser
import time
import socket_handler as socket_handler 
import logging
from datetime import datetime
from threading import Thread
import socket_logger
import signal
import atexit

class Sensor():
        
    FPS = 16  # Set the desired frame time
    CLI_COM_PORT = "/dev/ttyUSB0"
    DATA_COM_PORT = "/dev/ttyUSB1"

    def __init__(self):
        #Iniitalize socket handler
        #console_logger
        self.logger = logging.getLogger(__name__)

        c_handler = logging.StreamHandler()
        c_handler.setLevel(logging.INFO)
        self.logger.addHandler(c_handler)

        #file_logger
        f_handler = logging.FileHandler('{:%Y-%m-%d}_sensor_setup.log'.format(datetime.now()))
        f_handler.setLevel(logging.DEBUG)
        self.logger.addHandler(f_handler)
        self.logger.setLevel(logging.INFO)
        self.logger.info("Logger initialized")

        self.sh = socket_handler.socketHandeler()
        self.sh.init_socketIO()
        self.logger.info("SocketIO initialized")
        # register event handlers for commands from the server
        self.sh.sio.on('command', self.sensor_cmd)
    
        self.is_running = True

        atexit.register(self.sensor_stop)
        signal.signal(signal.SIGINT, self.sensor_stop)
        signal.signal(signal.SIGTERM, self.sensor_stop)

        self.logger.info("Initializing Sensor")

        self.parser = uartParser(type="3D People Tracking", socket_handler = self.sh)

        try:
            self.parser.connectComPorts(self.CLI_COM_PORT, self.DATA_COM_PORT)
            self.logger.info('Connected to COM ports')
        except Exception as e:
            self.logger.error(f"Error connecting to COM ports: {e}")

    def start(self):
        self.logger.info("Starting Sensor")
        
        
        with open("ISK_6m_default.cfg", 'r') as cfg_file:
                self.cfg = cfg_file.readlines()
        self.logger.info("sending cfg")
        self.parser.sendCfg(self.cfg)

        self.logger.info("entering main loop")
        parser_thread = Thread(target=self.parse_data, daemon=True)
        parser_thread.start()
        while True:
            logging.debug("running")
            time.sleep(1)
    def parse_data(self):
        while self.is_running:
            try:
                self.parser.readAndParseUartDoubleCOMPort()
            except Exception as e:
                self.logger.error(f"Error reading and parsing UART: {e}")
            time.sleep(1/self.FPS)


    def sensor_stop(self):
        self.logger.info("Stopping Sensor")
        self.parser.sendLine("resetDevice\n")
        self.logger.info("Sensor Stopped")

    def sensor_cmd(self, data):
        command = data['data']

        if command == 'startSensor':
            # Code to handle startSensor command
            self.parser.sendLine("sensorStart 0\n")

        elif command == 'stopSensor':
            # Code to handle stopSensor command
            self.parser.sendLine("sensorStop\n")

        elif command == 'resetSensor':
            self.parser.sendLine("resetDevice\n")
        
        elif command == 'cfg':
            self.parser.sendCfg(self.cfg)
        else:
            # Code to handle other commands
            print(f"Received command: {command}")
    
            

    # sensor_response
if __name__ == "__main__":
    sensor = Sensor()
    sensor.start()

