#!/bin/bash

HOME=/nethome/chevalla
source /mnt/globalNS/tmp/JADES/.venv/bin/activate
source /mnt/globalNS/tmp/JADES/params/env.sh
/mnt/globalNS/tmp/JADES/.venv/bin/python /mnt/globalNS/tmp/JADES/scripts/postprocessing/publish_results.py -r $1

