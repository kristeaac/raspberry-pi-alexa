import RPi.GPIO as GPIO
import time
import os
import requests
from memcache import Client
import json
import alsaaudio
import re

refresh_token = os.environ['ALEXA_REFRESH_TOKEN']
client_id = os.environ['ALEXA_CLIENT_ID']
client_secret = os.environ['ALEXA_CLIENT_SECRET']

path = os.path.realpath(__file__).rstrip(os.path.basename(__file__))

servers = ["127.0.0.1:11211"]
mc = Client(servers, debug=1)
device = "plughw:1"  # Name of your microphone/soundcard in arecord -L

push_button = 10

class RGBLed:

    def __init__(self, red, green, blue):
        self.pins = [red, green, blue]
        self.red = [red]
        self.green = [green]
        self.blue = [blue]
        self.cyan = [green, blue]
        self.magenta = [red, blue]
        self.yellow = [red, green]
        self.white = [red, green, blue]

    def setup(self):
        for pin in self.pins:
            GPIO.setup(pin, GPIO.OUT)

    def on(self, color):
        for pin in color:
            GPIO.output(pin, True)

    def off(self):
        for pin in self.pins:
            GPIO.output(pin, False)

    def blink(self, color, duration=.5, count=1):
        for i in range(count):
            self.on(color)
            time.sleep(duration)
            self.off()
            time.sleep(duration)

rgbLed = RGBLed(33, 35, 37)

# AVS
url = 'https://access-alexa-na.amazon.com/v1/avs/speechrecognizer/recognize'
request_data = {
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

def setup():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)
    rgbLed.setup()
    GPIO.setup(push_button, GPIO.IN)


def greeting():
    os.system('mpg123 -q {}1sec.mp3 {}hello.mp3'.format(path, path))


def cleanup():
    GPIO.cleanup()
    exit()


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
    token = mc.get("access_token")
    global refresh_token
    if token:
        return token
    elif refresh_token:
        payload = {"client_id": client_id, "client_secret": client_secret, "refresh_token": refresh_token,
                   "grant_type": "refresh_token", }
        url = "https://api.amazon.com/auth/o2/token"
        r = requests.post(url, data=payload)
        resp = json.loads(r.text)
        mc.set("access_token", resp['access_token'], 3570)
        return resp['access_token']
    else:
        return False


def pressed():
    return not GPIO.input(push_button)


def alexa():
    rgbLed.on(rgbLed.yellow)
    global url
    global request_data

    headers = {'Authorization': 'Bearer %s' % get_access_token()}

    with open(path + 'recording.wav') as inf:
        files = [
            ('file', ('request', json.dumps(request_data), 'application/json; charset=UTF-8')),
            ('file', ('audio', inf, 'audio/L16; rate=16000; channels=1'))
        ]
        response = requests.post(url, headers=headers, files=files)
    if response.status_code == 200:
        for v in response.headers['content-type'].split(";"):
            if re.match('.*boundary.*', v):
                boundary = v.split("=")[1]
        response_ata = response.content.split(boundary)
        for d in response_ata:
            if (len(d) >= 1024):
                audio = d.split('\r\n\r\n')[1].rstrip('--')
        with open(path + "response.mp3", 'wb') as f:
            f.write(audio)
        rgbLed.off()
        os.system('mpg123 -q {}1sec.mp3 {}response.mp3'.format(path, path))


def listen():
    recording = False
    while True:
        if pressed():
            if recording:
                l, data = inp.read()
                if l:
                    audio += data
            else:
                inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE, alsaaudio.PCM_NORMAL, device)
                inp.setchannels(1)
                inp.setrate(16000)
                inp.setformat(alsaaudio.PCM_FORMAT_S16_LE)
                inp.setperiodsize(500)
                audio = ""
                l, data = inp.read()
                if l:
                    audio += data
                rgbLed.on(rgbLed.green)
                print('recording started')
                recording = True
        elif recording:
            rf = open(path + 'recording.wav', 'w')
            rf.write(audio)
            rf.close()
            inp = None
            rgbLed.off()
            print('recording stopped')
            recording = False
            alexa()


if __name__ == "__main__":
    setup()
    try:
        # check internet connection
        if internet_on():
            # TODO would be nice to fade this blue in and out
            rgbLed.on(rgbLed.blue)
            greeting()
            rgbLed.off()
        else:
            rgbLed.blink(rgbLed.red)
            cleanup()

        get_access_token()

        listen()

    except Exception:
        cleanup()
        raise
    cleanup()
