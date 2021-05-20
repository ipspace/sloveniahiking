#!/bin/bash
#
cd $(dirname "${BASH_SOURCE[0]}")
echo "Updating GPX data"
time ./sync_gpx_data.py
echo "Calculating nearby trips"
time ./add_nearby.py
echo "Syncing hike data"
time ./sync_hike_data.py
echo "Creating hike JSON file"
./create_hike_json.py
git add ../static/data/hikes.json
