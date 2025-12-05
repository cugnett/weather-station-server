import serial
from struct import unpack
dataTagDict = { 
  "TEMPERATURE_INTERNAL":   0x0001,
  "TEMPERATURE":            0x0002,
  "PRESSURE":               0x0003,
  "WIND_SPEED":             0x0004,
  "RAIN_LEVEL":             0x0005,
  "HUMIDITY":               0x0006,
  "NONE":                   0xFFFF
}
BUFFER_INIT_VALUE = b'254' # Value to fill in buffer at startup with. BUFFER_INIT_VALUE is not a DataTag or any other frame control value, to avoid false detection at startup

UART_DATA_MAX_SIZE = 256

# Read data coming from STM32 Nucleo UART2 through COM3 port
ser = serial.Serial('COM3', 115200, timeout=10, parity=serial.PARITY_NONE, rtscts=0)
# Uart buffer
#s = list(bytearray(UART_DATA_MAX_SIZE)) # Warning this will do a list of UART_DATA_MAX_SIZE integer, list converts bytes into int!
s = [BUFFER_INIT_VALUE] * UART_DATA_MAX_SIZE #same as above but maybe less confusing. 
print(s)
i = 0
getDataTag = False
getDataSize = False
getData = False
data = []
dataByteCounter = 0
while(True):
    # first implementation NOT robust because datatag could be confused with data (1/65536 probability)
    # Frame format: DataTag (2 bytes) | DataSize (1 byte) | Data (DataSize byte(s))

    #To manage special case where the last byte of the buffer is the first byte of the DataTag and the first byte of the buffer the second byte of the DataTag
    if i == 0 and not getDataTag:
        print("Handling potential special case")
        s[i] = ser.read(1)
        # try to get data with last buffer value and first buffer value (buffer is circular)
        dataTagValue = int.from_bytes(b''.join([s[UART_DATA_MAX_SIZE-1], s[i]]), "little")
        if dataTagValue in dataTagDict.values():
            dataTag = list(dataTagDict.keys())[list(dataTagDict.values()).index(dataTagValue)] #get associated key   
            print("Tag detected special case:" + dataTag)
            getDataTag = True   
        i += 1
    
    # Regular loop
    s[i] = ser.read(1)
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
        # Get Data
        data.append(s[i])
        dataByteCounter += 1
        if(dataByteCounter == dataSize): # we got all the data
            #print("Data is " + str(data))
            getData = True
            #For test: we need here to handle different datatypes
            dataReal = unpack('<d',b''.join(data))
            print(dataTag + " is " + str(dataReal))
        
    if(getData or (getDataSize and dataSize == 0)): # next frame is expected, reset all
        getDataTag = False
        getDataSize = False
        getData = False
        data = []
        dataByteCounter = 0
    i += 1

    #print("Buffer ==" + str(s))
    # reset buffer if we reached the end
    if i >= UART_DATA_MAX_SIZE:
        i = 0

s = ser.read(100)
print(s)
print("Hello world")


