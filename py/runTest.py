import serial
import time
import sys
import binascii

import numpy as np
from matplotlib import pyplot as plt
import pickle as pkl


import pyDataConfig as pdc
ser = pdc.openSerialPort()

testDur = 3 # How long to wait and read data

testMax = 1000 # Max position to check
testMin = -500	# Min position to check
testGap = 30 # Gap between reads

testRepeats = 30 # Max loops of entire test process



# Dictionary for saving data
outData = {
	'timestamps':[],
	'dataPoints':[],
	'positions':[],
}


# Current data run (before saving)
timeStamp_set = []
readVal_set = []


# Init output plots
fig, ax = plt.subplots(2, 1)
plt.ion()
ax[0].set_xlabel('Position (mm)')
ax[0].set_ylabel('Pull (g)')

ax[1].set_xlabel('Time (S)')
ax[1].set_ylabel('Pull (g)')





# Get load cell reading and timestamp pair (blocking)
def getReading():
	readBytes = ser.read(8)

	# Do checksum and continue if not
	while sum(readBytes[:7])%256 != readBytes[7]:
		ser.read_all() # Clear read buffer
		readBytes = ser.read(8)
	
	readVal = int.from_bytes(readBytes[:3], byteorder=sys.byteorder, signed=True)
	timeStamp = int.from_bytes(readBytes[3:7], byteorder=sys.byteorder, signed=False)
	
	return ((readVal, timeStamp))



def readDataForSeconds(delayTime):
	global plt, ax
	global ser
	global timeStamp_set, readVal_set, currentPosition, outData
	global testMax, testMin

	startTime = time.time()

	# Read data until time is up
	while(time.time() < startTime+delayTime):
		# Wait until there is enough data to complete reading
		while ser.in_waiting < 8:
			plt.pause(0.001)

		readVal, timeStamp = getReading() # Load new data point

		# Check if we've starting a new run
		if len(timeStamp_set) > 0 and timeStamp < timeStamp_set[-1]:
			# Convert data to numpy arrays before processing
			timeStamp_set = np.array(timeStamp_set, dtype=np.int32)
			readVal_set = np.array(readVal_set, dtype=np.uint32)

			# Save data points
			outData['timestamps'].append(timeStamp_set)
			outData['dataPoints'].append(readVal_set)
			outData['positions'].append(currentPosition)
			
			# Save data to pickle
			outPickle = open('py/data/currentData.pkl', '+wb')
			pkl.dump(outData, outPickle)
			outPickle.close()

			print(f"Run {len(outData['positions'])} saved!")


			# Update plots
			
			# Convert data
			readVal_set = pdc.readingToGrams(np.array(readVal_set, dtype=np.double))
			timeStamp_set = np.array(timeStamp_set, dtype=np.double)/1000000
			currPosition_mm = pdc.convertStepToMM(currentPosition)

			# Plot curve of pull over time
			testFraction = (currentPosition-testMin)/(testMax-testMin)
			ax[1].plot(timeStamp_set/1000000, readVal_set, c=(0.0, testFraction, testFraction), alpha=0.5)
			
			# Plot range and mean of run
			pullValues = readVal_set[np.where((timeStamp_set > 1040000) & (timeStamp_set < 2000000) )] # Get values where solenoid was active and convert to mN
			ax[0].plot([currPosition_mm, currPosition_mm], [np.max(pullValues), np.min(pullValues)], c='Orange')
			ax[0].scatter([currPosition_mm], [np.mean(pullValues)], c='Blue')

			# Reset data arrays
			timeStamp_set = []
			readVal_set = []

		# Append data points to new run
		timeStamp_set.append(timeStamp)
		readVal_set.append(readVal)



# Go to target position
currentPosition = 0
def goToPosition(targetPos):
	global currentPosition, ser

	stepCount = abs(targetPos - currentPosition) # Calculate how many steps to move
	
	# Byte commands over serial and how many steps they correspond to
	forwardCommands = [(0xF1, 100), (0xF2, 10), (0xF3, 1)]
	backwardCommands =  [(0xF4, -100), (0xF5, -10), (0xF6, -1)]
	
	# Iteratively send corrective commands

	if currentPosition < targetPos: # If moving forward
		for commandByte, commandDist in forwardCommands:
			while currentPosition + commandDist <= targetPos:
				ser.write([commandByte])
				currentPosition += commandDist

	elif currentPosition > targetPos: # If moving backward
		for commandByte, commandDist in backwardCommands:
			while currentPosition + commandDist >= targetPos:
				ser.write([commandByte])
				currentPosition += commandDist

	print('\n')
	readDataForSeconds(stepCount*0.003+1.0)


# Repeatedly test data points
for repeatIter in range(testRepeats): # Loop entire test
	goToPosition(testMax+100) # Go to above test loop
	for testPos in range(testMax, testMin, -testGap): # Iterate through positions from top to bottom
		goToPosition(testPos) # Go to next position
		ser.write([0x01]) # Init solenoid sequence
		readDataForSeconds(testDur) # Wait for test duration and record data


ser.write([0x05]) # Send stepper back to 0

plt.pause(10)

