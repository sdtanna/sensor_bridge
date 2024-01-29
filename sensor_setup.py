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
import subprocess

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

        self.initialize_sensor()
        self.is_running = True
        self.sensor_powered = True  # Add a state variable for the sensor's power state

        atexit.register(self.sensor_stop)
        signal.signal(signal.SIGINT, self.sensor_stop)
        signal.signal(signal.SIGTERM, self.sensor_stop)

        self.logger.info("Initializing Sensor")

        self.parser = uartParser(self.CLI_COM_PORT, self.DATA_COM_PORT, type="3D People Tracking", socket_handler = self.sh)

        try:
            self.parser.connectComPorts(self.CLI_COM_PORT, self.DATA_COM_PORT)
            self.logger.info('Connected to COM ports')
        except Exception as e:
            self.logger.error(f"Error connecting to COM ports: {e}")

    def initialize_sensor(self):
        self.logger.info("Initializing Sensor")
        self.parser = uartParser(self.CLI_COM_PORT, self.DATA_COM_PORT, type="3D People Tracking", socket_handler = self.sh)
        time.sleep(10)  # Wait for the sensor to be ready
        self.parser.connectComPorts(self.CLI_COM_PORT, self.DATA_COM_PORT)  # Call connect_com_ports on the new parser object

    def connect_com_ports(self):
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
        try:
            self.parser.sendCfg(self.cfg)
        except Exception as e:
            self.logger.error(f"Error in sendCfg: {e}")
        self.logger.info("entering main loop")
        parser_thread = Thread(target=self.parse_data)
        parser_thread.start()
        parser_thread.join()

    def parse_data(self):
        while self.is_running:
            if self.sensor_powered:  # Only read from UART if sensor is powered
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
        self.sensor_cmd({'data': 'stopSensor'})  # Stop the sensor
        self.sensor_powered = False  # Set sensor_powered to False before turning off power to disallow UART reading
        # Turn off power to USB port
        self.logger.info("Beginning Restart")
        time.sleep(2)   #Ensure Sensor is stopped
        result = subprocess.run(['sudo', 'uhubctl', '-l', '2', '-a', '0'], capture_output=True)
        self.logger.info(f"Power off result: {result.stdout}, {result.stderr}")
        time.sleep(5)
        # Turn power back on
        result = subprocess.run(['sudo', 'uhubctl', '-l', '2', '-a', '1'], capture_output=True)
        self.logger.info(f"Power on result: {result.stdout}, {result.stderr}")
        
        time.sleep(10)  # Wait for the sensor to be ready
        self.logger.info("20 Seconds Left")
        time.sleep(10)  # Wait for the sensor to be ready
        self.logger.info("10 Seconds Left")
        time.sleep(5)  # Wait for the sensor to be ready
        self.logger.info("5 Seconds Left")
        time.sleep(5)  # Wait for the sensor to be ready
        self.logger.info("Reinitializing")

        self.initialize_sensor()  # Reinitialize the sensor
        self.start()  # Start the sensor

        self.sensor_powered = True  # Set sensor_powered back to True after turning power back on to allow UART reading

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