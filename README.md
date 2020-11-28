# hermes-respeaker-leds

Drives the APA102 LED ring on the ReSpeaker 4 mic array for Raspberry Pi using queues from Hermes protocol MQTT traffic.
Designed for use with Snips (RIP) or Rhasspy, both which use the Hermes MQTT protocol.

## Installing and running

### With Docker

1. Create a `config.yml`: `cp build/config.yml.example build/config.yml # edit and insert your own settings`
2. Build the image: `docker build . -t hermes-respeaker-leds`
3. Run the image:
```sh
docker run -d --device /dev/gpiomem --device /dev/spidev0.1 hermes-respeaker-leds
```

### Manually

1. Create a `config.yml`: `cp build/config.yml.example build/config.yml # edit and insert your own settings`
2. Install requirements: `pip install -r build/requirements.txt && pip install numpy`
3. Run app: `python build/hermes_respeaker_leds.py`

---

By default the app will use the Alexa LED pattern. The Google Home LED pattern can be used by specifying the `--google_home` flag:
```
python build/hermes_respeaker_leds.py --google_home
```
