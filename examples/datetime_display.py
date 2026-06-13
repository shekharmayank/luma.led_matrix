#!/usr/bin/env python
import time
import random
from datetime import datetime

from luma.led_matrix.device import max7219
from luma.core.interface.serial import spi, noop
from luma.core.render import canvas
from luma.core.legacy import text, show_message
from luma.core.legacy.font import proportional, CP437_FONT, TINY_FONT


WIDTH, HEIGHT = 32, 8

COOL_MSGS = [
    "HELLO WORLD", "KEEP GOING", "SMILE :D", "BE BRAVE",
    "DREAM BIG", "STAY GOLD", "MAKE ART", "CODE ON",
    "BE KIND", "CARPE DIEM", "WOW", "NICE",
]


def starfield(device, frames=30):
    stars = [[random.randint(0, WIDTH - 1), random.randint(0, HEIGHT - 1),
              random.randint(1, 4)] for _ in range(20)]
    for _ in range(frames):
        with canvas(device) as draw:
            for s in stars:
                draw.point((s[0], s[1]), fill="white")
                s[2] += 1
                if s[2] > 6:
                    s[0] = random.randint(0, WIDTH - 1)
                    s[1] = random.randint(0, HEIGHT - 1)
                    s[2] = 1
        time.sleep(0.06)


def type_in(device, full, y=1):
    for i in range(1, len(full) + 1):
        with canvas(device) as draw:
            text(draw, (0, y), full[:i], fill="white", font=proportional(CP437_FONT))
        time.sleep(0.12)


def slide_minutes(device, hours, old_m, new_m):
    for offset in range(0, 16):
        with canvas(device) as draw:
            text(draw, (0, 1), hours, fill="white", font=proportional(CP437_FONT))
            text(draw, (15, 1), ":", fill="white", font=proportional(TINY_FONT))
            text(draw, (17 - offset, 1), old_m, fill="white", font=proportional(CP437_FONT))
            text(draw, (17 + 16 - offset, 1), new_m, fill="white", font=proportional(CP437_FONT))
        time.sleep(0.02)


def slide_whole(device, old_str, new_str):
    for offset in range(0, 36):
        with canvas(device) as draw:
            text(draw, (0 - offset, 1), old_str, fill="white", font=proportional(CP437_FONT))
            text(draw, (36 - offset, 1), new_str, fill="white", font=proportional(CP437_FONT))
        time.sleep(0.02)


def matrix_rain(device, frames=50):
    drops = [{'x': random.randint(0, WIDTH - 1), 'y': random.uniform(-4, 0),
              'len': random.randint(2, 5)} for _ in range(WIDTH)]
    for _ in range(frames):
        with canvas(device) as draw:
            for d in drops:
                for i in range(d['len']):
                    y = int(d['y'] - i)
                    if 0 <= y < HEIGHT:
                        draw.point((d['x'], y), fill="white")
                d['y'] += 0.6
                if d['y'] > HEIGHT + d['len']:
                    d['x'] = random.randint(0, WIDTH - 1)
                    d['y'] = random.uniform(-4, 0)
        time.sleep(0.04)


def firework(device, frames=15):
    cx, cy = random.randint(4, WIDTH - 4), random.randint(2, HEIGHT - 2)
    pts = [(random.uniform(-0.8, 0.8), random.uniform(-0.8, 0.8)) for _ in range(8)]
    for f in range(frames):
        with canvas(device) as draw:
            for dx, dy in pts:
                px = int(cx + dx * f * 0.4)
                py = int(cy + dy * f * 0.4)
                if 0 <= px < WIDTH and 0 <= py < HEIGHT:
                    draw.point((px, py), fill="white")
        time.sleep(0.04)


def main():
    serial = spi(port=0, device=0, gpio=noop())
    device = max7219(serial, cascaded=4, block_orientation=-90,
                     blocks_arranged_in_reverse_order=False)
    device.contrast(16)

    starfield(device, 30)
    type_in(device, datetime.now().strftime("%H:%M"))
    time.sleep(0.5)

    toggle = False
    last_min = -1
    msg_due = random.randint(4, 8)

    while True:
        toggle = not toggle
        now = datetime.now()
        sec = now.second
        minute = now.minute
        hours = now.strftime('%H')
        minutes = now.strftime('%M')

        if minute != last_min:
            if last_min >= 0:
                old_m = f"{last_min:02d}"
                old_h = int(hours)
                if minute == 0:
                    old_h = (old_h - 1) % 24
                old_h_str = f"{old_h:02d}"
                if old_h_str != hours:
                    slide_whole(device, f"{old_h_str}:{old_m}", f"{hours}:{minutes}")
                else:
                    slide_minutes(device, hours, old_m, minutes)
                firework(device, 10)
            last_min = minute
            continue

        if sec == 0:
            show_message(device, now.strftime("%d %b %Y %a"),
                         fill="white", font=proportional(CP437_FONT))
            continue

        if sec == 35:
            matrix_rain(device, 40)
            continue

        if sec == 20:
            if msg_due <= 0:
                msg_due = random.randint(4, 8)
                show_message(device, random.choice(COOL_MSGS),
                             fill="white", font=proportional(TINY_FONT))
                continue
            msg_due -= 1

        if sec % 10 == 0 and sec != 0 and sec != 20:
            firework(device, 10)

        with canvas(device) as draw:
            text(draw, (0, 1), hours, fill="white", font=proportional(CP437_FONT))
            text(draw, (15, 1), ":" if toggle else " ",
                 fill="white", font=proportional(TINY_FONT))
            text(draw, (17, 1), minutes, fill="white", font=proportional(CP437_FONT))
            if random.random() < 0.15:
                draw.point((random.randint(0, WIDTH - 1), random.randint(0, HEIGHT - 1)),
                           fill="white")
        time.sleep(0.5)


if __name__ == "__main__":
    main()
