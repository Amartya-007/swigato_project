import customtkinter as ctk
from PIL import Image, ImageTk
from gui_constants import (
    FRAME_FG_COLOR, FRAME_BORDER_COLOR, BUTTON_MAIN_BG_COLOR, # Changed from BUTTON_FG_COLOR
    BUTTON_HOVER_COLOR, TEXT_COLOR, SUCCESS_COLOR, ERROR_COLOR, BUTTON_TEXT_COLOR # Added BUTTON_TEXT_COLOR
)
from utils.image_loader import load_image # Assuming you have this utility
from cart.models import CartItem # For type hinting

class CartScreen(ctk.CTkFrame):
    def __init__(self, master, user, cart, show_main_app_callback, show_menu_callback, checkout_callback): # Added show_menu_callback and checkout_callback
        super().__init__(master, fg_color=FRAME_FG_COLOR, border_color=FRAME_BORDER_COLOR, border_width=2)
        self.app = master  # Reference to the main App instance
        self.user = user 
        self.cart = cart 
        self.show_main_app_callback = show_main_app_callback
        self.show_menu_callback = show_menu_callback # Store menu callback
        self.checkout_callback = checkout_callback # Store checkout callback

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1) # For scrollable frame

        # Header Frame
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, pady=20, padx=20, sticky="ew")
        self.header_frame.grid_columnconfigure(0, weight=0) # Back button
        self.header_frame.grid_columnconfigure(1, weight=1) # Title label (center)
        self.header_frame.grid_columnconfigure(2, weight=0) # Spacer to help center if needed, or for future icons

        self.back_button = ctk.CTkButton(
            self.header_frame,
            text="< Back to Menu",
            command=self._go_back_to_menu, # This will use self.show_menu_callback
            fg_color=BUTTON_MAIN_BG_COLOR, # Use BUTTON_MAIN_BG_COLOR for background
            hover_color=BUTTON_HOVER_COLOR,
            text_color=BUTTON_TEXT_COLOR # Use BUTTON_TEXT_COLOR for text
        )
        self.back_button.grid(row=0, column=0, sticky="w")

        self.title_label = ctk.CTkLabel(self.header_frame, text="Your Shopping Cart", font=ctk.CTkFont(size=24, weight="bold"), text_color=TEXT_COLOR)
        self.title_label.grid(row=0, column=1, sticky="ew", padx=10) # Reduced padx for title

        # Scrollable Frame for Cart Items
        self.scrollable_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scrollable_frame.grid(row=1, column=0, pady=(0,10), padx=20, sticky="nsew")
        self.scrollable_frame.grid_columnconfigure(0, weight=1)

        # Footer Frame for Total and Checkout
        self.footer_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.footer_frame.grid(row=2, column=0, pady=10, padx=20, sticky="ew")
        self.footer_frame.grid_columnconfigure(1, weight=1) # Make total label expand

        self.total_price_label = ctk.CTkLabel(self.footer_frame, text="Total: ₹0.00", font=ctk.CTkFont(size=18, weight="bold"))
        self.total_price_label.grid(row=0, column=0, padx=(0,20), sticky="w")

        self.checkout_button = ctk.CTkButton(
            self.footer_frame,
            text="Proceed to Checkout",
            command=self.checkout_callback, # Use the direct callback from SwigatoApp
            fg_color=SUCCESS_COLOR,
            hover_color="#00C78C"
        )
        self.checkout_button.grid(row=0, column=1, sticky="e")
        
        self.empty_cart_label = ctk.CTkLabel(self.scrollable_frame, text="Your cart is empty.", font=ctk.CTkFont(size=16), text_color=ERROR_COLOR)
        
        self.load_cart_items() # Load items on init

    def _go_back_to_menu(self):
        if self.app.current_restaurant:
            self.show_menu_callback(self.app.current_restaurant) # Use the passed callback
        else: 
            self.show_main_app_callback(self.user) # Pass the current user

    def load_cart_items(self):
        # Clear previous items
        for widget in self.scrollable_frame.winfo_children():
            if widget != self.empty_cart_label: # Don't destroy the empty cart label itself
                widget.destroy()

        # Use the passed cart object
        if not self.cart or not self.cart.items:
            self.empty_cart_label.pack(pady=20, padx=10, anchor="center")
            self.total_price_label.configure(text="Total: ₹0.00")
            self.checkout_button.configure(state="disabled")
            return

        self.empty_cart_label.pack_forget() # Hide if items are present
        self.checkout_button.configure(state="normal")

        cart_items = self.cart.items.values() # Use self.cart
        for i, cart_item_obj in enumerate(cart_items):
            self._add_cart_item_card(self.scrollable_frame, cart_item_obj, i)

        self.update_total_price()

    def _add_cart_item_card(self, parent_frame, cart_item: CartItem, index: int):
        item_card = ctk.CTkFrame(parent_frame, fg_color="gray25", corner_radius=10)
        item_card.pack(pady=8, padx=5, fill="x")
        item_card.grid_columnconfigure(1, weight=1) # Name label
        item_card.grid_columnconfigure(3, weight=0) # Quantity controls
        item_card.grid_columnconfigure(5, weight=0) # Remove button

        # Placeholder for item image (optional)
        # img_label = ctk.CTkLabel(item_card, text="Img", width=50, height=50, fg_color="gray40")
        # img_label.grid(row=0, column=0, rowspan=2, padx=10, pady=10, sticky="ns")

        item_name_label = ctk.CTkLabel(item_card, text=cart_item.menu_item.name, font=ctk.CTkFont(size=16, weight="bold"), anchor="w")
        item_name_label.grid(row=0, column=1, padx=10, pady=(10,0), sticky="ew")

        item_price_label = ctk.CTkLabel(item_card, text=f"₹{cart_item.menu_item.price:.2f} each", font=ctk.CTkFont(size=12), anchor="w")
        item_price_label.grid(row=1, column=1, padx=10, pady=(0,10), sticky="ew")

        # Quantity controls
        quantity_frame = ctk.CTkFrame(item_card, fg_color="transparent")
        quantity_frame.grid(row=0, column=3, rowspan=2, padx=5, pady=5, sticky="e")

        minus_button = ctk.CTkButton(quantity_frame, text="-", width=30, command=lambda ci=cart_item: self._update_quantity(ci, -1))
        minus_button.pack(side="left", padx=(0,5))

        quantity_label = ctk.CTkLabel(quantity_frame, text=str(cart_item.quantity), font=ctk.CTkFont(size=14), width=30)
        quantity_label.pack(side="left")

        plus_button = ctk.CTkButton(quantity_frame, text="+", width=30, command=lambda ci=cart_item: self._update_quantity(ci, 1))
        plus_button.pack(side="left", padx=(5,0))

        item_total_label = ctk.CTkLabel(item_card, text=f"Subtotal: ₹{cart_item.item_total:.2f}", font=ctk.CTkFont(size=14))
        item_total_label.grid(row=0, column=4, rowspan=2, padx=10, pady=5, sticky="e")
        
        remove_button = ctk.CTkButton(
            item_card, text="Remove", width=80, fg_color=ERROR_COLOR, hover_color="#C00000",
            command=lambda item_id=cart_item.menu_item.item_id: self._remove_item(item_id)
        )
        remove_button.grid(row=0, column=5, rowspan=2, padx=10, pady=5, sticky="e")


    def _update_quantity(self, cart_item: CartItem, change: int):
        new_quantity = cart_item.quantity + change
        if new_quantity <= 0: # If quantity becomes 0 or less, remove the item
            self._remove_item(cart_item.menu_item.item_id)
        else:
            # Directly update quantity in cart model (assuming direct modification is okay or add a method in Cart)
            # For simplicity, we'll assume Cart's add_item can handle negative quantities for reduction if designed so,
            # or we call a specific update_quantity method if it exists.
            # Here, we'll use add_item with a positive quantity for adding, and remove_item for reducing by one.
            if self.cart:
                if change > 0:
                    self.cart.add_item(cart_item.menu_item, change)
                elif change < 0: # change is negative
                    self.cart.remove_item(cart_item.menu_item.item_id, abs(change))
            self.load_cart_items() # Reload to reflect changes

    def _remove_item(self, menu_item_id: str):
        if self.cart:
            self.cart.remove_item(menu_item_id) # Remove all quantity of this item
            self.load_cart_items() # Reload to reflect changes

    def update_total_price(self):
        if self.cart: # Use self.cart
            total = self.cart.get_total_price()
            self.total_price_label.configure(text=f"Total: ₹{total:.2f}")
        else:
            self.total_price_label.configure(text="Total: ₹0.00")

    def update_cart_display(self, user, cart):
        self.user = user
        self.cart = cart
        self.load_cart_items()
        if self.user:
            self.title_label.configure(text=f"{self.user.username}'s Shopping Cart")
        else:
            self.title_label.configure(text="Your Shopping Cart")


