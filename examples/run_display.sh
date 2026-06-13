#!/bin/bash
cd /root/luma.led_matrix
git pull origin master -q
/root/.local/bin/uv run examples/datetime_display.py
