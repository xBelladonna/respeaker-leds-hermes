#!/usr/bin/env python3

import pixels
import time

leds = pixels.Pixels()  # Alexa LED pattern by default
#leds.pattern = pixels.GoogleHomeLedPattern(show=leds.show)

while True:
    try:
        leds.wakeup()
        time.sleep(3)

        leds.think()
        time.sleep(3)

        leds.speak()
        time.sleep(6)

        leds.off()
        time.sleep(3)
    except KeyboardInterrupt:
        break

leds.off()
