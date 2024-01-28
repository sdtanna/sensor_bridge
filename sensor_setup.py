import numpy as np
from parser import uartParser
import time
import socket_handler as socket_handler 
import logging
import logging.config
from datetime import datetime
from threading import Thread
import socket_logger
import signal
import atexit
import os

class Sensor():
        
    FPS = 16  # Set the desired frame time
    CLI_COM_PORT = "/dev/ttyUSB0"
    DATA_COM_PORT = "/dev/ttyUSB1"

    def __init__(self):
        #Iniitalize socket handler
        #console_logger
        logging.config.fileConfig('logging.conf')
        self.logger = logging.getLogger(__name__)
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
        parser_thread = Thread(target=self.parse_data)
        parser_thread.start()
        parser_thread.join()
    def parse_data(self):
        while self.is_running:
            try:
                self.parser.readAndParseUartDoubleCOMPort()
            except Exception as e:
                self.logger.error(f"Error reading and parsing UART: {e}")
            time.sleep(1/self.FPS)


    def sensor_stop(self, signum=None, frame=None):
        self.is_running = False
        self.sh.sio.disconnect()
        self.logger.info("Stopping Sensor")
        self.parser.sendLine("resetDevice\n")
        self.logger.info("Sensor Stopped")
    
    def restartSensor(self):
        # Turn off power to all USB ports
        os.system("sudo ./hub-ctrl -h 0 -P 2 -p 0")
        self.logger.info(f"Restarting, Eliminating Power to Sensor")
        # Wait for 10 seconds
        time.sleep(10)
        # Turn power back on
        os.system("sudo ./hub-ctrl -h 0 -P 2 -p 1")
        self.logger.info(f"Restart Complete, Power Re-Initiated")
        

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

        elif command == 'restartSensor':
            self.restartSensor()
        else:
            # Code to handle other commands
            self.logger.info(f"Received command: {command}")
    
            

    # sensor_response
if __name__ == "__main__":
    sensor = Sensor()
    sensor.start()

