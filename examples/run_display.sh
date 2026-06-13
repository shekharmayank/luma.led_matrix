#!/bin/bash
cd /home/pi/luma.led_matrix
git pull origin master -q
uv run examples/datetime_display.py
