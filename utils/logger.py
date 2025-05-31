import datetime
import os

# Define the directory for logs (e.g., within the data directory)
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
LOG_FILE_NAME = os.path.join(LOG_DIR, 'swigato_app.log')

# Ensure log directory exists
if not os.path.exists(LOG_DIR):
    try:
        os.makedirs(LOG_DIR)
    except OSError as e:
        # Fallback to printing if directory creation fails
        print(f"[Swigato Log Setup Error]: Could not create log directory {LOG_DIR}: {e}")
        # Define a dummy log function if setup fails
        def log(msg):
            print(f"[Swigato Log (Fallback)]: {msg}")
        # Exit this script block as we can't set up file logging
        # This is a bit of a hack for the current tool structure.
        # In a real script, you might raise an exception or handle this differently.
        raise SystemExit("Logger setup failed due to directory creation error.")

def log(msg):
    """Logs a message to the swigato_app.log file with a timestamp."""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"{timestamp} [Swigato Log]: {msg}"
    try:
        with open(LOG_FILE_NAME, 'a') as f:
            f.write(log_message + "\n")
    except Exception as e:
        # If logging to file fails, print to console as a fallback
        print(f"FALLBACK_CONSOLE_LOG: {log_message}")
        print(f"Logging to file {LOG_FILE_NAME} failed: {e}")
