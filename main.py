#! /usr/bin/env python
# -*- coding: utf-8 -*-

# PBL29


import os
import cv
import cv2
import sys
import time
import smbus
import serial
import RPi.GPIO as GPIO


USB = "/dev/ttyUSB0"
BAUD_RATE = 9600
SER = serial.Serial(USB,BAUD_RATE)

SPEED = 20
TIME  = 20

port1 = 22
port2 = 23
port3 = 24
port4 = 25
port5 = 26
port6 = 27

bus_number = 1
bus = smbus.SMBus(bus_number)
adr = 0x3e
dat = 0x40
cmd = 0x00
kit = 317

INTERVAL = 33     
FRAME_RATE = 30
DEVICE_ID = 1


def START(x):
	c = 0
	while x > c:
		SER.write(chr(128))
		SER.write(chr(0))
		SER.write(chr(c))
		SER.write(chr(c))
		SER.write(chr(128))
		SER.write(chr(4))
		SER.write(chr(c))
		SER.write(chr(c+4))
		time.sleep(0.05)
		c = c + 1 
	
def STOP(x):
	while x > 0:
		SER.write(chr(128))
		SER.write(chr(0))
		SER.write(chr(x))
		SER.write(chr(x))
		SER.write(chr(128))
		SER.write(chr(4))
		SER.write(chr(x))
		SER.write(chr(x+4))
		time.sleep(0.05)
		x = x - 1
		
def RH(x):
	SER.write(chr(128))
	SER.write(chr(0))
	SER.write(chr(x))
	SER.write(chr(x))
	
def LH(x):
	SER.write(chr(128))
	SER.write(chr(4))
	SER.write(chr(x))
	SER.write(chr(x+4))

def initLCD():
	time.sleep(0.1)
	bus.write_i2c_block_data(adr, cmd, [0x38, 0x39, 0x14, 0x70, 0x56, 0x6c])
	time.sleep(0.3)
	bus.write_i2c_block_data(adr, cmd, [0x38, 0x0c, 0x01])
	bus.write_i2c_block_data(adr, cmd, [0x05, 0x01])
	
def LCD(length):
	initLCD()
	plen = list(length)
	for c in plen:
		bus.write_i2c_block_data(adr, dat, [ord(c)])

def CD(TIME):
	while TIME > -1:
		LCD("%d" %TIME)
		time.sleep(1)
		TIME = TIME - 1
	initLCD()
	
def SWC1():
	global SPEED
	global TIME
	global timer
	global kit
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(port1, GPIO.IN, pull_up_down = GPIO.PUD_UP)
	SW1 = GPIO.input(port1)
	if SW1 == 0:
		CD(3)
		START(SPEED)
		GPIO.cleanup()
		LCD("tr-star")
		RP = 0
		while True:
			ret,im = CAP.read()
			if RP == TIME:
				STOP(SPEED)
				LCD("bureku")
				break
			kao = cascade.detectMultiScale(im, 1.1, 3) 
			LCD("kasuke")
			for (x, y, w, h) in kao:
				LCD("for")
				kit = x
			if kit < 315:
				LCD("migi")
				RH(SPEED-10)
				LH(SPEED)
			elif kit > 320:
				LCD("hida")
				LH(SPEED-10)
				RH(SPEED) 
			LCD("1syu")
			#cv2.imshow('im',im)
			RP = RP + 1
			x = 317
			LCD("%d" %RP)
		LCD("E")
			
	
def SW1():
	global SPEED
	global TIME
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(port1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
	SW1 = GPIO.input(port1)
	if SW1 == 0:
		CD(3)
		START(SPEED)
		time.sleep(TIME)
		STOP(SPEED)
	GPIO.cleanup()
		
def SW2():
	global SPEED
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(port2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
	SW2 = GPIO.input(port2)
	if SW2 == 0:
		SPEED = SPEED - 10
		LCD("SPD:%d" %SPEED)
	GPIO.cleanup()
	
def SW3():
	global SPEED
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(port3, GPIO.IN, pull_up_down=GPIO.PUD_UP)
	SW3 = GPIO.input(port3)
	if SW3 == 0:
		SPEED = SPEED + 10
		LCD("SPD:%d" %SPEED)
	GPIO.cleanup()

def SW4():
	global TIME
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(port4, GPIO.IN, pull_up_down=GPIO.PUD_UP)
	SW4 = GPIO.input(port4)
	if SW4 == 0:
		LCD("TIME:%d" %TIME)
		TIME = TIME - 1
	GPIO.cleanup()
	
def SW5():
	global TIME
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(port5, GPIO.IN, pull_up_down=GPIO.PUD_UP)
	SW5 = GPIO.input(port5)
	if SW5 == 0:
		LCD("TIME:%d" %TIME)
		TIME = TIME + 1
	GPIO.cleanup()

def SW6():
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(port6, GPIO.IN, pull_up_down=GPIO.PUD_UP)
	SW6 = GPIO.input(port6)
	if SW6 == 0:
		LCD("BYE!")
		time.sleep(1)
		initLCD()
		sys.exit(0)
		#os.system("sudo shutdown -h now")
		

if __name__ == '__main__':
	
	LCD("HELLO!")
	time.sleep(1)
	initLCD()

	CAP = cv2.VideoCapture(DEVICE_ID)
	cascade = cv2.CascadeClassifier('cascade.xml')

	while True:
		
		SWC1()
		
		SW2()
		
		SW3()
		
		SW4()
		
		SW5()
		
		SW6()
