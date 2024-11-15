import os
import pandas as pd
from astropy.table import Table
from astropy.io import fits
import sys

SPEC_Z_FLAGS = [4, 5, 6, 7, 8]

def convert_csv_to_fits(csv_file):

    # Generate the output FITS file name by replacing .csv with .fits
    fits_file = csv_file.replace('.csv', '.fits')
    if os.path.isfile(fits_file) and os.path.getsize(fits_file) > 0:
      return

    # Read the CSV file into a pandas DataFrame
    df = pd.read_csv(csv_file)

    # Define the function to calculate z and z_err
    def calculate_z(row):
        flag_set = set(int(x.strip()) for x in row['flag'].strip('{}').split(','))
        sample = ''
        if any(i in flag_set for i in SPEC_Z_FLAGS):
          sample = 'spec_z'
        if row['z_visinsp'] != -1:
            z = row['z_visinsp']
            if 4 in flag_set:
              z_err = 0.05 * z
            else:
              z_err = 0.01 * z
        else:
            if 4 in flag_set:
                z = row['z_bagp']
                z_err = 0.1 * z
            else:
                z = row['z_phot']
                z_err = 0.3 * z
                if z > 0.: 
                  sample = 'phot_z'
        return z, z_err, sample

    # Apply the function to each row
    df['z'], df['z_err'], df['sample'] = zip(*df.apply(calculate_z, axis=1))

    # Reorder the DataFrame columns
    column_order = ['ID', 'z', 'z_err', 'z_phot', 'z_bagp', 'z_visinsp', 'flag', 'sample', 'comment']
    df = df[column_order]

    # Convert the DataFrame to an Astropy Table
    t = Table.from_pandas(df)

    # Write the Astropy Table to a FITS file
    t.write(fits_file, format='fits', overwrite=True)

# Check if the script got the filename parameter
if len(sys.argv) < 2:
    print("Usage: python script.py <csv_file>")
else:
    csv_file = sys.argv[1]
    convert_csv_to_fits(csv_file)
