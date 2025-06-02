import customtkinter as ctk
import logging
from gui_constants import (FONT_FAMILY, ADMIN_BACKGROUND_COLOR, ADMIN_TEXT_COLOR, 
                           ADMIN_BUTTON_FG_COLOR, ADMIN_BUTTON_HOVER_COLOR, ADMIN_BUTTON_TEXT_COLOR,
                           ADMIN_PRIMARY_ACCENT_COLOR, HEADING_FONT_SIZE, BUTTON_FONT_SIZE)
from gui_components.admin_users_screen import AdminUsersScreen # Renamed from AdminScreen
from gui_components.admin_orders_screen import AdminOrdersScreen
from gui_components.admin_restaurants_screen import AdminRestaurantsScreen
from gui_components.admin_menus_screen import AdminMenusScreen
from gui_components.admin_reviews_screen import AdminReviewsScreen

logger = logging.getLogger("swigato_app.admin_dashboard")

class AdminDashboard(ctk.CTkFrame):
    def __init__(self, master, app_callbacks, user, **kwargs):
        super().__init__(master, fg_color=ADMIN_BACKGROUND_COLOR, **kwargs)
        self.app_callbacks = app_callbacks
        self.loggedInUser = user
        self.current_screen_frame = None
        self.sidebar_buttons_widgets = [] # To store button widgets

        self.grid_columnconfigure(0, weight=0) # Sidebar - give it fixed width influence initially
        self.grid_columnconfigure(1, weight=1) # Content Area - let it expand
        self.grid_rowconfigure(0, weight=0)    # Title row
        self.grid_rowconfigure(1, weight=1)    # Main content row (sidebar + content_frame)

        # Title Label for the entire dashboard
        dashboard_title = ctk.CTkLabel(self, text="Swigato Admin Dashboard", 
                                       font=ctk.CTkFont(family=FONT_FAMILY, size=HEADING_FONT_SIZE + 4, weight="bold"), 
                                       text_color=ADMIN_TEXT_COLOR)
        dashboard_title.grid(row=0, column=0, columnspan=2, padx=20, pady=(20, 10), sticky="n")
        
        # Back to Main App Button (Top Right)
        back_button = ctk.CTkButton(
            self,
            text="Back to App",
            command=lambda: self.app_callbacks['show_main_app_screen'](self.loggedInUser),
            fg_color=ADMIN_BUTTON_FG_COLOR,
            hover_color=ADMIN_BUTTON_HOVER_COLOR,
            text_color=ADMIN_BUTTON_TEXT_COLOR,
            font=ctk.CTkFont(family=FONT_FAMILY, size=BUTTON_FONT_SIZE),
            corner_radius=8
        )
        back_button.grid(row=0, column=1, padx=20, pady=(20,10), sticky="ne")


        # Sidebar Frame
        self.sidebar_frame = ctk.CTkFrame(self, width=180, corner_radius=10, fg_color=ADMIN_BACKGROUND_COLOR) # Reduced width
        self.sidebar_frame.grid(row=1, column=0, padx=(20,10), pady=(0,20), sticky="nsw")
        self.sidebar_frame.grid_rowconfigure(6, weight=1) # Pushes logout to bottom

        sidebar_button_definitions = [ # Renamed for clarity
            ("Users", AdminUsersScreen, "Users Management"),
            ("Orders", AdminOrdersScreen, "Orders Management"),
            ("Restaurants", AdminRestaurantsScreen, "Restaurants Management"),
            ("Menus", AdminMenusScreen, "Menus Management"),
            ("Reviews", AdminReviewsScreen, "Reviews Management")
        ]

        for i, (text, screen_class, screen_title) in enumerate(sidebar_button_definitions):
            button = ctk.CTkButton(
                self.sidebar_frame,
                text=text,
                # Pass button's own text, screen class, and screen title to switch_screen
                command=lambda sc=screen_class, st=screen_title, btn_text=text: self.switch_screen(sc, st, btn_text),
                font=ctk.CTkFont(family=FONT_FAMILY, size=BUTTON_FONT_SIZE + 2),
                fg_color=ADMIN_BUTTON_FG_COLOR,
                hover_color=ADMIN_BUTTON_HOVER_COLOR,
                text_color=ADMIN_BUTTON_TEXT_COLOR,
                anchor="w",
                corner_radius=8
            )
            button.grid(row=i, column=0, padx=10, pady=10, sticky="ew")
            self.sidebar_buttons_widgets.append(button) # Store button

        # Content Frame
        self.content_frame = ctk.CTkFrame(self, fg_color=ADMIN_BACKGROUND_COLOR, corner_radius=10) # Adjusted fg_color
        self.content_frame.grid(row=1, column=1, padx=(10,20), pady=(0,20), sticky="nsew")
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=1)
        
        # Logout Button (Bottom of Sidebar)
        logout_button = ctk.CTkButton(
            self.sidebar_frame,
            text="Logout",
            command=self.app_callbacks['logout'], # Assuming a logout callback exists
            font=ctk.CTkFont(family=FONT_FAMILY, size=BUTTON_FONT_SIZE + 2),
            fg_color="#c0392b", # A distinct color for logout
            hover_color="#e74c3c",
            text_color="white",
            anchor="w",
            corner_radius=8
        )
        logout_button.grid(row=len(sidebar_button_definitions) + 1, column=0, padx=10, pady=(20,10), sticky="sew")


        # Initial screen
        # Pass the button text for the initial screen
        self.switch_screen(AdminUsersScreen, "Users Management", "Users")
        logger.info("AdminDashboard initialized, showing Users screen by default.")

    def switch_screen(self, screen_class, screen_title, active_button_text):
        logger.info(f"Switching to {screen_title}, active button: {active_button_text}")

        # Update sidebar button colors 
        active_color = "#c9370a"
        default_color = ADMIN_BUTTON_FG_COLOR
        for btn in self.sidebar_buttons_widgets:
            if btn.cget("text") == active_button_text:
                btn.configure(fg_color=active_color)
            else:
                btn.configure(fg_color=default_color)

        if self.current_screen_frame:
            self.current_screen_frame.destroy()
        
        self.current_screen_frame = screen_class(self.content_frame, self.app_callbacks, self.loggedInUser)
        self.current_screen_frame.grid(row=0, column=0, sticky="nsew", padx=0, pady=0)

    def show(self):
        self.lift()

    def hide(self):
        self.lower()
