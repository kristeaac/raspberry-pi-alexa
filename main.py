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


def greeting():
    os.system('mpg123 -q {}1sec.mp3 {}hello.mp3'.format(path, path))


def cleanup():
    GPIO.cleanup()
    exit()


def blink(pin, duration=3):
    GPIO.output(pin, True)
    time.sleep(duration)
    GPIO.output(pin, False)


def led_on(pin):
    GPIO.output(pin, True)


def led_off(pin):
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
    #GPIO.output(24, GPIO.HIGH)
    url = 'https://access-alexa-na.amazon.com/v1/avs/speechrecognizer/recognize'
    headers = {'Authorization': 'Bearer %s' % get_access_token()}
    d = {
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
    with open(path + 'recording.wav') as inf:
        files = [
            ('file', ('request', json.dumps(d), 'application/json; charset=UTF-8')),
            ('file', ('audio', inf, 'audio/L16; rate=16000; channels=1'))
        ]
        r = requests.post(url, headers=headers, files=files)
    if r.status_code == 200:
        for v in r.headers['content-type'].split(";"):
            if re.match('.*boundary.*', v):
                boundary = v.split("=")[1]
        data = r.content.split(boundary)
        for d in data:
            if (len(d) >= 1024):
                audio = d.split('\r\n\r\n')[1].rstrip('--')
        with open(path + "response.mp3", 'wb') as f:
            f.write(audio)
        # GPIO.output(25, GPIO.LOW)
        os.system('mpg123 -q {}1sec.mp3 {}response.mp3'.format(path, path))
        #GPIO.output(24, GPIO.LOW)
        # else:
        #     GPIO.output(lights, GPIO.LOW)
        #     for x in range(0, 3):
        #         time.sleep(.2)
        #         GPIO.output(25, GPIO.HIGH)
        #         time.sleep(.2)
        #         GPIO.output(lights, GPIO.LOW)


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
                led_on(green)
                print('recording started')
                recording = True
        elif recording:
            rf = open(path + 'recording.wav', 'w')
            rf.write(audio)
            rf.close()
            inp = None
            led_off(green)
            print('recording stopped')
            recording = False
            alexa()


if __name__ == "__main__":
    setup()
    try:
        # check internet connection
        if internet_on():
            # TODO would be nice to fade this blue in and out
            led_on(blue)
            greeting()
            led_off(blue)
        else:
            blink(red)
            cleanup()

        access_token = get_access_token()

        listen()

    except Exception:
        cleanup()
        raise
    cleanup()
