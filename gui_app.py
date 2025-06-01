import customtkinter as ctk
import os
import json
from tkinter import messagebox

# Import constants
from gui_constants import BACKGROUND_COLOR, TEXT_COLOR, PRIMARY_COLOR, BUTTON_HOVER_COLOR, SUCCESS_COLOR, DISABLED_BUTTON_COLOR

# Import screen components
from gui_components.login_screen import LoginScreen
from gui_components.signup_screen import SignupScreen
from gui_components.main_app_screen import MainAppScreen
from gui_components.menu_screen import MenuScreen
from gui_components.cart_screen import CartScreen
from cart.models import Cart
from users.auth import User

# Import for DB setup
from utils.database import initialize_database
from restaurants.models import populate_sample_restaurant_data


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Swigato Food Delivery")

        # Define project_root early
        self.project_root = os.path.dirname(os.path.abspath(__file__))

        ctk.set_appearance_mode("Dark")

        # Set window icon
        icon_path = os.path.join(self.project_root, "swigato_icon.ico")  # Use self.project_root
        try:
            self.iconbitmap(icon_path)
        except Exception as e:
            print(f"Error setting window icon: {e}")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.current_user: User | None = None
        self.current_restaurant = None
        self.cart: Cart | None = None

        self.current_screen_frame = None

        # Initialize database and populate sample data
        initialize_database()
        populate_sample_restaurant_data()

        self.show_login_screen()

    def _center_window(self, width, height):
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x_cordinate = int((screen_width / 2) - (width / 2))
        y_cordinate = int((screen_height / 2) - (height / 2))
        self.geometry(f"{width}x{height}+{x_cordinate}+{y_cordinate}")

    def _set_window_properties(self, title, width, height):
        self.title(title)
        self._center_window(width, height)

    def _create_login_screen(self):
        return LoginScreen(self, self.show_signup_screen, self.show_main_app_screen)

    def _create_signup_screen(self):
        return SignupScreen(self, self.show_login_screen)

    def _create_main_app_screen(self):
        return MainAppScreen(self, self.current_user, self.show_menu_screen, self.show_cart_screen, self.logout)

    def _create_menu_screen(self, restaurant):
        return MenuScreen(self, self.current_user, restaurant, self.show_cart_screen)

    def _create_cart_screen(self):
        self.cart_screen_instance = CartScreen(
            self, 
            self.current_user, 
            self.cart, 
            self.show_main_app_screen,  # Callback for general fallback/main screen
            self.show_menu_screen,      # Callback for "Back to Menu"
            self.handle_checkout        # Callback for "Proceed to Checkout"
        )
        return self.cart_screen_instance

    def _switch_screen(self, screen_factory_method, *factory_args, title, width, height):
        if self.current_screen_frame:
            self.current_screen_frame.destroy()
            self.current_screen_frame = None

        self.current_screen_frame = screen_factory_method(*factory_args)
        self.current_screen_frame.pack(fill="both", expand=True)
        self._set_window_properties(title, width, height)

    def show_login_screen(self, username=None):
        self.current_user = None
        self.current_restaurant = None
        self.cart = None

        self._switch_screen(self._create_login_screen, title="Swigato - Login", width=400, height=550)

        if username:
            self.current_screen_frame.username_entry.delete(0, 'end')
            self.current_screen_frame.username_entry.insert(0, username)
            self.current_screen_frame.password_entry.focus_set()
        else:
            if not self.current_screen_frame.username_entry.get():
                self.current_screen_frame.username_entry.focus_set()
            else:
                self.current_screen_frame.password_entry.focus_set()

    def show_signup_screen(self):
        self._switch_screen(self._create_signup_screen, title="Swigato - Sign Up", width=400, height=600)

    def show_main_app_screen(self, user: User):
        self.current_user = user
        self.cart = Cart(user_id=user.username if user else None)

        self._switch_screen(self._create_main_app_screen, title="Swigato - Home", width=900, height=700)

    def show_menu_screen(self, restaurant):
        if not self.current_user:
            print("Error: User not logged in. Cannot show menu.")
            self.show_login_screen()
            return
        self.current_restaurant = restaurant
        self._switch_screen(self._create_menu_screen, restaurant, title=f"Swigato - {restaurant.name}", width=900, height=700)
        # self.current_screen_frame is now the menu_screen_instance
        if self.current_screen_frame and hasattr(self.current_screen_frame, 'load_menu_items'):
            self.current_screen_frame.load_menu_items()

    def show_menu_screen_from_cart(self, restaurant):
        self.show_menu_screen(restaurant)

    def show_cart_screen(self):
        if not self.current_user:  # Check current_user first
            print("Error: User not logged in. Cannot show cart.")
            self.show_login_screen()
            return
        if not self.cart:  # Then check cart
            print("Error: Cart not initialized. Cannot show cart.")
            self.show_main_app_screen()  # Or some other appropriate screen
            return

        self._switch_screen(self._create_cart_screen, title=f"Swigato - {self.current_user.username}'s Cart", width=800, height=600)
        # self.current_screen_frame is now the cart_screen_instance
        if self.current_screen_frame and hasattr(self.current_screen_frame, 'load_cart_items'):
            self.current_screen_frame.load_cart_items()

    def handle_checkout(self):
        if self.cart and self.cart.items:
            print(f"Checkout initiated for user {self.current_user.username} with items: {self.cart.items}")
            
            # Actual order processing would happen here (e.g., save to DB)
            # For now, we just clear the cart.
            self.cart.items.clear()
            
            # If the current screen is CartScreen, update it to show it's empty before navigating
            if self.current_screen_frame and isinstance(self.current_screen_frame, CartScreen):
                 self.current_screen_frame.load_cart_items() # Update to show empty cart

            # Show a success message dialog
            try:
                messagebox.showinfo("Checkout Successful", "Your order has been placed!")
            except Exception as e:
                print(f"Error showing checkout messagebox: {e}")

            self.show_main_app_screen(self.current_user) # Go back to main screen
        else:
            print("Checkout attempt with empty cart.")
            if self.current_screen_frame and isinstance(self.current_screen_frame, CartScreen):
                try:
                    messagebox.showwarning("Empty Cart", "Your cart is empty. Please add items before checking out.")
                except Exception as e:
                    print(f"Error showing empty cart messagebox: {e}")

    def logout(self):
        self.current_user = None
        self.current_restaurant = None
        if self.cart:
            self.cart.items = {}
            self.cart = None

        remember_me_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "remember_me.json")
        if os.path.exists(remember_me_file_path):
            try:
                with open(remember_me_file_path, 'w') as f:
                    json.dump({}, f)
            except Exception as e:
                print(f"Error clearing remember_me.json on logout: {e}")

        self.show_login_screen()


if __name__ == "__main__":
    app = App()
    app.mainloop()
