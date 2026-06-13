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

# Each animation appears by name; full-minute showcase rotates through these.
FULL_ANIMS = []


def register(fn):
    FULL_ANIMS.append(fn.__name__)
    return fn


# ---------------------------------------------------------------------------
#  Startup
# ---------------------------------------------------------------------------

def starfield_tunnel(device, duration=8):
    stars = []
    for _ in range(28):
        stars.append([random.uniform(0, 2 * math.pi),
                      random.uniform(0.6, 2.0),
                      random.uniform(0, 1)])
    frames = int(duration / 0.04)
    for _ in range(frames):
        with canvas(device) as draw:
            for s in stars:
                s[2] += s[1] * 0.04
                if s[2] > 1:
                    s[0] = random.uniform(0, 2 * math.pi)
                    s[2] = 0
                    s[1] = random.uniform(0.6, 2.0)
                cx, cy = WIDTH // 2, HEIGHT // 2
                px = int(cx + math.cos(s[0]) * s[2] * 16)
                py = int(cy + math.sin(s[0]) * s[2] * 4)
                if 0 <= px < WIDTH and 0 <= py < HEIGHT:
                    draw.point((px, py), fill="white")
        time.sleep(0.04)


def breathe_startup(device, duration=4):
    frames = int(duration / 0.05)
    t = 0.0
    cx, cy = WIDTH // 2, HEIGHT // 2
    for _ in range(frames):
        t += 0.06
        radius = 2 + math.sin(t * 1.5) * 1.8
        with canvas(device) as draw:
            for x in range(WIDTH):
                for y in range(HEIGHT):
                    d = math.sqrt((x - cx) ** 2 + (y - cy) ** 2)
                    if abs(d - radius) < 0.8:
                        draw.point((x, y), fill="white")
        time.sleep(0.05)


def type_in(device, full, y=1):
    for i in range(1, len(full) + 1):
        with canvas(device) as draw:
            text(draw, (0, y), full[:i], fill="white", font=proportional(CP437_FONT))
        time.sleep(0.08)


# ---------------------------------------------------------------------------
#  Minute transition – TWO‑PHASE slide, never overlaps
# ---------------------------------------------------------------------------

def slide_in_right(device, text_str, y=1):
    for offset in range(32, -1, -1):
        with canvas(device) as draw:
            text(draw, (offset, y), text_str, fill="white", font=proportional(CP437_FONT))
        time.sleep(0.015)


def transition_minute(device, old_str, new_str):
    # Phase 1: old slides off left
    for offset in range(0, 36):
        with canvas(device) as draw:
            text(draw, (0 - offset, 1), old_str, fill="white", font=proportional(CP437_FONT))
        time.sleep(0.013)
    # brief pause
    time.sleep(0.04)
    # Phase 2: new slides in from right
    slide_in_right(device, new_str)


def transition_minutes_only(device, hours, old_m, new_m):
    for offset in range(0, 16):
        with canvas(device) as draw:
            text(draw, (0, 1), hours, fill="white", font=proportional(CP437_FONT))
            text(draw, (15, 1), ":", fill="white", font=proportional(TINY_FONT))
            text(draw, (17 - offset, 1), old_m, fill="white", font=proportional(CP437_FONT))
        time.sleep(0.013)
    time.sleep(0.04)
    for offset in range(16, -1, -1):
        with canvas(device) as draw:
            text(draw, (0, 1), hours, fill="white", font=proportional(CP437_FONT))
            text(draw, (15, 1), ":", fill="white", font=proportional(TINY_FONT))
            text(draw, (17 + offset, 1), new_m, fill="white", font=proportional(CP437_FONT))
        time.sleep(0.013)


# ---------------------------------------------------------------------------
#  Animations
# ---------------------------------------------------------------------------

@register
def plasma_swirl(device, duration=14):
    t = 0.0
    frames = int(duration / 0.04)
    for _ in range(frames):
        t += 0.18
        with canvas(device) as draw:
            for x in range(WIDTH):
                for y in range(HEIGHT):
                    v = (math.sin(x * 0.35 + t) +
                         math.sin(y * 0.25 + t * 0.7) +
                         math.sin((x + y) * 0.18 + t * 1.3) +
                         math.sin(math.hypot(x - 15, y - 4) * 0.45 + t * 0.6))
                    if v > 0.6:
                        draw.point((x, y), fill="white")
        time.sleep(0.04)


@register
def sine_worm(device, duration=14):
    frames = int(duration / 0.04)
    t = 0.0
    for _ in range(frames):
        t += 0.22
        with canvas(device) as draw:
            for x in range(WIDTH):
                base = HEIGHT // 2 + math.sin(x * 0.55 + t) * 2.8
                y0 = int(base)
                if 0 <= y0 < HEIGHT:
                    draw.point((x, y0), fill="white")
                for i in range(1, 4):
                    gy = int(base + math.sin(x * 0.55 + t + i * 0.35) * 1.2)
                    if 0 <= gy < HEIGHT and random.random() > 0.25 * i:
                        draw.point((x, gy), fill="white")
        time.sleep(0.04)


@register
def pendulum_wave(device, duration=14):
    frames = int(duration / 0.04)
    t = 0.0
    for _ in range(frames):
        t += 0.055
        with canvas(device) as draw:
            for x in range(WIDTH):
                phase = x * 0.35
                y = int(HEIGHT // 2 + math.sin(t * 1.6 + phase) * 3)
                if 0 <= y < HEIGHT:
                    draw.point((x, y), fill="white")
                    if y < HEIGHT - 1:
                        draw.point((x, y + 1), fill="white")
        time.sleep(0.04)


@register
def aurora_wave(device, duration=14):
    t = 0.0
    frames = int(duration / 0.035)
    for _ in range(frames):
        t += 0.09
        with canvas(device) as draw:
            for x in range(WIDTH):
                val = (math.sin(x * 0.25 + t * 0.8) +
                       math.sin(x * 0.4 + t * 1.4) * 0.6 +
                       math.sin(x * 0.15 + t * 2.1) * 0.3)
                base_y = HEIGHT // 2 + val * 1.2
                for y in range(HEIGHT):
                    dy = abs(y - base_y)
                    if dy < 1.5 and random.random() > 0.45:
                        draw.point((x, y), fill="white")
        time.sleep(0.035)


@register
def galaxy_spiral(device, duration=14):
    stars = []
    for _ in range(40):
        stars.append({
            'angle': random.uniform(0, 2 * math.pi),
            'radius': random.uniform(0.5, 5.5),
            'speed': random.uniform(0.3, 1.0),
            'drift': random.uniform(-0.02, 0.02),
        })
    frames = int(duration / 0.045)
    for f in range(frames):
        with canvas(device) as draw:
            cx, cy = WIDTH // 2, HEIGHT // 2
            for s in stars:
                s['angle'] += 0.06 * s['speed']
                s['radius'] += s['drift']
                if s['radius'] < 0.3 or s['radius'] > 5.8:
                    s['radius'] = random.uniform(0.5, 5.5)
                    s['angle'] = random.uniform(0, 2 * math.pi)
                    s['drift'] = random.uniform(-0.02, 0.02)
                arm_angle = s['angle'] + s['radius'] * 0.5
                px = int(cx + math.cos(arm_angle) * s['radius'])
                py = int(cy + math.sin(arm_angle) * s['radius'])
                if 0 <= px < WIDTH and 0 <= py < HEIGHT:
                    draw.point((px, py), fill="white")
        time.sleep(0.045)


@register
def matrix_rain_v2(device, duration=14):
    drops = []
    for _ in range(WIDTH * 2):
        drops.append({
            'x': random.randint(0, WIDTH - 1),
            'y': random.uniform(-8, 0),
            'len': random.randint(3, 7),
            'speed': random.uniform(0.4, 1.0),
        })
    frames = int(duration / 0.04)
    for _ in range(frames):
        with canvas(device) as draw:
            for d in drops:
                for i in range(1, d['len']):
                    y = int(d['y'] - i)
                    if 0 <= y < HEIGHT and random.random() > i * 0.1:
                        draw.point((d['x'], y), fill="white")
                yh = int(d['y'])
                if 0 <= yh < HEIGHT:
                    draw.point((d['x'], yh), fill="white")
                    if yh > 0:
                        draw.point((d['x'], yh - 1), fill="white")
                d['y'] += d['speed']
                if d['y'] > HEIGHT + d['len']:
                    d['x'] = random.randint(0, WIDTH - 1)
                    d['y'] = random.uniform(-8, -2)
                    d['len'] = random.randint(3, 7)
                    d['speed'] = random.uniform(0.4, 1.0)
        time.sleep(0.04)


@register
def meteor_shower_v2(device, duration=14):
    meteors = []
    for _ in range(6):
        meteors.append({
            'x': random.randint(0, WIDTH - 1),
            'y': -random.randint(0, 5),
            'dx': random.uniform(-0.6, 0.6),
            'dy': random.uniform(0.8, 1.6),
            'len': random.randint(5, 10),
        })
    frames = int(duration / 0.035)
    for _ in range(frames):
        with canvas(device) as draw:
            for m in meteors:
                for i in range(1, m['len']):
                    px = int(m['x'] - m['dx'] * i)
                    py = int(m['y'] - m['dy'] * i)
                    if (0 <= px < WIDTH and 0 <= py < HEIGHT
                            and random.random() > i * 0.07):
                        draw.point((px, py), fill="white")
                hx, hy = int(m['x']), int(m['y'])
                if 0 <= hx < WIDTH and 0 <= hy < HEIGHT:
                    draw.point((hx, hy), fill="white")
                m['x'] += m['dx']
                m['y'] += m['dy']
                if m['y'] > HEIGHT + 2 or m['x'] < -2 or m['x'] > WIDTH + 2:
                    m['x'] = random.randint(0, WIDTH - 1)
                    m['y'] = -random.randint(0, 5)
                    m['dy'] = random.uniform(0.8, 1.6)
                    m['dx'] = random.uniform(-0.6, 0.6)
                    m['len'] = random.randint(5, 10)
        time.sleep(0.035)


@register
def firework_sparks(device, duration=14):
    frames = int(duration / 0.035)
    bursts = []
    for _ in range(8):
        cx = random.randint(6, WIDTH - 6)
        cy = random.randint(2, HEIGHT - 2)
        pts = [(random.uniform(-1, 1), random.uniform(-1, 1)) for _ in range(12)]
        bursts.append({
            'cx': cx, 'cy': cy, 'pts': pts,
            'start_frame': random.randint(0, int(frames * 0.6)),
        })
    for f in range(frames):
        with canvas(device) as draw:
            for b in bursts:
                elapsed = f - b['start_frame']
                if elapsed < 0:
                    continue
                rate = 0.3
                r = elapsed * rate
                if elapsed < 14:
                    for dx, dy in b['pts']:
                        px = int(b['cx'] + dx * r * 3)
                        py = int(b['cy'] + dy * r * 3)
                        if 0 <= px < WIDTH and 0 <= py < HEIGHT:
                            draw.point((px, py), fill="white")
                elif elapsed < 28:
                    for dx, dy in b['pts']:
                        px = int(b['cx'] + dx * r * 3)
                        py = int(b['cy'] + dy * r * 3 + (elapsed - 14) * 0.12)
                        if 0 <= px < WIDTH and 0 <= py < HEIGHT:
                            draw.point((px, py), fill="white")
        time.sleep(0.035)


@register
def breathe(device, duration=12):
    frames = int(duration / 0.05)
    t = 0.0
    cx, cy = WIDTH // 2, HEIGHT // 2
    for _ in range(frames):
        t += 0.045
        r = 2.5 + math.sin(t * 1.3) * 2
        with canvas(device) as draw:
            for x in range(WIDTH):
                for y in range(HEIGHT):
                    d = math.hypot(x - cx, y - cy)
                    if abs(d - r) < 0.7:
                        draw.point((x, y), fill="white")
        time.sleep(0.05)


# ---------------------------------------------------------------------------
#  Time display
# ---------------------------------------------------------------------------

def show_time(device, hours, minutes, toggle):
    with canvas(device) as draw:
        text(draw, (0, 1), hours, fill="white", font=proportional(CP437_FONT))
        text(draw, (15, 1), ":" if toggle else " ",
             fill="white", font=proportional(TINY_FONT))
        text(draw, (17, 1), minutes, fill="white", font=proportional(CP437_FONT))
        for _ in range(3):
            draw.point((random.randint(0, WIDTH - 1),
                        random.randint(0, HEIGHT - 1)),
                       fill="white")


# ---------------------------------------------------------------------------
#  Main loop
# ---------------------------------------------------------------------------

def main():
    serial = spi(port=0, device=0, gpio=noop())
    device = max7219(serial, cascaded=4, block_orientation=-90,
                     blocks_arranged_in_reverse_order=False)
    device.contrast(16)

    now = datetime.now()
    starfield_tunnel(device, 8)
    breathe_startup(device, 4)
    type_in(device, now.strftime("%H:%M"))
    time.sleep(0.5)

    toggle = False
    last_min = -1
    done = {}
    anim_idx = 0

    while True:
        toggle = not toggle
        now = datetime.now()
        sec = now.second
        minute = now.minute
        hours = now.strftime('%H')
        minutes = now.strftime('%M')

        # -- minute change ------------------------------------------------
        if minute != last_min:
            if last_min >= 0:
                old_m = f"{last_min:02d}"
                old_h = int(hours)
                if minute == 0:
                    old_h = (old_h - 1) % 24
                old_hs = f"{old_h:02d}"
                if old_hs != hours:
                    transition_minute(device,
                                      f"{old_hs}:{old_m}",
                                      f"{hours}:{minutes}")
                else:
                    transition_minutes_only(device, hours, old_m, minutes)
                time.sleep(0.2)
            last_min = minute
            done = {}
            continue

        # -- date scroll --------------------------------------------------
        if 'date' not in done and sec < 20:
            done['date'] = True
            show_message(device, now.strftime("%d %b %Y %a"),
                         fill="white", font=proportional(CP437_FONT))
            continue

        # -- matrix rain --------------------------------------------------
        if 'rain' not in done and sec >= 15 and sec < 35:
            done['rain'] = True
            matrix_rain_v2(device, 14)
            continue

        # -- cool message -------------------------------------------------
        if 'msg' not in done and sec >= 30 and sec < 50:
            done['msg'] = True
            msg = random.choice(COOL_MSGS)
            show_message(device, msg, fill="white",
                         font=proportional(TINY_FONT))
            continue

        # -- showcase animation (rotates every minute) --------------------
        if 'showcase' not in done and sec >= 45:
            done['showcase'] = True
            name = FULL_ANIMS[anim_idx % len(FULL_ANIMS)]
            globals()[name](device, 14)
            anim_idx += 1
            continue

        # -- normal time display ------------------------------------------
        show_time(device, hours, minutes, toggle)
        time.sleep(0.5)


if __name__ == "__main__":
    main()
