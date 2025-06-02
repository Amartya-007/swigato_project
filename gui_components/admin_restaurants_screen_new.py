import customtkinter as ctk
import logging
from CTkTable import CTkTable
from gui_constants import (
    FONT_FAMILY, HEADING_FONT_SIZE, BODY_FONT_SIZE, BUTTON_FONT_SIZE,
    ADMIN_BACKGROUND_COLOR, ADMIN_TEXT_COLOR, ADMIN_PRIMARY_ACCENT_COLOR,
    ADMIN_SECONDARY_ACCENT_COLOR, ERROR_COLOR, SUCCESS_COLOR,
    ADMIN_FRAME_FG_COLOR, ADMIN_BUTTON_FG_COLOR, ADMIN_BUTTON_HOVER_COLOR,
    ADMIN_BUTTON_TEXT_COLOR, ADMIN_TABLE_HEADER_BG_COLOR, ADMIN_TABLE_ROW_LIGHT_COLOR,
    ADMIN_TABLE_ROW_DARK_COLOR, ADMIN_TABLE_BORDER_COLOR, ADMIN_TABLE_TEXT_COLOR,
    ADMIN_PRIMARY_COLOR,
    set_swigato_icon, safe_focus, center_window
)
from restaurants.models import Restaurant
from tkinter import messagebox
from .restaurant_management_screen import RestaurantManagementScreen

logger = logging.getLogger("swigato_app.admin_restaurants_screen")

class AdminRestaurantsScreen(ctk.CTkFrame):
    def __init__(self, master, app_callbacks, user, **kwargs):
        super().__init__(master, fg_color=ADMIN_BACKGROUND_COLOR, **kwargs)
        self.app_callbacks = app_callbacks
        self.loggedInUser = user
        self.current_restaurants_in_table = []
        self.management_window = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=1)

        title_label = ctk.CTkLabel(self, text="Restaurant Management",
                                   font=ctk.CTkFont(family=FONT_FAMILY, size=HEADING_FONT_SIZE, weight="bold"),
                                   text_color=ADMIN_TEXT_COLOR)
        title_label.grid(row=0, column=0, padx=20, pady=(10, 10), sticky="nw")

        controls_frame = ctk.CTkFrame(self, fg_color="transparent")
        controls_frame.grid(row=1, column=0, padx=20, pady=(0,10), sticky="ew")
        
        add_button = ctk.CTkButton(controls_frame, text="Add New Restaurant",
                                   font=ctk.CTkFont(family=FONT_FAMILY, size=BUTTON_FONT_SIZE),
                                   fg_color=ADMIN_BUTTON_FG_COLOR,
                                   hover_color=ADMIN_BUTTON_HOVER_COLOR,
                                   text_color=ADMIN_BUTTON_TEXT_COLOR,
                                   command=self._open_add_restaurant_screen,
                                   corner_radius=8)
        add_button.pack(side="right", padx=(0,0), pady=5)

        self.table_frame = ctk.CTkFrame(self, fg_color=ADMIN_FRAME_FG_COLOR, corner_radius=10)
        self.table_frame.grid(row=2, column=0, sticky="nsew", padx=20, pady=(0, 20))
        self.table_frame.grid_columnconfigure(0, weight=1)
        self.table_frame.grid_rowconfigure(0, weight=1)

        self.table = None
        self._load_and_display_restaurants()
        logger.info("AdminRestaurantsScreen initialized and restaurants loaded.")

    def _load_and_display_restaurants(self):
        if self.table and isinstance(self.table, CTkTable):
            self.table.destroy()
            self.table = None
        elif self.table:
            self.table.destroy()
            self.table = None

        restaurants_from_db = Restaurant.get_all()
        logger.info(f"Loaded {len(restaurants_from_db)} restaurants from database.")

        self.current_restaurants_in_table = []
        
        headers = ["ID", "Name", "Cuisine", "Address", "Rating", "Actions"]
        table_data = [headers]

        if not restaurants_from_db:
            logger.info("No restaurants found to display.")
            self.table = ctk.CTkLabel(self.table_frame, text="No restaurants found.",
                                         font=ctk.CTkFont(family=FONT_FAMILY, size=BODY_FONT_SIZE),
                                         text_color=ADMIN_TEXT_COLOR)
            self.table.pack(expand=True, anchor="center")
            return
        
        for r in restaurants_from_db:
            self.current_restaurants_in_table.append({
                "id": r.restaurant_id,
                "name": r.name,
                "cuisine": r.cuisine_type,
                "address": r.address,
                "rating": f"{r.rating:.1f}" if r.rating is not None else "N/A"
            })
            table_data.append([
                r.restaurant_id,
                r.name,
                r.cuisine_type,
                r.address,
                f"{r.rating:.1f}" if r.rating is not None else "N/A",
                "Update / View"
            ])
        
        header_font = ctk.CTkFont(family=FONT_FAMILY, size=BODY_FONT_SIZE+1, weight="bold")
        cell_font = ctk.CTkFont(family=FONT_FAMILY, size=BODY_FONT_SIZE)

        self.table = CTkTable(master=self.table_frame, 
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
                              wraplength=180,
                             )

        self.table.pack(expand=True, fill="both", padx=10, pady=10)
        logger.info("Restaurants table created and displayed.")

    def _on_cell_click(self, event_data):
        row_clicked = event_data["row"]
        column_clicked = event_data["column"]
        
        if self.management_window and self.management_window.winfo_exists():
            messagebox.showwarning("Window Busy", "Another restaurant management window is already open. Please close it first.")
            safe_focus(self.management_window)
            return

        if row_clicked == 0:
            logger.info(f"Header row clicked. Ignoring.")
            return

        data_row_idx = row_clicked - 1 
        
        if not (0 <= data_row_idx < len(self.current_restaurants_in_table)):
            logger.warning(f"Clicked data_row_idx {data_row_idx} is out of bounds for current_restaurants_in_table (len {len(self.current_restaurants_in_table)}).")
            return
        
        restaurant_info = self.current_restaurants_in_table[data_row_idx]
        restaurant_id = restaurant_info['id']

        actions_column_index = 5 

        if column_clicked == actions_column_index:
            logger.info(f"'Update / View' clicked for restaurant ID: {restaurant_id} (Name: {restaurant_info['name']}).")
            self._open_restaurant_management_screen(restaurant_id)
        else:
            logger.info(f"Clicked on non-action column {column_clicked} for restaurant ID {restaurant_id}.")

    def _open_add_restaurant_screen(self):
        logger.info("Attempting to open Restaurant Management Screen for a new restaurant.")
        if self.management_window and self.management_window.winfo_exists():
            messagebox.showwarning("Window Busy", "Another restaurant management window is already open. Please close it first.")
            self.management_window.focus()
            return
        self._open_restaurant_management_screen(restaurant_id=None)

    def _handle_management_window_close(self):
        logger.info("RestaurantManagementScreen closed, refreshing restaurant list.")
        self.management_window = None
        self.refresh_restaurants()

    def _open_restaurant_management_screen(self, restaurant_id):
        if self.management_window and self.management_window.winfo_exists():
            messagebox.showwarning("Window Busy", "Another restaurant management window is already open. Please close it first.")
            self.management_window.focus()
            return

        action = "NEW" if restaurant_id is None else f"ID: {restaurant_id}"
        logger.info(f"Opening Restaurant Management Screen for restaurant: {action}.")
        
        self.management_window = RestaurantManagementScreen(
            master=self.winfo_toplevel(),
            restaurant_id=restaurant_id,
            app_callbacks=self.app_callbacks,
            loggedInUser=self.loggedInUser,
            on_close_callback=self._handle_management_window_close 
        )
        self.management_window.grab_set()
        self.management_window.focus()

    def refresh_restaurants(self):
        logger.info("Refreshing restaurants list.")
        self._load_and_display_restaurants()

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    from utils.database import init_db
    from restaurants.models import populate_sample_restaurant_data
    try:
        init_db()
    except Exception as e:
        logger.error(f"Error initializing DB for standalone test: {e}")

    app = ctk.CTk()
    app.geometry("1000x700")
    app.title("Admin Restaurants Test")

    class DummyUser:
        def __init__(self, username, role):
            self.username = username
            self.role = role
            self.user_id = 1

    class DummyCallbacks:
        def get_current_user(self): return DummyUser("test_admin", "admin")
        def logout(self): logger.info("Logout called")
        def show_screen(self, screen_name): logger.info(f"Show screen: {screen_name}")
        def show_restaurant_detail_screen(self, restaurant_id):
            logger.info(f"Dummy callback: show_restaurant_detail_screen for ID {restaurant_id}")
            messagebox.showinfo("Dummy Callback", f"Would show details for restaurant ID: {restaurant_id}")

    dummy_user_obj = DummyUser(username="admin_test", role="admin")
    dummy_callbacks_obj = DummyCallbacks()

    admin_screen = AdminRestaurantsScreen(app, app_callbacks=dummy_callbacks_obj, user=dummy_user_obj)
    admin_screen.pack(expand=True, fill="both")
    
    app.mainloop()
