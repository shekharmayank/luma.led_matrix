#!/usr/bin/env python
import time
import random
import math
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


def starfield(device, frames=200):
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
        time.sleep(0.05)


def type_in(device, full, y=1):
    for i in range(1, len(full) + 1):
        with canvas(device) as draw:
            text(draw, (0, y), full[:i], fill="white", font=proportional(CP437_FONT))
        time.sleep(0.1)


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


def matrix_rain(device, duration=14):
    drops = [{'x': random.randint(0, WIDTH - 1), 'y': random.uniform(-4, 0),
              'len': random.randint(2, 5)} for _ in range(WIDTH)]
    frames = int(duration / 0.04)
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


def galaxy(device, duration=12):
    stars = []
    for _ in range(30):
        stars.append({
            'angle': random.uniform(0, 2 * math.pi),
            'speed': random.uniform(0.3, 1.2),
            'life': random.randint(10, 40),
        })
    frames = int(duration / 0.05)
    for f in range(frames):
        with canvas(device) as draw:
            for s in stars:
                s['angle'] += 0.05 * s['speed']
                r = min(f * 0.12, 5)
                px = int(WIDTH // 2 + math.cos(s['angle']) * r)
                py = int(HEIGHT // 2 + math.sin(s['angle']) * r)
                draw.point((px, py), fill="white")
                s['life'] -= 1
                if s['life'] <= 0:
                    s['life'] = random.randint(10, 40)
                    s['angle'] = random.uniform(0, 2 * math.pi)
        time.sleep(0.05)


def meteor_shower(device, duration=12):
    meteors = [{'x': random.randint(0, WIDTH - 1), 'y': -random.randint(0, 3),
                'dx': random.uniform(-0.4, 0.4), 'dy': random.uniform(0.6, 1.4),
                'len': random.randint(3, 7)} for _ in range(5)]
    frames = int(duration / 0.04)
    for _ in range(frames):
        with canvas(device) as draw:
            for m in meteors:
                for i in range(m['len']):
                    px = int(m['x'] - m['dx'] * i)
                    py = int(m['y'] - m['dy'] * i)
                    if 0 <= px < WIDTH and 0 <= py < HEIGHT:
                        draw.point((px, py), fill="white")
                m['x'] += m['dx']
                m['y'] += m['dy']
                if m['y'] > HEIGHT + 2 or m['x'] < -2 or m['x'] > WIDTH + 2:
                    m['x'] = random.randint(0, WIDTH - 1)
                    m['y'] = -random.randint(0, 3)
                    m['dy'] = random.uniform(0.6, 1.4)
                    m['dx'] = random.uniform(-0.4, 0.4)
        time.sleep(0.04)


def firework_bursts(device, duration=12):
    frames = int(duration / 0.04)
    bursts = []
    for _ in range(6):
        bursts.append({
            'cx': random.randint(4, WIDTH - 4),
            'cy': random.randint(2, HEIGHT - 2),
            'pts': [(random.uniform(-1, 1), random.uniform(-1, 1)) for _ in range(8)],
            'start_frame': random.randint(0, frames),
        })
    for f in range(frames):
        with canvas(device) as draw:
            for b in bursts:
                elapsed = f - b['start_frame']
                if elapsed < 0 or elapsed > 18:
                    continue
                for dx, dy in b['pts']:
                    px = int(b['cx'] + dx * elapsed * 0.3)
                    py = int(b['cy'] + dy * elapsed * 0.3)
                    if 0 <= px < WIDTH and 0 <= py < HEIGHT:
                        draw.point((px, py), fill="white")
        time.sleep(0.04)


def show_time(device, hours, minutes, toggle):
    with canvas(device) as draw:
        text(draw, (0, 1), hours, fill="white", font=proportional(CP437_FONT))
        text(draw, (15, 1), ":" if toggle else " ",
             fill="white", font=proportional(TINY_FONT))
        text(draw, (17, 1), minutes, fill="white", font=proportional(CP437_FONT))
        for _ in range(3):
            draw.point((random.randint(0, WIDTH - 1), random.randint(0, HEIGHT - 1)),
                       fill="white")


def main():
    serial = spi(port=0, device=0, gpio=noop())
    device = max7219(serial, cascaded=4, block_orientation=-90,
                     blocks_arranged_in_reverse_order=False)
    device.contrast(16)

    starfield(device, 200)
    type_in(device, datetime.now().strftime("%H:%M"))
    time.sleep(0.5)

    toggle = False
    last_min = -1
    done = {}

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
                time.sleep(0.3)
            last_min = minute
            done = {}
            continue

        if 'date' not in done and sec < 20:
            done['date'] = True
            show_message(device, now.strftime("%d %b %Y %a"),
                         fill="white", font=proportional(CP437_FONT))
            continue

        if 'rain' not in done and sec >= 15 and sec < 35:
            done['rain'] = True
            matrix_rain(device, 14)
            continue

        if 'msg' not in done and sec >= 30 and sec < 50:
            done['msg'] = True
            msg = random.choice(COOL_MSGS)
            show_message(device, msg, fill="white", font=proportional(TINY_FONT))
            continue

        if 'bigfx' not in done and sec >= 45:
            done['bigfx'] = True
            if minute % 2 == 0:
                firework_bursts(device, 6)
                galaxy(device, 8)
            else:
                meteor_shower(device, 8)
                firework_bursts(device, 6)
            continue

        show_time(device, hours, minutes, toggle)
        time.sleep(0.5)


if __name__ == "__main__":
    main()
