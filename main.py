import RPi.GPIO as GPIO
import time
import os
import requests

refreshToken = os.environ['ALEXA_REFRESH_TOKEN']

red = 8
green = 24
blue = 25
push_button = 10

GPIO.setmode(GPIO.BOARD)
GPIO.setup(red, GPIO.OUT)
GPIO.setup(push_button, GPIO.IN)

def cleanup():
    GPIO.cleanup()

def led_on(pin):
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
        led_on(blue)
except:
    cleanup()

cleanup()