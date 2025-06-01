import sqlite3
import sys
import os

# Add project root to sys.path to allow imports from utils
_PROJ_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _PROJ_ROOT not in sys.path:
    sys.path.insert(0, _PROJ_ROOT)

from utils.logger import log
# from utils.database import get_db_connection # Not strictly needed as the script uses direct sqlite3.connect

def add_image_filename_columns():
    """
    Adds the image_filename column to the restaurants and menu_items tables
    if they don't already exist.
    """
    db_path = "g:\\swigato_project\\data\\swigato.db" # Make sure this path is correct
    conn = None
    try:
        # conn = get_db_connection() # Assuming get_db_connection uses the correct path
        # For direct control over the path for this script:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Check and add column to restaurants table
        cursor.execute("PRAGMA table_info(restaurants)")
        columns = [column[1] for column in cursor.fetchall()]
        if "image_filename" not in columns:
            cursor.execute("ALTER TABLE restaurants ADD COLUMN image_filename TEXT")
            log("Added 'image_filename' column to 'restaurants' table.")
        else:
            log("'image_filename' column already exists in 'restaurants' table.")

        # Check and add column to menu_items table
        cursor.execute("PRAGMA table_info(menu_items)")
        columns = [column[1] for column in cursor.fetchall()]
        if "image_filename" not in columns:
            cursor.execute("ALTER TABLE menu_items ADD COLUMN image_filename TEXT")
            log("Added 'image_filename' column to 'menu_items' table.")
        else:
            log("'image_filename' column already exists in 'menu_items' table.")

        conn.commit()
        log("Database schema update check complete.")

    except sqlite3.Error as e:
        log(f"SQLite error during schema update: {e}")
        if conn:
            conn.rollback()
    except Exception as e:
        log(f"General error during schema update: {e}")
        if conn:
            conn.rollback()
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    # sys.path is adjusted at the top, and imports are resolved globally.
    add_image_filename_columns()
