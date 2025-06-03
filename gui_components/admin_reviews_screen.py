import customtkinter as ctk
from CTkTable import CTkTable
import logging
from tkinter import messagebox
from gui_constants import (
    FONT_FAMILY, BODY_FONT_SIZE, HEADING_FONT_SIZE,
    ADMIN_BACKGROUND_COLOR, ADMIN_FRAME_FG_COLOR, ADMIN_TEXT_COLOR,
    ADMIN_PRIMARY_ACCENT_COLOR, ADMIN_SECONDARY_ACCENT_COLOR,
    ADMIN_TABLE_HEADER_BG_COLOR, ADMIN_TABLE_ROW_LIGHT_COLOR, ADMIN_TABLE_ROW_DARK_COLOR,
    ADMIN_TABLE_BORDER_COLOR, ADMIN_TABLE_TEXT_COLOR, ERROR_COLOR
)
from reviews.models import Review

logger = logging.getLogger("swigato_app.admin_reviews_screen")

class AdminReviewsScreen(ctk.CTkFrame):
    def __init__(self, master, app_callbacks, user, **kwargs):
        super().__init__(master, fg_color=ADMIN_BACKGROUND_COLOR, **kwargs)
        self.app_callbacks = app_callbacks
        self.loggedInUser = user
        self.current_reviews = []

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)

        title_label = ctk.CTkLabel(self, text="Global Reviews Moderation",
                                   font=ctk.CTkFont(family=FONT_FAMILY, size=HEADING_FONT_SIZE, weight="bold"),
                                   text_color=ADMIN_TEXT_COLOR)
        title_label.grid(row=0, column=0, padx=20, pady=(10, 10), sticky="nw")

        self.table_frame = ctk.CTkFrame(self, fg_color=ADMIN_FRAME_FG_COLOR, corner_radius=10)
        self.table_frame.grid(row=1, column=0, padx=20, pady=(0,20), sticky="nsew")
        self.table_frame.grid_columnconfigure(0, weight=1)
        self.table_frame.grid_rowconfigure(0, weight=1)

        self.reviews_table = None
        self._load_and_display_reviews()
        logger.info("AdminReviewsScreen initialized and reviews loaded.")

    def _load_and_display_reviews(self):
        for widget in self.table_frame.winfo_children():
            widget.destroy()

        all_reviews = Review.get_all_reviews()
        self.current_reviews = all_reviews

        headers = ["ID", "Restaurant", "User", "Rating", "Comment", "Date", "Actions"]
        table_data = [headers]
        for review in all_reviews:
            date_str = review.review_date.strftime('%Y-%m-%d %H:%M') if hasattr(review.review_date, 'strftime') else str(review.review_date)
            comment_short = (review.comment[:40] + '...') if review.comment and len(review.comment) > 43 else (review.comment or "")
            table_data.append([
                review.review_id,
                review.restaurant_name,
                review.username,
                f"{review.rating}/5",
                comment_short,
                date_str,
                "Delete"
            ])

        if len(table_data) == 1:
            ctk.CTkLabel(self.table_frame, text="No reviews found in the system.",
                         font=ctk.CTkFont(family=FONT_FAMILY, size=BODY_FONT_SIZE),
                         text_color=ADMIN_TEXT_COLOR).pack(expand=True, anchor="center", padx=20, pady=20)
            return

        cell_font = ctk.CTkFont(family=FONT_FAMILY, size=BODY_FONT_SIZE - 1)
        header_font = ctk.CTkFont(family=FONT_FAMILY, size=BODY_FONT_SIZE + 1, weight="bold")
        self.reviews_table = CTkTable(
            master=self.table_frame,
            values=table_data,
            font=cell_font,
            header_color=ADMIN_TABLE_HEADER_BG_COLOR,
            text_color=ADMIN_TABLE_TEXT_COLOR,
            hover_color=ADMIN_PRIMARY_ACCENT_COLOR,
            colors=[ADMIN_TABLE_ROW_LIGHT_COLOR, ADMIN_TABLE_ROW_DARK_COLOR],
            corner_radius=8,
            border_width=1,
            border_color=ADMIN_TABLE_BORDER_COLOR,
            command=self._on_cell_click,
            wraplength=180
        )
        self.reviews_table.pack(expand=True, fill="both", padx=10, pady=10)
        self.actions_column_index = 6

    def _on_cell_click(self, event_data):
        row_clicked = event_data["row"]
        column_clicked = event_data["column"]
        if row_clicked == 0:
            return
        review_index = row_clicked - 1
        if not (0 <= review_index < len(self.current_reviews)):
            return
        review = self.current_reviews[review_index]
        if column_clicked == self.actions_column_index:
            self._confirm_delete_review(review.review_id)

    def _confirm_delete_review(self, review_id):
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this review?")
        if not confirm:
            return
        success = Review.delete_review(review_id)
        if success:
            messagebox.showinfo("Success", "Review deleted successfully.")
            self._load_and_display_reviews()
        else:
            messagebox.showerror("Error", "Failed to delete review. It may not exist.")
