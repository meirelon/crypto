#!/bin/bash
# set job vars
TYPE="$1"

if [[ $TYPE == "crypto" ]]; then
    gcloud functions deploy crypto \
    --project your-project \
    --runtime python37 \
    --trigger-your-trigger \
    --timeout 180

fi
