# Move stepper to specific for testing and calibration
# Useful for calculating relationship between step and distance

import serial
import time
import sys
import binascii

import numpy as np
from matplotlib import pyplot as plt
import pickle as pkl

import pyDataConfig as pdc
ser = pdc.openSerialPort()

# Go to target position
currentPosition = 0
def goToPosition(targetPos):
	global currentPosition, ser

	stepCount = abs(targetPos - currentPosition)
	
	forwardCommands = [(0xF1, 100), (0xF2, 10), (0xF3, 1)]
	backwardCommands =  [(0xF4, -100), (0xF5, -10), (0xF6, -1)]

	print(f"currentPosition:{currentPosition}")
	print(f"targetPos:{targetPos}")

	if currentPosition < targetPos:
		for commandByte, commandDist in forwardCommands:
			while currentPosition + commandDist <= targetPos:
				ser.write([commandByte])
				currentPosition += commandDist
				print(f"Sent {commandByte} : {commandDist}   (pos = {currentPosition})")

	elif currentPosition > targetPos:
		for commandByte, commandDist in backwardCommands:
			while currentPosition + commandDist >= targetPos:
				ser.write([commandByte])
				currentPosition += commandDist
				print(f"Sent {commandByte} : {commandDist}   (pos = {currentPosition})")

	print('\n')
	plt.pause(stepCount*0.003+1.0)


while True:
	targPos = input('Enter target position:')

	try:
		int(targPos)
	except:
		print(f"Unable to convert {targPos} to int")
		continue
	
	print(f"Moving to position {targPos} ({int(targPos)*0.2195} mm)")
	goToPosition(int(targPos))
