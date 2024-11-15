import os
import subprocess
from utils import run_command, list_to_string

SUFFIX = "BEAGLE.fits.gz"
PARAMS_NAMES = "/mnt/globalNS/tmp/JADES/params/references/params_names.json" 
LINE_LABELS = "/mnt/globalNS/tmp/JADES/params/references/emission_lines.json"
LOG_LEVEL = "ERROR"
REGEX = "*_masked"
BEAGLE_SUFFIX = "masked_BEAGLE.fits.gz"
SKIP_FILE = "automated_pyp_beagle.skip"
WL_RANGE = [1., 5.2]
WL_UNITS = "micron"
JSON_CALIB = "/mnt/globalNS/tmp/JADES/params/references/calibration_correction.json"

command_args = ["pyp_beagle", 
                  "--log-level", LOG_LEVEL,
                  "--plot-triangle", 
                  "--json-triangle", PARAMS_NAMES,
                  "--plot-marginal",
                  "--json-line-labels", LINE_LABELS,
                  "--show-residual",
                  "--show-MAP-SED",
                  "--show-line-labels",
                  "--draw-steps",
                  "--show-calibration-correction",
                  "--json-calibration-correction", JSON_CALIB,
                  "--print-ID",
                  "--wl-units", WL_UNITS,
                ]

command_args_except = ["--ID-ignore-regex", REGEX,
                  "--beagle-suffix", BEAGLE_SUFFIX]

def scan_and_convert(input_folder):
    # Iterate over all subdirectories of the given folder
    for root, dirs, files in os.walk(input_folder):
        command = command_args + ["-r", root, "--wl-range"] + [str(wl) for wl in WL_RANGE]
        
        if SKIP_FILE in files:
          continue

        # Check if any file in the directory ends with "_1D.fits"
        if len(files) > 0:
          if any((file.endswith(SUFFIX) and 
            os.path.getsize(os.path.join(root, file)) > 0) for file in files):
              # Call the convert_files.py script with the sub-directory as an argument
              run_command(command)
              #try:
              #  subprocess.run(command)
              #except:
              #  subprocess.run(command + command_args_except)
                    
if __name__ == "__main__":
    import sys

    # Check if the user provided an input folder
    if len(sys.argv) < 2:
        print("Usage: python scan_results_and_run_pyp_beagle.py <input_folder>")
        sys.exit(1)

    input_folder = sys.argv[1]

    # Check if the provided folder exists
    if not os.path.exists(input_folder):
        print(f"Error: Folder '{input_folder}' does not exist.")
        sys.exit(1)

    scan_and_convert(input_folder)

