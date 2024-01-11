import numpy as np
from parser import uartParser
import time
import socket_handler as socket_handler 
import logging
from datetime import datetime
from threading import Thread
import socket_logger
import atexit

class Sensor():
        
    FPS = 15  # Set the desired frame time
    CLI_COM_PORT = "/dev/tty.SLAB_USBtoUART"
    DATA_COM_PORT = "/dev/tty.SLAB_USBtoUART3"

    def __init__(self):
        #Iniitalize socket handler
        self.sh = socket_handler.socketHandeler()
        self.sh.init_socketIO()
        # register event handlers for commands from the server
        self.sh.sio.on('start_sensor1', self.sensor_start)
        self.sh.sio.on('stop_sensor1', self.sensor_stop)
        self.sh.sio.on('reset_sensor1', self.sensor_reset)

        self.logger = logging.getLogger(__name__)

        atexit.register(self.sensor_stop)

        

        #socket logger
        if self.sh.connected:
            s_handler = socket_logger.socket_logger(self.sh)
            s_handler.setLevel(logging.INFO)
            self.logger.addHandler(s_handler)


        #console_logger
        c_handler = logging.StreamHandler()
        c_handler.setLevel(logging.INFO)
        self.logger.addHandler(c_handler)

        #file_logger
        f_handler = logging.FileHandler('{:%Y-%m-%d}_sensor_setup.log'.format(datetime.now()))
        f_handler.setLevel(logging.DEBUG)
        self.logger.addHandler(f_handler)
        self.logger.setLevel(logging.INFO)
        self.logger.info("Logger initialized")
        self.logger.info("Initializing Sensor")
        self.parser = uartParser(type="3D People Tracking", socket_handler = self.sh, logger= self.logger)

        try:
            self.parser.connectComPorts(self.CLI_COM_PORT, self.DATA_COM_PORT)
            self.logger.info('Connected')
        except Exception as e:
            self.logger.error(f"Error connecting to COM ports: {e}")

    def start(self):
        self.logger.info("Starting Sensor")
        
        
        with open("ISK_6m_default.cfg", 'r') as cfg_file:
                self.cfg = cfg_file.readlines()
        self.logger.info("sending cfg")
        self.parser.sendCfg(self.cfg)

        self.logger.info("entering main loop")
        while True:

            self.parser.readAndParseUartDoubleCOMPort()
            time.sleep(1/self.FPS)


    def sensor_stop(self):
        self.parser.sendLine("sensorStop\n")
        self.sensor_reset()
    def sensor_reset(self):
        self.parser.sendLine("resetDevice\n")
    def sensor_start(self):
        self.parser.sendCfg(self.cfg)

if __name__ == "__main__":
    sensor = Sensor()
    sensor.start()

