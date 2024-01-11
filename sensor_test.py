import numpy as np
from parser import uartParser
import time
import socket_handler as socket_handler 
import logging
from datetime import datetime
from threading import Thread

CLI_COM_PORT = "/dev/tty.SLAB_USBtoUART3"
DATA_COM_POROT = "/dev/tty.SLAB_USBtoUART"

sh = socket_handler.socketHandeler(logger = None)
sh.init_socketIO()
parser = uartParser(type="3D People Tracking", socket_handler = sh, logger= None)
with open("ISK_6m_default.cfg", 'r') as cfg_file:
            cfg = cfg_file.readlines()
parser.connectComPorts(CLI_COM_PORT, DATA_COM_POROT)

def write_line(parser,line):
    parser.sendLine(line)