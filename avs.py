import requests
from memcache import Client
import os
import json
import re

REFRESH_TOKEN = os.environ['ALEXA_REFRESH_TOKEN']
CLIENT_ID = os.environ['ALEXA_CLIENT_ID']
CLIENT_SECRET = os.environ['ALEXA_CLIENT_SECRET']

SERVERS = ["127.0.0.1:11211"]
CACHE = Client(SERVERS, debug=1)

PATH = os.path.realpath(__file__).rstrip(os.path.basename(__file__))
RESPONSE_MP3 = PATH + 'audio/response.mp3'

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


def noop():
    pass


def alexa(recording, start_thinking_callback=noop, end_thinking_callback=noop):
    global AVS_URL
    global AVS_REQUEST_DATA
    global RESPONSE_MP3

    start_thinking_callback()

    print("Alexa is Thinking")

    headers = {'Authorization': 'Bearer %s' % get_access_token()}

    with open(recording) as inf:
        files = [
            ('file', ('request', json.dumps(AVS_REQUEST_DATA), 'application/json; charset=UTF-8')),
            ('file', ('audio', inf, 'audio/L16; rate=16000; channels=1'))
        ]
        response = requests.post(AVS_URL, headers=headers, files=files)
    print(response.status_code)
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
        end_thinking_callback(RESPONSE_MP3)
    print("Alexa has Handled the Request")
