import RPi.GPIO as GPIO
import time
import threading
from enum import Enum


class Color(Enum):
    red = 0,
    green = 1,
    blue = 2,
    cyan = 3,
    magenta = 4,
    yellow = 5,
    white = 6


class RGBLed:
    def __init__(self, red_pin, green_pin, blue_pin):
        self.pins = [red_pin, green_pin, blue_pin]
        self.color_map = {
            Color.red: [red_pin],
            Color.green: [green_pin],
            Color.blue: [blue_pin],
            Color.cyan: [green_pin, blue_pin],
            Color.magenta: [red_pin, blue_pin],
            Color.yellow: [red_pin, green_pin],
            Color.white: [red_pin, green_pin, blue_pin],
        }
        self.lock = threading.Lock()

    def setup(self):
        GPIO.setup(self.pins, GPIO.OUT)

    def on(self, color):
        self.lock.acquire()
        try:
            GPIO.output(self.pins, False)
            GPIO.output(self.color_map[color], True)
        finally:
            self.lock.release()

    def off(self):
        self.lock.acquire()
        try:
            GPIO.output(self.pins, False)
        finally:
            self.lock.release()

    def blink(self, color, duration=.5, count=1):
        self.lock.acquire()
        try:
            GPIO.output(self.pins, False)
            for i in range(count):
                GPIO.output(self.color_map[color], True)
                time.sleep(duration)
                GPIO.output(self.color_map[color], False)
                time.sleep(duration)
        finally:
            self.lock.release()