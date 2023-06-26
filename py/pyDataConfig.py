pf_m = 0.00031268392922220777
pf_b = -17.095216162831747

def readingToGrams(reading):
	return(pf_m*reading + pf_b)


step_mm_conversion = 0.0195
def convertStepToMM(step):
	return(step*step_mm_conversion)

import serial
import time
def openSerialPort():
	outSer = serial.Serial('/dev/ttyUSB0', 115200)
	time.sleep(1) # Wait for Arduino to init
	return(outSer)