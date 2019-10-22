#! /usr/bin/env python
# -*- coding: utf-8 -*-

# PBL29

# デバッグようのLCD表示けっこうあるっぽい

# 使うやつ
import os
import cv
import cv2
import sys
import time
import smbus
import serial
import RPi.GPIO as GPIO


# USBでシリアル通信するための機器のパス
USB = "/dev/ttyUSB0"
# ボーレート。これはモータードライバー由来のはず
BAUD_RATE = 9600
# シリアル通信のための設定
SER = serial.Serial(USB,BAUD_RATE)

# どのスピードで動かすかっていう初期設定
SPEED = 20
# どれだけ動かすかっていうための初期設定(タイムとあるがなんループするかなのね)(画像取得と検出に時間がまあまあかかるから1秒くらいだった気がする)
TIME  = 20

# AppplePiのボタンのためのポートですね6個の
port1 = 22
port2 = 23
port3 = 24
port4 = 25
port5 = 26
port6 = 27

# どの場所に刺されたUSBのかてやつ
bus_number = 1
# なにこれ
bus = smbus.SMBus(bus_number)
# ApplePi系の通信にいる定数かな
adr = 0x3e
dat = 0x40
cmd = 0x00
# 顔検出の際に右にあるか左にあるか的な？
kit = 317

# なにこれ、、使ってないしいらんっしょ
INTERVAL = 33     
FRAME_RATE = 30
# カメラつなぐのに必要なやつやね。どのUSBかで変わったりしそう
DEVICE_ID = 1


# スタート。引数の値まで1づつ加速する
def START(x):
	c = 0
	while x > c:
		# 右の車輪
		SER.write(chr(128))
		SER.write(chr(0))
		SER.write(chr(c))
		SER.write(chr(c))
		# 左の車輪
		SER.write(chr(128))
		SER.write(chr(4))
		SER.write(chr(c))
		SER.write(chr(c+4))
		# いい感じの間隔で
		time.sleep(0.05)
		c = c + 1 
	
# ストップ。引数の値から1づつ減速して止まる
def STOP(x):
	while x > 0:
		# 右の車輪
		SER.write(chr(128))
		SER.write(chr(0))
		SER.write(chr(x))
		SER.write(chr(x))
		# 左の車輪
		SER.write(chr(128))
		SER.write(chr(4))
		SER.write(chr(x))
		SER.write(chr(x+4))
		# いい感じの間隔で
		time.sleep(0.05)
		x = x - 1
		
# 右の車輪の変速(?)引数の値にしそう
def RH(x):
	SER.write(chr(128))
	SER.write(chr(0))
	SER.write(chr(x))
	SER.write(chr(x))

# 左の車輪の変速(?)引数の値にしそう
def LH(x):
	SER.write(chr(128))
	SER.write(chr(4))
	SER.write(chr(x))
	SER.write(chr(x+4))

# ApplePiのLCDモニタを初期化する処理
def initLCD():
	time.sleep(0.1)
	bus.write_i2c_block_data(adr, cmd, [0x38, 0x39, 0x14, 0x70, 0x56, 0x6c])
	time.sleep(0.3)
	bus.write_i2c_block_data(adr, cmd, [0x38, 0x0c, 0x01])
	bus.write_i2c_block_data(adr, cmd, [0x05, 0x01])
	
# ApplePiのLCDモニタに映す処理
def LCD(length):
	initLCD()
	plen = list(length)
	for c in plen:
		bus.write_i2c_block_data(adr, dat, [ord(c)])

# ApplePiのLCDモニタにカウントダウンする見栄えの処理
def CD(TIME):
	while TIME > -1:
		LCD("%d" %TIME)
		time.sleep(1)
		TIME = TIME - 1
	initLCD()
	
# スイッチ1の処理
# 決められた速さと時間で顔検出出でた方向に向きながらすすむ
def SWC1():
	global SPEED
	global TIME
	global kit
	# 謎の定形処理
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(port1, GPIO.IN, pull_up_down = GPIO.PUD_UP)
	SW1 = GPIO.input(port1)
	# おされてたら
	if SW1 == 0:
		# 3.2.1...って出す
		CD(3)
		# 定義されてるスピードまで加速
		START(SPEED)
		# ?
		GPIO.cleanup()
		# LCD表示
		LCD("tr-star")
		RP = 0
		# 無限ループ
		while True:
			# いまのwebカメラからの情報を画像として読みこみ
			ret,im = CAP.read()
			# 設定された時間動いてたらおわる
			if RP == TIME:
				STOP(SPEED)
				LCD("bureku")
				break
			# 顔検出
			kao = cascade.detectMultiScale(im, 1.1, 3) 
			LCD("kasuke")
			# 顔の位置取得
			for (x, y, w, h) in kao:
				LCD("for")
				kit = x
			# 顔が右にあったら右に
			if kit < 315:
				LCD("migi")
				RH(SPEED-10)
				LH(SPEED)
			# 顔が左にあったら左に
			elif kit > 320:
				LCD("hida")
				LH(SPEED-10)
				RH(SPEED) 
			LCD("1syu")
			# ループしてよってやつを追加
			RP = RP + 1
			# 顔のいち初期化
			x = 317
			LCD("%d" %RP)
		LCD("E")
			
# スイッチ1で時間と速さで進んで止まるだけの処理。テスト用
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
		
# スイッチ2
# 設定されているスピードを10下げる
def SW2():
	global SPEED
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(port2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
	SW2 = GPIO.input(port2)
	if SW2 == 0:
		SPEED = SPEED - 10
		LCD("SPD:%d" %SPEED)
	GPIO.cleanup()
	
# スイッチ3
# 設定されているスピードを10上げる
def SW3():
	global SPEED
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(port3, GPIO.IN, pull_up_down=GPIO.PUD_UP)
	SW3 = GPIO.input(port3)
	if SW3 == 0:
		SPEED = SPEED + 10
		LCD("SPD:%d" %SPEED)
	GPIO.cleanup()

# スイッチ4
# 設定されているスピードを1下げる
def SW4():
	global TIME
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(port4, GPIO.IN, pull_up_down=GPIO.PUD_UP)
	SW4 = GPIO.input(port4)
	if SW4 == 0:
		LCD("TIME:%d" %TIME)
		TIME = TIME - 1
	GPIO.cleanup()
	
# スイッチ5
# 設定されているスピードを1上げる
def SW5():
	global TIME
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(port5, GPIO.IN, pull_up_down=GPIO.PUD_UP)
	SW5 = GPIO.input(port5)
	if SW5 == 0:
		LCD("TIME:%d" %TIME)
		TIME = TIME + 1
	GPIO.cleanup()

# スイッチ6
# RaspberryPiをシャットダウンする
def SW6():
	GPIO.setmode(GPIO.BCM)
	GPIO.setup(port6, GPIO.IN, pull_up_down=GPIO.PUD_UP)
	SW6 = GPIO.input(port6)
	if SW6 == 0:
		LCD("BYE!")
		time.sleep(1)
		initLCD()
		sys.exit(0)
		os.system("sudo shutdown -h now")
		

# これがめいんです
if __name__ == '__main__':
	
	# おはよう
	LCD("HELLO!")
	time.sleep(1)
	initLCD()

	# このカメラで撮るでってやつ
	CAP = cv2.VideoCapture(DEVICE_ID)
	# 顔検出のための辞書ファイルのパス(OpenCVのとこからだうんろーどして使った気がします)
	cascade = cv2.CascadeClassifier('cascade.xml')

	# THE無限ループ
	# 各スイッっちの動きをずっと見続けるんね
	while True:
		
		SWC1()
		
		SW2()
		
		SW3()
		
		SW4()
		
		SW5()
		
		SW6()
