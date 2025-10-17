import argparse
import os
import shutil
import glob
# Add any missing imports here
from typing import List, Optional
import numpy as np
from astropy.io import fits
import logging


LOG_FILE = 'copy_log.txt'

class CustomFormatter(logging.Formatter):
    newline_marker = 'NEWLINE'

    def emit(self, record):
        # Check if the newline marker is in the message
        if self.newline_marker in record.msg:
            # If so, remove the marker and prepend a newline to the entire log output
            record.msg = record.msg.replace(self.newline_marker, "")
            # Temporarily prepend a newline to the format
            original_format = self.formatter._fmt
            self.formatter._fmt = "\n" + original_format
            
            super().emit(record)
            # Restore the original format
            self.formatter._fmt = original_format
        else:
            super().emit(record)

def main() -> None:
    """
    Parse command line arguments, determine the list of IDs, create the output folder
    and search and copy files based on IDs and suffixes.
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Copy files based on ID and suffixes.')

    parser.add_argument('--IDs', 
                        nargs='+',
                        type=str,
                        required=True,
                        help='List of IDs or file containing list of IDs')
    
    parser.add_argument('--parent-folder', 
                        type=str, 
                        required=True,
                        help='Parent folder to search within')
    
    parser.add_argument('--output-folder', 
                        type=str,
                        required=True,
                        help='Folder where files are copied to')
    
    parser.add_argument('--suffixes', 
                        nargs='+',
                        required=True,
                        help='List of suffixes for file names')
    
    parser.add_argument('--log', 
                        default='INFO', 
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help='Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)')

    
    args = parser.parse_args()

    _setup_logging(args.log)
    
    # Determine the list of IDs based on input method
    if len(args.IDs) == 1 and os.path.isfile(args.IDs[0]):
        ids = _get_ids_from_file(args.IDs[0])
    else:
        ids = args.IDs
    
    # Ensure output folder exists
    os.makedirs(args.output_folder, exist_ok=True)

    # Search and copy files
    _search_and_copy_files(args.parent_folder, ids, args.suffixes, args.output_folder)

def _setup_logging(level):
    """
    Setup the logging level for the application.

    Args:
        level (str): Logging level to configure.

    Raises:
        ValueError: If the provided logging level is invalid.
    """
    # Convert the logging level to its corresponding numeric representation
    numeric_level = getattr(logging, level.upper(), None)
    
    # If the provided logging level is not valid, raise an error
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {level}')
    
    ch = logging.StreamHandler()
    ch.setFormatter(CustomFormatter('%(levelname)s: %(message)s'))
    logging.basicConfig(level=numeric_level, handlers=[ch])
    

def _get_ids_from_file(file: str) -> List[str]:
    """
    Read IDs from a file.

    Args:
        file (str): Path to the file containing IDs.

    Returns:
        List[str]: List of IDs.

    Raises:
        ValueError: If no IDs are provided.
    """
    # Check if file is provided
    if file is None:
        raise ValueError('No IDs provided. Use --file to specify a file or --ids for inline ID list.')
    
    # Read IDs from file
    with open(file, 'r') as f:
        # Split each line by whitespace and take the first element as the ID
        return [line.split()[0] for line in f.readlines() if not line.startswith('#')]

def _compute_median_sn(fits_file: str) -> float:
    """
    Compute the median S/N from a FITS file.

    Args:
        fits_file (str): Path to the FITS file.

    Returns:
        float: The median S/N.
    """
    # Open the FITS file
    with fits.open(fits_file) as hdul:
        # Extract data and error arrays
        data: np.ndarray = hdul['DATA'].data  # type: ignore
        err: np.ndarray = hdul['ERR'].data  # type: ignore

        # Compute the S/N
        sn: np.ndarray = data[data > 0] / err[data > 0]

        # Compute the median S/N
    return np.median(sn), np.max(sn)

def _find_best_file(files: List[str]) -> str:
    """
    Find the file with the highest median S/N among a list of files.

    Args:
        files (List[str]): List of file paths.

    Returns:
        Optional[str]: The path to the file with the highest median S/N, or None if files is empty.
    """
    # Initialize variables to keep track of the best file and its S/N
    best_file: Optional[str] = None
    highest_sn: float = -np.inf
    
    # Loop over each file
    for file in files:
        # Log information
        logging.info(f"NEWLINEProcessing file: {file}")

        try:
            # Compute the median S/N
            sn, peak_sn = _compute_median_sn(file)
            logging.info(f"Median S/N: {sn}")
            logging.info(f"Peak S/N: {peak_sn}")
            sn = np.sqrt(sn*peak_sn)
            logging.info(f"Geometric mean median-peak S/N: {sn}")
            
            # If the current S/N is higher than the best one, update the best file
            if sn > highest_sn:
                highest_sn = sn
                best_file = file
        except Exception as e:
            # Print error message if there is an issue processing a file
            print(f"Error processing {file}: {e}")
    
    # Return the best file
    logging.info(f"Best file: {best_file}")
    return best_file

def _copy_file_overwrite(src: str, dst: str) -> None:
    """
    Copy a file from src to dst. Overwrites the file at dst if it exists.

    Args:
        src (str): Path to the source file.
        dst (str): Path to the destination file. Can be a directory, in which case the source file name is appended.

    Raises:
        OSError: If there is an error while removing an existing destination file.

    """
    # Check if dst is a directory
    if os.path.isdir(dst):
        # Append the source file name to the destination directory if dst is a directory
        dst_ = os.path.join(dst, os.path.basename(src))
        
    # If the destination file exists, remove it (to allow overwriting)
    if os.path.exists(dst_):
        # Remove the existing destination file
        try:
            os.remove(dst_)
        except OSError as e:
            # Raise an exception if there is an error while removing the file
            raise OSError(f"Error while removing {dst_}: {e}")

    if not os.path.exists(src) and '_2D.fits' in src:
        logging.warning(f"Source file {src} does not exist. Skipping copy of 2D file.")
        return
    
    try:
        shutil.copy2(src, dst)  # type: ignore
    except Exception as e:
        # Raise an exception if there is an error while copying the file
        raise Exception(f"Error while copying {src} to {dst}: {e}")
    

def _log_copy(src: str, dst: str) -> None:
    """
    Log the copy of a file by writing the source and destination paths to a file named 'copy_log.txt' in the destination directory.
    If the log file already exists, it is removed before writing.

    Args:
        src (str): Path to the source file.
        dst (str): Path to the destination directory.

    Raises:
        OSError: If there is an error while removing the existing log file.

    """
    # Construct the path to the log file
    log_file_path = os.path.join(dst, LOG_FILE)
    
    # Open the log file in append mode
    with open(log_file_path, 'a') as log_file:
        # Write the source and destination paths to the log file
        log_file.write(f"{src} --> {os.path.join(dst, os.path.basename(src))}\n")

def _search_and_copy_files(parent_folder: str, ids: List[str], suffixes: List[str], output_folder: str) -> None:
    """
    Search for files in the parent folder with given IDs and suffixes, and copy them to the output folder.
    If no file is found for a given ID, a warning is printed.

    Args:
        parent_folder (str): The folder to search within.
        ids (List[str]): List of IDs to search for.
        suffixes (List[str]): List of suffixes to append to the IDs.
        output_folder (str): The folder where files are copied to.
    """
    output_folder_normalized = os.path.normpath(output_folder)

    for id_ in ids:
        # If id_ has a length of less than 6 characetrs, add 0's to the front to reach 6 characters
        if len(id_) < 6:
            id_ = '0'*(6-len(id_)) + id_
              
        # Flag to keep track if a file was found for a given ID
        found = False
        
        # Iterate over suffixes
        for suffix in suffixes:
            # Construct the pattern to search for
            pattern = os.path.join(parent_folder, "**", id_ + suffix)
            matching_files = glob.glob(pattern, recursive=True)
            matching_files = [f for f in matching_files if not f.startswith(output_folder_normalized)]

            best_file = _find_best_file(matching_files)
            if best_file:
                _copy_file_overwrite(best_file, output_folder)
                if "_1D.fits" in best_file:
                    best_file_2d = best_file.replace("_1D.fits", "_2D.fits")
                    _copy_file_overwrite(best_file_2d, output_folder)
                _log_copy(best_file, output_folder)
                found = True
        
        # If no file was found for a given ID, print a warning
        if not found:
            print(f'Warning: No file found for ID {id_} with any of the provided suffixes.')

if __name__ == '__main__':
    main()
