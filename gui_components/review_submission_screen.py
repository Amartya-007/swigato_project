\
import customtkinter as ctk
from tkinter import messagebox
from gui_constants import TEXT_COLOR, BUTTON_FG_COLOR, BUTTON_HOVER_COLOR, SUCCESS_COLOR, ERROR_COLOR, FRAME_FG_COLOR
# Assuming Review model and add_review function are in reviews.models
from reviews.models import add_review 
from users.models import User # For type hinting
from restaurants.models import Restaurant # For type hinting

class ReviewSubmissionScreen(ctk.CTkToplevel):
    def __init__(self, app_ref, user: User, restaurant: Restaurant, menu_screen_ref=None):
        super().__init__(app_ref)
        self.app_ref = app_ref
        self.user = user
        self.restaurant = restaurant
        self.menu_screen_ref = menu_screen_ref # To call a refresh method later

        self.title(f"Review {self.restaurant.name}")
        self.geometry("450x450")
        self.grab_set() # Make this window modal
        self.resizable(False, False)
        
        self.configure(fg_color=FRAME_FG_COLOR)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1) # Textbox row

        # Restaurant Name Label
        restaurant_label = ctk.CTkLabel(self, text=f"Leave a review for: {self.restaurant.name}", font=ctk.CTkFont(size=16, weight="bold"), text_color=TEXT_COLOR)
        restaurant_label.grid(row=0, column=0, padx=20, pady=(20,10), sticky="ew")

        # Rating Frame
        rating_frame = ctk.CTkFrame(self, fg_color="transparent")
        rating_frame.grid(row=1, column=0, padx=20, pady=5, sticky="ew")
        rating_frame.grid_columnconfigure(1, weight=1)

        rating_text_label = ctk.CTkLabel(rating_frame, text="Rating (1-5):", font=ctk.CTkFont(size=14), text_color=TEXT_COLOR)
        rating_text_label.grid(row=0, column=0, padx=(0,10), sticky="w")
        
        self.rating_var = ctk.StringVar(value="5") # Default to 5 stars
        self.rating_options = [str(i) for i in range(1, 6)]
        self.rating_menu = ctk.CTkOptionMenu(rating_frame, variable=self.rating_var, values=self.rating_options, width=80)
        self.rating_menu.grid(row=0, column=1, sticky="w")

        # Comment Label
        comment_label = ctk.CTkLabel(self, text="Your Comment:", font=ctk.CTkFont(size=14), text_color=TEXT_COLOR)
        comment_label.grid(row=2, column=0, padx=20, pady=(10,0), sticky="w")

        # Comment Textbox
        self.comment_textbox = ctk.CTkTextbox(self, height=150, border_width=1, border_color="gray60")
        self.comment_textbox.grid(row=3, column=0, padx=20, pady=5, sticky="nsew")

        # Buttons Frame
        buttons_frame = ctk.CTkFrame(self, fg_color="transparent")
        buttons_frame.grid(row=4, column=0, padx=20, pady=(10,20), sticky="ew")
        buttons_frame.grid_columnconfigure(0, weight=1) # For spacing
        buttons_frame.grid_columnconfigure(1, weight=0) # Cancel
        buttons_frame.grid_columnconfigure(2, weight=0) # Submit

        self.cancel_button = ctk.CTkButton(buttons_frame, text="Cancel", command=self.destroy,
                                           fg_color="gray50", hover_color="gray40")
        self.cancel_button.grid(row=0, column=1, padx=(0,10))

        self.submit_button = ctk.CTkButton(buttons_frame, text="Submit Review", command=self._submit_review,
                                           fg_color=SUCCESS_COLOR, hover_color="#00C78C")
        self.submit_button.grid(row=0, column=2)
        
        self.comment_textbox.focus()

    def _submit_review(self):
        rating_str = self.rating_var.get()
        comment = self.comment_textbox.get("1.0", "end-1c").strip() # Get text and strip trailing newline

        if not rating_str:
            messagebox.showerror("Error", "Please select a rating.", parent=self)
            return
        
        try:
            rating = int(rating_str)
            if not (1 <= rating <= 5):
                raise ValueError("Rating out of range")
        except ValueError:
            messagebox.showerror("Error", "Invalid rating value. Please select a number between 1 and 5.", parent=self)
            return

        # Ensure user and restaurant objects are valid
        if not self.user or not self.user.user_id or not self.user.username:
            messagebox.showerror("Error", "User information is missing. Cannot submit review.", parent=self)
            return
        if not self.restaurant or not self.restaurant.restaurant_id:
            messagebox.showerror("Error", "Restaurant information is missing. Cannot submit review.", parent=self)
            return

        # Call the add_review function from reviews.models
        new_review = add_review(
            user_id=self.user.user_id,
            username=self.user.username,
            restaurant_id=self.restaurant.restaurant_id,
            rating=rating,
            comment=comment
        )

        if new_review:
            messagebox.showinfo("Success", "Review submitted successfully!", parent=self)
            # Optionally, refresh the menu screen if a reference is passed
            if self.menu_screen_ref and hasattr(self.menu_screen_ref, 'refresh_reviews'):
                self.menu_screen_ref.refresh_reviews()
            self.destroy() # Close the review window
        else:
            messagebox.showerror("Error", "Failed to submit review. Please try again.", parent=self)

if __name__ == '__main__':
    # This is for testing the ReviewSubmissionScreen independently
    # You'll need to mock or create App, User, and Restaurant objects
    
    class MockApp(ctk.CTk):
        def __init__(self):
            super().__init__()
            self.title("Test App for Review Screen")
            self.geometry("200x100")
            # Mock user and restaurant
            self.current_user = User(user_id=1, username="TestUser", password_hash="hash", address="123 Test St")
            self.current_restaurant = Restaurant(restaurant_id=1, name="Test Restaurant", cuisine_type="Test Cuisine", address="456 Test Ave")
            
            self.test_button = ctk.CTkButton(self, text="Open Review Screen", command=self.open_review_screen)
            self.test_button.pack(pady=20)

        def open_review_screen(self):
            review_screen = ReviewSubmissionScreen(self, self.current_user, self.current_restaurant)
            review_screen.mainloop() # This might not be ideal for Toplevel, grab_set() handles modality

    # To run this test, you would need to ensure database is initialized
    # and the mock user/restaurant IDs exist or handle it gracefully.
    # For now, this __main__ block is more of a placeholder.
    # app = MockApp()
    # app.mainloop()
    print("ReviewSubmissionScreen created. Run through the main Swigato app to test.")

