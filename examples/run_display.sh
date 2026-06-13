#!/bin/bash
cd /home/pi/luma.led_matrix
git pull origin master -q
python examples/datetime_display.py
