import customtkinter as ctk
from PIL import Image  # For handling images
import os  # To construct absolute paths for images

# Color Palette
PRIMARY_COLOR = "#FF6347"  # Tomato Red
BACKGROUND_COLOR = "#2C3E50"  # Midnight Blue
ENTRY_BG_COLOR = "#34495E"  # Slightly Lighter Blue
TEXT_COLOR = "#ECF0F1"  # Light Gray/Off-White
BUTTON_HOVER_COLOR = "#FF7F50"  # Coral (for hover effect)
SUCCESS_COLOR = "#2ECC71"  # Emerald Green
DISABLED_BUTTON_COLOR = "#566573"  # A darker gray for disabled state


class LoginScreen(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=BACKGROUND_COLOR)
        self.master = master
        self.password_visible = False  # State for password visibility

        # Load Swigato image
        current_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(current_dir, "swigato_icon.png")
        try:
            self.swigato_image = ctk.CTkImage(light_image=Image.open(image_path), size=(100, 100))  # Adjust size as needed
            self.swigato_image_label = ctk.CTkLabel(self, image=self.swigato_image, text="")
            self.swigato_image_label.grid(row=1, column=0, pady=(20, 5), sticky="s")
        except Exception as e:
            print(f"Error loading Swigato icon: {e}")
            self.swigato_image_label = ctk.CTkLabel(self, text="Swigato", text_color=PRIMARY_COLOR, font=ctk.CTkFont(size=36, weight="bold"))
            self.swigato_image_label.grid(row=1, column=0, pady=(20, 10), sticky="s")

        # Main frame grid configuration
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)  # Top spacer
        self.grid_rowconfigure(1, weight=0)  # Swigato Image/Title
        self.grid_rowconfigure(2, weight=0)  # Form Frame
        self.grid_rowconfigure(3, weight=0)  # Signup Link
        self.grid_rowconfigure(4, weight=1)  # Bottom spacer

        # Frame for login form elements
        form_frame = ctk.CTkFrame(self, fg_color="transparent")
        form_frame.grid(row=2, column=0, padx=50, pady=(5, 20), sticky="nwe")  # Adjusted pady
        form_frame.grid_columnconfigure(0, weight=1)

        # Header within the form frame
        header_label = ctk.CTkLabel(form_frame, text="Welcome Back!", text_color=TEXT_COLOR, font=ctk.CTkFont(size=24, weight="bold"))
        header_label.grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky="n")

        # Username
        username_label = ctk.CTkLabel(form_frame, text="Username or Email:", text_color=TEXT_COLOR, font=ctk.CTkFont(size=14))
        username_label.grid(row=1, column=0, columnspan=2, pady=(0, 0), sticky="sw")
        self.username_entry = ctk.CTkEntry(form_frame, width=300, height=40, fg_color=ENTRY_BG_COLOR, text_color=TEXT_COLOR,
                                           border_color=PRIMARY_COLOR, corner_radius=5, placeholder_text="Enter your username or email")
        self.username_entry.grid(row=2, column=0, columnspan=2, pady=(0, 10), sticky="nwe")
        self.username_entry.bind("<Return>", self.login_event)
        self.username_entry.focus()  # Set initial focus

        # Password
        password_label = ctk.CTkLabel(form_frame, text="Password:", text_color=TEXT_COLOR, font=ctk.CTkFont(size=14))
        password_label.grid(row=3, column=0, columnspan=2, pady=(5, 0), sticky="sw")

        password_input_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        password_input_frame.grid(row=4, column=0, columnspan=2, pady=(0, 10), sticky="nwe")
        password_input_frame.grid_columnconfigure(0, weight=1)
        password_input_frame.grid_columnconfigure(1, weight=0)

        self.password_entry = ctk.CTkEntry(password_input_frame, width=250, height=40, fg_color=ENTRY_BG_COLOR, text_color=TEXT_COLOR,
                                           border_color=PRIMARY_COLOR, show="*", corner_radius=5, placeholder_text="Enter your password")
        self.password_entry.grid(row=0, column=0, sticky="nwe")
        self.password_entry.bind("<Return>", self.login_event)

        self.toggle_password_button = ctk.CTkButton(password_input_frame, text="Show", width=40, height=40,
                                                    fg_color=ENTRY_BG_COLOR, text_color=TEXT_COLOR, hover_color=PRIMARY_COLOR,
                                                    command=self.toggle_password_visibility)
        self.toggle_password_button.grid(row=0, column=1, padx=(5, 0), sticky="nwe")

        # Remember Me Checkbox
        self.remember_me_checkbox = ctk.CTkCheckBox(form_frame, text="Remember Me", text_color=TEXT_COLOR,
                                                    fg_color=PRIMARY_COLOR, hover_color=BUTTON_HOVER_COLOR,
                                                    border_color=PRIMARY_COLOR)
        self.remember_me_checkbox.grid(row=5, column=0, columnspan=2, pady=(0, 15), sticky="w")

        # Login Button
        self.login_button = ctk.CTkButton(form_frame, text="Login", command=self.login_event, width=300, height=40,
                                          fg_color=PRIMARY_COLOR, text_color=TEXT_COLOR, hover_color=BUTTON_HOVER_COLOR,
                                          font=ctk.CTkFont(size=16, weight="bold"), corner_radius=5)
        self.login_button.grid(row=6, column=0, columnspan=2, pady=10, sticky="nwe")

        # Status Label
        self.status_label = ctk.CTkLabel(form_frame, text="", font=ctk.CTkFont(size=12))  # Color set dynamically
        self.status_label.grid(row=7, column=0, columnspan=2, pady=(0, 10), sticky="nwe")

        # Sign Up Link
        signup_button = ctk.CTkButton(self, text="Don't have an account? Sign Up", fg_color="transparent",
                                      text_color=PRIMARY_COLOR, hover_color=BACKGROUND_COLOR,
                                      command=self.go_to_signup, font=ctk.CTkFont(size=12, underline=True))
        signup_button.grid(row=3, column=0, pady=(5, 20), sticky="n")

    def toggle_password_visibility(self):
        if self.password_visible:
            self.password_entry.configure(show="*")
            self.toggle_password_button.configure(text="Show")
            self.password_visible = False
        else:
            self.password_entry.configure(show="")
            self.toggle_password_button.configure(text="Hide")
            self.password_visible = True

    def login_event(self, event=None):
        self.status_label.configure(text="")  # Clear previous status
        original_button_text = "Login"
        self.login_button.configure(state="disabled", text="Logging in...", fg_color=DISABLED_BUTTON_COLOR)

        username = self.username_entry.get()
        password = self.password_entry.get()
        remember_me = self.remember_me_checkbox.get()

        print(f"Login attempt: Username: {username}, Password: {password}, Remember Me: {remember_me}")

        def process_login_attempt():
            if not username or not password:
                self.status_label.configure(text="Username and Password are required.", text_color=PRIMARY_COLOR)
            else:
                self.status_label.configure(text="Login: Placeholder success!", text_color=SUCCESS_COLOR)
            self.login_button.configure(state="normal", text=original_button_text, fg_color=PRIMARY_COLOR)

        self.after(500, process_login_attempt)  # Simulate network delay

    def go_to_signup(self):
        self.master.show_signup_screen()


class SignupScreen(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master, fg_color=BACKGROUND_COLOR)
        self.master = master
        self.password_visible = False
        self.confirm_password_visible = False

        # Load Swigato image
        current_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(current_dir, "swigato_icon.png")
        try:
            self.swigato_image = ctk.CTkImage(light_image=Image.open(image_path), size=(100, 100))  # Adjust size as needed
            self.swigato_image_label = ctk.CTkLabel(self, image=self.swigato_image, text="")
            self.swigato_image_label.grid(row=1, column=0, pady=(20, 5), sticky="s")
        except Exception as e:
            print(f"Error loading Swigato icon: {e}")
            self.swigato_image_label = ctk.CTkLabel(self, text="Swigato", text_color=PRIMARY_COLOR, font=ctk.CTkFont(size=36, weight="bold"))
            self.swigato_image_label.grid(row=1, column=0, pady=(20, 10), sticky="s")

        # Main frame grid configuration
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)  # Top spacer
        self.grid_rowconfigure(1, weight=0)  # Swigato Image/Title
        self.grid_rowconfigure(2, weight=0)  # Form Frame
        self.grid_rowconfigure(3, weight=0)  # Login Link
        self.grid_rowconfigure(4, weight=1)  # Bottom spacer

        form_frame = ctk.CTkFrame(self, fg_color="transparent")
        form_frame.grid(row=2, column=0, padx=50, pady=(5, 10), sticky="nwe")  # Adjusted pady
        form_frame.grid_columnconfigure(0, weight=1)

        header_label = ctk.CTkLabel(form_frame, text="Create Your Account", text_color=TEXT_COLOR,
                                    font=ctk.CTkFont(size=24, weight="bold"))
        header_label.grid(row=0, column=0, columnspan=2, pady=(0, 15), sticky="n")

        username_label = ctk.CTkLabel(form_frame, text="Username:", text_color=TEXT_COLOR, font=ctk.CTkFont(size=14))
        username_label.grid(row=1, column=0, columnspan=2, pady=(5, 0), sticky="sw")
        self.username_entry = ctk.CTkEntry(form_frame, width=300, height=40, fg_color=ENTRY_BG_COLOR, text_color=TEXT_COLOR,
                                           border_color=PRIMARY_COLOR, corner_radius=5, placeholder_text="Choose a username")
        self.username_entry.grid(row=2, column=0, columnspan=2, pady=(0, 10), sticky="nwe")
        self.username_entry.bind("<Return>", self.signup_event)
        self.username_entry.focus()  # Set initial focus

        email_label = ctk.CTkLabel(form_frame, text="Email:", text_color=TEXT_COLOR, font=ctk.CTkFont(size=14))
        email_label.grid(row=3, column=0, columnspan=2, pady=(5, 0), sticky="sw")
        self.email_entry = ctk.CTkEntry(form_frame, width=300, height=40, fg_color=ENTRY_BG_COLOR, text_color=TEXT_COLOR,
                                        border_color=PRIMARY_COLOR, corner_radius=5, placeholder_text="Enter your email address")
        self.email_entry.grid(row=4, column=0, columnspan=2, pady=(0, 10), sticky="nwe")
        self.email_entry.bind("<Return>", self.signup_event)

        # Password Frame
        password_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        password_frame.grid(row=5, column=0, columnspan=2, sticky="nwe")
        password_frame.grid_columnconfigure(0, weight=1)
        password_frame.grid_columnconfigure(1, weight=0)

        password_label = ctk.CTkLabel(password_frame, text="Password:", text_color=TEXT_COLOR, font=ctk.CTkFont(size=14))
        password_label.grid(row=0, column=0, columnspan=2, pady=(5, 0), sticky="sw")
        self.password_entry = ctk.CTkEntry(password_frame, width=250, height=40, fg_color=ENTRY_BG_COLOR, text_color=TEXT_COLOR,
                                           border_color=PRIMARY_COLOR, show="*", corner_radius=5, placeholder_text="Create a password")
        self.password_entry.grid(row=1, column=0, pady=(0, 10), sticky="nwe")
        self.password_entry.bind("<Return>", self.signup_event)
        self.toggle_pass_btn = ctk.CTkButton(password_frame, text="Show", width=40, height=40,
                                             command=lambda: self.toggle_visibility(self.password_entry, self.toggle_pass_btn, "password_visible"),
                                             fg_color=ENTRY_BG_COLOR, text_color=TEXT_COLOR, hover_color=PRIMARY_COLOR)
        self.toggle_pass_btn.grid(row=1, column=1, padx=(5, 0), pady=(0, 10), sticky="nwe")

        # Confirm Password Frame
        confirm_password_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        confirm_password_frame.grid(row=6, column=0, columnspan=2, sticky="nwe")
        confirm_password_frame.grid_columnconfigure(0, weight=1)
        confirm_password_frame.grid_columnconfigure(1, weight=0)

        confirm_password_label = ctk.CTkLabel(confirm_password_frame, text="Confirm Password:", text_color=TEXT_COLOR,
                                              font=ctk.CTkFont(size=14))
        confirm_password_label.grid(row=0, column=0, columnspan=2, pady=(5, 0), sticky="sw")
        self.confirm_password_entry = ctk.CTkEntry(confirm_password_frame, width=250, height=40, fg_color=ENTRY_BG_COLOR,
                                                   text_color=TEXT_COLOR, border_color=PRIMARY_COLOR, show="*",
                                                   corner_radius=5, placeholder_text="Confirm your password")
        self.confirm_password_entry.grid(row=1, column=0, pady=(0, 20), sticky="nwe")
        self.confirm_password_entry.bind("<Return>", self.signup_event)
        self.toggle_confirm_pass_btn = ctk.CTkButton(confirm_password_frame, text="Show", width=40, height=40,
                                                     command=lambda: self.toggle_visibility(self.confirm_password_entry, self.toggle_confirm_pass_btn, "confirm_password_visible"),
                                                     fg_color=ENTRY_BG_COLOR, text_color=TEXT_COLOR, hover_color=PRIMARY_COLOR)
        self.toggle_confirm_pass_btn.grid(row=1, column=1, padx=(5, 0), pady=(0, 20), sticky="nwe")

        self.signup_button = ctk.CTkButton(form_frame, text="Sign Up", command=self.signup_event, width=300, height=40,
                                           fg_color=PRIMARY_COLOR, text_color=TEXT_COLOR, hover_color=BUTTON_HOVER_COLOR,
                                           font=ctk.CTkFont(size=16, weight="bold"), corner_radius=5)
        self.signup_button.grid(row=7, column=0, columnspan=2, pady=10, sticky="nwe")

        self.status_label = ctk.CTkLabel(form_frame, text="", font=ctk.CTkFont(size=12))  # Color set dynamically
        self.status_label.grid(row=8, column=0, columnspan=2, pady=(0, 10), sticky="nwe")

        login_link_button = ctk.CTkButton(self, text="Already have an account? Login", fg_color="transparent",
                                          text_color=PRIMARY_COLOR, hover_color=BACKGROUND_COLOR,
                                          command=self.go_to_login, font=ctk.CTkFont(size=12, underline=True))
        login_link_button.grid(row=3, column=0, pady=(5, 20), sticky="n")

    def toggle_visibility(self, entry_widget, button_widget, visibility_attr_name):
        visibility_attr = getattr(self, visibility_attr_name)
        if visibility_attr:
            entry_widget.configure(show="*")
            button_widget.configure(text="Show")
            setattr(self, visibility_attr_name, False)
        else:
            entry_widget.configure(show="")
            button_widget.configure(text="Hide")
            setattr(self, visibility_attr_name, True)

    def signup_event(self, event=None):
        self.status_label.configure(text="")  # Clear previous status
        original_button_text = "Sign Up"
        self.signup_button.configure(state="disabled", text="Signing up...", fg_color=DISABLED_BUTTON_COLOR)

        username = self.username_entry.get()
        email = self.email_entry.get()
        password = self.password_entry.get()
        confirm_password = self.confirm_password_entry.get()

        print(f"Signup attempt: User: {username}, Email: {email}, Pass: {password}, Confirm: {confirm_password}")

        def process_signup_attempt():
            if not all([username, email, password, confirm_password]):
                self.status_label.configure(text="All fields are required.", text_color=PRIMARY_COLOR)
            elif ".com" not in email or "@" not in email:
                self.status_label.configure(text="Invalid email format.", text_color=PRIMARY_COLOR)
            elif len(password) < 6:
                self.status_label.configure(text="Password must be at least 6 characters.", text_color=PRIMARY_COLOR)
            elif password != confirm_password:
                self.status_label.configure(text="Passwords do not match.", text_color=PRIMARY_COLOR)
            else:
                self.status_label.configure(text="Signup: Placeholder success!", text_color=SUCCESS_COLOR)
            self.signup_button.configure(state="normal", text=original_button_text, fg_color=PRIMARY_COLOR)

        self.after(500, process_signup_attempt)  # Simulate network/processing delay

    def go_to_login(self):
        self.master.show_login_screen()


class App(ctk.CTk):
    def __init__(self):
        super().__init__(fg_color=BACKGROUND_COLOR)

        self.title("Swigato - Food Delivery")
        self.geometry("500x700")  # Increased height slightly for image
        ctk.set_appearance_mode("Dark")

        # Set window icon
        current_dir = os.path.dirname(os.path.abspath(__file__))
        icon_path = os.path.join(current_dir, "swigato_icon.ico")  # Changed to .ico
        try:
            self.iconbitmap(icon_path)  # For Windows
        except Exception as e:
            print(f"Error setting window icon: {e}")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.login_screen = None
        self.signup_screen = None

        self.show_login_screen()

    def show_login_screen(self):
        if self.signup_screen:
            self.signup_screen.grid_forget()
            self.signup_screen.destroy()
            self.signup_screen = None

        if not self.login_screen:
            self.login_screen = LoginScreen(self)
        self.login_screen.grid(row=0, column=0, sticky="nsew")

    def show_signup_screen(self):
        if self.login_screen:
            self.login_screen.grid_forget()
            self.login_screen.destroy()
            self.login_screen = None

        if not self.signup_screen:
            self.signup_screen = SignupScreen(self)
        self.signup_screen.grid(row=0, column=0, sticky="nsew")


if __name__ == "__main__":
    app = App()
    app.mainloop()
