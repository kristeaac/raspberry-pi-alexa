import RPi.GPIO as GPIO
import os
import requests
import alsaaudio
from rgbled import RGBLed, Color
from avs import get_access_token, alexa
import sys
import getopt

PATH = os.path.realpath(__file__).rstrip(os.path.basename(__file__))

DEVICE = "plughw:1"

HELLO_MP3 = PATH + 'audio/hello.mp3'
RECORDING_WAV = PATH + 'audio/recording.wav'
RESPONSE_MP3 = PATH + 'audio/response.mp3'

PUSH_BUTTON = 10

rgbLed = RGBLed(33, 35, 37)

def setup():
    print("Started GPIO Setup")
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)
    rgbLed.setup()
    GPIO.setup(PUSH_BUTTON, GPIO.IN)
    print("GPIO Setup Complete")


def speak(utterance_file):
    os.system('mpg123 -q {}audio/1sec.mp3 {}'.format(PATH, utterance_file))

def ttw(text):
    global RECORDING_WAV
    os.system('echo \"{}\" | text2wave -o {}'.format(text, RECORDING_WAV))
    return RECORDING_WAV

def greeting():
    global HELLO_MP3
    speak(HELLO_MP3)


def cleanup():
    print("Started GPIO Cleanup")
    try:
        GPIO.cleanup()
        exit()
    finally:
        print("Cleanup Complete")


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
    return not GPIO.input(PUSH_BUTTON)


def thinking(lock):
    while lock.locked():
        rgbLed.blink(Color.yellow)


def listen():
    global RECORDING_WAV
    global DEVICE
    recording = False
    rgbLed.on(Color.white)
    while True:
        if pressed():
            if recording:
                l, data = inp.read()
                if l:
                    audio += data
            else:
                inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE, alsaaudio.PCM_NORMAL, DEVICE)
                inp.setchannels(1)
                inp.setrate(16000)
                inp.setformat(alsaaudio.PCM_FORMAT_S16_LE)
                inp.setperiodsize(500)
                audio = ""
                l, data = inp.read()
                if l:
                    audio += data
                rgbLed.on(Color.green)
                print('Recording Started')
                recording = True
        elif recording:
            rf = open(RECORDING_WAV, 'w')
            rf.write(audio)
            rf.close()
            inp = None
            rgbLed.off()
            print('Recording Stopped')
            recording = False
            alexa(RECORDING_WAV)
            rgbLed.on(Color.white)


if __name__ == "__main__":
    opts, args = getopt.getopt(sys.argv[1:], 't:i', ['type=', 'input='])
    input_type = 'voice'
    for opt, arg in opts:
        if opt in ("-t", "--type"):
            input_type = arg
        if opt in ("-i", "--input"):
            input = arg
    setup()
    try:
        if internet_on():
            rgbLed.on(Color.blue)
            greeting()
            rgbLed.off()
            get_access_token()
            if input_type is 'voice':
                listen()
            elif input_type is 'audio_file':
                alexa(input)
            elif input_type is 'text':
                alexa(ttw(input))
        else:
            rgbLed.on(Color.red).on()
    finally:
        cleanup()
