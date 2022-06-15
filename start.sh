#!/bin/bash

# If you want to restore previously set alsamixe settings
# saved with alsactl --file=asound.state store
#echo '[ Restoring ASOUND state ]'
#alsactl --file=asound.state restore

echo '[ Loading Voiceflow Assistant ]'
python3 ./src/main.py
