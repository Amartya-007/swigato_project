import logging

PRIMARY_COLOR = "#FF5722"      # Swiggy Orange
SECONDARY_COLOR = "#D32F2F"    # Zomato Red
BACKGROUND_COLOR = "#FFF5F0"   # Light Cream/Peach
FRAME_FG_COLOR = "#FFFFFF"     # Card/Section Background
FRAME_BORDER_COLOR = "#FFCCBC" # Light Orange border
ENTRY_BG_COLOR = "#FBE9E7"     # Pale Orange (Input field)
TEXT_COLOR = "#212121"         # Dark Charcoal
BUTTON_TEXT_COLOR = "#FFFFFF"  # White text on buttons
BUTTON_MAIN_BG_COLOR = PRIMARY_COLOR # Main background for buttons
BUTTON_HOVER_COLOR = "#C62828" # Dark Zomato Red
SUCCESS_COLOR = "#43A047"      # Fresh Green
ERROR_COLOR = "#E53935"        # Alert Red
DISABLED_BUTTON_COLOR = "#B0BEC5" # Cool Grey

# Font Settings (unchanged)
FONT_FAMILY = "Roboto"
FONT_SIZE_NORMAL = 14
FONT_SIZE_LARGE = 18

# Derived font sizes for specific UI elements
HEADING_FONT_SIZE = FONT_SIZE_LARGE  # e.g., 18
BODY_FONT_SIZE = FONT_SIZE_NORMAL    # e.g., 14
BUTTON_FONT_SIZE = FONT_SIZE_NORMAL  # e.g., 14

# Other Constants
WINDOW_ICON_PATH = "swigato_icon.ico"
APP_LOGO_PATH = "swigato_icon.png"

# Admin Panel Light Theme Colors
ADMIN_BACKGROUND_COLOR = "#F0F2F5"  # Light Grayish Blue (Modern UI)
ADMIN_TEXT_COLOR = "#282828"        # Dark grey for text
ADMIN_PRIMARY_COLOR = "#0078FF"     # A modern, friendly Blue (can be used for accents or buttons)
ADMIN_PRIMARY_ACCENT_COLOR = "#E6F3FF" # Very light blue for accents/hovers
ADMIN_SECONDARY_ACCENT_COLOR = "#D0E7FF" # Slightly darker light blue

ADMIN_TABLE_HEADER_BG_COLOR = "#B3D9FF"  # Soft pastel blue
ADMIN_TABLE_HEADER_TEXT_COLOR = "#000000" # Black
ADMIN_TABLE_ROW_LIGHT_COLOR = "#FFFFFF"   # White
ADMIN_TABLE_ROW_DARK_COLOR = "#F8F9FA"    # Very light grey (almost white)
ADMIN_TABLE_BORDER_COLOR = "#DDE2E5"   # Light grey for borders
ADMIN_TABLE_TEXT_COLOR = "#333333"       # Dark grey for cell text
ADMIN_FRAME_FG_COLOR = "#FFFFFF"       # White for card-like elements within admin panel

ADMIN_BUTTON_FG_COLOR = "#007BFF"       # Primary blue for buttons
ADMIN_BUTTON_HOVER_COLOR = "#0056b3"    # Darker blue for hover
ADMIN_BUTTON_TEXT_COLOR = "#FFFFFF"     # White text for buttons

ICON_PATH = "swigato_icon.ico"

def set_swigato_icon(window):
    """Set the Swigato brand icon on a Tkinter/CTk window, with error handling."""
    from gui_constants import ICON_PATH
    if hasattr(window, 'iconbitmap'):
        try:
            import os
            if os.path.exists(ICON_PATH):
                window.iconbitmap(ICON_PATH)
            else:
                logging.warning(f"Swigato icon file not found at {ICON_PATH}.")
        except Exception as e:
            logging.error(f"Failed to set Swigato icon: {e}")
    else:
        logging.warning("Window does not support iconbitmap().")

def safe_focus(widget):
    """Safely set focus to a widget if it exists and its top-level window exists."""
    try:
        if widget and widget.winfo_exists():
            # Check if the widget's top-level window also exists
            toplevel_window = widget.winfo_toplevel()
            if toplevel_window and toplevel_window.winfo_exists():
                widget.focus()
            else:
                logging.warning(f"Could not set focus: Widget's top-level window does not exist for {widget}.")
    except Exception as e:
        # This might catch errors if winfo_exists() or winfo_toplevel() are called on an already destroyed widget
        logging.warning(f"Could not set focus due to an error: {e} for widget {widget}")

def center_window(window, width, height):
    """Center a window on the screen with the given width and height."""
    window.update_idletasks()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    window.geometry(f"{width}x{height}+{x}+{y}")