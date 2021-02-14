#!/bin/bash
set -e
while [ true ]; do
  python3 read_hike.py --count 2
  echo "Waiting for two minutes..."
  sleep 120
done
