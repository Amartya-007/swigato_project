import customtkinter as ctk
import os  # Added for path joining
from PIL import Image  # Added to handle potential errors if image is not found by load_image
from gui_constants import BACKGROUND_COLOR, TEXT_COLOR, PRIMARY_COLOR, BUTTON_HOVER_COLOR, FRAME_BORDER_COLOR, FRAME_FG_COLOR, SECONDARY_COLOR, SUCCESS_COLOR
from restaurants.models import MenuItem
from utils.image_loader import load_image  # Import the image loader
from utils.logger import log  # Import the logger

class MenuScreen(ctk.CTkFrame):
    def __init__(self, app_ref, user, restaurant, show_cart_callback):  # Changed master to app_ref
        super().__init__(app_ref, fg_color=BACKGROUND_COLOR)  # Pass app_ref as master to CTkFrame
        self.app_ref = app_ref  # Store SwigatoApp instance as app_ref
        self.user = user  # Can be None initially
        self.restaurant = restaurant  # Can be None initially
        self.show_cart_callback = show_cart_callback  # Store callback

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)  # For header (Back button and Restaurant Name)
        self.grid_rowconfigure(1, weight=1)  # For menu items list

        # --- Header Frame ---
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        header_frame.grid_columnconfigure(0, weight=0)  # Back button
        header_frame.grid_columnconfigure(1, weight=1)  # Restaurant name (centered or to the right of back)
        header_frame.grid_columnconfigure(2, weight=0)  # View Cart button

        back_button = ctk.CTkButton(header_frame, text="< Back to Restaurants",
                                    command=self.go_back_to_main_app,
                                    fg_color=SECONDARY_COLOR, text_color=TEXT_COLOR,
                                    hover_color=BUTTON_HOVER_COLOR,
                                    font=ctk.CTkFont(weight="bold"))
        back_button.grid(row=0, column=0, sticky="w")

        restaurant_name_text = self.restaurant.name if self.restaurant else "Menu"
        restaurant_name_label = ctk.CTkLabel(header_frame, text=restaurant_name_text,
                                             text_color=PRIMARY_COLOR,
                                             font=ctk.CTkFont(size=24, weight="bold"))
        restaurant_name_label.grid(row=0, column=1, padx=(20, 0), sticky="w")

        view_cart_button = ctk.CTkButton(header_frame, text="View Cart",
                                         command=self.show_cart_callback,  # Use the new callback
                                         fg_color=SUCCESS_COLOR,
                                         hover_color=BUTTON_HOVER_COLOR,
                                         text_color=TEXT_COLOR,
                                         font=ctk.CTkFont(weight="bold"))
        view_cart_button.grid(row=0, column=2, padx=(10, 0), sticky="e")

        # Status Label (for messages like "Item added to cart")
        self.status_label = ctk.CTkLabel(self, text="", font=ctk.CTkFont(size=12), text_color=SUCCESS_COLOR)
        self.status_label.grid(row=2, column=0, pady=(0, 10))

        # --- Menu Items Scrollable Frame ---
        self.menu_items_scroll_frame = ctk.CTkScrollableFrame(self, fg_color=BACKGROUND_COLOR, border_width=0)
        self.menu_items_scroll_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.menu_items_scroll_frame.grid_columnconfigure(0, weight=1)

        self.load_menu_items()

    def load_menu_items(self):
        log(f"MenuScreen.load_menu_items called for restaurant: {self.restaurant.name if self.restaurant else 'None'}")  # ADDED LOG
        # Clear existing items
        for widget in self.menu_items_scroll_frame.winfo_children():
            widget.destroy()

        if not self.restaurant:  # Check if a restaurant is actually loaded
            log("No restaurant selected, displaying message.")  # ADDED LOG
            no_restaurant_label = ctk.CTkLabel(self.menu_items_scroll_frame,
                                               text="No restaurant selected or menu available.",
                                               text_color=TEXT_COLOR,
                                               font=ctk.CTkFont(size=16))
            no_restaurant_label.grid(row=0, column=0, pady=20)
            return

        menu_items = self.restaurant.menu

        log(f"Retrieved {len(menu_items)} items from restaurant.menu for '{self.restaurant.name}'")  # ADDED LOG

        if not menu_items:
            log(f"Menu for '{self.restaurant.name}' is empty, displaying message.")  # ADDED LOG
            no_items_label = ctk.CTkLabel(self.menu_items_scroll_frame,
                                          text="This restaurant's menu is currently empty.",
                                          text_color=TEXT_COLOR,
                                          font=ctk.CTkFont(size=16))
            no_items_label.grid(row=0, column=0, pady=20)
            return

        categorized_menu = {}
        for item in menu_items:
            if item.category not in categorized_menu:
                categorized_menu[item.category] = []
            categorized_menu[item.category].append(item)

        current_row = 0
        for category, items_in_category in categorized_menu.items():
            category_label = ctk.CTkLabel(self.menu_items_scroll_frame, text=category,
                                          font=ctk.CTkFont(size=20, weight="bold"),
                                          text_color=PRIMARY_COLOR)
            category_label.grid(row=current_row, column=0, pady=(15, 5), sticky="w")
            current_row += 1

            for item in items_in_category:
                item_card = ctk.CTkFrame(self.menu_items_scroll_frame,
                                         fg_color=FRAME_FG_COLOR,
                                         border_color=FRAME_BORDER_COLOR,
                                         border_width=1,
                                         corner_radius=8)
                item_card.grid(row=current_row, column=0, pady=(0, 10), sticky="ew")
                # Configure columns for image, details, and button
                item_card.grid_columnconfigure(0, weight=0)  # Image column (fixed size)
                item_card.grid_columnconfigure(1, weight=1)  # Name, desc, price
                item_card.grid_columnconfigure(2, weight=0)  # Add to cart button

                # Load and display menu item image
                image_label = None
                if item.image_filename:
                    # Construct absolute path to the image
                    project_root = self.app_ref.project_root  # Use app_ref
                    image_path = os.path.join(project_root, "assets", "menu_items", item.image_filename)
                    
                    # Log the path being attempted
                    log(f"Attempting to load menu item image from: {image_path}")
                    
                    ctk_image = load_image(image_path, size=(100, 100))  # Smaller size for menu items
                    if ctk_image:
                        image_label = ctk.CTkLabel(item_card, image=ctk_image, text="")
                        image_label.grid(row=0, column=0, rowspan=3, padx=10, pady=10, sticky="ns")  # Span 3 rows (name, desc, price)

                if not image_label:  # Fallback if image is not loaded or not available
                    image_label = ctk.CTkLabel(item_card, text="No Image", width=100, height=100, fg_color="gray", text_color="white")
                    image_label.grid(row=0, column=0, rowspan=3, padx=10, pady=10, sticky="ns")

                # Frame for text details (name, desc, price)
                details_frame = ctk.CTkFrame(item_card, fg_color="transparent")
                details_frame.grid(row=0, column=1, rowspan=3, padx=(0, 10), pady=10, sticky="nsew")
                details_frame.grid_columnconfigure(0, weight=1)

                item_name_label = ctk.CTkLabel(details_frame, text=item.name,
                                               font=ctk.CTkFont(size=16, weight="bold"),
                                               text_color=TEXT_COLOR, anchor="w")
                item_name_label.grid(row=0, column=0, pady=(0, 2), sticky="ew")

                item_desc_label = ctk.CTkLabel(details_frame, text=item.description,
                                               font=ctk.CTkFont(size=12),
                                               text_color=TEXT_COLOR, wraplength=300, justify="left", anchor="w")  # Adjusted wraplength
                item_desc_label.grid(row=1, column=0, pady=(0, 5), sticky="ew")

                item_price_label = ctk.CTkLabel(details_frame, text=f"₹{item.price:.2f}",
                                                font=ctk.CTkFont(size=14, weight="bold"),
                                                text_color=SUCCESS_COLOR, anchor="w")
                item_price_label.grid(row=2, column=0, pady=(0, 0), sticky="ew")

                add_to_cart_button = ctk.CTkButton(item_card, text="Add to Cart",
                                                   fg_color=PRIMARY_COLOR,
                                                   hover_color=BUTTON_HOVER_COLOR,
                                                   text_color=TEXT_COLOR,
                                                   font=ctk.CTkFont(weight="bold"),
                                                   width=100,
                                                   command=lambda i=item: self._add_to_cart(i))
                add_to_cart_button.grid(row=0, column=2, rowspan=3, padx=15, pady=10, sticky="e")  # Placed in column 2
                current_row += 1

    def _add_to_cart(self, menu_item: MenuItem):
        if self.app_ref.cart:  # Use app_ref
            added = self.app_ref.cart.add_item(menu_item, 1)  # Use app_ref
            if added:
                self.status_label.configure(text=f"'{menu_item.name}' added to cart!", text_color=SUCCESS_COLOR)
            else:
                self.status_label.configure(text=f"Failed to add '{menu_item.name}'.", text_color="red")
        else:
            self.status_label.configure(text="Error: Cart not available.", text_color="red")
        self.after(3000, lambda: self.status_label.configure(text=""))

    def go_back_to_main_app(self):
        self.app_ref.show_main_app_screen(self.user)  # Use app_ref
