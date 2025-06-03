import customtkinter as ctk
import logging
from tkinter import filedialog
from PIL import Image, ImageTk # For image handling
import os
import shutil

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
from reviews.models import get_reviews_for_restaurant, Review
import datetime

# Setup logger for this module
logger = logging.getLogger("swigato_app.restaurant_management_screen")

ICON_PATH = "swigato_icon.ico"
DEFAULT_RESTAURANT_IMAGE = "assets/restaurants/default_restaurant.png" 
DEFAULT_MENU_ITEM_IMAGE = "assets/menu_items/menu_default.jpg"
MENU_ITEM_IMAGE_ASSETS_DIR = "assets/menu_items"

class RestaurantManagementScreen(ctk.CTkToplevel):
    def __init__(self, master, app_callbacks, loggedInUser, on_close_callback=None, restaurant_id=None, **kwargs):
        super().__init__(master, **kwargs)
        self.master_window = master
        self.app_callbacks = app_callbacks
        self.loggedInUser = loggedInUser
        self.restaurant_id = restaurant_id
        self.on_close_callback = on_close_callback

        self.current_restaurant = None
        self.restaurant_image_path = None
        self.restaurant_image_label = None
        self.menu_items_in_table = []
        self.menu_table = None
        self.current_edit_item_image_path = None
        self.current_add_item_image_path = None

        self.configure(fg_color=ADMIN_BACKGROUND_COLOR)

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

        self.update_idletasks()
        window_width = 1100
        window_height = 700
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        self.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        main_frame = ctk.CTkFrame(self, fg_color=ADMIN_BACKGROUND_COLOR)
        main_frame.pack(expand=True, fill="both", padx=10, pady=10)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=0)

        self.tab_view = ctk.CTkTabview(main_frame, 
                                       fg_color=ADMIN_FRAME_FG_COLOR,
                                       segmented_button_fg_color=ADMIN_FRAME_FG_COLOR,
                                       segmented_button_selected_color=ADMIN_PRIMARY_COLOR,
                                       segmented_button_selected_hover_color=ADMIN_PRIMARY_ACCENT_COLOR,
                                       segmented_button_unselected_color=ADMIN_SECONDARY_ACCENT_COLOR,
                                       segmented_button_unselected_hover_color=ADMIN_BUTTON_HOVER_COLOR,
                                       text_color=ADMIN_TEXT_COLOR,
                                       height=650
                                       )
        self.tab_view.grid(row=0, column=0, padx=0, pady=(0,10), sticky="nsew")

        self.tab_details = self.tab_view.add("Restaurant Details")
        self.tab_menu = self.tab_view.add("Menu Management")
        self.tab_reviews = self.tab_view.add("Reviews Management")

        self._create_details_tab(self.tab_details)
        self._create_menu_tab(self.tab_menu)
        self._create_reviews_tab(self.tab_reviews)
        
        buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        buttons_frame.grid(row=1, column=0, padx=0, pady=(10,0), sticky="ew")
        
        buttons_frame.grid_columnconfigure(0, weight=1)
        buttons_frame.grid_columnconfigure(1, weight=0)
        buttons_frame.grid_columnconfigure(2, weight=0)

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
            self._load_menu_items()
        else:
            pass 
            
        self.tab_view.set("Restaurant Details")

    def _create_details_tab(self, tab_frame):
        tab_frame.configure(fg_color=ADMIN_FRAME_FG_COLOR)
        tab_frame.grid_columnconfigure(0, weight=1)
        tab_frame.grid_columnconfigure(1, weight=1)
        tab_frame.grid_rowconfigure(5, weight=1)

        ctk.CTkLabel(tab_frame, text="Restaurant Name:", font=ctk.CTkFont(family=FONT_FAMILY, size=BODY_FONT_SIZE), text_color=ADMIN_TEXT_COLOR).grid(row=0, column=0, padx=10, pady=(10,5), sticky="w")
        self.name_entry = ctk.CTkEntry(tab_frame, font=ctk.CTkFont(family=FONT_FAMILY, size=BODY_FONT_SIZE), width=300, text_color=ADMIN_TEXT_COLOR, fg_color=ADMIN_TABLE_ROW_LIGHT_COLOR, border_color=ADMIN_TABLE_BORDER_COLOR)
        self.name_entry.grid(row=0, column=1, padx=10, pady=(10,5), sticky="ew")

        ctk.CTkLabel(tab_frame, text="Cuisine Type:", font=ctk.CTkFont(family=FONT_FAMILY, size=BODY_FONT_SIZE), text_color=ADMIN_TEXT_COLOR).grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.cuisine_entry = ctk.CTkEntry(tab_frame, font=ctk.CTkFont(family=FONT_FAMILY, size=BODY_FONT_SIZE), width=300, text_color=ADMIN_TEXT_COLOR, fg_color=ADMIN_TABLE_ROW_LIGHT_COLOR, border_color=ADMIN_TABLE_BORDER_COLOR)
        self.cuisine_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(tab_frame, text="Address:", font=ctk.CTkFont(family=FONT_FAMILY, size=BODY_FONT_SIZE), text_color=ADMIN_TEXT_COLOR).grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.address_entry = ctk.CTkEntry(tab_frame, font=ctk.CTkFont(family=FONT_FAMILY, size=BODY_FONT_SIZE), width=300, text_color=ADMIN_TEXT_COLOR, fg_color=ADMIN_TABLE_ROW_LIGHT_COLOR, border_color=ADMIN_TABLE_BORDER_COLOR)
        self.address_entry.grid(row=2, column=1, padx=10, pady=5, sticky="ew")
        
        ctk.CTkLabel(tab_frame, text="Description:", font=ctk.CTkFont(family=FONT_FAMILY, size=BODY_FONT_SIZE), text_color=ADMIN_TEXT_COLOR).grid(row=3, column=0, padx=10, pady=5, sticky="nw")
        desc_border_frame = ctk.CTkFrame(tab_frame, fg_color=ADMIN_TABLE_BORDER_COLOR, corner_radius=6)
        desc_border_frame.grid(row=3, column=1, padx=10, pady=5, sticky="nsew")
        desc_border_frame.grid_columnconfigure(0, weight=1)
        desc_border_frame.grid_rowconfigure(0, weight=1)
        self.description_textbox = ctk.CTkTextbox(desc_border_frame, font=ctk.CTkFont(family=FONT_FAMILY, size=BODY_FONT_SIZE), height=100, text_color=ADMIN_TEXT_COLOR, fg_color=ADMIN_TABLE_ROW_LIGHT_COLOR, border_color=ADMIN_TABLE_BORDER_COLOR, wrap="word", corner_radius=4)
        self.description_textbox.grid(row=0, column=0, sticky="nsew", padx=1, pady=1)

        ctk.CTkLabel(tab_frame, text="Restaurant Image:", font=ctk.CTkFont(family=FONT_FAMILY, size=BODY_FONT_SIZE), text_color=ADMIN_TEXT_COLOR).grid(row=4, column=0, padx=10, pady=5, sticky="nw")
        
        image_frame = ctk.CTkFrame(tab_frame, fg_color="transparent")
        image_frame.grid(row=4, column=1, padx=10, pady=5, sticky="nsew")
        image_frame.grid_columnconfigure(0, weight=0)
        image_frame.grid_columnconfigure(1, weight=1)

        self.restaurant_image_label = ctk.CTkLabel(image_frame, text="No image selected", width=200, height=150, fg_color=ADMIN_TABLE_ROW_DARK_COLOR, text_color=ADMIN_TEXT_COLOR, corner_radius=8)
        self.restaurant_image_label.grid(row=0, column=0, padx=(0,10), pady=5, sticky="nw")

        self.upload_image_button = ctk.CTkButton(image_frame, text="Upload Image", command=self._upload_restaurant_image, font=ctk.CTkFont(family=FONT_FAMILY, size=BUTTON_FONT_SIZE), fg_color=ADMIN_BUTTON_FG_COLOR, hover_color=ADMIN_BUTTON_HOVER_COLOR, text_color=ADMIN_BUTTON_TEXT_COLOR, width=120)
        self.upload_image_button.grid(row=0, column=1, padx=10, pady=(5,5), sticky="sw")
        
        self.details_status_label = ctk.CTkLabel(tab_frame, text="", font=ctk.CTkFont(family=FONT_FAMILY, size=BODY_FONT_SIZE-1), text_color=ERROR_COLOR)
        self.details_status_label.grid(row=6, column=0, columnspan=2, padx=10, pady=(10,0), sticky="ew")

    def _create_menu_tab(self, tab_frame):
        tab_frame.grid_columnconfigure(0, weight=1)
        tab_frame.grid_rowconfigure(1, weight=1)

        menu_controls_frame = ctk.CTkFrame(tab_frame, fg_color="transparent")
        menu_controls_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        add_menu_item_button = ctk.CTkButton(menu_controls_frame, text="Add New Menu Item",
                                        font=ctk.CTkFont(family=FONT_FAMILY, size=BUTTON_FONT_SIZE),
                                        fg_color=ADMIN_BUTTON_FG_COLOR,
                                        hover_color=ADMIN_BUTTON_HOVER_COLOR,
                                        text_color=ADMIN_BUTTON_TEXT_COLOR,
                                        command=self._open_add_menu_item_dialog)
        add_menu_item_button.pack(side="right")

        self.menu_table_frame = ctk.CTkFrame(tab_frame, fg_color=ADMIN_FRAME_FG_COLOR, corner_radius=8)
        self.menu_table_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0,10))
        self.menu_table_frame.grid_columnconfigure(0, weight=1)
        self.menu_table_frame.grid_rowconfigure(0, weight=1)
        
        if not self.restaurant_id:
            no_menu_label = ctk.CTkLabel(self.menu_table_frame, 
                                         text="Save the restaurant details first to manage its menu.",
                                         font=ctk.CTkFont(family=FONT_FAMILY, size=BODY_FONT_SIZE),
                                         text_color=ADMIN_TEXT_COLOR)
            no_menu_label.pack(expand=True, anchor="center", padx=20, pady=20)

    def _load_menu_items(self):
        if not self.restaurant_id:
            logger.info("Cannot load menu items: restaurant_id is None (new restaurant).")
            if self.menu_table:
                self.menu_table.destroy()
                self.menu_table = None
            for widget in self.menu_table_frame.winfo_children():
                widget.destroy()
            no_menu_label = ctk.CTkLabel(self.menu_table_frame, 
                                         text="Save the restaurant details first to manage its menu.",
                                         font=ctk.CTkFont(family=FONT_FAMILY, size=BODY_FONT_SIZE),
                                         text_color=ADMIN_TEXT_COLOR)
            no_menu_label.pack(expand=True, anchor="center", padx=20, pady=20)
            return

        logger.info(f"Loading menu items for restaurant ID: {self.restaurant_id}")
        
        if self.menu_table and isinstance(self.menu_table, ctk.CTkFrame):
            self.menu_table.destroy()
        elif self.menu_table:
             self.menu_table.destroy()
        self.menu_table = None
        for widget in self.menu_table_frame.winfo_children():
            widget.destroy()

        menu_items_from_db = MenuItem.get_for_restaurant(self.restaurant_id)
        logger.info(f"Found {len(menu_items_from_db)} menu items for restaurant ID: {self.restaurant_id}")
        self.menu_items_in_table = []

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
            })
            table_data.append([
                item.item_id,
                item.name,
                item.category,
                f"{item.price:.2f}",
                item.description if item.description else "N/A",
                "Edit / Delete"
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

        if row_clicked == 0:
            logger.info("Menu item table header clicked. Ignoring.")
            return

        data_row_idx = row_clicked - 1
        if not (0 <= data_row_idx < len(self.menu_items_in_table)):
            logger.warning(f"Clicked menu item data_row_idx {data_row_idx} is out of bounds.")
            return
        
        menu_item_info = self.menu_items_in_table[data_row_idx]
        menu_item_id = menu_item_info['id']
        actions_column_index = 5

        if column_clicked == actions_column_index:
            logger.info(f"\'Edit / Delete\' clicked for menu item ID: {menu_item_id} (Name: {menu_item_info['name']}).")
            self._open_edit_menu_item_dialog(menu_item_id) 
        else:
            logger.info(f"Clicked on non-action column {column_clicked} for menu item ID {menu_item_id}.")

    def _open_add_menu_item_dialog(self):
        if not self.restaurant_id:
            messagebox.showerror("Error", "Please save the restaurant details before adding menu items.")
            return
        logger.info(f"Opening dialog to ADD a new menu item for restaurant ID: {self.restaurant_id}")

        if hasattr(self, 'add_menu_item_dialog_instance') and self.add_menu_item_dialog_instance.winfo_exists():
            self.add_menu_item_dialog_instance.lift()
            safe_focus(self.add_menu_item_dialog_instance)
            return

        self.add_menu_item_dialog_instance = ctk.CTkToplevel(self)
        self.add_menu_item_dialog_instance.title("Add New Menu Item")
        set_swigato_icon(self.add_menu_item_dialog_instance)
        center_window(self.add_menu_item_dialog_instance, 500, 600)
        self.add_menu_item_dialog_instance.configure(fg_color=ADMIN_FRAME_FG_COLOR)
        self.add_menu_item_dialog_instance.transient(self)
        self.add_menu_item_dialog_instance.grab_set()
        self.current_add_item_image_path = None

        dialog_main_frame = ctk.CTkFrame(self.add_menu_item_dialog_instance, fg_color="transparent")
        dialog_main_frame.pack(expand=True, fill="both", padx=20, pady=20)
        dialog_main_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(dialog_main_frame, text="Name:", font=ctk.CTkFont(family=FONT_FAMILY, size=BODY_FONT_SIZE), text_color=ADMIN_TEXT_COLOR).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.add_item_name_entry = ctk.CTkEntry(dialog_main_frame, width=300, font=ctk.CTkFont(family=FONT_FAMILY, size=BODY_FONT_SIZE), text_color=ADMIN_TEXT_COLOR, fg_color=ADMIN_TABLE_ROW_LIGHT_COLOR, border_color=ADMIN_TABLE_BORDER_COLOR)
        self.add_item_name_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ctk.CTkLabel(dialog_main_frame, text="Description:", font=ctk.CTkFont(family=FONT_FAMILY, size=BODY_FONT_SIZE), text_color=ADMIN_TEXT_COLOR).grid(row=1, column=0, padx=5, pady=5, sticky="nw")
        self.add_item_desc_textbox = ctk.CTkTextbox(dialog_main_frame, height=80, font=ctk.CTkFont(family=FONT_FAMILY, size=BODY_FONT_SIZE), text_color=ADMIN_TEXT_COLOR, fg_color=ADMIN_TABLE_ROW_LIGHT_COLOR, border_color=ADMIN_TABLE_BORDER_COLOR, wrap="word")
        self.add_item_desc_textbox.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        ctk.CTkLabel(dialog_main_frame, text="Price (₹):", font=ctk.CTkFont(family=FONT_FAMILY, size=BODY_FONT_SIZE), text_color=ADMIN_TEXT_COLOR).grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.add_item_price_entry = ctk.CTkEntry(dialog_main_frame, font=ctk.CTkFont(family=FONT_FAMILY, size=BODY_FONT_SIZE), text_color=ADMIN_TEXT_COLOR, fg_color=ADMIN_TABLE_ROW_LIGHT_COLOR, border_color=ADMIN_TABLE_BORDER_COLOR)
        self.add_item_price_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        ctk.CTkLabel(dialog_main_frame, text="Category:", font=ctk.CTkFont(family=FONT_FAMILY, size=BODY_FONT_SIZE), text_color=ADMIN_TEXT_COLOR).grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.add_item_category_entry = ctk.CTkEntry(dialog_main_frame, font=ctk.CTkFont(family=FONT_FAMILY, size=BODY_FONT_SIZE), text_color=ADMIN_TEXT_COLOR, fg_color=ADMIN_TABLE_ROW_LIGHT_COLOR, border_color=ADMIN_TABLE_BORDER_COLOR)
        self.add_item_category_entry.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

        ctk.CTkLabel(dialog_main_frame, text="Image:", font=ctk.CTkFont(family=FONT_FAMILY, size=BODY_FONT_SIZE), text_color=ADMIN_TEXT_COLOR).grid(row=4, column=0, padx=5, pady=5, sticky="nw")
        
        add_item_image_frame = ctk.CTkFrame(dialog_main_frame, fg_color="transparent")
        add_item_image_frame.grid(row=4, column=1, padx=5, pady=5, sticky="nsew")
        add_item_image_frame.grid_columnconfigure(0, weight=0) 
        add_item_image_frame.grid_columnconfigure(1, weight=1)

        self.add_item_image_label = ctk.CTkLabel(add_item_image_frame, text="No image", width=150, height=100, fg_color=ADMIN_TABLE_ROW_DARK_COLOR, text_color=ADMIN_TEXT_COLOR, corner_radius=8)
        self.add_item_image_label.grid(row=0, column=0, padx=(0,10), pady=5, sticky="nw")
        self._display_image(DEFAULT_MENU_ITEM_IMAGE, self.add_item_image_label, default_img_path=DEFAULT_MENU_ITEM_IMAGE, target_size=(150,100))

        upload_item_image_button = ctk.CTkButton(add_item_image_frame, text="Upload Image", 
                                                 command=lambda: self._upload_menu_item_image(self.add_item_image_label, "current_add_item_image_path"),
                                                 font=ctk.CTkFont(family=FONT_FAMILY, size=BUTTON_FONT_SIZE-1), 
                                                 fg_color=ADMIN_BUTTON_FG_COLOR, hover_color=ADMIN_BUTTON_HOVER_COLOR, 
                                                 text_color=ADMIN_BUTTON_TEXT_COLOR, width=100)
        upload_item_image_button.grid(row=0, column=1, padx=10, pady=5, sticky="sw")
        
        self.add_item_status_label = ctk.CTkLabel(dialog_main_frame, text="", font=ctk.CTkFont(family=FONT_FAMILY, size=BODY_FONT_SIZE-2), text_color=ERROR_COLOR)
        self.add_item_status_label.grid(row=5, column=0, columnspan=2, padx=5, pady=(10,5), sticky="ew")

        buttons_frame_add_item = ctk.CTkFrame(dialog_main_frame, fg_color="transparent")
        buttons_frame_add_item.grid(row=6, column=0, columnspan=2, pady=(10,0), sticky="ew")
        buttons_frame_add_item.grid_columnconfigure(0, weight=1) 
        
        save_item_button = ctk.CTkButton(buttons_frame_add_item, text="Save Item", 
                                     command=self._save_new_menu_item,
                                     fg_color=ADMIN_BUTTON_FG_COLOR, hover_color=ADMIN_BUTTON_HOVER_COLOR, 
                                     text_color=ADMIN_BUTTON_TEXT_COLOR,
                                     font=ctk.CTkFont(family=FONT_FAMILY, size=BUTTON_FONT_SIZE))
        save_item_button.grid(row=0, column=1, padx=(0,10), sticky="e")

        cancel_item_button = ctk.CTkButton(buttons_frame_add_item, text="Cancel", 
                                       command=self.add_menu_item_dialog_instance.destroy,
                                       fg_color=ADMIN_SECONDARY_ACCENT_COLOR, hover_color=ADMIN_PRIMARY_ACCENT_COLOR, 
                                       text_color=ADMIN_TEXT_COLOR,
                                       font=ctk.CTkFont(family=FONT_FAMILY, size=BUTTON_FONT_SIZE))
        cancel_item_button.grid(row=0, column=2, sticky="e")
        
        safe_focus(self.add_item_name_entry)

    def _upload_menu_item_image(self, image_label_widget, path_attr_name):
        file_path = filedialog.askopenfilename(
            title="Select Menu Item Image",
            filetypes=(("Image files", "*.jpg *.jpeg *.png *.gif"), ("All files", "*.*")),
            initialdir=MENU_ITEM_IMAGE_ASSETS_DIR
        )
        if file_path:
            setattr(self, path_attr_name, file_path)
            self._display_image(file_path, image_label_widget, default_img_path=DEFAULT_MENU_ITEM_IMAGE, target_size=(150,100))
            logger.info(f"Menu item image selected: {file_path}")
            if hasattr(self, 'edit_item_status_label') and self.edit_item_status_label.winfo_exists():
                 self.edit_item_status_label.configure(text=f"Image selected: {os.path.basename(file_path)}", text_color=ADMIN_TEXT_COLOR)
            elif hasattr(self, 'add_item_status_label') and self.add_item_status_label.winfo_exists():
                 self.add_item_status_label.configure(text=f"Image selected: {os.path.basename(file_path)}", text_color=ADMIN_TEXT_COLOR)
        else:
            logger.info("Menu item image selection cancelled.")

    def _save_new_menu_item(self):
        logger.info(f"Attempting to save new menu item for restaurant ID: {self.restaurant_id}")
        
        name = self.add_item_name_entry.get().strip()
        description = self.add_item_desc_textbox.get("1.0", "end-1c").strip()
        price_str = self.add_item_price_entry.get().strip()
        category = self.add_item_category_entry.get().strip()

        if not name or not price_str or not category:
            self.add_item_status_label.configure(text="Name, Price, and Category are required.", text_color=ERROR_COLOR)
            return
        
        try:
            price = float(price_str)
            if price < 0:
                self.add_item_status_label.configure(text="Price cannot be negative.", text_color=ERROR_COLOR)
                return
        except ValueError:
            self.add_item_status_label.configure(text="Invalid price format. Please enter a number.", text_color=ERROR_COLOR)
            return

        final_image_filename = None

        if self.current_add_item_image_path and os.path.exists(self.current_add_item_image_path):
            try:
                img_basename = os.path.basename(self.current_add_item_image_path)
                target_dir = MENU_ITEM_IMAGE_ASSETS_DIR
                os.makedirs(target_dir, exist_ok=True)
                
                target_path = os.path.join(target_dir, img_basename)
                
                shutil.copy(self.current_add_item_image_path, target_path)
                logger.info(f"New menu item image '{img_basename}' copied to '{target_path}'.")
                final_image_filename = img_basename
            except Exception as e:
                logger.error(f"Error copying new menu item image '{self.current_add_item_image_path}' to '{target_path}': {e}")
                self.add_item_status_label.configure(text=f"Error saving image: {e}", text_color=ERROR_COLOR)
                return 
        
        new_item = MenuItem.create(
            restaurant_id=self.restaurant_id,
            name=name,
            description=description,
            price=price,
            category=category,
            image_filename=final_image_filename
        )

        if new_item:
            logger.info(f"New menu item '{name}' created successfully for restaurant ID {self.restaurant_id}.")
            self.add_item_status_label.configure(text="Menu item added successfully!", text_color=ADMIN_PRIMARY_COLOR)
            self._load_menu_items() 
            if hasattr(self, 'add_menu_item_dialog_instance') and self.add_menu_item_dialog_instance.winfo_exists():
                self.add_menu_item_dialog_instance.after(1000, self.add_menu_item_dialog_instance.destroy)
        else:
            logger.error(f"Failed to create new menu item '{name}' for restaurant ID {self.restaurant_id}.")
            self.add_item_status_label.configure(text="Failed to add menu item. Check logs.", text_color=ERROR_COLOR)

    def _save_edited_menu_item(self, item_id):
        logger.info(f"Attempting to save changes for menu item ID: {item_id}")
        
        if not (hasattr(self, 'edit_menu_item_dialog_instance') and self.edit_menu_item_dialog_instance.winfo_exists()):
            logger.error("Edit menu item dialog no longer exists. Cannot save.")
            messagebox.showerror("Error", "Edit dialog is closed. Cannot save changes.", parent=self)
            return

        original_item = MenuItem.get_by_id(item_id)
        if not original_item:
            messagebox.showerror("Error", "Original menu item not found. Cannot save changes.", parent=self.edit_menu_item_dialog_instance)
            self._load_menu_items()
            self.edit_menu_item_dialog_instance.destroy()
            return

        name = self.edit_item_name_entry.get().strip()
        description = self.edit_item_desc_textbox.get("1.0", "end-1c").strip()
        price_str = self.edit_item_price_entry.get().strip()
        category = self.edit_item_category_entry.get().strip()

        if not name or not price_str or not category:
            self.edit_item_status_label.configure(text="Name, Price, and Category are required.", text_color=ERROR_COLOR)
            return
        
        try:
            price = float(price_str)
            if price < 0:
                self.edit_item_status_label.configure(text="Price cannot be negative.", text_color=ERROR_COLOR)
                return
        except ValueError:
            self.edit_item_status_label.configure(text="Invalid price format. Please enter a number.", text_color=ERROR_COLOR)
            return

        final_image_filename = original_item.image_filename 

        if self.current_edit_item_image_path and os.path.exists(self.current_edit_item_image_path):
            original_image_in_assets_path = None
            if original_item.image_filename:
                original_image_in_assets_path = os.path.join(MENU_ITEM_IMAGE_ASSETS_DIR, original_item.image_filename)
            
            norm_current_selected_path = os.path.normpath(self.current_edit_item_image_path)
            norm_original_assets_path = os.path.normpath(original_image_in_assets_path) if original_image_in_assets_path else None

            is_new_or_different_image = True 
            if norm_original_assets_path and norm_current_selected_path == norm_original_assets_path:
                is_new_or_different_image = False
                final_image_filename = original_item.image_filename 
            
            if is_new_or_different_image:
                try:
                    img_basename = os.path.basename(self.current_edit_item_image_path)
                    target_dir = MENU_ITEM_IMAGE_ASSETS_DIR
                    os.makedirs(target_dir, exist_ok=True)
                    target_path = os.path.join(target_dir, img_basename)
                    
                    if norm_current_selected_path != os.path.normpath(target_path):
                         shutil.copy(self.current_edit_item_image_path, target_path)
                         logger.info(f"Menu item image '{img_basename}' copied/updated to '{target_path}'.")
                    else:
                         logger.info(f"Menu item image '{img_basename}' is already at target '{target_path}'. No copy needed.")
                    final_image_filename = img_basename
                except Exception as e:
                    logger.error(f"Error copying menu item image '{self.current_edit_item_image_path}' to assets: {e}")
                    self.edit_item_status_label.configure(text=f"Error saving image: {e}", text_color=ERROR_COLOR)
                    final_image_filename = original_item.image_filename 
        elif not self.current_edit_item_image_path and original_item.image_filename:
            pass 
        elif not original_item.image_filename and not self.current_edit_item_image_path:
            final_image_filename = None

        success = original_item.update(
            name=name,
            description=description,
            price=price,
            category=category,
            image_filename=final_image_filename
        )

        if success:
            logger.info(f"Menu item ID {item_id} updated successfully.")
            self.edit_item_status_label.configure(text="Menu item updated successfully!", text_color=ADMIN_PRIMARY_COLOR)
            self._load_menu_items() 
            if hasattr(self, 'edit_menu_item_dialog_instance') and self.edit_menu_item_dialog_instance.winfo_exists():
                self.edit_menu_item_dialog_instance.after(1000, self.edit_menu_item_dialog_instance.destroy) 
        else:
            logger.error(f"Failed to update menu item ID {item_id}.")
            self.edit_item_status_label.configure(text="Failed to update menu item. Check logs.", text_color=ERROR_COLOR)

    def _open_edit_menu_item_dialog(self, menu_item_id):
        logger.info(f"Opening dialog to EDIT menu item ID: {menu_item_id}")
        
        menu_item_to_edit = MenuItem.get_by_id(menu_item_id)

        if not menu_item_to_edit:
            messagebox.showerror("Error", "Could not find menu item data to edit. It might have been deleted.")
            self._load_menu_items()
            return

        if hasattr(self, 'edit_menu_item_dialog_instance') and self.edit_menu_item_dialog_instance.winfo_exists():
            if getattr(self.edit_menu_item_dialog_instance, "editing_item_id", None) == menu_item_id:
                safe_focus(self.edit_menu_item_dialog_instance)
                return
            else:
                self.edit_menu_item_dialog_instance.destroy()

        self.edit_menu_item_dialog_instance = ctk.CTkToplevel(self)
        self.edit_menu_item_dialog_instance.editing_item_id = menu_item_id
        self.edit_menu_item_dialog_instance.title(f"Edit Menu Item: {menu_item_to_edit.name}")
        set_swigato_icon(self.edit_menu_item_dialog_instance)
        center_window(self.edit_menu_item_dialog_instance, 500, 600)
        self.edit_menu_item_dialog_instance.configure(fg_color=ADMIN_FRAME_FG_COLOR)
        self.edit_menu_item_dialog_instance.transient(self)
        self.edit_menu_item_dialog_instance.grab_set()

        dialog_main_frame = ctk.CTkFrame(self.edit_menu_item_dialog_instance, fg_color="transparent")
        dialog_main_frame.pack(expand=True, fill="both", padx=20, pady=20)
        dialog_main_frame.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(dialog_main_frame, text="Name:", font=ctk.CTkFont(family=FONT_FAMILY, size=BODY_FONT_SIZE), text_color=ADMIN_TEXT_COLOR).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.edit_item_name_entry = ctk.CTkEntry(dialog_main_frame, width=300, font=ctk.CTkFont(family=FONT_FAMILY, size=BODY_FONT_SIZE), text_color=ADMIN_TEXT_COLOR, fg_color=ADMIN_TABLE_ROW_LIGHT_COLOR, border_color=ADMIN_TABLE_BORDER_COLOR)
        self.edit_item_name_entry.insert(0, menu_item_to_edit.name)
        self.edit_item_name_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ctk.CTkLabel(dialog_main_frame, text="Description:", font=ctk.CTkFont(family=FONT_FAMILY, size=BODY_FONT_SIZE), text_color=ADMIN_TEXT_COLOR).grid(row=1, column=0, padx=5, pady=5, sticky="nw")
        self.edit_item_desc_textbox = ctk.CTkTextbox(dialog_main_frame, height=80, font=ctk.CTkFont(family=FONT_FAMILY, size=BODY_FONT_SIZE), text_color=ADMIN_TEXT_COLOR, fg_color=ADMIN_TABLE_ROW_LIGHT_COLOR, border_color=ADMIN_TABLE_BORDER_COLOR, wrap="word")
        self.edit_item_desc_textbox.insert("1.0", menu_item_to_edit.description or "")
        self.edit_item_desc_textbox.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        ctk.CTkLabel(dialog_main_frame, text="Price (₹):", font=ctk.CTkFont(family=FONT_FAMILY, size=BODY_FONT_SIZE), text_color=ADMIN_TEXT_COLOR).grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.edit_item_price_entry = ctk.CTkEntry(dialog_main_frame, font=ctk.CTkFont(family=FONT_FAMILY, size=BODY_FONT_SIZE), text_color=ADMIN_TEXT_COLOR, fg_color=ADMIN_TABLE_ROW_LIGHT_COLOR, border_color=ADMIN_TABLE_BORDER_COLOR)
        self.edit_item_price_entry.insert(0, str(menu_item_to_edit.price))
        self.edit_item_price_entry.grid(row=2, column=1, padx=5, pady=5, sticky="ew")

        ctk.CTkLabel(dialog_main_frame, text="Category:", font=ctk.CTkFont(family=FONT_FAMILY, size=BODY_FONT_SIZE), text_color=ADMIN_TEXT_COLOR).grid(row=3, column=0, padx=5, pady=5, sticky="w")
        self.edit_item_category_entry = ctk.CTkEntry(dialog_main_frame, font=ctk.CTkFont(family=FONT_FAMILY, size=BODY_FONT_SIZE), text_color=ADMIN_TEXT_COLOR, fg_color=ADMIN_TABLE_ROW_LIGHT_COLOR, border_color=ADMIN_TABLE_BORDER_COLOR)
        self.edit_item_category_entry.insert(0, menu_item_to_edit.category or "")
        self.edit_item_category_entry.grid(row=3, column=1, padx=5, pady=5, sticky="ew")

        ctk.CTkLabel(dialog_main_frame, text="Image:", font=ctk.CTkFont(family=FONT_FAMILY, size=BODY_FONT_SIZE), text_color=ADMIN_TEXT_COLOR).grid(row=4, column=0, padx=5, pady=5, sticky="nw")
        
        edit_item_image_frame = ctk.CTkFrame(dialog_main_frame, fg_color="transparent")
        edit_item_image_frame.grid(row=4, column=1, padx=5, pady=5, sticky="nsew")
        edit_item_image_frame.grid_columnconfigure(0, weight=0) 
        edit_item_image_frame.grid_columnconfigure(1, weight=1)

        self.edit_item_image_label = ctk.CTkLabel(edit_item_image_frame, text="No image", width=150, height=100, fg_color=ADMIN_TABLE_ROW_DARK_COLOR, text_color=ADMIN_TEXT_COLOR, corner_radius=8)
        self.edit_item_image_label.grid(row=0, column=0, padx=(0,10), pady=5, sticky="nw")
        self.current_edit_item_image_path = None

        if menu_item_to_edit.image_filename:
            img_path = os.path.join(MENU_ITEM_IMAGE_ASSETS_DIR, menu_item_to_edit.image_filename)
            self._display_image(img_path, self.edit_item_image_label, default_img_path=DEFAULT_MENU_ITEM_IMAGE, target_size=(150,100))
            self.current_edit_item_image_path = img_path 
        else:
            self._display_image(DEFAULT_MENU_ITEM_IMAGE, self.edit_item_image_label, default_img_path=DEFAULT_MENU_ITEM_IMAGE, target_size=(150,100))

        upload_item_image_button = ctk.CTkButton(edit_item_image_frame, text="Upload Image", 
                                                 command=lambda: self._upload_menu_item_image(self.edit_item_image_label, "current_edit_item_image_path"),
                                                 font=ctk.CTkFont(family=FONT_FAMILY, size=BUTTON_FONT_SIZE-1), 
                                                 fg_color=ADMIN_BUTTON_FG_COLOR, hover_color=ADMIN_BUTTON_HOVER_COLOR, 
                                                 text_color=ADMIN_BUTTON_TEXT_COLOR, width=100)
        upload_item_image_button.grid(row=0, column=1, padx=10, pady=5, sticky="sw")
        
        self.edit_item_status_label = ctk.CTkLabel(dialog_main_frame, text="", font=ctk.CTkFont(family=FONT_FAMILY, size=BODY_FONT_SIZE-2), text_color=ERROR_COLOR)
        self.edit_item_status_label.grid(row=5, column=0, columnspan=2, padx=5, pady=(10,5), sticky="ew")

        buttons_frame_edit_item = ctk.CTkFrame(dialog_main_frame, fg_color="transparent")
        buttons_frame_edit_item.grid(row=6, column=0, columnspan=2, pady=(10,0), sticky="ew")
        buttons_frame_edit_item.grid_columnconfigure(0, weight=1) 
        
        delete_item_button = ctk.CTkButton(buttons_frame_edit_item, text="Delete Item", 
                                     command=lambda item_id=menu_item_id: self._confirm_delete_menu_item(item_id),
                                     fg_color=ERROR_COLOR, hover_color="#C00000", text_color="white",
                                     font=ctk.CTkFont(family=FONT_FAMILY, size=BUTTON_FONT_SIZE))
        delete_item_button.grid(row=0, column=1, padx=(0,10), sticky="e")

        save_item_button = ctk.CTkButton(buttons_frame_edit_item, text="Save Changes", 
                                     command=lambda item_id=menu_item_id: self._save_edited_menu_item(item_id),
                                     fg_color=ADMIN_BUTTON_FG_COLOR, hover_color=ADMIN_BUTTON_HOVER_COLOR, 
                                     text_color=ADMIN_BUTTON_TEXT_COLOR,
                                     font=ctk.CTkFont(family=FONT_FAMILY, size=BUTTON_FONT_SIZE))
        save_item_button.grid(row=0, column=2, padx=(0,10), sticky="e")

        cancel_item_button = ctk.CTkButton(buttons_frame_edit_item, text="Cancel", 
                                       command=self.edit_menu_item_dialog_instance.destroy,
                                       fg_color=ADMIN_SECONDARY_ACCENT_COLOR, hover_color=ADMIN_PRIMARY_ACCENT_COLOR, 
                                       text_color=ADMIN_TEXT_COLOR,
                                       font=ctk.CTkFont(family=FONT_FAMILY, size=BUTTON_FONT_SIZE))
        cancel_item_button.grid(row=0, column=3, sticky="e")
        
        safe_focus(self.edit_item_name_entry)

    def _confirm_delete_menu_item(self, menu_item_id):
        menu_item_data = next((item for item in self.menu_items_in_table if item['id'] == menu_item_id), None)
        if not menu_item_data:
            return

        confirm = messagebox.askyesno("Confirm Delete",
                                       f"Are you sure you want to delete menu item: {menu_item_data['name']}?")
        if confirm:
            logger.info(f"Attempting to delete menu item ID: {menu_item_id}")
            item_to_delete = MenuItem.get_by_id(menu_item_id)
            if item_to_delete:
                if item_to_delete.delete():
                    messagebox.showinfo("Success", f"Menu item '{menu_item_data['name']}' deleted successfully.", parent=self.edit_menu_item_dialog_instance if hasattr(self, 'edit_menu_item_dialog_instance') and self.edit_menu_item_dialog_instance.winfo_exists() else self)
                    self._load_menu_items()
                    if hasattr(self, 'edit_menu_item_dialog_instance') and self.edit_menu_item_dialog_instance.winfo_exists() and getattr(self.edit_menu_item_dialog_instance, "editing_item_id", None) == menu_item_id:
                        self.edit_menu_item_dialog_instance.destroy()
                else:
                    messagebox.showerror("Error", f"Failed to delete menu item '{menu_item_data['name']}'.", parent=self.edit_menu_item_dialog_instance if hasattr(self, 'edit_menu_item_dialog_instance') and self.edit_menu_item_dialog_instance.winfo_exists() else self)
            else:
                messagebox.showerror("Error", "Menu item not found for deletion.", parent=self.edit_menu_item_dialog_instance if hasattr(self, 'edit_menu_item_dialog_instance') and self.edit_menu_item_dialog_instance.winfo_exists() else self)
                self._load_menu_items()

    def _create_reviews_tab(self, tab_frame):
        tab_frame.configure(fg_color=ADMIN_FRAME_FG_COLOR)
        tab_frame.grid_columnconfigure(0, weight=1)
        tab_frame.grid_rowconfigure(1, weight=1)

        self.reviews_table_frame = ctk.CTkFrame(tab_frame, fg_color="transparent")
        self.reviews_table_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.reviews_table_frame.grid_columnconfigure(0, weight=1)
        self.reviews_table_frame.grid_rowconfigure(0, weight=1)

        self._load_reviews()

    def _load_reviews(self):
        for widget in self.reviews_table_frame.winfo_children():
            widget.destroy()

        if not self.restaurant_id:
            ctk.CTkLabel(self.reviews_table_frame, text="Save the restaurant details first to manage reviews.",
                         font=ctk.CTkFont(family=FONT_FAMILY, size=BODY_FONT_SIZE),
                         text_color=ADMIN_TEXT_COLOR).pack(expand=True, anchor="center", padx=20, pady=20)
            return

        reviews = get_reviews_for_restaurant(self.restaurant_id)
        self.reviews_in_table = reviews

        headers = ["ID", "User", "Rating", "Comment", "Date", "Actions"]
        table_data = [headers]
        for review in reviews:
            date_str = review.review_date.strftime('%Y-%m-%d %H:%M') if isinstance(review.review_date, datetime.datetime) else str(review.review_date)
            comment_short = (review.comment[:40] + '...') if review.comment and len(review.comment) > 43 else (review.comment or "")
            table_data.append([
                review.review_id,
                review.username,
                f"{review.rating}/5",
                comment_short,
                date_str,
                "Delete"
            ])

        if len(table_data) == 1:
            ctk.CTkLabel(self.reviews_table_frame, text="No reviews found for this restaurant.",
                         font=ctk.CTkFont(family=FONT_FAMILY, size=BODY_FONT_SIZE),
                         text_color=ADMIN_TEXT_COLOR).pack(expand=True, anchor="center", padx=20, pady=20)
            return

        cell_font = ctk.CTkFont(family=FONT_FAMILY, size=BODY_FONT_SIZE - 1)
        self.reviews_table = CTkTable(master=self.reviews_table_frame,
                                      values=table_data,
                                      font=cell_font,
                                      header_color=ADMIN_TABLE_HEADER_BG_COLOR,
                                      text_color=ADMIN_TABLE_TEXT_COLOR,
                                      hover_color=ADMIN_PRIMARY_ACCENT_COLOR,
                                      colors=[ADMIN_TABLE_ROW_LIGHT_COLOR, ADMIN_TABLE_ROW_DARK_COLOR],
                                      corner_radius=6,
                                      border_width=1,
                                      border_color=ADMIN_TABLE_BORDER_COLOR,
                                      command=self._on_review_table_cell_click,
                                      wraplength=150)
        self.reviews_table.pack(expand=True, fill="both", padx=5, pady=5)

    def _on_review_table_cell_click(self, event_data):
        row_clicked = event_data["row"]
        column_clicked = event_data["column"]
        if row_clicked == 0:
            return
        data_row_idx = row_clicked - 1
        if not (0 <= data_row_idx < len(self.reviews_in_table)):
            return
        review = self.reviews_in_table[data_row_idx]
        actions_column_index = 5
        if column_clicked == actions_column_index:
            self._delete_review(review.review_id)

    def _delete_review(self, review_id):
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this review?")
        if not confirm:
            return
        success = Review.delete_review(review_id)
        if success:
            messagebox.showinfo("Success", "Review deleted successfully.")
            self._load_reviews()
        else:
            messagebox.showerror("Error", "Failed to delete review. It may not exist.")

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

    def _display_image(self, image_path, image_label_widget, default_img_path=None, target_size=(200,150)):
        try:
            effective_image_path = image_path
            if not os.path.exists(effective_image_path):
                logger.warning(f"Image not found at path: {effective_image_path}. Attempting default.")
                effective_image_path = default_img_path or DEFAULT_RESTAURANT_IMAGE 
                if not os.path.exists(effective_image_path): 
                    logger.error(f"Default image also not found at {effective_image_path}.")
                    image_label_widget.configure(text="Image not found", image=None)
                    image_label_widget.image = None 
                    return

            img = Image.open(effective_image_path)
            img.thumbnail(target_size) 
            ctk_image = ctk.CTkImage(light_image=img, dark_image=img, size=(img.width, img.height))
            image_label_widget.configure(image=ctk_image, text="")
            image_label_widget.image = ctk_image 
        except Exception as e:
            logger.error(f"Error displaying image {image_path} (effective: {effective_image_path}): {e}")
            image_label_widget.configure(text="Error loading image", image=None)
            image_label_widget.image = None

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
                self._load_menu_items()
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
                self._load_menu_items()
            else:
                logger.error(f"Failed to create restaurant '{name}'.")
                self.details_status_label.configure(text="Failed to create restaurant. Check logs.", text_color=ERROR_COLOR)

    def _on_close(self):
        logger.info(f"RestaurantManagementScreen (ID: {self.restaurant_id if self.restaurant_id else 'New'}) is closing.")
        if self.on_close_callback:
            self.on_close_callback()
        self.destroy()
        if self.master and hasattr(self.master, 'restaurant_management_window_closed'):
            self.master.restaurant_management_window_closed()
