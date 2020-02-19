#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# TUKKIMITTARI - GIVARNA - för fullt!!!
# by Robin Bäckman
# 2020

import RPi.GPIO as GPIO
import time
import json

GPIO.setmode(GPIO.BCM)
GPIO.setup(20, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(21, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

calib = 200
countcm = 0
oldcount = 0
counted = False
givare1 = True
givare2 = True
while True:
    oldcount = countcm
    if GPIO.input(21) == 1:
        givare1 = False
    if GPIO.input(21) == 0:
        givare1 = True

    if GPIO.input(20) == 1:
        givare2 = False
    if GPIO.input(20 == 0:
        givare2 = True

    if givare1 == True and givare2 == False:
        if counted == False:
            countcm = countcm + calib
            counted = True

    if givare1 == False and givare2 == True:
        if counted == False:
            countcm = countcm - calib
            counted = True

    if givare1 == False and givare2 == False:
        counted = False

    if countcm != oldcount:
        #print(str(countcm))
        try:
            f = open("/dev/shm/kaparens_givare", "w")
            f.write(str(countcm))
            f.close()
        except:
            pass

    time.sleep(0.0001)
