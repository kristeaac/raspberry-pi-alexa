import RPi.GPIO as GPIO
import time
import os
import requests

refreshToken = os.environ['ALEXA_REFRESH_TOKEN']

internetConnectionPin = 8
buttonPin = 10

GPIO.setmode(GPIO.BOARD)
GPIO.setup(internetConnectionPin, GPIO.OUT)
GPIO.setup(buttonPin, GPIO.IN)

def cleanup():
    GPIO.cleanup()

def ledOn(pin):
    GPIO.output(pin, True)

def internet_on():
    print "Checking Internet Connection"
    try:
        requests.get('https://api.amazon.com/auth/o2/token')
        print "Connection OK"
        return True
    except:
        print "Connection Failed"
        return False

try:
    if internet_on():
        ledOn(internetConnectionPin)
except:
    cleanup()

cleanup()