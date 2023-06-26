#include <Arduino.h>
#include "ComponentDrivers.h"

byte PD_SCK = 2;	// Power Down and Serial Clock Input Pin
byte DOUT = 3;		// Serial Data Output Pin
byte GAIN = 1; // 3

byte SOLENOID = 34; // Pin controlling solenoid

uint8_t data[3] = { 0 }; // Data read from HX711

// put function declarations here:
uint8_t readHX711();

// // Height Stepper
dynStepper posStepper(53, 52, 51, 50);

double currTime;
double lastTime;

double lastTrigger; // Time of trigger
long int stepperPosition; // Current position of stepper

uint32_t solenoidDuration = 1000000; // Duration to fire solenoid in mS

// How many ticks to move for different commands
long int stepperTickInterval_0xF1 = 100;
long int stepperTickInterval_0xF2 = 10;
long int stepperTickInterval_0xF3 = 1;
long int stepperTickInterval_0xF4 = -100;
long int stepperTickInterval_0xF5 = -10;
long int stepperTickInterval_0xF6 = -1;


void setup() {
	Serial.begin(115200);
	
	pinMode(PD_SCK, OUTPUT);
	pinMode(DOUT, INPUT);

	pinMode(SOLENOID, OUTPUT);

	currTime = micros();
	lastTime = micros();
	lastTrigger = 0;
}



void loop() {
	// Update time duration
	currTime = micros();
	uint16_t timeGap = currTime - lastTime;
	lastTime = currTime;
	

	// Read command from serial
	while(Serial.available() > 0){
		// unsigned int ii = 0;

		uint8_t readCommand = Serial.read();
		
		// Serial.write(readCommand);
		// for (ii = 0; ii < 6; ii++){ Serial.write(0); }
		// Serial.write(readCommand);

		switch (readCommand)
		{
		// Fire solenoid
		case 0x01:
			lastTrigger = currTime;
			break;

		// Do different length moves
		case 0xF1:
			stepperPosition += stepperTickInterval_0xF1;
			posStepper.setTarget(stepperPosition);
			break;

		case 0xF2:
			stepperPosition += stepperTickInterval_0xF2;
			posStepper.setTarget(stepperPosition);
			break;

		case 0xF3:
			stepperPosition += stepperTickInterval_0xF3;
			posStepper.setTarget(stepperPosition);
			break;

		case 0xF4:
			stepperPosition += stepperTickInterval_0xF4;
			posStepper.setTarget(stepperPosition);
			break;

		case 0xF5:
			stepperPosition += stepperTickInterval_0xF5;
			posStepper.setTarget(stepperPosition);
			break;

		case 0xF6:
			stepperPosition += stepperTickInterval_0xF6;
			posStepper.setTarget(stepperPosition);
			break;


		
		// Go to zero
		case 0x05:
			stepperPosition = 0;
			posStepper.setTarget(stepperPosition);
		default:
			break;
		}
	}

	// Update stepper
	posStepper.update(timeGap);

	uint32_t trigGap = currTime - lastTrigger;
	if(trigGap > solenoidDuration && trigGap < solenoidDuration*2){
		digitalWrite(SOLENOID, HIGH);
	}
	else{
		digitalWrite(SOLENOID, LOW);
	}

	// Load and save data from load cell
	if(readHX711()){ // If successfully read from HX711
		uint8_t checkSum = 0x00;

		for (unsigned int ii = 0; ii < 3; ii++) {
			Serial.write(data[ii]);
			checkSum += data[ii];
		}


		for (unsigned int ii = 0; ii < 4; ii++) {
			uint8_t timeStampByte = trigGap >> (ii*8);
			Serial.write(timeStampByte);
			checkSum += timeStampByte;
		}


		Serial.write(checkSum);
	}
	
}


uint8_t readHX711() {
	if(digitalRead(DOUT) != LOW) return(0);

	// Pulse the clock pin 24 times to read the data.
	data[2] = shiftIn(DOUT, PD_SCK, MSBFIRST);
	data[1] = shiftIn(DOUT, PD_SCK, MSBFIRST);
	data[0] = shiftIn(DOUT, PD_SCK, MSBFIRST);

	// Set the channel and the gain factor for the next reading using the clock pin.
	for (unsigned int i = 0; i < GAIN; i++) {
		digitalWrite(PD_SCK, HIGH);
		digitalWrite(PD_SCK, LOW);
	}

	return(1);
}
