import numpy as np
from parser import uartParser
import time

# Configuration
frame_time = 30  # Set the desired frame time

class SensorParser:
    def __init__(self, cfg):
        self.parser = uartParser(type="3D People Tracking")
        self.cfg = cfg

    def connectComPorts(self, cli_com_port, data_com_port):
        try:
            self.parser.connectComPorts(cli_com_port, data_com_port)
            print('Connected')
            return True
        except Exception as e:
            print(f"Error connecting to COM ports: {e}")
            return False
   
    def sendCfg(self):
        self.parser.sendCfg(self.cfg)

    def readData(self):
        # Read data from the sensor. Implement this based on your sensor's protocol.
            print(self.parser.readAndParseUartDoubleCOMPort())


# Main script
def main():
    with open("ISK_6m_default.cfg", 'r') as cfg_file:
            cfg = cfg_file.readlines()
    parser = SensorParser(cfg)

    # Read configuration file

    # Connect to sensor

    if not parser.connectComPorts("/dev/ttyUSB0", "/dev/ttyUSB1"):
    # if not parser.connectComPorts("/dev/tty.SLAB_USBtoUART3", "/dev/tty.SLAB_USBtoUART"):
        print("Failed to connect to the sensor.")
        return

    # Send configuration to sensor
    parser.sendCfg()
    # Start reading data
    while True:
        parser.readData()
        time.sleep(frame_time / 1000)

if __name__ == "__main__":
    main()
