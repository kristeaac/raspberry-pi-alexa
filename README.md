## About this project
This project is an example of an Alexa-enabled Raspberry Pi using the [Alexa Voice Service (AVS)](https://developer.amazon.com/alexa-voice-service) and a [Raspberry Pi 3 Model B](https://www.amazon.com/Raspberry-Pi-RASP-PI-3-Model-Motherboard/dp/B01CD5VC92).

## Setup
### Hardware
A [pushbutton](https://www.amazon.com/6x6x6mm-Momentary-Push-Button-Switch/dp/B01GN79QF8) and an [RGB LED](https://www.amazon.com/DIY-3-Color-RGB-Module-Arduino/dp/B0100A92BC) wired to the Raspberry Pi are used to interface with Alexa. Similar to [the Amazon Tap](https://www.amazon.com/Amazon-Tap-Alexa-Enabled-Portable-Bluetooth/dp/B01BH83OOM), this device is not "always listening", but rather, you have to press and hold the pushbutton while speaking. The LED indicates the current state of the client:
* __blue__ - starting up
* __red__ - no internet connection
* __white__ - ready
* __green__ - recording speech
* __blinking yellow__ - posting Speech to Alexa and waiting for response
* __solid yellow__ - playing response from Alexa

#### Wiring
* The __RGB LED__ is wired to pins 33, 35, and 37 on the Raspberry Pi in [buttons.py](buttons.py#L10) and [main.py](main.py#L20)
* The __pushbutton__ is wired to pin 10 in [main.py](main.py#L18) and [buttons.py](buttons.py#L8)

### Software
Follow [this tutorial](https://www.youtube.com/watch?v=frH9HaQTFL8) for a one-time install of the necessary dependencies for this project, and for obtaining the client credentials and refresh token needed to call AVS.

Once you have your client credentials and refresh token, set them as environment variables on your Pi:

```
$ export ALEXA_REFRESH_TOKEN="<YOUR_REFRESH_TOKEN>"
$ export ALEXA_CLIENT_ID="<YOUR_CLIENT_ID>"
$ export ALEXA_CLIENT_SECRET="<YOUR_CLIENT_SECRET>"
```

These environment variables are needed in [avs.py](avs.py#L7-L9) to obtain an AVS access token:

```
REFRESH_TOKEN = os.environ['ALEXA_REFRESH_TOKEN']
CLIENT_ID = os.environ['ALEXA_CLIENT_ID']
CLIENT_SECRET = os.environ['ALEXA_CLIENT_SECRET']
```

Now just run `python main.py` to start your Alexa client.

## Thanks
Special thanks to Novaspirit Tech for [the video tutorial](https://www.youtube.com/watch?v=frH9HaQTFL8) on setting up AVS on the Pi, and the [AlexaPi tutorial](https://github.com/novaspirit/AlexaPi/) it references. A lot of the logic in this project is taken directly from AlexaPi.
