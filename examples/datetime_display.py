#!/usr/bin/env python
import time
import random
from datetime import datetime

from luma.led_matrix.device import max7219
from luma.core.interface.serial import spi, noop
from luma.core.render import canvas
from luma.core.legacy import text, show_message
from luma.core.legacy.font import proportional, CP437_FONT, TINY_FONT, SINCLAIR_FONT


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

STAR_W = 32
STAR_H = 8
NUM_STARS = 15


def stars_init():
    return [[random.randint(0, STAR_W - 1), random.randint(0, STAR_H - 1), random.randint(1, 3)] for _ in range(NUM_STARS)]


def stars_update(stars):
    for s in stars:
        s[2] += 1
        if s[2] > 6:
            s[0] = random.randint(0, STAR_W - 1)
            s[1] = random.randint(0, STAR_H - 1)
            s[2] = 1


def starfield(device, frames=30):
    stars = stars_init()
    for _ in range(frames):
        with canvas(device) as draw:
            for s in stars:
                intensity = min(255, (s[2] * 40))
                color = (intensity >> 4) & 0xF
                draw.point((s[0], s[1]), fill="white")
        stars_update(stars)
        time.sleep(0.08)


def breathe(device, steps=10, delay=0.04):
    for intensity in range(0, 16 * steps):
        device.contrast(intensity // steps)
        time.sleep(delay)
    for intensity in range(16 * steps, -1, -1):
        device.contrast(intensity // steps)
        time.sleep(delay)


def minute_change(device):
    hours = datetime.now().strftime('%H')
    minutes = datetime.now().strftime('%M')

    def helper(current_y):
        with canvas(device) as draw:
            text(draw, (0, 1), hours, fill="white", font=proportional(CP437_FONT))
            text(draw, (15, 1), ":", fill="white", font=proportional(TINY_FONT))
            text(draw, (17, current_y), minutes, fill="white", font=proportional(CP437_FONT))
        time.sleep(0.1)
    for current_y in range(1, 9):
        helper(current_y)
    minutes = datetime.now().strftime('%M')
    for current_y in range(9, 1, -1):
        helper(current_y)


def animation(device, from_y, to_y):
    hourstime = datetime.now().strftime('%H')
    mintime = datetime.now().strftime('%M')
    current_y = from_y
    while current_y != to_y:
        with canvas(device) as draw:
            text(draw, (0, current_y), hourstime, fill="white", font=proportional(CP437_FONT))
            text(draw, (15, current_y), ":", fill="white", font=proportional(TINY_FONT))
            text(draw, (17, current_y), mintime, fill="white", font=proportional(CP437_FONT))
        time.sleep(0.1)
        current_y += 1 if to_y > from_y else -1


def scroll_date(device):
    now = datetime.now()
    date_str = now.strftime("%d %b %Y %a")
    animation(device, 1, 8)
    show_message(device, date_str, fill="white", font=proportional(CP437_FONT))
    animation(device, 8, 1)


def show_fun_message(device):
    msg = random.choice(COOL_MSGS)
    animation(device, 1, 8)
    show_message(device, msg, fill="white", font=proportional(SINCLAIR_FONT))
    animation(device, 8, 1)


def main():
    serial = spi(port=0, device=0, gpio=noop())
    device = max7219(serial, cascaded=4, block_orientation=-90, blocks_arranged_in_reverse_order=False)
    device.contrast(16)

    starfield(device, 25)

    animation(device, 8, 1)

    toggle = False
    last_min = -1
    fun_countdown = random.randint(3, 6)

    while True:
        toggle = not toggle
        now = datetime.now()
        sec = now.second
        minute = now.minute

        if minute != last_min:
            last_min = minute
            fun_countdown -= 1
            if fun_countdown == 0:
                breathe(device, 6, 0.03)
                fun_countdown = random.randint(3, 6)

        if sec == 59:
            minute_change(device)
        elif sec == 30:
            scroll_date(device)
        elif fun_countdown == 0 and sec % 10 == 0:
            show_fun_message(device)
            fun_countdown = random.randint(3, 6)
        else:
            hours = now.strftime('%H')
            minutes = now.strftime('%M')
            with canvas(device) as draw:
                text(draw, (0, 1), hours, fill="white", font=proportional(CP437_FONT))
                text(draw, (15, 1), ":" if toggle else " ", fill="white", font=proportional(TINY_FONT))
                text(draw, (17, 1), minutes, fill="white", font=proportional(CP437_FONT))
            time.sleep(0.5)


if __name__ == "__main__":
    main()
