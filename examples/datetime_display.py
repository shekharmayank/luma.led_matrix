#!/usr/bin/env python
import time
import random
from datetime import datetime

from luma.led_matrix.device import max7219
from luma.core.interface.serial import spi, noop
from luma.core.render import canvas
from luma.core.legacy import text
from luma.core.legacy.font import proportional, TINY_FONT


COOL_MSGS = [
    "HELLO WORLD",
    "KEEP GOING",
    "SMILE :D",
    "BE BRAVE",
    "DREAM BIG",
    "STAY GOLD",
    "MAKE ART",
    "CODE ON",
    "BE KIND",
    "CARPE DIEM",
]


def random_bottom_text():
    now = datetime.now()
    r = random.randint(0, 4)
    if r == 0:
        return now.strftime("%a %d %b")
    elif r == 1:
        return random.choice(COOL_MSGS)
    elif r == 2:
        return now.strftime("%d %b %Y")
    elif r == 3:
        return random.choice(COOL_MSGS)
    else:
        return now.strftime("%I:%M %p").lstrip("0").lower()


def starfield(device, frames=30):
    w, h = device.width, device.height
    stars = [[random.randint(0, w - 1), random.randint(0, h - 1),
              random.randint(1, 3)] for _ in range(15)]
    for _ in range(frames):
        with canvas(device) as draw:
            for s in stars:
                draw.point((s[0], s[1]), fill="white")
            for s in stars:
                s[2] += 1
                if s[2] > 6:
                    s[0] = random.randint(0, w - 1)
                    s[1] = random.randint(0, h - 1)
                    s[2] = 1
        time.sleep(0.08)


def breathe(device, steps=8, delay=0.03):
    for i in range(0, 16 * steps):
        device.contrast(i // steps)
        time.sleep(delay)
    for i in range(16 * steps, -1, -1):
        device.contrast(i // steps)
        time.sleep(delay)


def main():
    serial = spi(port=0, device=0, gpio=noop())
    device = max7219(serial, cascaded=4, block_orientation=-90,
                     blocks_arranged_in_reverse_order=False)
    device.contrast(16)

    starfield(device, 25)

    toggle = False
    bottom_msg = random_bottom_text()
    msg_ticks = 0
    breath_ticks = 0

    while True:
        toggle = not toggle
        now = datetime.now()
        sec = now.second

        msg_ticks += 1
        if msg_ticks >= 24:
            msg_ticks = 0
            bottom_msg = random_bottom_text()

        breath_ticks += 1
        if breath_ticks >= 240:
            breath_ticks = 0
            breathe(device, 6, 0.02)

        hours = now.strftime('%H')
        minutes = now.strftime('%M')

        with canvas(device) as draw:
            text(draw, (0, 0), hours, fill="white", font=proportional(TINY_FONT))
            text(draw, (12, 0), ":" if toggle else " ",
                 fill="white", font=proportional(TINY_FONT))
            text(draw, (15, 0), minutes, fill="white", font=proportional(TINY_FONT))
            text(draw, (0, 4), bottom_msg, fill="white", font=proportional(TINY_FONT))

        time.sleep(0.5)


if __name__ == "__main__":
    main()
