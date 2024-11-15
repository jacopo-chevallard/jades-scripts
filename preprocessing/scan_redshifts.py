import os
import subprocess
from utils import run_command

def scan_and_convert(input_folder):
    # Iterate over all subdirectories of the given folder
    for root, dirs, files in os.walk(input_folder):
      if os.path.basename(root) == "redshifts":
        if ".fits" not in files:
          for file in files:
            if file.endswith('.csv'):
              command = ["python", "/mnt/globalNS/tmp/JADES/scripts/preprocessing/convert_redshifts_csv_to_fits.py", os.path.join(root, file)]
              run_command(command)

if __name__ == "__main__":
    import sys

    # Check if the user provided an input folder
    if len(sys.argv) < 2:
        print("Usage: python scan_and_convert.py <input_folder>")
        sys.exit(1)

    input_folder = sys.argv[1]

    # Check if the provided folder exists
    if not os.path.exists(input_folder):
        print(f"Error: Folder '{input_folder}' does not exist.")
        sys.exit(1)

    scan_and_convert(input_folder)

