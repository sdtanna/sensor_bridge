# ----- Imports -------------------------------------------------------

# Standard Imports
import logging
import struct
import serial
import time
import numpy as np
import math
import datetime


 

# Local Imports
from parseFrame import *

#Initialize this Class to create a UART Parser. Initialization takes one argument:
# 1: String Lab_Type - These can be:
#   a. 3D People Tracking
#   b. SDK Out of Box Demo
#   c. Long Range People Detection
#   d. Indoor False Detection Mitigation
#   e. (Legacy): Overhead People Counting
#   f. (Legacy) 2D People Counting
# Default is (f). Once initialize, call connectComPorts(self, cliComPort, DataComPort) to connect to device com ports.
# Then call readAndParseUart() to read one frame of data from the device. The gui this is packaged with calls this every frame period.
# readAndParseUart() will return all radar detection and tracking information.
class uartParser():
    def __init__(self,type='SDK Out of Box Demo', socket_handler = None):
        # Set this option to 1 to save UART output from the radar device
        self.socket_handler = socket_handler
        self.saveBinary = 0
        self.replay = 0
        self.binData = bytearray(0)
        self.uartCounter = 0
        self.framesPerFile = 100
        self.first_file = True

        self.logger = logging.getLogger(__name__)
        self.logger.info("Logger initialized")


        self.filepath = datetime.datetime.now().strftime("%m_%d_%Y_%H_%M_%S")

            
        
        self.parserType = "DoubleCOMPort"

        # Data storage
        self.now_time = datetime.datetime.now().strftime('%Y%m%d-%H%M')
        
    
    def readAndParseUartDoubleCOMPort(self):
        self.fail = 0
        if self.replay:
            return self.replayHist()

        # Magic word detection
        magicWordLength = len(UART_MAGIC_WORD)
        foundMagicWord = False
        magicWordBuffer = bytearray(magicWordLength)

        while not foundMagicWord:
            byte = self.dataCom.read(1)

            if len(byte) < 1:
                continue

            magicWordBuffer.pop(0)
            magicWordBuffer.append(byte[0])

            if bytes(magicWordBuffer) == UART_MAGIC_WORD:
                foundMagicWord = True

        frameData = bytearray(magicWordBuffer)

        # Read version and length
        frameData += self.dataCom.read(8)
        frameLength = int.from_bytes(frameData[-4:], byteorder='little')

        # Read the rest of the frame
        frameLength -= 16  # Adjust for the already read bytes
        frameData += self.dataCom.read(frameLength)

        # Parse frame data
        try:
            if self.parserType == "DoubleCOMPort":
                outputDict = parseStandardFrame(frameData)
            else:
                self.logger.error('FAILURE: Bad parserType')
                return

            data = self.socket_handler.convert_numpy_to_list(outputDict)
            self.socket_handler.send_data_to_websocket("sensor_datapacket_1", data)

            return outputDict
        except Exception as e:
            self.logger.error(f"Error parsing frame: {e}")

   
            
  
    # Find various utility functions here for connecting to COM Ports, send data, etc...
    # Connect to com ports
    # Call this function to connect to the comport. This takes arguments self (intrinsic), cliCom, and dataCom. No return, but sets internal variables in the parser object.
    def connectComPorts(self, cliCom, dataCom):
        self.cliCom = serial.Serial(cliCom, 115200, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE,timeout=1)
        self.dataCom = serial.Serial(dataCom, 921600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, timeout=1)
        self.dataCom.reset_output_buffer()
        self.logger.info('Connected')
    
    #send cfg over uart
    def sendCfg(self, cfg):
        for i, line in enumerate(cfg):
            if(line == '\n'):
                cfg.remove(line)
            elif(line[-1] != '\n'):
                cfg[i] = cfg[i] + '\n'
        for line in cfg:
            time.sleep(.1) # Line delay
            try:
                if(self.cliCom.baudrate == 1250000):
                    for char in [*line]:
                        time.sleep(.01) # Character delay. Required for demos which are 1250000 baud by default else characters are skipped
                        self.cliCom.write(char.encode())
                else:
                    self.cliCom.write(line.encode())
                ack = self.cliCom.readline()
                self.logger.info(ack)
                ack = self.cliCom.readline()
                self.logger.info(ack)
                splitLine = line.split()
                if(splitLine[0] == "baudRate"): # The baudrate CLI line changes the CLI baud rate on the next cfg line to enable greater data streaming off the IWRL device.
                    try:
                        self.cliCom.baudrate = int(splitLine[1])
                    except:
                        self.logger.error("Invalid baud rate")
                        sys.exit(1)
            except Exception as e:
                self.logger.error(f"Error in sendCfg loop: {e}")
        time.sleep(0.1)
        self.cliCom.reset_input_buffer()


    #send single command to device over UART Com.
    def sendLine(self, line):
        self.cliCom.write(line.encode())
        time.sleep(.1)
        ack = self.cliCom.readline()

        self.logger.info(ack)
        time.sleep(.1)

        ack = self.cliCom.readline()
        time.sleep(.1)

        self.logger.info(ack)
        time.sleep(.1)

        
def getBit(byte, bitNum):
    mask = 1 << bitNum
    if (byte&mask):
        return 1
    else:
        return 0
