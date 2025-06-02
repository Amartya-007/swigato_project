import customtkinter as ctk
from PIL import Image
import os
from users.auth import sign_up
from gui_constants import PRIMARY_COLOR, BACKGROUND_COLOR, ENTRY_BG_COLOR, TEXT_COLOR, BUTTON_HOVER_COLOR, SUCCESS_COLOR, DISABLED_BUTTON_COLOR, ERROR_COLOR
from utils.validation import is_valid_password

class SignupScreen(ctk.CTkFrame):
    def __init__(self, master, show_login_callback):
        super().__init__(master, fg_color=BACKGROUND_COLOR)
        self.app = master
        self.show_login_callback = show_login_callback
        self.password_visible = False
        self.confirm_password_visible = False

        current_dir = os.path.dirname(os.path.abspath(__file__))
        image_path = os.path.join(current_dir, "..", "swigato_icon.png")
        try:
            self.swigato_image = ctk.CTkImage(light_image=Image.open(image_path), size=(100, 100))
            self.swigato_image_label = ctk.CTkLabel(self, image=self.swigato_image, text="")
            self.swigato_image_label.grid(row=1, column=0, pady=(20, 5), sticky="s")
        except Exception as e:
            print(f"Error loading Swigato icon in SignupScreen: {e}")
            self.swigato_image_label = ctk.CTkLabel(self, text="Swigato", text_color=PRIMARY_COLOR, font=ctk.CTkFont(size=36, weight="bold"))
            self.swigato_image_label.grid(row=1, column=0, pady=(20, 10), sticky="s")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=0)
        self.grid_rowconfigure(3, weight=0)
        self.grid_rowconfigure(4, weight=1)

        form_frame = ctk.CTkFrame(self, fg_color="transparent")
        form_frame.grid(row=2, column=0, padx=50, pady=(5, 10), sticky="nwe")
        form_frame.grid_columnconfigure(0, weight=1)

        header_label = ctk.CTkLabel(form_frame, text="Create Your Account", text_color=TEXT_COLOR, font=ctk.CTkFont(size=24, weight="bold"))
        header_label.grid(row=0, column=0, columnspan=2, pady=(0, 15), sticky="n")

        username_label = ctk.CTkLabel(form_frame, text="Username:", text_color=TEXT_COLOR, font=ctk.CTkFont(size=14))
        username_label.grid(row=1, column=0, columnspan=2, pady=(5, 0), sticky="sw")
        self.username_entry = ctk.CTkEntry(form_frame, width=300, height=40, fg_color=ENTRY_BG_COLOR, text_color=TEXT_COLOR,
                                           border_color=PRIMARY_COLOR, corner_radius=5, placeholder_text="Choose a username")
        self.username_entry.grid(row=2, column=0, columnspan=2, pady=(0, 10), sticky="nwe")
        self.username_entry.bind("<Return>", self.signup_event)
        self.username_entry.focus()

        password_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        password_frame.grid(row=3, column=0, columnspan=2, sticky="nwe")
        password_frame.grid_columnconfigure(0, weight=1)
        password_frame.grid_columnconfigure(1, weight=0)

        password_label = ctk.CTkLabel(password_frame, text="Password:", text_color=TEXT_COLOR, font=ctk.CTkFont(size=14))
        password_label.grid(row=0, column=0, columnspan=2, pady=(5, 0), sticky="sw")
        self.password_entry = ctk.CTkEntry(password_frame, width=250, height=40, fg_color=ENTRY_BG_COLOR, text_color=TEXT_COLOR,
                                           border_color=PRIMARY_COLOR, show="*", corner_radius=5, placeholder_text="Create a password")
        self.password_entry.grid(row=1, column=0, pady=(0, 0), sticky="nwe")
        self.password_entry.bind("<Return>", self.signup_event)
        self.password_entry.bind("<KeyRelease>", self._validate_password_strength_live)

        self.toggle_pass_btn = ctk.CTkButton(password_frame, text="Show", width=40, height=40,
                                             command=lambda: self.toggle_visibility(self.password_entry, self.toggle_pass_btn, "password_visible"),
                                             fg_color=ENTRY_BG_COLOR, text_color=TEXT_COLOR, hover_color=PRIMARY_COLOR)
        self.toggle_pass_btn.grid(row=1, column=1, padx=(5,0), pady=(0,0), sticky="nwe")

        self.password_strength_label = ctk.CTkLabel(password_frame, text="", font=ctk.CTkFont(size=10), anchor="w")
        self.password_strength_label.grid(row=2, column=0, columnspan=2, pady=(2, 10), sticky="nwe")

        confirm_password_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        confirm_password_frame.grid(row=4, column=0, columnspan=2, sticky="nwe")
        confirm_password_frame.grid_columnconfigure(0, weight=1)
        confirm_password_frame.grid_columnconfigure(1, weight=0)

        confirm_password_label = ctk.CTkLabel(confirm_password_frame, text="Confirm Password:", text_color=TEXT_COLOR, font=ctk.CTkFont(size=14))
        confirm_password_label.grid(row=0, column=0, columnspan=2, pady=(5,0), sticky="sw")
        self.confirm_password_entry = ctk.CTkEntry(confirm_password_frame, width=250, height=40, fg_color=ENTRY_BG_COLOR,
                                                   text_color=TEXT_COLOR, border_color=PRIMARY_COLOR, show="*",
                                                   corner_radius=5, placeholder_text="Confirm your password")
        self.confirm_password_entry.grid(row=1, column=0, pady=(0, 20), sticky="nwe")
        self.confirm_password_entry.bind("<Return>", self.signup_event)
        self.toggle_confirm_pass_btn = ctk.CTkButton(confirm_password_frame, text="Show", width=40, height=40,
                                                     command=lambda: self.toggle_visibility(self.confirm_password_entry, self.toggle_confirm_pass_btn, "confirm_password_visible"),
                                                     fg_color=ENTRY_BG_COLOR, text_color=TEXT_COLOR, hover_color=PRIMARY_COLOR)
        self.toggle_confirm_pass_btn.grid(row=1, column=1, padx=(5,0), pady=(0,20), sticky="nwe")

        self.signup_button = ctk.CTkButton(form_frame, text="Sign Up", command=self.signup_event, width=300, height=40,
                                           fg_color=PRIMARY_COLOR, text_color=TEXT_COLOR, hover_color=BUTTON_HOVER_COLOR,
                                           font=ctk.CTkFont(size=16, weight="bold"), corner_radius=5)
        self.signup_button.grid(row=5, column=0, columnspan=2, pady=10, sticky="nwe")

        self.status_label = ctk.CTkLabel(form_frame, text="", font=ctk.CTkFont(size=12))
        self.status_label.grid(row=6, column=0, columnspan=2, pady=(0,10), sticky="nwe")

        login_link_button = ctk.CTkButton(self, text="Already have an account? Login", fg_color="transparent",
                                          text_color=PRIMARY_COLOR, hover_color=BACKGROUND_COLOR,
                                          command=self._go_to_login, font=ctk.CTkFont(size=12, underline=True))
        login_link_button.grid(row=3, column=0, pady=(5,20), sticky="n")

    def _validate_password_strength_live(self, event=None):
        password = self.password_entry.get()
        is_valid, message = is_valid_password(password)
        if not password:
            self.password_strength_label.configure(text="", text_color=TEXT_COLOR)
        elif is_valid:
            self.password_strength_label.configure(text=message, text_color=SUCCESS_COLOR)
        else:
            self.password_strength_label.configure(text=message, text_color=ERROR_COLOR)

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
        self.status_label.configure(text="") # Clear previous status
        original_button_text = "Sign Up"
        self.signup_button.configure(state="disabled", text="Signing up...", fg_color=DISABLED_BUTTON_COLOR)

        username = self.username_entry.get()
        password = self.password_entry.get()
        confirm_password = self.confirm_password_entry.get()

        is_valid_pass, pass_message = is_valid_password(password)
        if not is_valid_pass:
            self.status_label.configure(text=pass_message, text_color=ERROR_COLOR)
            self.password_strength_label.configure(text=pass_message, text_color=ERROR_COLOR)
            self.signup_button.configure(state="normal", text=original_button_text, fg_color=PRIMARY_COLOR)
            return
        else:
            self.password_strength_label.configure(text="Password is strong!", text_color=SUCCESS_COLOR)

        if password != confirm_password:
            self.status_label.configure(text="Passwords do not match.", text_color=ERROR_COLOR)
            self.signup_button.configure(state="normal", text=original_button_text, fg_color=PRIMARY_COLOR)
            return

        def process_signup_attempt():
            if not username:
                self.status_label.configure(text="Username is required.", text_color=ERROR_COLOR)
                self.signup_button.configure(state="normal", text=original_button_text, fg_color=PRIMARY_COLOR)
                return

            try:
                success = sign_up(username, password)

                if success:
                    self.status_label.configure(text="Account created successfully! Redirecting to login...", text_color=SUCCESS_COLOR)
                    self.signup_button.configure(state="disabled", text="Account Created", fg_color=DISABLED_BUTTON_COLOR)
                    self.after(2000, lambda: self.app.show_login_screen(username_to_fill=username))
                else:
                    self.status_label.configure(text="Signup failed. Username might already exist or another issue occurred.", text_color=ERROR_COLOR)
                    self.signup_button.configure(state="normal", text=original_button_text, fg_color=PRIMARY_COLOR)

            except Exception as e:
                error_message = str(e)
                if "already exists" in error_message.lower():
                     self.status_label.configure(text="Username already exists. Please choose another.", text_color=ERROR_COLOR)
                else:
                    self.status_label.configure(text=f"An error occurred: {error_message}", text_color=ERROR_COLOR)
                self.signup_button.configure(state="normal", text=original_button_text, fg_color=PRIMARY_COLOR)

        self.after(100, process_signup_attempt)

    def _go_to_login(self):
        self.show_login_callback()
