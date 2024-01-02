import numpy as np
from parser import uartParser
import time
import socket_handler as socket_handler 
import logging
from datetime import datetime
from threading import Thread


# Configuration
FRAME_TIME = 30  # Set the desired frame time
CLI_COM_PORT = "/dev/tty.SLAB_USBtoUART3"
DATA_COM_POROT = "/dev/tty.SLAB_USBtoUART"




logger = logging.getLogger(__name__)

# Create handlers
import socket_logger
s_handler = socket_logger.socket_logger()
c_handler = logging.StreamHandler()
f_handler = logging.FileHandler('{:%Y-%m-%d}_sensor_setup.log'.format(datetime.now()))
c_handler.setLevel(logging.INFO)
f_handler.setLevel(logging.DEBUG)
s_handler.setLevel(logging.INFO)

# Create formatters and add it to handlers
c_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
f_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
s_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
c_handler.setFormatter(c_format)
f_handler.setFormatter(f_format)
s_handler.setFormatter(s_format)


# Add handlers to the logger
logger.addHandler(c_handler)
logger.addHandler(f_handler)
logger.addHandler(s_handler)


logger.warning('This is a warning')
logger.error('This is an error')

is_running = True
# Main script
def main():

    socket_handler = socket_handler.socketHandeler(logger = None)
    socket_handler.init_socketIO()
    
    parser = uartParser(type="3D People Tracking", socket_handler = socket_handler)

    try:
        parser.connectComPorts(CLI_COM_PORT, DATA_COM_POROT)
        print('Connected')
    except Exception as e:
        print(f"Error connecting to COM ports: {e}")

    with open("ISK_6m_default.cfg", 'r') as cfg_file:
            cfg = cfg_file.readlines()
    parser.sendCfg(cfg)

    reader_thread = Thread(target=read_data, args=[parser])
    reader_thread.run()
    reader_thread.join()

def read_data(parser):

    while is_running:
        print(parser.readAndParseUartDoubleCOMPort())
        time.sleep(FRAME_TIME / 1000)
    

def write_line(parser,line):
    parser.sendLine(line)

def stop_reading():
    global is_running
    is_running = False
    
if __name__ == "__main__":
    main()


