import customtkinter as ctk
import logging
from gui_constants import FONT_FAMILY, BODY_FONT_SIZE, ADMIN_BACKGROUND_COLOR, ADMIN_TEXT_COLOR

logger = logging.getLogger("swigato_app.admin_reviews_screen")

class AdminReviewsScreen(ctk.CTkFrame):
    def __init__(self, master, app_callbacks, user, **kwargs):
        super().__init__(master, fg_color=ADMIN_BACKGROUND_COLOR, **kwargs)
        self.app_callbacks = app_callbacks
        self.loggedInUser = user
        logger.info("AdminReviewsScreen initialized")

        label = ctk.CTkLabel(self, text="Reviews Management Screen - Placeholder", font=ctk.CTkFont(family=FONT_FAMILY, size=BODY_FONT_SIZE, weight="bold"), text_color=ADMIN_TEXT_COLOR)
        label.pack(pady=20, padx=20, expand=True, anchor="center")
        # TODO: Implement review viewing and moderation
