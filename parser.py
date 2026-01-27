import serial
from struct import unpack
from threading import Lock
from datetime import datetime
import os
from time import sleep


dataTagDict = { 
  "TEMPERATURE_INTERNAL":   0x0001,
  "TEMPERATURE":            0x0002,
  "PRESSURE":               0x0003,
  "WIND_SPEED":             0x0004,
  "RAIN_LEVEL":             0x0005,
  "HUMIDITY":               0x0006,
  "TIMESTAMP":              0x0007,
  "NONE":                   0xFFFF
}
BUFFER_INIT_VALUE = b'254' # Value to fill in buffer at startup with. BUFFER_INIT_VALUE is not a DataTag or any other frame control value, to avoid false detection at startup

UART_DATA_MAX_SIZE = 256

MAX_DELAY_TO_RECEIVE_DATA = 10
DEVBYPASS_COMPORT = "COM9"

class Parser:

    def __init__(self):
        
        self.ser = None
        # Uart buffer
        #s = list(bytearray(UART_DATA_MAX_SIZE)) # Warning this will do a list of UART_DATA_MAX_SIZE integer, list converts bytes into int!
        self.newData = False
        self.newDataConsumed = False
        self.dataReal = None
        self.dataTag = None
        self.bufferPtr = 0
        self.data_lock = Lock()


    def parse_data(self):
        # Read data coming from STM32 Nucleo UART2 through serial port
        self.ser = self.connectToSerial()

        s = [BUFFER_INIT_VALUE] * UART_DATA_MAX_SIZE #same as above but maybe less confusing. 
        i = 0
        getDataTag = False
        getDataSize = False
        getData = False
        data = []
        dataByteCounter = 0
        dataSize = 0
        dataTag = None
        dataReal = None

        while(True):

            # first implementation NOT very robust because datatag could be confused with data (1/65536 probability)
            # Frame format: DataTag (2 bytes) | DataSize (1 byte) | Data (DataSize byte(s))

            #To manage special case where the last byte of the buffer is the first byte of the DataTag and the first byte of the buffer the second byte of the DataTag
            if i == 0 and not getDataTag:
                #print("Handling potential special case")
                s[i] = self.ser.read(1)
                # try to get data with last buffer value and first buffer value (buffer is circular)
                dataTagValue = int.from_bytes(b''.join([s[UART_DATA_MAX_SIZE-1], s[i]]), "little")
                if dataTagValue in dataTagDict.values():
                    dataTag = list(dataTagDict.keys())[list(dataTagDict.values()).index(dataTagValue)] #get associated key   
                    #print("Tag detected special case:" + dataTag)
                    getDataTag = True   
                i += 1
            
            # Regular loop
            # print("read data from UART")
            s[i] = self.ser.read(1)
            # print("1 byte read from UART")
            # Detect DataTag
            if(not getDataTag):
                dataTagValue = int.from_bytes(b''.join(s[i-1:i+1]), "little") #little endian communication #basic but I did mistake: to get s[i-1] + s[i] => s[i-1:i+1] 
                if dataTagValue in dataTagDict.values():
                    dataTag = list(dataTagDict.keys())[list(dataTagDict.values()).index(dataTagValue)] #get associated key
                    #print("Tag detected:" + dataTag)
                    getDataTag = True
            elif(not getDataSize):
                # Get DataSize
                dataSize = int.from_bytes(s[i])
                #print("Data size is " + str(dataSize))
                getDataSize = True
            else:
                # Get Data (if at least 1 byte of data is expected, otherwise skip)
                if dataSize != 0:
                    data.append(s[i])
                    dataByteCounter += 1
                    if(dataByteCounter == dataSize): # we got all the data
                        #print("Data is " + str(data))
                        getData = True
                        if dataTag == "TIMESTAMP":
                            dataReal = self.unpackTimestamp(data, dataSize)
                        elif dataSize == 8:
                            (dataReal,) = unpack('<d',b''.join(data)) # unpack returns a tuple even if there is a single value, so we extract the value from the tuple here into dataReal
                        else:
                            print("WARNING - PARSER: Unhandled case")
                            dataReal = -1 # if we are in a case we don't handle fix the value to -1 for now
                        #print(dataTag + " is " + str(dataReal))
                
            if(getData or (getDataSize and dataSize == 0)): # we finished to parse  the frame next frame is expected, reset all
                getDataTag = False
                getDataSize = False
                getData = False
                data = []
                dataByteCounter = 0
                if dataSize != 0: # we notify that new data is available in buffer, only if there was at least one byte of data
                    with self.data_lock:
                        #print(f"New data available {dataTag}:{dataReal}")
                        self.newData = True
                        self.newDataConsumed = False
                        self.dataTag = dataTag
                        self.dataReal = dataReal
                    while self.newDataConsumed == False: # Wait until data is consumed
                        pass
            i += 1

            # print("Buffer ==" + str(s))
            # reset buffer if we reached the end
            if i >= UART_DATA_MAX_SIZE:
                i = 0

    """
    Unpack a nbBytes byte array into a timestamp
    """
    def unpackTimestamp(self, data, nbBytes):
        # Unpack bytes by byte and convert into datetime. it is at format Weekday (Monday = 1), Month, Date, Year in 2 digits (26 for 2026),  H,M,S
        for i in range(0,nbBytes):
           if i == 1:
               (monthstr,) = unpack('<b', data[i])
           if i == 2:
               (daystr,) = unpack('<b', data[i])
           if i == 3:
               (yearstr,) = unpack('<b', data[i])
               yearstr = 2000 + yearstr # Because the date is not complete
           if i == 4:
               (hourstr,) = unpack('<b', data[i])
           if i == 5:
               (minstr,) = unpack('<b', data[i])
           if i == 6:
               (secstr,) = unpack('<b', data[i])
        dateString = f"{daystr}/{monthstr}/{yearstr} {hourstr}:{minstr}:{secstr}"
        datetimeValue = datetime.strptime(dateString,"%d/%m/%Y %H:%M:%S")
        return datetimeValue

    """
    Connect automatically to a talking serial port
    Warning: If it happens data is transmitting on another port we could connect to the wrong port.
    TO DO: Complicated but we may to a more advanced system later to ensure we connect only to weather station port
    """
    def connectToSerial(self): 
        ser = None
        if os.name == "nt": #Windows
            portName = "COM"
        elif os.name == "posix": #Unix
            portName = "/dev/ttyACM"
        else:
            raise Exception('Unsupported OS')

        tryAgain = 1
        ## Dev bypass, when it is ok to modify manually instead of searching automatically because it takes too much time
        try:
            tryAgain = 0
            ser = serial.Serial( DEVBYPASS_COMPORT, 115200, timeout=MAX_DELAY_TO_RECEIVE_DATA * 2, parity=serial.PARITY_NONE, rtscts=0)
        except:
            tryAgain = 1

        
        for i in range(0,20):
            if tryAgain == 1:
                try:
                    tryAgain = 0
                    print("Trying to connect to " +  portName + str(i) + "...")
                    ser = serial.Serial( portName + str(i), 115200, timeout=1, parity=serial.PARITY_NONE, rtscts=0)
                    sleep(MAX_DELAY_TO_RECEIVE_DATA) # To ensure that data will be available on the port we want to connect
                    val = ser.read(1)
                    if val == b'':
                        tryAgain = 1
                except:
                    print(portName + str(i) + " not available")
                    tryAgain = 1
            else:
                break     
       
        if tryAgain == 1: # Mean we couldn't connect to serial port
            raise Exception('Impossible to connect to serial port')
        
        # If we are here it means we successfully connect to port with data available
        ser.timeout = MAX_DELAY_TO_RECEIVE_DATA * 2 
        return ser


