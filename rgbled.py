import RPi.GPIO as GPIO
import time
import threading


class RGBLed:
    def __init__(self, red, green, blue):
        self.pins = [red, green, blue]
        self.RED = [red]
        self.GREEN = [green]
        self.BLUE = [blue]
        self.CYAN = [green, blue]
        self.MAGENTA = [red, blue]
        self.YELLOW = [red, green]
        self.WHITE = [red, green, blue]
        self.lock = threading.Lock()
        self.pwms = {}

    def setup(self):
        for pin in self.pins:
            GPIO.setup(pin, GPIO.OUT)

    def on(self, color):
        self.lock.acquire()
        try:
            for pin in color:
                GPIO.output(pin, True)
        finally:
            self.lock.release()

    def off(self):
        self.lock.acquire()
        try:
            for pin in self.pins:
                GPIO.output(pin, False)
        finally:
            self.lock.release()

    def blink(self, color, duration=.5, count=1):
        self.lock.acquire()
        try:
            for i in range(count):
                for pin in color:
                    GPIO.output(pin, True)
                time.sleep(duration)
                for pin in self.pins:
                    GPIO.output(pin, False)
                time.sleep(duration)
        finally:
            self.lock.release()