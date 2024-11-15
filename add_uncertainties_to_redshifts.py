import os
import pandas as pd
from astropy.table import Table
from astropy.io import fits
import sys

def add_uncertainties(file):

    table = Table.read(file).to_pandas()

    # Define the function to calculate z and z_err
    def calculate_z(row):
        # Ensure row['flag'] is a string
        if isinstance(row['flag'], bytes):
            row['flag']= row['flag'].decode('utf-8')  # Decode bytes to str
        if row['z_visinsp'] != -1:
            z = row['z_visinsp']
            z_err = 0.01 * z
        else:
            flag_set = set(int(x.strip()) for x in row['flag'].strip('{}').split(','))
            if 4 in flag_set:
                z = row['z_bagp']
                z_err = 0.1 * z
            else:
                z = row['z_phot']
                z_err = 0.3 * z
        return z, z_err

    # Apply the function to each row
    table['z'], table['z_err'] = zip(*table.apply(calculate_z, axis=1))

    # Reorder the DataFrame columns
    column_order = ['NIRSpec_ID', 'NIRCam_ID', 'z', 'z_err', 'z_phot', 'z_bagp', 'z_visinsp', 'flag', 'comment']
    table = table[column_order]

    table['NIRSpec_ID'] = table['NIRSpec_ID'].astype(str).str.zfill(6)


    # Generate the output FITS file name by replacing .csv with .fits
    fits_file = os.path.splitext(file)[0] + "_with_uncertainties.fits"

    # Write the Astropy Table to a FITS file
    Table.from_pandas(table).write(fits_file, format='fits', overwrite=True)

    print(f"FITS table saved to {fits_file}")

# Check if the script got the filename parameter
if len(sys.argv) < 2:
    print("Usage: python script.py <csv_file>")
else:
    file = sys.argv[1]
    add_uncertainties(file)
