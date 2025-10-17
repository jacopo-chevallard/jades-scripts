#!/usr/bin/env python3
"""
Convert FITS files ending with _1D.fits to extr3_1D.fits format.

This script processes multi-extension FITS files and replaces specific extensions:
- DATA --> EXTR3 (renamed to DATA)
- ERR --> EXTR3ERR (renamed to ERR)
- DIRTY_DATA --> EXTR3DIRTY (renamed to DIRTY_DATA)

All other extensions remain unchanged.
"""

import argparse
import sys
from pathlib import Path
from astropy.io import fits
import shutil


def convert_fits_file(input_path, output_path):
    """
    Convert a single FITS file by replacing specific extensions.

    Parameters
    ----------
    input_path : Path
        Path to input FITS file
    output_path : Path
        Path to output FITS file
    """
    # Extension mapping: old_name -> new_name
    extension_mapping = {
        'DATA': 'EXTR3',
        'ERR': 'EXTR3ERR',
        'DIRTY_DATA': 'EXTR3DIRTY'
    }

    # Open the input FITS file
    with fits.open(input_path) as hdul:
        # Create a new HDU list
        new_hdul = fits.HDUList()

        # Process each HDU
        for hdu in hdul:
            # Get the extension name
            extname = hdu.header.get('EXTNAME', '').strip()

            # Check if this extension should be replaced
            if extname in extension_mapping:
                # Get the new extension name from mapping
                new_extname = extension_mapping[extname]

                # Find the corresponding new extension in the original file
                try:
                    new_hdu = hdul[new_extname]
                    # Copy the HDU and update its EXTNAME to match the old name
                    if isinstance(new_hdu, fits.ImageHDU):
                        copied_hdu = fits.ImageHDU(data=new_hdu.data.copy(),
                                                   header=new_hdu.header.copy())
                    elif isinstance(new_hdu, fits.BinTableHDU):
                        copied_hdu = fits.BinTableHDU(data=new_hdu.data.copy(),
                                                     header=new_hdu.header.copy())
                    else:
                        copied_hdu = new_hdu.copy()

                    # Update the EXTNAME to the original name
                    copied_hdu.header['EXTNAME'] = extname
                    new_hdul.append(copied_hdu)

                except (KeyError, IndexError):
                    print(f"Warning: Extension {new_extname} not found in {input_path.name}, "
                          f"keeping original {extname}")
                    new_hdul.append(hdu.copy())
            else:
                # Keep the extension as-is (unless it's one of the source extensions)
                if extname not in extension_mapping.values():
                    new_hdul.append(hdu.copy())
                # If it's one of the EXTR3* extensions, skip it (already used to replace)

        # Write the new FITS file
        new_hdul.writeto(output_path, overwrite=True)
        print(f"Created: {output_path.name}")


def process_folder(folder_path, overwrite=False):
    """
    Process all *_1D.fits files in a folder.

    Parameters
    ----------
    folder_path : Path
        Path to folder containing FITS files
    overwrite : bool
        Whether to overwrite existing output files
    """
    folder = Path(folder_path)

    if not folder.is_dir():
        print(f"Error: {folder} is not a valid directory")
        sys.exit(1)

    # Find all files ending with _1D.fits
    fits_files = list(folder.glob("*_1D.fits"))

    if not fits_files:
        print(f"No files ending with _1D.fits found in {folder}")
        return

    print(f"Found {len(fits_files)} files to process")

    # Process each file
    for fits_file in fits_files:
        # Create output filename
        output_name = fits_file.name.replace("_1D.fits", "_extr3_1D.fits")
        output_path = folder / output_name

        # Check if output already exists
        if output_path.exists() and not overwrite:
            print(f"Skipping {fits_file.name}: output already exists (use --overwrite to replace)")
            continue

        try:
            convert_fits_file(fits_file, output_path)
        except Exception as e:
            print(f"Error processing {fits_file.name}: {e}")
            continue

    print("Processing complete!")


def main():
    """Main function to parse arguments and run the conversion."""
    parser = argparse.ArgumentParser(
        description="Convert FITS files from v5.x format to extr3 format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s /path/to/fits/folder
  %(prog)s /path/to/fits/folder --overwrite
        """
    )

    parser.add_argument(
        "folder",
        type=str,
        help="Path to folder containing *_1D.fits files"
    )

    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing output files"
    )

    args = parser.parse_args()

    process_folder(args.folder, overwrite=args.overwrite)


if __name__ == "__main__":
    main()
