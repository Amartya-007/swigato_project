import customtkinter as ctk
from CTkTable import CTkTable
import logging
from tkinter import messagebox
import os
from gui_constants import (
    FONT_FAMILY, HEADING_FONT_SIZE, BODY_FONT_SIZE, BUTTON_FONT_SIZE, # Font definitions
    ADMIN_BACKGROUND_COLOR, ADMIN_FRAME_FG_COLOR, ADMIN_TEXT_COLOR,      # Admin basic colors
    ADMIN_PRIMARY_ACCENT_COLOR, ADMIN_SECONDARY_ACCENT_COLOR,         # Admin accent colors
    ADMIN_TABLE_HEADER_BG_COLOR, ADMIN_TABLE_HEADER_TEXT_COLOR,     # Admin Table specific colors
    ADMIN_TABLE_ROW_LIGHT_COLOR, ADMIN_TABLE_ROW_DARK_COLOR,
    ADMIN_TABLE_BORDER_COLOR, ADMIN_TABLE_TEXT_COLOR,
    ADMIN_BUTTON_FG_COLOR, ADMIN_BUTTON_HOVER_COLOR, ADMIN_BUTTON_TEXT_COLOR, ADMIN_PRIMARY_COLOR, # Admin Button colors
    ICON_PATH, # Icon path for dialogs
    set_swigato_icon, safe_focus, center_window # Utility functions
)
from users.models import User # Import the User model
from utils.database import get_db_connection # For direct DB operations if needed, though User model should handle most

logger = logging.getLogger("swigato_app.admin_users_screen") # Updated logger name

class AdminUsersScreen(ctk.CTkFrame): # Renamed class
    def __init__(self, master, app_callbacks, user, **kwargs): # Removed users_data_list
        super().__init__(master, fg_color=ADMIN_BACKGROUND_COLOR, **kwargs)
        self.app_callbacks = app_callbacks
        self.loggedInUser = user # Logged-in admin user
        self.current_view_users = [] # To store the currently displayed (filtered/sorted) user objects

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0) # Title row
        self.grid_rowconfigure(1, weight=0) # Controls frame (new)
        self.grid_rowconfigure(2, weight=1) # Table frame (shifted)

        self.admin_column_index = 2 # Column index for "Admin?"
        self.edit_action_column_index = 4 # New column index for "Edit Action"
        self.delete_action_column_index = 5 # New column index for "Delete Action"
        self.current_edit_user_id = None # Will store the ID of the user being edited

        # Title
        title_label = ctk.CTkLabel(self, text="User Management", font=ctk.CTkFont(family=FONT_FAMILY, size=HEADING_FONT_SIZE, weight="bold"), text_color=ADMIN_TEXT_COLOR)
        title_label.grid(row=0, column=0, padx=20, pady=(10, 10), sticky="nw") # Adjusted pady

        # Controls Frame
        self.controls_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.controls_frame.grid(row=1, column=0, columnspan=2, padx=20, pady=(10,10), sticky="ew")

        # Left part of controls (Search, Filter, Clear)
        left_controls_subframe = ctk.CTkFrame(self.controls_frame, fg_color="transparent")
        left_controls_subframe.pack(side="left", fill="x", expand=True, padx=(0,10))

        self.search_entry = ctk.CTkEntry(
            left_controls_subframe,
            placeholder_text="Search ID, Name, Address...",
            font=ctk.CTkFont(family=FONT_FAMILY, size=BODY_FONT_SIZE),
            width=300 
        )
        self.search_entry.pack(side="left", padx=(0,10), pady=5)
        self.search_entry.bind("<Return>", lambda event: self._apply_filters_and_refresh_table())

        self.admin_filter_var = ctk.StringVar(value="All")
        self.admin_filter_menu = ctk.CTkOptionMenu(
            left_controls_subframe,
            variable=self.admin_filter_var,
            values=["All", "Admin", "Non-Admin"],
            font=ctk.CTkFont(family=FONT_FAMILY, size=BODY_FONT_SIZE),
            dropdown_font=ctk.CTkFont(family=FONT_FAMILY, size=BODY_FONT_SIZE),
            command=lambda choice: self._apply_filters_and_refresh_table(),
            fg_color=ADMIN_BUTTON_FG_COLOR, # Consistent button styling
            button_color=ADMIN_BUTTON_FG_COLOR,
            button_hover_color=ADMIN_BUTTON_HOVER_COLOR,
            text_color_disabled=ADMIN_TEXT_COLOR # Ensure text is visible
        )
        self.admin_filter_menu.pack(side="left", padx=(0,10), pady=5)

        self.clear_filters_button = ctk.CTkButton(
            left_controls_subframe,
            text="Clear Filters",
            command=self._clear_filters_and_refresh_table,
            fg_color=ADMIN_SECONDARY_ACCENT_COLOR, 
            hover_color=ADMIN_PRIMARY_ACCENT_COLOR,
            text_color=ADMIN_TEXT_COLOR,
            font=ctk.CTkFont(family=FONT_FAMILY, size=BUTTON_FONT_SIZE),
            corner_radius=8,
            width=120 # Adjusted width
        )
        self.clear_filters_button.pack(side="left", padx=(0,10), pady=5)

        # Right part of controls (Add User)
        right_controls_subframe = ctk.CTkFrame(self.controls_frame, fg_color="transparent")
        right_controls_subframe.pack(side="right", fill="none", expand=False)

        self.add_user_button = ctk.CTkButton(
            right_controls_subframe,
            text="Add New User",
            command=self._open_add_user_dialog,
            fg_color=ADMIN_BUTTON_FG_COLOR,
            hover_color=ADMIN_BUTTON_HOVER_COLOR,
            text_color=ADMIN_BUTTON_TEXT_COLOR,
            font=ctk.CTkFont(family=FONT_FAMILY, size=BUTTON_FONT_SIZE),
            corner_radius=8
        )
        self.add_user_button.pack(pady=5)

        # Frame for the table
        self.table_frame = ctk.CTkFrame(self, fg_color=ADMIN_FRAME_FG_COLOR, corner_radius=10)
        self.table_frame.grid(row=2, column=0, columnspan=2, padx=20, pady=(0,20), sticky="nsew") # Removed top pady from table_frame
        self.table_frame.grid_columnconfigure(0, weight=1)
        self.table_frame.grid_rowconfigure(0, weight=1)

        self.user_table = None
        self._load_and_display_users() # Initial load

    def _apply_filters_and_refresh_table(self):
        logger.debug("Applying filters and refreshing table.")
        self._load_and_display_users()

    def _clear_filters_and_refresh_table(self):
        logger.debug("Clearing filters and refreshing table.")
        self.search_entry.delete(0, "end")
        self.admin_filter_var.set("All")
        self._load_and_display_users()
    
    def _open_add_user_dialog(self):
        if hasattr(self, 'add_user_dialog') and self.add_user_dialog.winfo_exists():
            safe_focus(self.add_user_dialog)
            return

        self.add_user_dialog = ctk.CTkToplevel(self)
        self.add_user_dialog.title("Add New User")
        set_swigato_icon(self.add_user_dialog)
        
        # Center the dialog
        center_window(self.add_user_dialog, 400, 450)
        
        self.add_user_dialog.transient(self.master) # Dialog is transient to the main app window
        self.add_user_dialog.grab_set() # Modal behavior

        dialog_main_frame = ctk.CTkFrame(self.add_user_dialog, fg_color=ADMIN_BACKGROUND_COLOR)
        dialog_main_frame.pack(expand=True, fill="both", padx=20, pady=20)

        # Username
        ctk.CTkLabel(dialog_main_frame, text="Username:", font=ctk.CTkFont(family=FONT_FAMILY, size=BODY_FONT_SIZE), text_color=ADMIN_TEXT_COLOR).pack(anchor="w", pady=(0,2))
        self.username_entry_add = ctk.CTkEntry(dialog_main_frame, width=300, font=ctk.CTkFont(family=FONT_FAMILY, size=BODY_FONT_SIZE))
        self.username_entry_add.pack(fill="x", pady=(0,10))

        # Password
        ctk.CTkLabel(dialog_main_frame, text="Password:", font=ctk.CTkFont(family=FONT_FAMILY, size=BODY_FONT_SIZE), text_color=ADMIN_TEXT_COLOR).pack(anchor="w", pady=(0,2))
        self.password_entry_add = ctk.CTkEntry(dialog_main_frame, width=300, show="*", font=ctk.CTkFont(family=FONT_FAMILY, size=BODY_FONT_SIZE))
        self.password_entry_add.pack(fill="x", pady=(0,10))
        
        # Confirm Password
        ctk.CTkLabel(dialog_main_frame, text="Confirm Password:", font=ctk.CTkFont(family=FONT_FAMILY, size=BODY_FONT_SIZE), text_color=ADMIN_TEXT_COLOR).pack(anchor="w", pady=(0,2))
        self.confirm_password_entry_add = ctk.CTkEntry(dialog_main_frame, width=300, show="*", font=ctk.CTkFont(family=FONT_FAMILY, size=BODY_FONT_SIZE))
        self.confirm_password_entry_add.pack(fill="x", pady=(0,10))

        # Address
        ctk.CTkLabel(dialog_main_frame, text="Address:", font=ctk.CTkFont(family=FONT_FAMILY, size=BODY_FONT_SIZE), text_color=ADMIN_TEXT_COLOR).pack(anchor="w", pady=(0,2))
        self.address_entry_add = ctk.CTkEntry(dialog_main_frame, width=300, font=ctk.CTkFont(family=FONT_FAMILY, size=BODY_FONT_SIZE))
        self.address_entry_add.pack(fill="x", pady=(0,10))

        # Admin Flag
        self.is_admin_var_add = ctk.BooleanVar()
        admin_switch = ctk.CTkSwitch(dialog_main_frame, text="Is Admin?", variable=self.is_admin_var_add,
                                      font=ctk.CTkFont(family=FONT_FAMILY, size=BODY_FONT_SIZE),
                                      text_color=ADMIN_TEXT_COLOR,
                                      progress_color=ADMIN_PRIMARY_COLOR)
        admin_switch.pack(anchor="w", pady=(0,15))

        # Error Label (initially hidden)
        self.error_label_add_user = ctk.CTkLabel(dialog_main_frame, text="", text_color="red", font=ctk.CTkFont(family=FONT_FAMILY, size=BODY_FONT_SIZE-1))
        self.error_label_add_user.pack(pady=(5,0))

        # Buttons Frame
        buttons_frame = ctk.CTkFrame(dialog_main_frame, fg_color="transparent")
        buttons_frame.pack(fill="x", pady=(10,0), side="bottom") # Ensure buttons are at the bottom

        save_button = ctk.CTkButton(
            buttons_frame, text="Save User", command=self._save_new_user,
            fg_color=ADMIN_BUTTON_FG_COLOR, hover_color=ADMIN_BUTTON_HOVER_COLOR, text_color=ADMIN_BUTTON_TEXT_COLOR,
            font=ctk.CTkFont(family=FONT_FAMILY, size=BUTTON_FONT_SIZE),
            corner_radius=8
        )
        save_button.pack(side="right", padx=(10,0))

        cancel_button = ctk.CTkButton(
            buttons_frame, text="Cancel", command=self.add_user_dialog.destroy,
            fg_color=ADMIN_SECONDARY_ACCENT_COLOR, hover_color=ADMIN_PRIMARY_ACCENT_COLOR, text_color=ADMIN_TEXT_COLOR,
            font=ctk.CTkFont(family=FONT_FAMILY, size=BUTTON_FONT_SIZE),
            corner_radius=8
        )
        cancel_button.pack(side="right")
        
        # Set safe focus on the username entry after dialog is shown
        self.add_user_dialog.after(100, lambda: safe_focus(self.username_entry_add))

    def _save_new_user(self):
        username = self.username_entry_add.get().strip()
        password = self.password_entry_add.get() # No strip, keep as is for now
        confirm_password = self.confirm_password_entry_add.get()
        address = self.address_entry_add.get().strip()
        is_admin = self.is_admin_var_add.get()

        if not username:
            logger.warning("Attempted to add user with empty username.")
            self.error_label_add_user.configure(text="Username cannot be empty.")
            return
        
        if not password:
            logger.warning("Attempted to add user with empty password.")
            self.error_label_add_user.configure(text="Password cannot be empty.")
            return

        if password != confirm_password:
            logger.warning("Passwords do not match during new user creation.")
            self.error_label_add_user.configure(text="Passwords do not match.")
            return
        
        # Check for duplicate username using User model
        if User.get_by_username(username):
            logger.warning(f"Attempted to add user with duplicate username: {username}")
            self.error_label_add_user.configure(text=f"Username '{username}' already exists.")
            return

        self.error_label_add_user.configure(text="")

        # Create user using User.create()
        new_user_obj = User.create(username=username, password=password, address=address, is_admin=is_admin)

        if new_user_obj:
            logger.info(f"New user '{username}' (ID: {new_user_obj.user_id}) created successfully in DB.")
            self._load_and_display_users() # Refresh table from DB
            if hasattr(self, 'add_user_dialog') and self.add_user_dialog.winfo_exists():
                self.add_user_dialog.destroy()
        else:
            logger.error(f"Failed to create user '{username}' in database.")
            self.error_label_add_user.configure(text="Failed to save user. Check logs.")

    def _open_edit_user_dialog(self, user_id_to_edit):
        if hasattr(self, 'edit_user_dialog') and self.edit_user_dialog.winfo_exists():
            self.edit_user_dialog.focus()
            return
        
        user_to_edit_obj = User.get_by_id(user_id_to_edit) # Fetch user object from DB
        if not user_to_edit_obj:
            logger.error(f"User with ID {user_id_to_edit} not found for editing in DB.")
            messagebox.showerror("Error", "Could not find the user to edit. The user list may have been updated.")
            self._load_and_display_users() # Refresh from DB
            return
        
        self.current_edit_user_id = user_id_to_edit
        self.edit_user_dialog = ctk.CTkToplevel(self)
        self.edit_user_dialog.title(f"Edit User - {user_to_edit_obj.username}")
        set_swigato_icon(self.edit_user_dialog)
        
        # Center the dialog
        center_window(self.edit_user_dialog, 400, 400)
        
        self.edit_user_dialog.transient(self.master)
        self.edit_user_dialog.grab_set()

        dialog_main_frame = ctk.CTkFrame(self.edit_user_dialog, fg_color=ADMIN_BACKGROUND_COLOR)
        dialog_main_frame.pack(expand=True, fill="both", padx=20, pady=20)

        ctk.CTkLabel(dialog_main_frame, text="Username:", font=ctk.CTkFont(family=FONT_FAMILY, size=BODY_FONT_SIZE), text_color=ADMIN_TEXT_COLOR).pack(anchor="w", pady=(0,2))
        self.username_entry_edit = ctk.CTkEntry(dialog_main_frame, width=300, font=ctk.CTkFont(family=FONT_FAMILY, size=BODY_FONT_SIZE))
        self.username_entry_edit.insert(0, user_to_edit_obj.username)
        self.username_entry_edit.pack(fill="x", pady=(0,10))

        ctk.CTkLabel(dialog_main_frame, text="Address:", font=ctk.CTkFont(family=FONT_FAMILY, size=BODY_FONT_SIZE), text_color=ADMIN_TEXT_COLOR).pack(anchor="w", pady=(0,2))
        self.address_entry_edit = ctk.CTkEntry(dialog_main_frame, width=300, font=ctk.CTkFont(family=FONT_FAMILY, size=BODY_FONT_SIZE))
        self.address_entry_edit.insert(0, user_to_edit_obj.address if user_to_edit_obj.address else '') 
        self.address_entry_edit.pack(fill="x", pady=(0,10))

        self.is_admin_var_edit = ctk.BooleanVar(value=user_to_edit_obj.is_admin)
        admin_switch_edit = ctk.CTkSwitch(dialog_main_frame, text="Is Admin?", variable=self.is_admin_var_edit,
                                      font=ctk.CTkFont(family=FONT_FAMILY, size=BODY_FONT_SIZE),
                                      text_color=ADMIN_TEXT_COLOR,
                                      progress_color=ADMIN_PRIMARY_COLOR)
        admin_switch_edit.pack(anchor="w", pady=(0,15))

        self.error_label_edit_user = ctk.CTkLabel(dialog_main_frame, text="", text_color="red", font=ctk.CTkFont(family=FONT_FAMILY, size=BODY_FONT_SIZE-1))
        self.error_label_edit_user.pack(pady=(5,0))

        buttons_frame = ctk.CTkFrame(dialog_main_frame, fg_color="transparent")
        buttons_frame.pack(fill="x", pady=(10,0), side="bottom")

        save_button = ctk.CTkButton(
            buttons_frame, text="Save Changes", command=self._save_edited_user,
            fg_color=ADMIN_BUTTON_FG_COLOR, hover_color=ADMIN_BUTTON_HOVER_COLOR, text_color=ADMIN_BUTTON_TEXT_COLOR,
            font=ctk.CTkFont(family=FONT_FAMILY, size=BUTTON_FONT_SIZE),
            corner_radius=8
        )
        save_button.pack(side="right", padx=(10,0))

        cancel_button = ctk.CTkButton(
            buttons_frame, text="Cancel", command=lambda: (self.edit_user_dialog.destroy(), setattr(self, 'current_edit_user_id', None)),
            fg_color=ADMIN_SECONDARY_ACCENT_COLOR, hover_color=ADMIN_PRIMARY_ACCENT_COLOR, text_color=ADMIN_TEXT_COLOR,
            font=ctk.CTkFont(family=FONT_FAMILY, size=BUTTON_FONT_SIZE),
            corner_radius=8
        )
        cancel_button.pack(side="right")
        
        # Set safe focus on the username entry after dialog is shown
        self.edit_user_dialog.after(100, lambda: safe_focus(self.username_entry_edit))

    def _save_edited_user(self):
        if self.current_edit_user_id is None:
            logger.error("Attempted to save edited user but no user ID was set.")
            if hasattr(self, 'edit_user_dialog') and self.edit_user_dialog.winfo_exists():
                self.edit_user_dialog.destroy()
            return

        user_to_update_obj = User.get_by_id(self.current_edit_user_id) # Get user object from DB
        if not user_to_update_obj:
            logger.error(f"User with ID {self.current_edit_user_id} not found for saving in DB.")
            self.error_label_edit_user.configure(text="User not found. Please refresh.")
            if hasattr(self, 'edit_user_dialog') and self.edit_user_dialog.winfo_exists():
                self.edit_user_dialog.destroy()
            self.current_edit_user_id = None
            self._load_and_display_users() # Refresh table
            return

        original_username = user_to_update_obj.username
        new_username = self.username_entry_edit.get().strip()
        new_address = self.address_entry_edit.get().strip()
        new_is_admin = self.is_admin_var_edit.get()

        if not new_username:
            logger.warning("Attempted to save user with empty username.")
            self.error_label_edit_user.configure(text="Username cannot be empty.")
            return

        if new_username.lower() != original_username.lower():
            existing_user_with_new_name = User.get_by_username(new_username)
            if existing_user_with_new_name and existing_user_with_new_name.user_id != self.current_edit_user_id:
                logger.warning(f"Attempted to save user with duplicate username: {new_username}")
                self.error_label_edit_user.configure(text=f"Username '{new_username}' already exists.")
                return
        
        self.error_label_edit_user.configure(text="")

        update_success = True
        if user_to_update_obj.username != new_username:
            conn = get_db_connection()
            cursor = conn.cursor()
            try:
                cursor.execute("UPDATE users SET username = ? WHERE user_id = ?", (new_username, user_to_update_obj.user_id))
                conn.commit()
                user_to_update_obj.username = new_username
                logger.info(f"Username for user ID {user_to_update_obj.user_id} updated to '{new_username}'.")
            except Exception as e:
                logger.error(f"Error updating username for user ID {user_to_update_obj.user_id}: {e}")
                update_success = False
            finally:
                conn.close()

        if user_to_update_obj.address != new_address:
            if not user_to_update_obj.update_address(new_address):
                update_success = False
                logger.error(f"Failed to update address for user {user_to_update_obj.username}")
        
        if user_to_update_obj.is_admin != new_is_admin:
            if not user_to_update_obj.update_admin_status(new_is_admin):
                update_success = False
                logger.error(f"Failed to update admin status for user {user_to_update_obj.username}")
        
        if update_success:
            logger.info(f"User data updated for '{user_to_update_obj.username}' (ID: {user_to_update_obj.user_id}).")
            self._load_and_display_users() # Refresh table from DB
            if hasattr(self, 'edit_user_dialog') and self.edit_user_dialog.winfo_exists():
                self.edit_user_dialog.destroy()
            self.current_edit_user_id = None
        else:
            self.error_label_edit_user.configure(text="Failed to save some changes. Check logs.")

    def _on_cell_click(self, event_data):
        row_clicked_on_gui = event_data["row"]
        column_clicked = event_data["column"]
        logger.info(f"Cell clicked: Display Row {row_clicked_on_gui}, Column {column_clicked}")

        if row_clicked_on_gui == 0: 
            return

        user_view_index = row_clicked_on_gui - 1 

        if not (0 <= user_view_index < len(self.current_view_users)):
            logger.warning(f"Clicked on table but view_index {user_view_index} is out of bounds for current_view_users (len {len(self.current_view_users)}).")
            return
        
        user_dict = self.current_view_users[user_view_index]
        user_id = user_dict['id']

        if column_clicked == self.edit_action_column_index:
            self._open_edit_user_dialog(user_id)
        elif column_clicked == self.delete_action_column_index:
            self._confirm_delete_user(user_id)
        else:
            logger.info(f"Clicked on non-interactive column {column_clicked} for user ID {user_id}. No action.")

    def _confirm_delete_user(self, user_id_to_delete): 
        user_to_delete_obj = User.get_by_id(user_id_to_delete)
        if not user_to_delete_obj:
            logger.error(f"User with ID {user_id_to_delete} not found for deletion confirmation in DB.")
            messagebox.showerror("Error", "User not found. The list may have been updated.")
            self._load_and_display_users()
            return
        
        confirm = messagebox.askyesno(
            "Confirm Deletion", 
            f"Are you sure you want to delete user '{user_to_delete_obj.username}' (ID: {user_to_delete_obj.user_id})?"
        )
        if confirm:
            self._delete_user(user_id_to_delete, user_to_delete_obj.username)

    def _delete_user(self, user_id_to_delete, username_for_logging):
        if User.delete_by_username(username_for_logging):
            logger.info(f"User '{username_for_logging}' (ID: {user_id_to_delete}) deleted successfully from DB.")
            self._load_and_display_users()        
        else:
            logger.warning(f"Failed to delete user '{username_for_logging}' (ID: {user_id_to_delete}) from DB. They might have already been deleted or an error occurred.")
            messagebox.showwarning(
                "Deletion Failed", 
                f"User '{username_for_logging}' could not be deleted. The list might have been updated or an error occurred."
            )
            self._load_and_display_users()

    def _toggle_admin_status(self, user_id_to_toggle): 
        user_to_modify_obj = User.get_by_id(user_id_to_toggle)
        if not user_to_modify_obj:
            logger.error(f"User with ID {user_id_to_toggle} not found for toggling admin status in DB.")
            messagebox.showerror("Error", "User not found. The list may have been updated.")
            self._load_and_display_users()
            return
        
        old_status = user_to_modify_obj.is_admin
        new_status = not old_status
        if user_to_modify_obj.update_admin_status(new_status):
            logger.info(f"Toggled admin status for user '{user_to_modify_obj.username}' (ID: {user_id_to_toggle}) from {old_status} to {new_status} in DB.")
            self._load_and_display_users()
        else:
            logger.error(f"Failed to toggle admin status for user '{user_to_modify_obj.username}' (ID: {user_id_to_toggle}) in DB.")
            messagebox.showerror("Error", "Failed to update admin status. Check logs.")
            self._load_and_display_users()

    def _load_and_display_users(self):
        search_term = self.search_entry.get().lower() if hasattr(self, 'search_entry') and self.search_entry.winfo_exists() else ""
        admin_filter_status = self.admin_filter_var.get() if hasattr(self, 'admin_filter_var') else "All"
        
        logger.debug(f"Loading users from DB. Search: '{search_term}', Filter: '{admin_filter_status}'")

        all_users_from_db = User.get_all_users()
        
        self.users_data = []
        if all_users_from_db:
            for user_obj in all_users_from_db:
                self.users_data.append({
                    'id': user_obj.user_id,
                    'username': user_obj.username,
                    'is_admin': user_obj.is_admin,
                    'address': user_obj.address if user_obj.address else ""
                })

        filtered_user_list = []
        source_users = self.users_data

        for user_item in source_users:
            passes_admin_filter = False
            if admin_filter_status == "All":
                passes_admin_filter = True
            elif admin_filter_status == "Admin" and user_item['is_admin']:
                passes_admin_filter = True
            elif admin_filter_status == "Non-Admin" and not user_item['is_admin']:
                passes_admin_filter = True

            if not passes_admin_filter:
                continue

            passes_search_filter = False
            if not search_term: 
                passes_search_filter = True
            else:
                if search_term in str(user_item['id']).lower():
                    passes_search_filter = True
                elif search_term in user_item['username'].lower():
                    passes_search_filter = True
                elif 'address' in user_item and user_item['address'] and search_term in user_item['address'].lower():
                    passes_search_filter = True
            
            if not passes_search_filter:
                continue
            
            filtered_user_list.append(user_item)

        self.current_view_users = filtered_user_list 
        logger.debug(f"Displaying {len(self.current_view_users)} users after filtering.")

        table_values = [["User ID", "Username", "Admin?", "Address", "Edit", "Delete"]]
        for user_item_view in self.current_view_users: 
            table_values.append([
                user_item_view['id'],
                user_item_view['username'],
                "Yes" if user_item_view['is_admin'] else "No",
                user_item_view.get('address', 'N/A'), 
                "Edit",
                "Delete"
            ])

        if self.user_table:
            self.user_table.destroy()
            self.user_table = None 

        header_font = ctk.CTkFont(family=FONT_FAMILY, size=BODY_FONT_SIZE+1, weight="bold")
        cell_font = ctk.CTkFont(family=FONT_FAMILY, size=BODY_FONT_SIZE)
        
        if len(table_values) == 1 and (search_term or admin_filter_status != "All"):
             logger.info("No users match current filter criteria. Table will be empty or show header only.")
        elif not source_users:
             logger.info("No users in the master list. Table will be empty or show header only.")

        self.user_table = CTkTable(
            master=self.table_frame,
            values=table_values, 
            font=cell_font,
            colors=[ADMIN_TABLE_ROW_LIGHT_COLOR, ADMIN_TABLE_ROW_DARK_COLOR],
            header_color=ADMIN_TABLE_HEADER_BG_COLOR,
            corner_radius=8,
            border_width=1,
            border_color=ADMIN_TABLE_BORDER_COLOR,
            command=self._on_cell_click
        )
        self.user_table.pack(expand=True, fill="both", padx=10, pady=10)

        if table_values: 
            self.user_table.edit_row(0, text_color=ADMIN_TABLE_HEADER_TEXT_COLOR, font=header_font, fg_color=ADMIN_TABLE_HEADER_BG_COLOR)

        for i in range(1, len(table_values)): 
            current_bg_color = ADMIN_TABLE_ROW_LIGHT_COLOR if i % 2 != 0 else ADMIN_TABLE_ROW_DARK_COLOR
            self.user_table.edit_row(i, fg_color=current_bg_color, text_color=ADMIN_TABLE_TEXT_COLOR, hover_color=ADMIN_PRIMARY_ACCENT_COLOR, font=cell_font)

    def refresh_data(self):
        logger.info("AdminUsersScreen: Refreshing data (called externally)...")
        self._load_and_display_users()
        self.update_idletasks()

