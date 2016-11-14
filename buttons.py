import RPi.GPIO as GPIO
from rgbled import RGBLed, Color
import requests
import os
from avs import get_access_token, alexa
import threading

PUSH_BUTTON = 10

rgbLed = RGBLed(33, 35, 37)

PATH = os.path.realpath(__file__).rstrip(os.path.basename(__file__))
HELLO_MP3 = PATH + 'audio/hello.mp3'
RECORDING_WAV = PATH + 'audio/recording.wav'


def setup():
    print("Started GPIO Setup")
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)
    rgbLed.setup()
    GPIO.setup(PUSH_BUTTON, GPIO.IN)
    print("GPIO Setup Complete")

def internet_on():
    print "Checking Internet Connection"
    try:
        requests.get('https://api.amazon.com/auth/o2/token')
        print "Connection OK"
        return True
    except:
        print "Connection Failed"
        return False

def speak(utterance_file):
    os.system('mpg123 -q {}audio/1sec.mp3 {}'.format(PATH, utterance_file))

def greeting():
    global HELLO_MP3
    speak(HELLO_MP3)

def pressed():
    return not GPIO.input(PUSH_BUTTON)

def ttw(text):
    global RECORDING_WAV
    os.system('echo \"{}\" | text2wave -o {}'.format(text, RECORDING_WAV))
    return RECORDING_WAV

def thinking(lock):
    while lock.locked():
        rgbLed.blink(Color.yellow)

processing = False
lock = threading.Lock()
def start_thinking():
    lock.acquire()
    thinking_thread = threading.Thread(target=thinking, args=(lock, ))
    thinking_thread.start()


def end_thinking(response_file):
    global processing
    lock.release()  # stop blinking
    print("Alexa is Ready to Speak")
    rgbLed.on(Color.yellow)
    speak(response_file)
    rgbLed.off()
    rgbLed.on(Color.white)
    processing = False

def run():
    global processing
    while True:
        if pressed() and not processing:
            processing = True
            alexa(ttw("What's the weather like in Seattle?"), start_thinking_callback=start_thinking, end_thinking_callback=end_thinking)

def cleanup():
    print("Started GPIO Cleanup")
    try:
        GPIO.cleanup()
        exit()
    finally:
        print("Cleanup Complete")

if __name__ == "__main__":
    setup()
    try:
        if internet_on():
            rgbLed.on(Color.blue)
            greeting()
            rgbLed.off()
            get_access_token()
            run()
        else:
            rgbLed.on(Color.red).on()
    finally:
        cleanup()