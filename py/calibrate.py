# Calibrate load cells by loading differently sized masses and taking measurements
# For each test, enter the mass in grams and wait a second for the measurements to be taken and saved
# Appends data to py/data/calData.csv, delete before cal to overwrite
# Paste pf_m and pf_b to py/pyDataConfig.py to use in other runs

import serial
import serial.tools.list_ports
import time
import sys
import binascii
import sys
import numpy as np

from matplotlib import pyplot as plt

import pyDataConfig as pdc
ser = pdc.openSerialPort()



def showPlot():
	weights = []
	vals = []

	readFile = open("py/data/calData.csv", 'r')
	for fooLine in readFile.readlines():
		splt = fooLine.split(',')
		weights.append(int(splt[0]))
		vals.append(int(splt[1][:-1]))
	readFile.close()
	weights = np.array(weights)
	vals = np.array(vals)
	plt.scatter(vals, weights)

	polyFit = np.polyfit(vals, weights, 1)

	print(f"pf_m = {polyFit[0]}")
	print(f"pf_b = {polyFit[1]}")
	xPts = np.arange(np.min(vals)-3, np.max(vals)+3)

	plt.plot(xPts, xPts*polyFit[0] + polyFit[1])

	plt.show()

if "-plot" in sys.argv:
	showPlot()
	exit()


for foo in serial.tools.list_ports.comports():
	print(foo)


testDur = 3
waitDur = 3

# testDur = 0.1
# waitDur = 0.1

def getReading():
	readBytes = ser.read(8)

	# Do checksum and continue if not
	while sum(readBytes[:7])%256 != readBytes[7]:
		# print('\n!!!!!!!!!\n')
		ser.read_all()
		readBytes = ser.read(8)
	
	readVal = int.from_bytes(readBytes[:3], byteorder=sys.byteorder, signed=True)
	timeStamp = int.from_bytes(readBytes[3:7], byteorder=sys.byteorder, signed=False)
	
	print(f"{binascii.hexlify(readBytes)} -> {timeStamp} : {readVal}")

	return ((readVal, timeStamp))

dataOut = open("py/data/calData.csv", '+a')

testIter = 0
while True:
	currWeight = input("Enter added weight:")

	if currWeight == 'X' or currWeight == 'x': break

	# Check that value is int
	try:
		int(currWeight)
	except:
		print(f"Unable to convert {currWeight} to int\n")
		continue

	time.sleep(0.5)
	ser.read_all()

	for ii in range(50):
		time.sleep(0.02)
		ser.read_all()

		readVal, timeStamp = getReading()

		dataOut.write(f"{currWeight},{readVal}\n")

	dataOut.flush()

showPlot()