#!/usr/bin/env python

import argparse
import os
import subprocess

JSON_SUMMARY = "/mnt/globalNS/tmp/JADES/params/references/summary_config.json"
LOG_LEVEL = "ERROR"
DATA_FOLDER = "pyp-beagle/data"
SUMMARY_CAT = "BEAGLE_summary_catalogue.fits"
PYP_BEAGLE = "pyp-beagle"
INPUT_FILES = "BEAGLE-input-files"
NEOGAL_FTP_PATH = "/mnt/shares/public/JADES"
REF_FILES = "/mnt/globalNS/tmp/JADES/params/references"
NUM_PROC = "8"

if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
        '-r', '--results-dir',
        help="Directory containing BEAGLE results",
        action="store", 
        type=str, 
        dest="results_dir", 
        default=os.getcwd()
    )

    args = parser.parse_args()

    # First, we compute the UV slope
    subprocess.run(["/mnt/globalNS/tmp/JADES/scripts/postprocessing/add_UV_slope.py",
        "-r", args.results_dir,
        "-np", NUM_PROC
      ])

    # First, we compute the summary catalogue
    subprocess.run(["pyp_beagle", 
      "-r", args.results_dir, 
      "--log-level", LOG_LEVEL,
      "--compute-summary", 
      "--json-summary", JSON_SUMMARY,
      "--flatten-columns",
      "-np", NUM_PROC
    ])

    # We then reformat the catalogue with a reduced list of columns
    subprocess.run([
      "/mnt/globalNS/tmp/JADES/scripts/postprocessing/reformat_Beagle_summary_catalogue.py", 
      "--summary-catalogue", os.path.join(args.results_dir, DATA_FOLDER, SUMMARY_CAT),
      "--include", "M_tot M_star max_stellar_age metallicity mass_w_age mass_w_Z tau tauv_eff L_UV L_UV_unatt L_UV_unatt_stellar xi_ion_unatt_stellar UV_slope redshift SFR sSFR_100 A_1500 A_1500_stellar A_B A_V logU xi_d logOH",
      "--output", os.path.join(args.results_dir, DATA_FOLDER, "BEAGLE_summary_catalogue_reformatted.fits")
    ])
      
    # We reformat the catalogue using all columns
    subprocess.run([
      "/mnt/globalNS/tmp/JADES/scripts/postprocessing/reformat_Beagle_summary_catalogue.py", 
      "--summary-catalogue", os.path.join(args.results_dir, DATA_FOLDER, SUMMARY_CAT),
      "--output", os.path.join(args.results_dir, DATA_FOLDER, "BEAGLE_summary_catalogue_reformatted_full.fits")
    ])


    # We create the output folder on NEOGAL FTP
    new_dir = args.results_dir.split("JADES/results/")[1]

    def create_directory(base_path, new_dir):
        # Change to the base directory
        original_dir = os.getcwd()
        try:
            os.chdir(base_path)
            os.makedirs(new_dir, exist_ok=True)
        except Exception as e:
            print(f"An error occurred: {e}")
        finally:
            # Change back to the original directory
            os.chdir(original_dir)

    create_directory(NEOGAL_FTP_PATH, new_dir)

    # And finally, rsync the results!
    subprocess.run([
      "rsync",
      "-az", 
      os.path.join(args.results_dir, PYP_BEAGLE),
      os.path.join(NEOGAL_FTP_PATH, new_dir)
    ])

    subprocess.run([
      "rsync",
      "-az", 
      os.path.join(args.results_dir, INPUT_FILES),
      os.path.join(NEOGAL_FTP_PATH, new_dir)
    ])

    subprocess.run([
      "rsync",
      "-az", 
      os.path.join(REF_FILES, "README_BEAGLE_summary_catalogue_reformatted"),
      os.path.join(NEOGAL_FTP_PATH, new_dir, DATA_FOLDER)
    ])
