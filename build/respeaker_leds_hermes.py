#!/usr/bin/env python3

import argparse
import json
import logging
import paho.mqtt.client as mqtt
import pixels
import socket
import yaml
from os import getpid, path
from time import sleep

def on_message(client, userdata, msg):
    logging.debug(f"{msg.topic} {str(msg.qos)} {msg.payload.decode('utf-8')}")
    payload = json.loads(msg.payload)
    logging.debug(payload)

    try:
        if payload["siteId"] == config["site_id"]:
            if msg.topic == "hermes/dialogueManager/sessionStarted":
                logging.debug("haha Rhasspy go brrrrr")
                leds.wakeup()

            if msg.topic == "hermes/nlu/query":
                logging.debug("Rhasspy is thinking...")
                leds.think()

            if msg.topic == "hermes/nlu/intentParsed":
                logging.debug("Rhasspy thunk")
                leds.off()

            if msg.topic == "hermes/tts/say":
                logging.debug(f'Rhasspy said "{payload["text"]}"')
                leds.speak()
            if msg.topic == "hermes/tts/sayFinished":
                logging.debug("Rhasspy is finished speaking")
                leds.off()

            if msg.topic == "hermes/dialogueManager/sessionEnded":
               if payload["termination"]["reason"] == "intentNotRecognized":
                    logging.debug("Rhasspy did not understand you")
               elif payload["termination"]["reason"] == "timeout":
                    logging.debug("Rhasspy timed out waiting for you. Try being faster.")

               logging.debug("Rhasspy is so done")
               leds.off()

    except Exception as e:
        logging.error(f"haha exception go crashhh: {str(e)}")


def on_connect(client, userdata, flags, rc):
    logging.info("Connected to MQTT broker, subscribing to topics...")
    for topic in config["topics"]:
        client.subscribe(topic, config["qos"] if "qos" in config and config["qos"] else 0)


def on_disconnect(client, userdata, rc):
    logging.info("Haha MQTT client go crashhh")
    sleep(10)


# Start program
CONFIG = path.join(path.dirname(path.abspath(__file__)), "config.yml")

# Load config
try:
    with open(CONFIG, "r") as file:
        config = yaml.load(file, Loader=yaml.FullLoader)
except Exception as e:
    logging.error(f"Cannot log configuration from {CONFIG}:\n{str(e)}")

# Configure logging
LOGFORMAT = "%(asctime)s: %(message)s"
DEBUG = config["debug"] if "debug" in config else False
if DEBUG:
    logging.basicConfig(level=logging.DEBUG, format=LOGFORMAT)
else:
    logging.basicConfig(level=logging.INFO, format=LOGFORMAT)

logging.info("Starting...")
logging.debug("DEBUG MODE")

if "site_id" not in config or not config["site_id"]:
    logging.error("No site ID. Aborting")
    exit(1)
if "topics" not in config or not config["topics"]:
    logging.info("No topic list. Aborting")
    exit(2)

# Get and parse arguments
parser = argparse.ArgumentParser()
parser.add_argument("--google_home", action="store_true", help="Use the Google Home LED pattern")
args = parser.parse_args()

# Initialize LED controller
leds = pixels.Pixels()  # defauts to Alexa LED pattern
if args.google_home:
    leds.pattern = pixels.GoogleHomeLedPattern(show=leds.show)

# Initialize client
client_id = config["client_id"] if "client_id" in config and config["client_id"] else f"hermes-respeaker-leds_{getpid()}"
client = mqtt.Client(client_id=client_id)

# Attach callbacks
client.on_message = on_message
client.on_connect = on_connect
client.on_disconnect = on_disconnect

# Set will and reconnect delay
#client.will_set('clients/hermes-respeaker-leds', payload="unavailable", qos=0, retain=False)
# Delays will be: 3, 6, 12, 24, 30, 30, ...
#client.reconnect_delay_set(delay=3, delay_max=30, exponential_backoff=True)

# Set credentials
if "username" in config and config["username"]:
    client.username_pw_set(config["username"], config["password"])

# Finally, connect
client.connect(config["hostname"], config["port"] if "port" in config and config["port"] else 1883, 60)

while True:
    try:
        client.loop_forever()
    except socket.error:
        sleep(5)
    except KeyboardInterrupt:
        exit(0)
