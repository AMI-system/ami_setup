#!/usr/bin/env python

from time import sleep
import os
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setup(21, GPIO.OUT)
GPIO.setup(20, GPIO.OUT)
sleep(0.5);

try:
   GPIO.output(21,GPIO.LOW) 
   GPIO.output(20,GPIO.LOW)                           
   
finally:
   GPIO.cleanup()
