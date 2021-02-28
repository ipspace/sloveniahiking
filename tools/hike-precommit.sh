#!/bin/bash
#
cd $(dirname "${BASH_SOURCE[0]}")
./sync_hike_data.py
./create_hike_json.py
git update-index --add ../static/data/hikes.json
