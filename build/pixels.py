# Copyright (C) 2017 Seeed Technology Limited
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import numpy
from apa102 import APA102
from gpiozero import LED
from threading import Thread
from time import sleep
try:
    from queue import Queue
except ImportError:
    from Queue import Queue


class AlexaLedPattern(object):
    def __init__(self, show=None, number=12):
        self.pixels_number = number
        self.pixels = [0] * 4 * number

        if not show or not callable(show):
            def dummy(data):
                pass
            show = dummy

        self.show = show
        self.stop = False

    def wakeup(self, direction=0):
        position = int((direction + 15) /
                       (360 / self.pixels_number)) % self.pixels_number

        pixels = [0, 0, 0, 24] * self.pixels_number
        pixels[position * 4 + 2] = 48

        self.show(pixels)

    def listen(self):
        pixels = [0, 0, 0, 24] * self.pixels_number

        self.show(pixels)

    def think(self):
        pixels = [0, 0, 12, 12, 0, 0, 0, 24] * self.pixels_number

        while not self.stop:
            self.show(pixels)
            sleep(0.2)
            pixels = pixels[-4:] + pixels[:-4]

    def speak(self):
        step = 1
        position = 12
        while not self.stop:
            pixels = [0, 0, position, 24 - position] * self.pixels_number
            self.show(pixels)
            sleep(0.01)
            if position <= 0:
                step = 1
                sleep(0.4)
            elif position >= 12:
                step = -1
                sleep(0.4)

            position += step

    def off(self):
        self.show([0] * 4 * 12)


class GoogleHomeLedPattern(object):
    def __init__(self, show=None):
        self.basis = numpy.array([0] * 4 * 12)
        self.basis[0 * 4 + 1] = 2
        self.basis[3 * 4 + 1] = 1
        self.basis[3 * 4 + 2] = 1
        self.basis[6 * 4 + 2] = 2
        self.basis[9 * 4 + 3] = 2

        self.pixels = self.basis * 24

        if not show or not callable(show):
            def dummy(data):
                pass
            show = dummy

        self.show = show
        self.stop = False

    def wakeup(self, direction=0):
        position = int((direction + 15) / 30) % 12

        basis = numpy.roll(self.basis, position * 4)
        for i in range(1, 25):
            pixels = basis * i
            self.show(pixels)
            sleep(0.005)

        pixels = numpy.roll(pixels, 4)
        self.show(pixels)
        sleep(0.1)

        for i in range(2):
            new_pixels = numpy.roll(pixels, 4)
            self.show(new_pixels * 0.5 + pixels)
            pixels = new_pixels
            sleep(0.1)

        self.show(pixels)
        self.pixels = pixels

    def listen(self):
        pixels = self.pixels
        for i in range(1, 25):
            self.show(pixels * i / 24)
            sleep(0.01)

    def think(self):
        pixels = self.pixels

        while not self.stop:
            pixels = numpy.roll(pixels, 4)
            self.show(pixels)
            sleep(0.2)

        t = 0.1
        for i in range(0, 5):
            pixels = numpy.roll(pixels, 4)
            self.show(pixels * (4 - i) / 4)
            sleep(t)
            t /= 2

        self.pixels = pixels

    def speak(self):
        pixels = self.pixels
        step = 1
        brightness = 5
        while not self.stop:
            self.show(pixels * brightness / 24)
            sleep(0.02)

            if brightness <= 5:
                step = 1
                sleep(0.4)
            elif brightness >= 24:
                step = -1
                sleep(0.4)

            brightness += step

    def off(self):
        self.show([0] * 4 * 12)


class Pixels:
    NUM_LEDS = 12
    PIN_MOSI = 10
    PIN_SCLK = 11
    PIN_SEL = 7  # CE1
    brightness = 5

    def __init__(self, pattern=AlexaLedPattern):
        self.pattern = pattern(show=self.show)

        self.dev = APA102(num_led=self.NUM_LEDS)

        self.power = LED(5)
        self.power.on()

        self.queue = Queue()
        self.thread = Thread(target=self._run)
        self.thread.daemon = True
        self.thread.start()

        self.last_direction = None

    def wakeup(self, direction=0):
        self.last_direction = direction

        def f():
            self.pattern.wakeup(direction)

        self.put(f)

    def listen(self):
        if self.last_direction:
            def f():
                self.pattern.wakeup(self.last_direction)
            self.put(f)
        else:
            self.put(self.pattern.listen)

    def think(self):
        self.put(self.pattern.think)

    def speak(self):
        self.put(self.pattern.speak)

    def off(self):
        self.put(self.pattern.off)

    def put(self, func):
        self.pattern.stop = True
        self.queue.put(func)

    def _run(self):
        while True:
            func = self.queue.get()
            self.pattern.stop = False
            func()

    def show(self, data):
        for i in range(self.NUM_LEDS):
            self.dev.set_pixel(i, int(data[4*i + 1]), int(data[4*i + 2]), int(data[4*i + 3]))

        self.dev.show()
