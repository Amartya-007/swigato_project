import customtkinter as ctk
from PIL import Image, ImageTk
from gui_constants import (
    FRAME_FG_COLOR, FRAME_BORDER_COLOR, BUTTON_MAIN_BG_COLOR,
    BUTTON_HOVER_COLOR, TEXT_COLOR, SUCCESS_COLOR, ERROR_COLOR, BUTTON_TEXT_COLOR
)
from utils.image_loader import load_image
from cart.models import CartItem

class CartScreen(ctk.CTkFrame):
    def __init__(self, master, user, cart, show_main_app_callback, show_menu_callback, checkout_callback):
        super().__init__(master, fg_color=FRAME_FG_COLOR, border_color=FRAME_BORDER_COLOR, border_width=2)
        self.app = master
        self.user = user 
        self.cart = cart 
        self.show_main_app_callback = show_main_app_callback
        self.show_menu_callback = show_menu_callback
        self.checkout_callback = checkout_callback

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0) # Header Frame
        self.grid_rowconfigure(1, weight=1) # Scrollable Frame (now contains everything else)

        # Header Frame
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, pady=20, padx=20, sticky="ew")
        self.header_frame.grid_columnconfigure(0, weight=0) 
        self.header_frame.grid_columnconfigure(1, weight=1) 
        self.header_frame.grid_columnconfigure(2, weight=0)

        self.back_button = ctk.CTkButton(
            self.header_frame,
            text="< Back to Menu",
            command=self._go_back_to_menu,
            fg_color=BUTTON_MAIN_BG_COLOR,
            hover_color=BUTTON_HOVER_COLOR,
            text_color=BUTTON_TEXT_COLOR
        )
        self.back_button.grid(row=0, column=0, sticky="w")

        self.title_label = ctk.CTkLabel(self.header_frame, text="Your Shopping Cart", font=ctk.CTkFont(size=24, weight="bold"), text_color=TEXT_COLOR)
        self.title_label.grid(row=0, column=1, sticky="ew", padx=10)

        # Scrollable Frame for Cart Items AND Footer
        self.scrollable_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scrollable_frame.grid(row=1, column=0, pady=(0,20), padx=20, sticky="nsew")
        self.scrollable_frame.grid_columnconfigure(0, weight=1)

        # Footer Frame for Total and Checkout - NOW A CHILD OF SCROLLABLE_FRAME
        self.footer_frame = ctk.CTkFrame(self.scrollable_frame, fg_color="transparent")
        
        self.footer_frame.grid_columnconfigure(0, weight=1) # Total label side
        self.footer_frame.grid_columnconfigure(1, weight=0) # Button (natural width)
        self.footer_frame.grid_columnconfigure(2, weight=1) # Right spacer for centering button

        self.total_price_label = ctk.CTkLabel(self.footer_frame, text="Total: ₹0.00", font=ctk.CTkFont(size=18, weight="bold"), text_color=TEXT_COLOR)
        self.total_price_label.grid(row=0, column=0, padx=(0,10), sticky="w")

        self.checkout_button = ctk.CTkButton(
            self.footer_frame,
            text="Proceed to Checkout",
            command=self.checkout_callback,
            fg_color=SUCCESS_COLOR,
            hover_color="#00C78C",
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.checkout_button.grid(row=0, column=1, padx=10, sticky="")

        self.empty_cart_label = ctk.CTkLabel(self.scrollable_frame, text="Your cart is empty.", font=ctk.CTkFont(size=16), text_color=ERROR_COLOR)
        
        self.load_cart_items()

    def _go_back_to_menu(self):
        if self.app.current_restaurant:
            self.show_menu_callback(self.app.current_restaurant)
        else: 
            self.show_main_app_callback(self.user)

    def load_cart_items(self):
        # Clear previous item cards only
        for widget in self.scrollable_frame.winfo_children():
            if widget not in [self.empty_cart_label, self.footer_frame] and isinstance(widget, ctk.CTkFrame):
                widget.destroy()

        # Ensure footer and empty_cart_label are initially unmanaged by pack before repacking
        self.empty_cart_label.pack_forget()
        self.footer_frame.pack_forget()

        if not self.cart or not self.cart.items:
            self.empty_cart_label.pack(pady=20, padx=10, anchor="center", fill="x")
            self.total_price_label.configure(text="Total: ₹0.00")
            self.checkout_button.configure(state="disabled")
        else:
            self.checkout_button.configure(state="normal")
            cart_items = self.cart.items.values()
            for i, cart_item_obj in enumerate(cart_items):
                self._add_cart_item_card(self.scrollable_frame, cart_item_obj, i)

        # Always pack the footer at the bottom of the scrollable_frame's content
        self.footer_frame.pack(side="bottom", fill="x", pady=(15,5), padx=5)

        self.update_total_price()

    def _add_cart_item_card(self, parent_frame, cart_item: CartItem, index: int):
        item_card = ctk.CTkFrame(parent_frame, fg_color="gray25", corner_radius=10)
        item_card.pack(pady=8, padx=5, fill="x")
        item_card.grid_columnconfigure(1, weight=1)
        item_card.grid_columnconfigure(3, weight=0)
        item_card.grid_columnconfigure(5, weight=0)

        item_name_label = ctk.CTkLabel(item_card, text=cart_item.menu_item.name, font=ctk.CTkFont(size=16, weight="bold"), anchor="w")
        item_name_label.grid(row=0, column=1, padx=10, pady=(10,0), sticky="ew")

        item_price_label = ctk.CTkLabel(item_card, text=f"₹{cart_item.menu_item.price:.2f} each", font=ctk.CTkFont(size=12), anchor="w")
        item_price_label.grid(row=1, column=1, padx=10, pady=(0,10), sticky="ew")

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
        if new_quantity <= 0:
            self._remove_item(cart_item.menu_item.item_id)
        else:
            if self.cart:
                if change > 0:
                    self.cart.add_item(cart_item.menu_item, change)
                elif change < 0:
                    self.cart.remove_item(cart_item.menu_item.item_id, abs(change))
            self.load_cart_items()

    def _remove_item(self, menu_item_id: str):
        if self.cart:
            self.cart.remove_item(menu_item_id)
            self.load_cart_items()

    def update_total_price(self):
        if self.cart:
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


