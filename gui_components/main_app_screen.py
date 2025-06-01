import customtkinter as ctk
import os
from PIL import Image, ImageTk
from gui_constants import BACKGROUND_COLOR, TEXT_COLOR, PRIMARY_COLOR, BUTTON_HOVER_COLOR, FRAME_BORDER_COLOR, FRAME_FG_COLOR, SECONDARY_COLOR
from utils.image_loader import load_image
from utils.logger import log

class MainAppScreen(ctk.CTkFrame):
    def __init__(self, app_ref, user, show_menu_callback, show_cart_callback, logout_callback):
        super().__init__(app_ref, fg_color=BACKGROUND_COLOR)
        self.app_ref = app_ref # Store reference to the main SwigatoApp instance
        self.user = user
        self.show_menu_callback = show_menu_callback
        self.show_cart_callback = show_cart_callback
        self.logout_callback = logout_callback
        self.restaurants = []

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # --- Header Frame ---
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        header_frame.grid_columnconfigure(0, weight=1) # Welcome message
        header_frame.grid_columnconfigure(1, weight=0) # View Cart button
        header_frame.grid_columnconfigure(2, weight=0) # Logout button
        header_frame.grid_columnconfigure(3, weight=0) # Admin Panel button (if admin)

        welcome_text = f"Welcome, {self.user.username}!"
        self.welcome_label = ctk.CTkLabel(header_frame, text=welcome_text,
                                          text_color=PRIMARY_COLOR,
                                          font=ctk.CTkFont(size=20, weight="bold"))
        self.welcome_label.grid(row=0, column=0, sticky="w")

        view_cart_button = ctk.CTkButton(header_frame, text="View Cart",
                                         command=self.show_cart_callback,
                                         fg_color=SECONDARY_COLOR,
                                         hover_color=BUTTON_HOVER_COLOR,
                                         text_color=TEXT_COLOR,
                                         font=ctk.CTkFont(weight="bold"))
        view_cart_button.grid(row=0, column=1, padx=(0,10), sticky="e")

        # Add Admin Panel button if user is admin
        if hasattr(self.user, "is_admin") and self.user.is_admin:
            admin_panel_button = ctk.CTkButton(
                header_frame,
                text="Admin Panel",
                command=lambda: self.app_ref.show_admin_screen(self.user),
                fg_color=SECONDARY_COLOR,
                hover_color=BUTTON_HOVER_COLOR,
                text_color=TEXT_COLOR,
                font=ctk.CTkFont(weight="bold")
            )
            admin_panel_button.grid(row=0, column=2, padx=(0,10), sticky="e")
            logout_col = 3
        else:
            logout_col = 2

        logout_button = ctk.CTkButton(header_frame, text="Logout",
                                      command=self.logout_callback,
                                      fg_color="#D32F2F",  # Red color for logout
                                      hover_color="#B71C1C",
                                      text_color=TEXT_COLOR,
                                      font=ctk.CTkFont(weight="bold"))
        logout_button.grid(row=0, column=logout_col, sticky="e")

        # --- Restaurant List Scrollable Frame ---
        self.restaurant_scroll_frame = ctk.CTkScrollableFrame(self, fg_color=BACKGROUND_COLOR, border_width=0)
        self.restaurant_scroll_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.restaurant_scroll_frame.grid_columnconfigure(0, weight=1)

        self.load_restaurants()

    def load_restaurants(self):
        log("MainAppScreen.load_restaurants called")
        # Clear existing restaurant widgets
        for widget in self.restaurant_scroll_frame.winfo_children():
            widget.destroy()

        # Fetch restaurants (assuming a method in SwigatoApp or a direct model call)
        # For now, using the restaurant model directly as per previous structure
        from restaurants.models import Restaurant # Local import to avoid circular dependency issues at module level
        self.restaurants = Restaurant.get_all()
        log(f"Loaded {len(self.restaurants)} restaurants.")

        if not self.restaurants:
            no_restaurants_label = ctk.CTkLabel(self.restaurant_scroll_frame,
                                                text="No restaurants available at the moment.",
                                                text_color=TEXT_COLOR,
                                                font=ctk.CTkFont(size=16))
            no_restaurants_label.grid(row=0, column=0, pady=20)
            return

        for i, restaurant in enumerate(self.restaurants):
            restaurant_card = ctk.CTkFrame(self.restaurant_scroll_frame,
                                           fg_color=FRAME_FG_COLOR,
                                           border_color=FRAME_BORDER_COLOR,
                                           border_width=1,
                                           corner_radius=8)
            restaurant_card.grid(row=i, column=0, pady=(0, 10), sticky="ew")
            restaurant_card.grid_columnconfigure(0, weight=0) # Image
            restaurant_card.grid_columnconfigure(1, weight=1) # Details
            restaurant_card.grid_columnconfigure(2, weight=0) # Button

            image_label = None
            if restaurant.image_filename:
                project_root = self.app_ref.project_root # Use app_ref
                image_path = os.path.join(project_root, "assets", "restaurants", restaurant.image_filename)
                log(f"Attempting to load restaurant image from: {image_path}")
                ctk_image = load_image(image_path, size=(120, 120))
                if ctk_image:
                    image_label = ctk.CTkLabel(restaurant_card, image=ctk_image, text="")
                    image_label.grid(row=0, column=0, rowspan=3, padx=10, pady=10, sticky="ns")
            
            if not image_label: # Fallback if image loading fails or no image_filename
                image_label = ctk.CTkLabel(restaurant_card, text="No Image", width=120, height=120, fg_color="gray", text_color="white")
                image_label.grid(row=0, column=0, rowspan=3, padx=10, pady=10, sticky="ns")

            details_frame = ctk.CTkFrame(restaurant_card, fg_color="transparent")
            details_frame.grid(row=0, column=1, rowspan=3, padx=(0,10), pady=10, sticky="nsew")
            details_frame.grid_columnconfigure(0, weight=1)

            name_label = ctk.CTkLabel(details_frame, text=restaurant.name,
                                      font=ctk.CTkFont(size=18, weight="bold"),
                                      text_color=TEXT_COLOR, anchor="w")
            name_label.grid(row=0, column=0, pady=(0, 2), sticky="ew")

            cuisine_text = f"Cuisine: {restaurant.cuisine_type}"
            cuisine_label = ctk.CTkLabel(details_frame, text=cuisine_text,
                                         font=ctk.CTkFont(size=12),
                                         text_color=TEXT_COLOR, anchor="w")
            cuisine_label.grid(row=1, column=0, pady=(0, 2), sticky="ew")

            rating_text = f"Rating: {restaurant.rating:.1f}/5.0 ({restaurant.get_review_count()} reviews)"
            rating_label = ctk.CTkLabel(details_frame, text=rating_text,
                                        font=ctk.CTkFont(size=12),
                                        text_color=TEXT_COLOR, anchor="w")
            rating_label.grid(row=2, column=0, pady=(0, 5), sticky="ew")

            view_menu_button = ctk.CTkButton(restaurant_card, text="View Menu",
                                             fg_color=PRIMARY_COLOR,
                                             hover_color=BUTTON_HOVER_COLOR,
                                             text_color=TEXT_COLOR,
                                             font=ctk.CTkFont(weight="bold"),
                                             width=100,
                                             command=lambda r=restaurant: self.show_menu_callback(r))
            view_menu_button.grid(row=0, column=2, rowspan=3, padx=15, pady=10, sticky="e")

    def update_user_info(self, user):
        self.user = user
        self.welcome_label.configure(text=f"Welcome, {self.user.username}!")
        self.load_restaurants() # Reload restaurants, in case of user-specific content in future
