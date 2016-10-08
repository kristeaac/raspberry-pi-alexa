## About this project
This project is an example of an Alexa-enabled Raspberry Pi using the [Alexa Voice Service (AVS)](https://developer.amazon.com/alexa-voice-service) and a [Raspberry Pi 3 Model B](https://www.amazon.com/Raspberry-Pi-RASP-PI-3-Model-Motherboard/dp/B01CD5VC92).

## Setup
### Hardware
A pushbutton and an RGB LED wired to the Raspberry Pi are used interface with Alexa. Similar to [the Amazon Tap](https://www.amazon.com/Amazon-Tap-Alexa-Enabled-Portable-Bluetooth/dp/B01BH83OOM), this device is not "always listening", but rather, you have to press and hold the pushbutton while speaking. The LED indicates the current state of the client:
* **blue** - starting up
* **red** - no internet connection
* **white** - ready
* **green** - recording speech
* **blinking yellow** - posting Speech to Alexa and waiting for response
* **solid yellow** - playing response from Alexa

### Software
Follow [this tutorial]([the video tutorial](https://www.youtube.com/watch?v=frH9HaQTFL8)) for a one-time install of the necessary dependencies for this project, and for obtaining the client credentials and refresh token needed to call AVS.

Once you have your client credentials and refresh token, add them as environment variables:

```
$ export ALEXA_REFRESH_TOKEN="<YOUR_REFRESH_TOKEN>"
$ export ALEXA_CLIENT_ID="<YOUR_CLIENT_ID>"
$ export ALEXA_CLIENT_SECRET="<YOUR_CLIENT_SECRET>"
```

These environment variables are needed in [main.py](main.py) to obtain an AVS access token:

```
REFRESH_TOKEN = os.environ['ALEXA_REFRESH_TOKEN']
CLIENT_ID = os.environ['ALEXA_CLIENT_ID']
CLIENT_SECRET = os.environ['ALEXA_CLIENT_SECRET']
```

Now just run `python main.py` to start your Alexa client.

## Thanks
Special thanks to Novaspirit Tech for [the video tutorial](https://www.youtube.com/watch?v=frH9HaQTFL8) on setting up AVS on the Pi, and the [AlexaPi tutorial](https://github.com/novaspirit/AlexaPi/) it references. A lot of the logic in this project is taken directly from AlexaPi.
