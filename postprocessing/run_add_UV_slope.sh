#!/bin/bash

HOME=/nethome/chevalla
source /mnt/globalNS/tmp/JADES/.venv/bin/activate
source /mnt/globalNS/tmp/JADES/params/env.sh
/mnt/globalNS/tmp/JADES/.venv/bin/python /mnt/globalNS/tmp/JADES/scripts/postprocessing/scan_results_and_run_add_UV_slope.py /mnt/globalNS/tmp/JADES/results

