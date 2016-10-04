import RPi.GPIO as GPIO


class Led:
    def __init__(self, pin):
        self.pin = pin

    def setup(self):
        GPIO.setup(self.pin, GPIO.OUT)

    def on(self):
        GPIO.output(self.pin, True)

    def off(self):
        GPIO.output(self.pin, False)