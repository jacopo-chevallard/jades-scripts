import subprocess
import sys
import traceback
import shlex


def list_to_string(command_list):
    # Join the command list into a single string for display
    return ' '.join(shlex.quote(arg) for arg in command_list)

def log_error(command, error):
    error_message = f"Command: {command}\n{error}\n"
    sys.stderr.write(error_message)

def run_command(command):
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        error_traceback = traceback.format_exc()
        log_error(command, f"Return code: {e.returncode}\nOutput: {e.output}\nError: {e.stderr}\n")
        #log_error(command, f"Return code: {e.returncode}")
        raise
