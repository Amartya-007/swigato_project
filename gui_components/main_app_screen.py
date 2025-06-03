import customtkinter as ctk
import os
from PIL import Image, ImageTk
from gui_constants import BACKGROUND_COLOR, TEXT_COLOR, PRIMARY_COLOR, BUTTON_HOVER_COLOR, FRAME_BORDER_COLOR, FRAME_FG_COLOR, SECONDARY_COLOR
from utils.image_loader import load_image
from utils.logger import log
from orders.models import get_orders_by_user_id

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
        header_frame.grid_columnconfigure(2, weight=0) # Admin Panel button (if admin)

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

        # Only show Order History button for non-admin users
        if not (hasattr(self.user, "is_admin") and self.user.is_admin):
            order_history_button = ctk.CTkButton(header_frame, text="Order History",
                                                 command=self.show_order_history,
                                                 fg_color=SECONDARY_COLOR,
                                                 hover_color=BUTTON_HOVER_COLOR,
                                                 text_color=TEXT_COLOR,
                                                 font=ctk.CTkFont(weight="bold"))
            order_history_button.grid(row=0, column=3, padx=(10,0), sticky="e")

        # --- Restaurant List Scrollable Frame ---
        self.restaurant_scroll_frame = ctk.CTkScrollableFrame(self, fg_color=BACKGROUND_COLOR, border_width=0)
        self.restaurant_scroll_frame.grid(row=1, column=0, padx=20, pady=(10,80), sticky="nsew")
        self.restaurant_scroll_frame.grid_columnconfigure(0, weight=1)

        # --- Sticky Bottom Bar for Logout (use .place() to avoid grid/pack conflict) ---
        self.bottom_bar = ctk.CTkFrame(self, fg_color="#fef2f2", height=60, corner_radius=0)
        self.bottom_bar.place(relx=0, rely=1.0, relwidth=1.0, anchor="sw", y=0)
        self.bottom_bar.pack_propagate(0)
        border = ctk.CTkFrame(self.bottom_bar, fg_color="#FFCCBC", height=2)
        border.pack(side="top", fill="x")

        self.logout_button = ctk.CTkButton(
            self.bottom_bar,
            text="Logout",
            command=self.logout_callback,
            fg_color="#D32F2F",
            hover_color="#B71C1C",
            text_color="#FFFFFF",
            font=ctk.CTkFont(weight="bold"),
            corner_radius=12,
            width=120,
            height=40
        )
        self.logout_button.place(relx=1.0, rely=1.0, anchor="se", x=-20, y=-10)

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

    def show_order_history(self):
        # Destroy any previous order history window
        if hasattr(self, 'order_history_window') and self.order_history_window:
            self.order_history_window.destroy()
        self.order_history_window = ctk.CTkToplevel(self)
        self.order_history_window.title("Order History")
        self.order_history_window.geometry("900x500")
        self.order_history_window.grab_set()

        # Light theme: white background, dark text
        self.order_history_window.configure(fg_color=FRAME_FG_COLOR)
        self.order_history_window.grid_columnconfigure(0, weight=1)
        self.order_history_window.grid_rowconfigure(0, weight=0)
        self.order_history_window.grid_rowconfigure(1, weight=1)

        # Add heading label (centered, no corners, transparent background, orange text)
        heading_label = ctk.CTkLabel(
            self.order_history_window,
            text="Your Order History",
            font=ctk.CTkFont(size=25, weight="bold"),
            text_color=PRIMARY_COLOR,
            fg_color="transparent",
            anchor="center",
            justify="center"
        )
        heading_label.grid(row=0, column=0, pady=(18, 0), padx=20, sticky="n")

        orders = get_orders_by_user_id(self.user.user_id)
        orders = orders[:20]

        # --- Scrollable Frame for Table ---
        scroll_frame = ctk.CTkScrollableFrame(self.order_history_window, fg_color=FRAME_FG_COLOR, corner_radius=14, border_width=1, border_color=FRAME_BORDER_COLOR)
        scroll_frame.grid(row=1, column=0, padx=24, pady=24, sticky="nsew")
        scroll_frame.grid_columnconfigure(0, weight=1)
        scroll_frame.grid_rowconfigure(0, weight=1)

        headers = ["Order ID", "Restaurant", "Date", "Total (₹)", "Status", "Items", "Address"]
        table_data = [headers]
        for order in orders:
            date_str = order.order_date.strftime('%Y-%m-%d %H:%M') if hasattr(order.order_date, 'strftime') else str(order.order_date)
            items_str = ", ".join([f"{item.name} x{item.quantity}" for item in getattr(order, 'items', [])])
            if len(items_str) > 60:
                items_str = items_str[:57] + "..."
            address_str = order.delivery_address or "N/A"
            if len(address_str) > 30:
                address_str = address_str[:27] + "..."
            table_data.append([
                order.order_id,
                order.restaurant_name,
                date_str,
                f"{order.total_amount:.2f}",
                order.status,
                items_str,
                address_str
            ])

        if len(table_data) == 1:
            ctk.CTkLabel(scroll_frame, text="No orders found.", font=ctk.CTkFont(size=12), text_color=TEXT_COLOR, fg_color="transparent").pack(expand=True, anchor="center", padx=20, pady=20)
            return

        from CTkTable import CTkTable
        cell_font = ctk.CTkFont(size=11)
        header_font = ctk.CTkFont(size=12, weight="bold")
        orders_table = CTkTable(
            master=scroll_frame,
            values=table_data,
            font=cell_font,
            header_color=FRAME_BORDER_COLOR,
            text_color=TEXT_COLOR,
            hover_color=PRIMARY_COLOR,
            colors=[FRAME_FG_COLOR, BACKGROUND_COLOR],
            corner_radius=10,
            border_width=1,
            border_color=FRAME_BORDER_COLOR
        )
        orders_table.pack(expand=True, fill="both", padx=8, pady=8)
