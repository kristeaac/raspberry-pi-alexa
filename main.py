import RPi.GPIO as GPIO
import os
import requests
from memcache import Client
import json
import alsaaudio
import re
import threading
from led import Led

REFRESH_TOKEN = os.environ['ALEXA_REFRESH_TOKEN']
CLIENT_ID = os.environ['ALEXA_CLIENT_ID']
CLIENT_SECRET = os.environ['ALEXA_CLIENT_SECRET']

PATH = os.path.realpath(__file__).rstrip(os.path.basename(__file__))

SERVERS = ["127.0.0.1:11211"]
CACHE = Client(SERVERS, debug=1)
DEVICE = "plughw:1"

HELLO_MP3 = PATH + 'hello.mp3'
RECORDING_WAV = PATH + 'recording.wav'
RESPONSE_MP3 = PATH + 'response.mp3'

PUSH_BUTTON = 10

# AVS
AVS_URL = 'https://access-alexa-na.amazon.com/v1/avs/speechrecognizer/recognize'
AVS_REQUEST_DATA = {
    "messageHeader": {
        "deviceContext": [
            {
                "name": "playbackState",
                "namespace": "AudioPlayer",
                "payload": {
                    "streamId": "",
                    "offsetInMilliseconds": "0",
                    "playerActivity": "IDLE"
                }
            }
        ]
    },
    "messageBody": {
        "profile": "alexa-close-talk",
        "locale": "en-us",
        "format": "audio/L16; rate=16000; channels=1"
    }
}

bad_led = Led(33) # red
recording_led = Led(35) # green
ok_led = Led(37) # blue
working_led = ok_led # until we add yellow
leds = [bad_led, recording_led, ok_led]

def setup():
    print("Started GPIO Setup")
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)
    for led in leds:
        led.setup()
    GPIO.setup(PUSH_BUTTON, GPIO.IN)
    print("GPIO Setup Complete")


def speak(utterance_file):
    os.system('mpg123 -q {}1sec.mp3 {}'.format(PATH, utterance_file))


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


def get_access_token():
    token = CACHE.get("access_token")
    global REFRESH_TOKEN
    if token:
        return token
    elif REFRESH_TOKEN:
        payload = {"client_id": CLIENT_ID, "client_secret": CLIENT_SECRET, "refresh_token": REFRESH_TOKEN,
                   "grant_type": "refresh_token", }
        url = "https://api.amazon.com/auth/o2/token"
        r = requests.post(url, data=payload)
        resp = json.loads(r.text)
        CACHE.set("access_token", resp['access_token'], 3570)
        return resp['access_token']
    else:
        return False


def pressed():
    return not GPIO.input(PUSH_BUTTON)


def thinking(lock):
    while lock.locked():
        working_led.blink()


def alexa():
    global AVS_URL
    global AVS_REQUEST_DATA
    global RECORDING_WAV
    global RESPONSE_MP3

    lock = threading.Lock()
    lock.acquire()
    thinking_thread = threading.Thread(target=thinking, args=(lock, ))
    thinking_thread.start()

    try:
        print("Alexa is Thinking")

        headers = {'Authorization': 'Bearer %s' % get_access_token()}

        with open(RECORDING_WAV) as inf:
            files = [
                ('file', ('request', json.dumps(AVS_REQUEST_DATA), 'application/json; charset=UTF-8')),
                ('file', ('audio', inf, 'audio/L16; rate=16000; channels=1'))
            ]
            response = requests.post(AVS_URL, headers=headers, files=files)
        if response.status_code == 200:
            for v in response.headers['content-type'].split(";"):
                if re.match('.*boundary.*', v):
                    boundary = v.split("=")[1]
            response_ata = response.content.split(boundary)
            for d in response_ata:
                if len(d) >= 1024:
                    audio = d.split('\r\n\r\n')[1].rstrip('--')
            with open(RESPONSE_MP3, 'wb') as f:
                f.write(audio)
            lock.release()  # stop blinking
            print("Alexa is Ready to Speak")
            working_led.on()
            speak(RESPONSE_MP3)
            working_led.off()
        print("Alexa has Handled the Request")
    finally:
        if lock and lock.locked():
            lock.release()


def listen():
    recording = False
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
                recording_led.on()
                print('Recording Started')
                recording = True
        elif recording:
            rf = open(RECORDING_WAV, 'w')
            rf.write(audio)
            rf.close()
            inp = None
            recording_led.off()
            print('Recording Stopped')
            recording = False
            alexa()


if __name__ == "__main__":
    setup()
    try:
        if internet_on():
            ok_led.on()
            greeting()
            ok_led.off()
            get_access_token()
            listen()
        else:
            bad_led.off()
    finally:
        cleanup()