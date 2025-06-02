import customtkinter as ctk
import logging
from tkinter import filedialog
from PIL import Image, ImageTk # For image handling
import os

from gui_constants import (
    FONT_FAMILY, HEADING_FONT_SIZE, BODY_FONT_SIZE, BUTTON_FONT_SIZE,
    ADMIN_BACKGROUND_COLOR, ADMIN_FRAME_FG_COLOR, ADMIN_TEXT_COLOR,
    ADMIN_BUTTON_FG_COLOR, ADMIN_BUTTON_HOVER_COLOR, ADMIN_BUTTON_TEXT_COLOR,
    ADMIN_TABLE_HEADER_BG_COLOR, ADMIN_TABLE_ROW_LIGHT_COLOR, ADMIN_TABLE_ROW_DARK_COLOR,
    ADMIN_TABLE_BORDER_COLOR, ERROR_COLOR, ADMIN_PRIMARY_COLOR, ADMIN_SECONDARY_ACCENT_COLOR,
    ADMIN_PRIMARY_ACCENT_COLOR, ADMIN_TABLE_TEXT_COLOR, set_swigato_icon, safe_focus, center_window
)
from restaurants.models import Restaurant, MenuItem
from CTkTable import CTkTable
from tkinter import messagebox

# Setup logger for this module
logger = logging.getLogger("swigato_app.restaurant_management_screen")

ICON_PATH = "swigato_icon.ico"
DEFAULT_RESTAURANT_IMAGE = "assets/restaurants/default_restaurant.png" 
DEFAULT_MENU_ITEM_IMAGE = "assets/menu_items/menu_default.jpg"
MENU_ITEM_IMAGE_ASSETS_DIR = "assets/menu_items" # Added for menu item images

class RestaurantManagementScreen(ctk.CTkToplevel):
    # Modified __init__ to explicitly accept on_close_callback
    def __init__(self, master, app_callbacks, loggedInUser, on_close_callback=None, restaurant_id=None, **kwargs):
        super().__init__(master, **kwargs) # on_close_callback is not passed to super
        self.master_window = master # Keep a reference if needed, master is already the parent
        self.app_callbacks = app_callbacks
        self.loggedInUser = loggedInUser
        self.restaurant_id = restaurant_id
        self.on_close_callback = on_close_callback # Store the callback

        self.current_restaurant = None # To store the loaded Restaurant object
        self.restaurant_image_path = None # To store path of loaded restaurant image
        self.restaurant_image_label = None # Label to display restaurant image
        self.menu_items_in_table = [] # To store MenuItem objects or dicts
        self.menu_table = None # For the menu items table

        self.configure(fg_color=ADMIN_BACKGROUND_COLOR) # Main window background

        if self.restaurant_id:
            self.current_restaurant = Restaurant.get_by_id(self.restaurant_id)            
            if not self.current_restaurant:
                logger.error(f"RestaurantManagementScreen: Restaurant with ID {self.restaurant_id} not found.")
                messagebox.showerror("Error", "Could not load restaurant data.")
                self.destroy()
                return
            self.title(f"Swigato - Manage Restaurant: {self.current_restaurant.name}")
            set_swigato_icon(self)
        else:
            self.title("Swigato - Add New Restaurant")
            set_swigato_icon(self)

        self.update_idletasks()  # Ensure all geometry is calculated
        window_width = 1100
        window_height = 700
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        self.protocol("WM_DELETE_WINDOW", self._on_close) # Handle window close button

        # Main frame
        main_frame = ctk.CTkFrame(self, fg_color=ADMIN_BACKGROUND_COLOR)
        main_frame.pack(expand=True, fill="both", padx=10, pady=10)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(0, weight=1) # Tab view row
        main_frame.grid_rowconfigure(1, weight=0) # Buttons row

        # Tab View
        self.tab_view = ctk.CTkTabview(main_frame, 
                                       fg_color=ADMIN_FRAME_FG_COLOR,
                                       segmented_button_fg_color=ADMIN_FRAME_FG_COLOR,
                                       segmented_button_selected_color=ADMIN_PRIMARY_COLOR,
                                       segmented_button_selected_hover_color=ADMIN_PRIMARY_ACCENT_COLOR,
                                       segmented_button_unselected_color=ADMIN_SECONDARY_ACCENT_COLOR,
                                       segmented_button_unselected_hover_color=ADMIN_BUTTON_HOVER_COLOR,
                                       text_color=ADMIN_TEXT_COLOR,
                                       height=650 # Give tab view more height
                                       )
        self.tab_view.grid(row=0, column=0, padx=0, pady=(0,10), sticky="nsew")

        self.tab_details = self.tab_view.add("Restaurant Details")
        self.tab_menu = self.tab_view.add("Menu Management")
        self.tab_reviews = self.tab_view.add("Reviews Management")

        self._create_details_tab(self.tab_details)
        self._create_menu_tab(self.tab_menu)
        self._create_reviews_tab(self.tab_reviews)
        
        # Bottom Buttons Frame
        buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        buttons_frame.grid(row=1, column=0, padx=0, pady=(10,0), sticky="ew")
        
        buttons_frame.grid_columnconfigure(0, weight=1) # Spacer
        buttons_frame.grid_columnconfigure(1, weight=0) # Save/Create button
        buttons_frame.grid_columnconfigure(2, weight=0) # Close button

        self.save_or_create_button = ctk.CTkButton(
            buttons_frame, 
            text="Save Changes" if self.restaurant_id else "Create Restaurant", 
            command=self._save_or_create_restaurant,
            fg_color=ADMIN_BUTTON_FG_COLOR, 
            hover_color=ADMIN_BUTTON_HOVER_COLOR, 
            text_color=ADMIN_BUTTON_TEXT_COLOR,
            font=ctk.CTkFont(family=FONT_FAMILY, size=BUTTON_FONT_SIZE), corner_radius=8
        )
        self.save_or_create_button.grid(row=0, column=1, padx=(0,10), sticky="e")

        self.close_button = ctk.CTkButton(
            buttons_frame, text="Close", command=self._on_close,
            fg_color=ADMIN_SECONDARY_ACCENT_COLOR, hover_color=ADMIN_PRIMARY_ACCENT_COLOR, text_color=ADMIN_TEXT_COLOR,
            font=ctk.CTkFont(family=FONT_FAMILY, size=BUTTON_FONT_SIZE), corner_radius=8
        )
        self.close_button.grid(row=0, column=2, padx=(0,0), sticky="e")

        if self.current_restaurant:
            self._load_restaurant_data_into_forms()
            self._load_menu_items() # Load menu items if editing an existing restaurant
        else:
            # Potentially set default values for a new restaurant form
            pass 
            
        self.tab_view.set("Restaurant Details") # Set default tab

    def _create_details_tab(self, tab_frame):
        tab_frame.configure(fg_color=ADMIN_FRAME_FG_COLOR)
        tab_frame.grid_columnconfigure(0, weight=1) # Allow content to expand
        tab_frame.grid_columnconfigure(1, weight=1)
        tab_frame.grid_rowconfigure(5, weight=1) # Give space to description

        # Restaurant Name
        ctk.CTkLabel(tab_frame, text="Restaurant Name:", font=ctk.CTkFont(family=FONT_FAMILY, size=BODY_FONT_SIZE), text_color=ADMIN_TEXT_COLOR).grid(row=0, column=0, padx=10, pady=(10,5), sticky="w")
        self.name_entry = ctk.CTkEntry(tab_frame, font=ctk.CTkFont(family=FONT_FAMILY, size=BODY_FONT_SIZE), width=300, text_color=ADMIN_TEXT_COLOR, fg_color=ADMIN_TABLE_ROW_LIGHT_COLOR, border_color=ADMIN_TABLE_BORDER_COLOR)
        self.name_entry.grid(row=0, column=1, padx=10, pady=(10,5), sticky="ew")

        # Cuisine Type
        ctk.CTkLabel(tab_frame, text="Cuisine Type:", font=ctk.CTkFont(family=FONT_FAMILY, size=BODY_FONT_SIZE), text_color=ADMIN_TEXT_COLOR).grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.cuisine_entry = ctk.CTkEntry(tab_frame, font=ctk.CTkFont(family=FONT_FAMILY, size=BODY_FONT_SIZE), width=300, text_color=ADMIN_TEXT_COLOR, fg_color=ADMIN_TABLE_ROW_LIGHT_COLOR, border_color=ADMIN_TABLE_BORDER_COLOR)
        self.cuisine_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        # Address
        ctk.CTkLabel(tab_frame, text="Address:", font=ctk.CTkFont(family=FONT_FAMILY, size=BODY_FONT_SIZE), text_color=ADMIN_TEXT_COLOR).grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.address_entry = ctk.CTkEntry(tab_frame, font=ctk.CTkFont(family=FONT_FAMILY, size=BODY_FONT_SIZE), width=300, text_color=ADMIN_TEXT_COLOR, fg_color=ADMIN_TABLE_ROW_LIGHT_COLOR, border_color=ADMIN_TABLE_BORDER_COLOR)
        self.address_entry.grid(row=2, column=1, padx=10, pady=5, sticky="ew")
        
        # Description
        ctk.CTkLabel(tab_frame, text="Description:", font=ctk.CTkFont(family=FONT_FAMILY, size=BODY_FONT_SIZE), text_color=ADMIN_TEXT_COLOR).grid(row=3, column=0, padx=10, pady=5, sticky="nw") # sticky nw for label
        # Add border frame for description to match other input fields
        desc_border_frame = ctk.CTkFrame(tab_frame, fg_color=ADMIN_TABLE_BORDER_COLOR, corner_radius=6)
        desc_border_frame.grid(row=3, column=1, padx=10, pady=5, sticky="nsew")
        desc_border_frame.grid_columnconfigure(0, weight=1)
        desc_border_frame.grid_rowconfigure(0, weight=1)
        self.description_textbox = ctk.CTkTextbox(desc_border_frame, font=ctk.CTkFont(family=FONT_FAMILY, size=BODY_FONT_SIZE), height=100, text_color=ADMIN_TEXT_COLOR, fg_color=ADMIN_TABLE_ROW_LIGHT_COLOR, border_color=ADMIN_TABLE_BORDER_COLOR, wrap="word", corner_radius=4)
        self.description_textbox.grid(row=0, column=0, sticky="nsew", padx=1, pady=1)

        # Restaurant Image
        ctk.CTkLabel(tab_frame, text="Restaurant Image:", font=ctk.CTkFont(family=FONT_FAMILY, size=BODY_FONT_SIZE), text_color=ADMIN_TEXT_COLOR).grid(row=4, column=0, padx=10, pady=5, sticky="nw")
        
        image_frame = ctk.CTkFrame(tab_frame, fg_color="transparent")
        image_frame.grid(row=4, column=1, padx=10, pady=5, sticky="nsew")
        image_frame.grid_columnconfigure(0, weight=0) # Image label
        image_frame.grid_columnconfigure(1, weight=1) # Upload button

        self.restaurant_image_label = ctk.CTkLabel(image_frame, text="No image selected", width=200, height=150, fg_color=ADMIN_TABLE_ROW_DARK_COLOR, text_color=ADMIN_TEXT_COLOR, corner_radius=8)
        self.restaurant_image_label.grid(row=0, column=0, padx=(0,10), pady=5, sticky="nw")

        self.upload_image_button = ctk.CTkButton(image_frame, text="Upload Image", command=self._upload_restaurant_image, font=ctk.CTkFont(family=FONT_FAMILY, size=BUTTON_FONT_SIZE), fg_color=ADMIN_BUTTON_FG_COLOR, hover_color=ADMIN_BUTTON_HOVER_COLOR, text_color=ADMIN_BUTTON_TEXT_COLOR, width=120)
        self.upload_image_button.grid(row=0, column=1, padx=10, pady=(5,5), sticky="sw")
        
        # Error/Status Label for Details Tab
        self.details_status_label = ctk.CTkLabel(tab_frame, text="", font=ctk.CTkFont(family=FONT_FAMILY, size=BODY_FONT_SIZE-1), text_color=ERROR_COLOR)
        self.details_status_label.grid(row=6, column=0, columnspan=2, padx=10, pady=(10,0), sticky="ew")

    def _create_menu_tab(self, tab_frame):
        tab_frame.grid_columnconfigure(0, weight=1)
        tab_frame.grid_rowconfigure(1, weight=1) # For the table

        # Controls Frame (for Add button)
        menu_controls_frame = ctk.CTkFrame(tab_frame, fg_color="transparent")
        menu_controls_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        add_menu_item_button = ctk.CTkButton(menu_controls_frame, text="Add New Menu Item",
                                        font=ctk.CTkFont(family=FONT_FAMILY, size=BUTTON_FONT_SIZE),
                                        fg_color=ADMIN_BUTTON_FG_COLOR,
                                        hover_color=ADMIN_BUTTON_HOVER_COLOR,
                                        text_color=ADMIN_BUTTON_TEXT_COLOR,
                                        command=self._open_add_menu_item_dialog)
        add_menu_item_button.pack(side="right")

        # Menu Items Table Frame
        self.menu_table_frame = ctk.CTkFrame(tab_frame, fg_color=ADMIN_FRAME_FG_COLOR, corner_radius=8)
        self.menu_table_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0,10))
        self.menu_table_frame.grid_columnconfigure(0, weight=1)
        self.menu_table_frame.grid_rowconfigure(0, weight=1)
        
        # Placeholder for table, will be populated by _load_menu_items
        if not self.restaurant_id: # If it's a new restaurant, show a message
            no_menu_label = ctk.CTkLabel(self.menu_table_frame, 
                                         text="Save the restaurant details first to manage its menu.",
                                         font=ctk.CTkFont(family=FONT_FAMILY, size=BODY_FONT_SIZE),
                                         text_color=ADMIN_TEXT_COLOR)
            no_menu_label.pack(expand=True, anchor="center", padx=20, pady=20)

    def _load_menu_items(self):
        if not self.restaurant_id:
            logger.info("Cannot load menu items: restaurant_id is None (new restaurant).")
            # Ensure the "Save restaurant first" message is shown if the table frame was already configured
            if self.menu_table:
                self.menu_table.destroy()
                self.menu_table = None
            for widget in self.menu_table_frame.winfo_children(): # Clear previous widgets like the label
                widget.destroy()
            no_menu_label = ctk.CTkLabel(self.menu_table_frame, 
                                         text="Save the restaurant details first to manage its menu.",
                                         font=ctk.CTkFont(family=FONT_FAMILY, size=BODY_FONT_SIZE),
                                         text_color=ADMIN_TEXT_COLOR)
            no_menu_label.pack(expand=True, anchor="center", padx=20, pady=20)
            return

        logger.info(f"Loading menu items for restaurant ID: {self.restaurant_id}")
        
        # Clear existing table if any
        if self.menu_table and isinstance(self.menu_table, ctk.CTkFrame):
            self.menu_table.destroy()
        elif self.menu_table: # If it was a label or something else
             self.menu_table.destroy()
        self.menu_table = None
        for widget in self.menu_table_frame.winfo_children(): # Clear previous widgets like the label
            widget.destroy()

        menu_items_from_db = MenuItem.get_for_restaurant(self.restaurant_id)
        logger.info(f"Found {len(menu_items_from_db)} menu items for restaurant ID: {self.restaurant_id}")
        self.menu_items_in_table = [] # Reset

        headers = ["ID", "Name", "Category", "Price (₹)", "Description", "Actions"]
        table_data = [headers]

        if not menu_items_from_db:
            no_items_label = ctk.CTkLabel(self.menu_table_frame, text="No menu items found for this restaurant.",
                                         font=ctk.CTkFont(family=FONT_FAMILY, size=BODY_FONT_SIZE),
                                         text_color=ADMIN_TEXT_COLOR)
            no_items_label.pack(expand=True, anchor="center")
            self.menu_items_in_table = []
            return

        for item in menu_items_from_db:
            self.menu_items_in_table.append({
                "id": item.item_id, "name": item.name, "category": item.category, 
                "price": item.price, "description": item.description, "image": item.image_filename
            }) # Store essential info
            table_data.append([
                item.item_id,
                item.name,
                item.category,
                f"{item.price:.2f}",
                item.description if item.description else "N/A",
                "Edit / Delete" # Placeholder for action buttons/text
            ])
        
        header_font = ctk.CTkFont(family=FONT_FAMILY, size=BODY_FONT_SIZE, weight="bold")
        cell_font = ctk.CTkFont(family=FONT_FAMILY, size=BODY_FONT_SIZE -1)

        self.menu_table = CTkTable(master=self.menu_table_frame,
                                   values=table_data,
                                   font=cell_font,
                                   header_color=ADMIN_TABLE_HEADER_BG_COLOR,
                                   text_color=ADMIN_TABLE_TEXT_COLOR,
                                   hover_color=ADMIN_PRIMARY_ACCENT_COLOR,
                                   colors=[ADMIN_TABLE_ROW_LIGHT_COLOR, ADMIN_TABLE_ROW_DARK_COLOR],
                                   corner_radius=6,
                                   border_width=1,
                                   border_color=ADMIN_TABLE_BORDER_COLOR,
                                   command=self._on_menu_item_cell_click,
                                   wraplength=150 
                                  )
        self.menu_table.pack(expand=True, fill="both", padx=5, pady=5)
        logger.info("Menu items table created and displayed.")

    def _on_menu_item_cell_click(self, event_data):
        row_clicked = event_data["row"]
        column_clicked = event_data["column"]

        if row_clicked == 0: # Header row
            logger.info("Menu item table header clicked. Ignoring.")
            return

        data_row_idx = row_clicked - 1
        if not (0 <= data_row_idx < len(self.menu_items_in_table)):
            logger.warning(f"Clicked menu item data_row_idx {data_row_idx} is out of bounds.")
            return
        
        menu_item_info = self.menu_items_in_table[data_row_idx]
        menu_item_id = menu_item_info['id']
        actions_column_index = 5 # Assuming "Actions" is the 6th column (index 5)

        if column_clicked == actions_column_index:
            logger.info(f"\'Edit / Delete\' clicked for menu item ID: {menu_item_id} (Name: {menu_item_info['name']}).")
            self._open_edit_menu_item_dialog(menu_item_id) 
        else:
            logger.info(f"Clicked on non-action column {column_clicked} for menu item ID {menu_item_id}.")

    def _open_add_menu_item_dialog(self):
        if not self.restaurant_id:
            messagebox.showerror("Error", "Please save the restaurant details before adding menu items.")
            return
        logger.info(f"Placeholder: Opening dialog to ADD a new menu item for restaurant ID: {self.restaurant_id}")
        messagebox.showinfo("Add Menu Item", f"Functionality to ADD a menu item for restaurant {self.restaurant_id} is under development.")

    def _open_edit_menu_item_dialog(self, menu_item_id):
        logger.info(f"Placeholder: Opening dialog to EDIT menu item ID: {menu_item_id}")
        menu_item_data = next((item for item in self.menu_items_in_table if item['id'] == menu_item_id), None)
        if not menu_item_data:
            messagebox.showerror("Error", "Could not find menu item data to edit.")
            return
        messagebox.showinfo("Edit Menu Item", f"Functionality to EDIT menu item ID {menu_item_id} (Name: {menu_item_data['name']}) is under development.")

    def _confirm_delete_menu_item(self, menu_item_id):
        menu_item_data = next((item for item in self.menu_items_in_table if item['id'] == menu_item_id), None)
        if not menu_item_data:
            return

        confirm = messagebox.askyesno("Confirm Delete",
                                       f"Are you sure you want to delete menu item: {menu_item_data['name']}?")
        if confirm:
            logger.info(f"Placeholder: Deleting menu item ID: {menu_item_id}")
            messagebox.showinfo("Delete Menu Item", f"Functionality to DELETE menu item ID {menu_item_id} is under development.")

    def _create_reviews_tab(self, tab_frame):
        tab_frame.configure(fg_color=ADMIN_FRAME_FG_COLOR)
        tab_frame.grid_columnconfigure(0, weight=1)
        tab_frame.grid_rowconfigure(1, weight=1) # Table row
        ctk.CTkLabel(tab_frame, text="Reviews Management (Under Construction)", 
                     font=ctk.CTkFont(family=FONT_FAMILY, size=HEADING_FONT_SIZE),
                     text_color=ADMIN_TEXT_COLOR).pack(pady=20, padx=20, anchor="center")

    def _load_restaurant_data_into_forms(self):
        if not self.current_restaurant:
            return
        logger.info(f"Loading data for restaurant: {self.current_restaurant.name} into forms.")
        self.name_entry.insert(0, self.current_restaurant.name or "")
        self.cuisine_entry.insert(0, self.current_restaurant.cuisine_type or "")
        self.address_entry.insert(0, self.current_restaurant.address or "")
        self.description_textbox.insert("1.0", self.current_restaurant.description or "")
        
        if self.current_restaurant.image_filename:
            image_full_path = os.path.join("assets", "restaurants", self.current_restaurant.image_filename)
            self._display_image(image_full_path, self.restaurant_image_label)
            self.restaurant_image_path = image_full_path
        else:
            self.restaurant_image_label.configure(text="No image available")
            self.restaurant_image_path = None

    def _upload_restaurant_image(self):
        base_upload_dir = os.path.join("assets", "restaurants")
        os.makedirs(base_upload_dir, exist_ok=True)

        file_path = filedialog.askopenfilename(
            title="Select Restaurant Image",
            filetypes=(("Image files", "*.jpg *.jpeg *.png *.gif"), ("All files", "*.*"))
        )
        if file_path:
            self.restaurant_image_path = file_path
            self._display_image(file_path, self.restaurant_image_label)
            self.details_status_label.configure(text=f"Image selected: {os.path.basename(file_path)}", text_color=ADMIN_TEXT_COLOR)
            logger.info(f"Restaurant image selected: {file_path}")
        else:
            logger.info("Restaurant image selection cancelled.")

    def _display_image(self, image_path, image_label_widget):
        try:
            # Use default image if the given image_path does not exist
            if not os.path.exists(image_path):
                logger.warning(f"Image not found at path: {image_path} for display. Using default image.")
                image_path = DEFAULT_RESTAURANT_IMAGE
                if not os.path.exists(image_path):
                    image_label_widget.configure(text="Image not found", image=None)
                    return

            img = Image.open(image_path)
            img.thumbnail((200, 150))
            ctk_image = ctk.CTkImage(light_image=img, dark_image=img, size=(img.width, img.height))
            image_label_widget.configure(image=ctk_image, text="")
            image_label_widget.image = ctk_image
        except Exception as e:
            logger.error(f"Error displaying image {image_path}: {e}")
            image_label_widget.configure(text="Error loading image", image=None)

    def _save_or_create_restaurant(self):
        name = self.name_entry.get().strip()
        cuisine = self.cuisine_entry.get().strip()
        address = self.address_entry.get().strip()
        description = self.description_textbox.get("1.0", "end-1c").strip()

        if not name or not cuisine or not address:
            self.details_status_label.configure(text="Name, Cuisine, and Address are required.", text_color=ERROR_COLOR)
            logger.warning("Attempt to save/create restaurant with missing required fields.")
            return

        final_image_filename = None
        if self.current_restaurant and self.current_restaurant.image_filename:
            final_image_filename = self.current_restaurant.image_filename

        if self.restaurant_image_path:
            if os.path.exists(self.restaurant_image_path):
                try:
                    img_basename = os.path.basename(self.restaurant_image_path)
                    target_dir = os.path.join("assets", "restaurants")
                    os.makedirs(target_dir, exist_ok=True)
                    target_path = os.path.join(target_dir, img_basename)

                    # Only copy if source and destination are different files
                    if os.path.abspath(self.restaurant_image_path) != os.path.abspath(target_path):
                        import shutil
                        shutil.copy(self.restaurant_image_path, target_path)
                        logger.info(f"Image {img_basename} copied to {target_path} for restaurant.")
                    else:
                        logger.info(f"Image {img_basename} already in target directory; skipping copy.")
                    final_image_filename = img_basename
                except Exception as e:
                    logger.error(f"Error copying image {self.restaurant_image_path} to {target_path}: {e}")
                    self.details_status_label.configure(text=f"Error saving image: {e}", text_color=ERROR_COLOR)
                    final_image_filename = self.current_restaurant.image_filename if self.current_restaurant else None
            else:
                logger.warning(f"Selected image path {self.restaurant_image_path} does not exist at save time.")
                final_image_filename = self.current_restaurant.image_filename if self.current_restaurant else None

        if self.restaurant_id and self.current_restaurant:
            success = self.current_restaurant.update(
                name=name, cuisine_type=cuisine,
                address=address, description=description,
                image_filename=final_image_filename
            )
            if success:
                logger.info(f"Restaurant ID {self.restaurant_id} updated successfully.")
                self.details_status_label.configure(text="Restaurant updated successfully!", text_color=ADMIN_PRIMARY_COLOR)
                if self.master and hasattr(self.master, 'refresh_restaurants'):
                    self.master.refresh_restaurants()
            else:
                logger.error(f"Failed to update restaurant ID {self.restaurant_id}.")
                self.details_status_label.configure(text="Failed to update restaurant. Check logs.", text_color=ERROR_COLOR)
        else:
            new_restaurant = Restaurant.create(
                name=name, cuisine_type=cuisine,
                address=address, description=description,
                image_filename=final_image_filename
            )
            if new_restaurant:
                logger.info(f"New restaurant '{name}' created with ID {new_restaurant.restaurant_id}.")
                self.details_status_label.configure(text="Restaurant created successfully!", text_color=ADMIN_PRIMARY_COLOR)
                self.restaurant_id = new_restaurant.restaurant_id
                self.current_restaurant = new_restaurant
                self.title(f"Swigato - Manage Restaurant: {self.current_restaurant.name}")
                self.save_or_create_button.configure(text="Save Changes")
                if self.master and hasattr(self.master, 'refresh_restaurants'):
                    self.master.refresh_restaurants()
            else:
                logger.error(f"Failed to create restaurant '{name}'.")
                self.details_status_label.configure(text="Failed to create restaurant. Check logs.", text_color=ERROR_COLOR)

    def _on_close(self):
        logger.info(f"RestaurantManagementScreen (ID: {self.restaurant_id if self.restaurant_id else 'New'}) is closing.")
        if self.on_close_callback:
            self.on_close_callback() # Call the callback if it exists
        self.destroy()
        if self.master and hasattr(self.master, 'restaurant_management_window_closed'):
            self.master.restaurant_management_window_closed()
