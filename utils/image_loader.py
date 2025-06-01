# filepath: g:\swigato_project\utils\image_loader.py
from PIL import Image, ImageTk
import customtkinter as ctk
import os

def load_image(image_path: str, size: tuple[int, int] = (100, 100)) -> ctk.CTkImage | None:
    """
    Loads an image from the given path and returns a CTkImage object.
    If the image cannot be loaded, it returns None.

    Args:
        image_path (str): The absolute or relative path to the image file.
        size (tuple[int, int]): The desired size (width, height) for the image.

    Returns:
        ctk.CTkImage | None: A CTkImage object if successful, None otherwise.
    """
    try:
        if not os.path.exists(image_path):
            # Try to construct path from project root if it's a relative path like 'assets/image.png'
            # This assumes 'assets' is a common folder name. Adjust if your structure is different.
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # g:\swigato_project
            potential_path = os.path.join(base_dir, image_path)
            if os.path.exists(potential_path):
                image_path = potential_path
            else:
                print(f"Error: Image not found at path: {image_path} or {potential_path}")
                return None
        
        img = Image.open(image_path)
        return ctk.CTkImage(light_image=img, dark_image=img, size=size)
    except Exception as e:
        print(f"Error loading image {image_path}: {e}")
        return None
