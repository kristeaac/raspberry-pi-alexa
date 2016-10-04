import RPi.GPIO as GPIO
import threading
import time


class Led:
    def __init__(self, pin):
        self.pin = pin
        self.lock = threading.Lock()

    def setup(self):
        GPIO.setup(self.pin, GPIO.OUT)

    def on(self):
        self.lock.acquire()
        try:
            GPIO.output(self.pin, True)
        finally:
            self.lock.release()

    def off(self):
        self.lock.acquire()
        try:
            GPIO.output(self.pin, False)
        finally:
            self.lock.release()

    def blink(self, duration=.5, count=1):
        self.lock.acquire()
        try:
            for i in range(count):
                GPIO.output(self.pin, True)
                time.sleep(duration)
                GPIO.output(self.pin, False)
                time.sleep(duration)
        finally:
            self.lock.release()