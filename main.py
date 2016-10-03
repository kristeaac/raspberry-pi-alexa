import RPi.GPIO as GPIO
import time

ledPin = 8
buttonPin = 10

GPIO.setmode(GPIO.BOARD)
GPIO.setup(ledPin, GPIO.OUT)
GPIO.setup(buttonPin, GPIO.IN)

blink=0
while blink < 100:
    val = GPIO.input(buttonPin)
    if val:
        GPIO.output(ledPin, True)
        time.sleep(.5)
        GPIO.output(ledPin, False)
        time.sleep(.5)
        blink += 1
    else:
        GPIO.output(ledPin, True)

GPIO.cleanup()