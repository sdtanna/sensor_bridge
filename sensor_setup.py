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
    
        self.is_running = True
        self.is_powered = True

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
            if self.is_powered:
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
        #Stop Sensor Communications & UART Reading
        self.logger.info("Beginning Restart")
        self.is_powered = False                                             #Set is_running back to False after turning power back on to allow UART reading
        time.sleep(1)
        self.sensor_cmd({'data': 'stopSensor'})                             #Stop the sensor
        self.logger.info("Sensor Stopped Successfully")
        time.sleep(5)
        self.logger.info("Attempting to Disconnect COM Ports")
        self.parser.disconnectComPorts()                                    #Disconnect the Com Ports
        self.logger.info("Both COM Ports Disconnected")
        time.sleep(5)                                                       #Ensure Sensor is stopped

        #Turn off power to USB port
        self.logger.info("Turning USB Power OFF")
        subprocess.run(['sudo', 'uhubctl', '-l', '2', '-a', '0'])           #Turn Power Off
        self.logger.info("10 Seconds Left")
        time.sleep(10)                                                      #Wait 10 Seconds
        self.logger.info("Reboot Complete, Turning USB Power ON")       

        #Turn USB power back on
        subprocess.run(['sudo', 'uhubctl', '-l', '2', '-a', '1'])           #Turn Power Back On
        self.logger.info("Power Re-Initialized, Please Wait 10 Seconds")    #Wait 30 Seconds
        time.sleep(5)                                                       #Wait for the sensor to be ready
        self.logger.info("5 Seconds Left")
        time.sleep(5)
        self.logger.info("Re-starting the Sensor Up")

        #Re-Connect to COM Ports
        try:
            self.parser.connectComPorts(self.CLI_COM_PORT, self.DATA_COM_PORT)
            self.logger.info('Connected to COM ports')
        except Exception as e:
            self.logger.error(f"Error connecting to COM ports: {e}")

        #Start Sensor Communications and UART Reading
        self.start()                                                        #Start up the Sensor again
        self.logger.info("Sensor Restart Completed SUCCESSFULLY")
        self.is_powered = True                                              #Set is_running back to True after turning power back on to allow UART reading

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