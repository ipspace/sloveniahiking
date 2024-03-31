#!/bin/bash
#
cd $(dirname "${BASH_SOURCE[0]}")
echo "Updating GPX data"
time ./sync_gpx_data.py
echo "Syncing hike data"
time ./sync_hike_data.py
echo "Updating biking data"
time ./update_biking_data.py
echo "Calculating nearby trips"
time ./add_nearby.py
echo "Creating hike JSON file"
./create_hike_json.py
git add ../static/data/hikes.json
echo "Synching flower data"
time ./flower-sync-data.py
echo "Building flower lookup tables"
time ./flower-build-lookup.py
