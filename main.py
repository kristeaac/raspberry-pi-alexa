import RPi.GPIO as GPIO
import time
import os
import requests

refreshToken = os.environ['ALEXA_REFRESH_TOKEN']

red = 33
green = 35
blue = 37
led_pins = [red, green, blue]
push_button = 10

def setup():
    GPIO.setmode(GPIO.BOARD)
    for pin in led_pins:
        GPIO.setup(pin, GPIO.OUT)
    GPIO.setup(push_button, GPIO.IN)

def cleanup():
    GPIO.cleanup()

def blink(pin, duration=3):
    GPIO.output(pin, True)
    time.sleep(duration)
    GPIO.output(pin, False)

def internet_on():
    print "Checking Internet Connection"
    try:
        requests.get('https://api.amazon.com/auth/o2/token')
        print "Connection OK"
        return True
    except:
        print "Connection Failed"
        return False

def pressed():
    return GPIO.input(push_button)

if __name__ == "__main__":
    setup()
    try:
        # check internet connection
        if internet_on():
            blink(blue)

        # wait for push button to be pressed
        while True:
            if pressed():
                blink(green)
    except:
        cleanup()
    cleanup()
