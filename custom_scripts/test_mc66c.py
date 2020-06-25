# Importing modules
#################################
import serial
from time import sleep

# Loading config
#################################
serialport = '/dev/ttyUSB0'

# Function
#################################
def get_meter_readings():
    mc66c = serial.Serial(port=serialport,
        bytesize=serial.SEVENBITS,
        parity=serial.PARITY_EVEN,
        stopbits=serial.STOPBITS_ONE,
        timeout=2)
    mc66c.baudrate = 300
    mc66c.write('/#1'.encode('utf-8'))
    mc66c.flush()
    sleep(1)
    mc66c.baudrate = 1200
    mc66c.flushInput()
    data = mc66c.read(87).split()
    mc66c.close()
    return data

# Getting information from Kamstrup Multical 66C
###############################
new_data = get_meter_readings()

# Decode and transform new data
###############################
new_energy = int((new_data[0]).decode('utf-8'))/1000
new_volume = int((new_data[1]).decode('utf-8'))/1000
new_temp_in = int((new_data[3]).decode('utf-8'))/100
new_temp_out = int((new_data[4]).decode('utf-8'))/100

# Print collected values
###############################
print("Energy: "+str(new_energy))
print("Volume: "+str(new_volume))
print("Temperature in: "+str(new_temp_in))
print("Temperature out: "+str(new_temp_out))