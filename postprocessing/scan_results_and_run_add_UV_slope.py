import os
import subprocess

SUFFIX = "BEAGLE.fits.gz"
LOG_LEVEL = "ERROR"
REGEX = "*_masked"
BEAGLE_SUFFIX = "masked_BEAGLE.fits.gz"
SKIP_FILE = "automated_pyp_beagle.skip"

def scan_and_convert(input_folder):
    # Iterate over all subdirectories of the given folder
    for root, dirs, files in os.walk(input_folder):
        if len(files) > 0:
          if any((file.endswith(SUFFIX) and 
            os.path.getsize(os.path.join(root, file)) > 0) for file in files) and not SKIP_FILE in files:
              subprocess.run(["/mnt/globalNS/tmp/JADES/scripts/postprocessing/add_UV_slope.py",
                  "-r", root 
                ])

if __name__ == "__main__":
    import sys

    # Check if the user provided an input folder
    if len(sys.argv) < 2:
        print("Usage: python scan_results_and_run_add_UV_slope.py <input_folder>")
        sys.exit(1)

    input_folder = sys.argv[1]

    # Check if the provided folder exists
    if not os.path.exists(input_folder):
        print(f"Error: Folder '{input_folder}' does not exist.")
        sys.exit(1)

    scan_and_convert(input_folder)

