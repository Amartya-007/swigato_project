# filepath: g:\swigato_project\gui_components\admin_orders_screen.py
import customtkinter as ctk
from CTkTable import CTkTable
import logging
from tkinter import messagebox
import tkinter
from orders.models import Order
from gui_constants import (
    FONT_FAMILY, BODY_FONT_SIZE, BUTTON_FONT_SIZE, ADMIN_BACKGROUND_COLOR, 
    ADMIN_TEXT_COLOR, ADMIN_FRAME_FG_COLOR, ADMIN_BUTTON_FG_COLOR, 
    ADMIN_BUTTON_HOVER_COLOR, ADMIN_BUTTON_TEXT_COLOR, ADMIN_PRIMARY_ACCENT_COLOR, 
    ADMIN_SECONDARY_ACCENT_COLOR, ADMIN_TABLE_HEADER_BG_COLOR, ADMIN_TABLE_ROW_LIGHT_COLOR, 
    ADMIN_TABLE_ROW_DARK_COLOR, ADMIN_TABLE_BORDER_COLOR, HEADING_FONT_SIZE, 
    ADMIN_PRIMARY_COLOR, ADMIN_TABLE_TEXT_COLOR, ICON_PATH,
    set_swigato_icon, safe_focus, center_window
)

import os

logger = logging.getLogger("swigato_app.admin_orders_screen")

class AdminOrdersScreen(ctk.CTkFrame):
    def __init__(self, master, app_callbacks, user, **kwargs):
        super().__init__(master, fg_color=ADMIN_BACKGROUND_COLOR, **kwargs)
        self.app_callbacks = app_callbacks
        self.loggedInUser = user
        self.current_orders_view = []

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=0)
        self.grid_rowconfigure(2, weight=1)

        title_label = ctk.CTkLabel(self, text="Orders Management", 
                                   font=ctk.CTkFont(family=FONT_FAMILY, size=HEADING_FONT_SIZE, weight="bold"), 
                                   text_color=ADMIN_TEXT_COLOR)
        title_label.grid(row=0, column=0, padx=20, pady=(10, 10), sticky="nw")

        controls_frame = ctk.CTkFrame(self, fg_color="transparent")
        controls_frame.grid(row=1, column=0, padx=20, pady=(0,10), sticky="ew")

        self.refresh_button = ctk.CTkButton(
            controls_frame,
            text="Refresh Orders",
            command=self._load_and_display_orders,
            fg_color=ADMIN_BUTTON_FG_COLOR,
            hover_color=ADMIN_BUTTON_HOVER_COLOR,
            text_color=ADMIN_BUTTON_TEXT_COLOR,
            font=ctk.CTkFont(family=FONT_FAMILY, size=BUTTON_FONT_SIZE),
            corner_radius=8
        )
        self.refresh_button.pack(side="left", padx=(0,10))

        self.table_frame = ctk.CTkFrame(self, fg_color=ADMIN_FRAME_FG_COLOR, corner_radius=10)
        self.table_frame.grid(row=2, column=0, padx=20, pady=(0,20), sticky="nsew")
        self.table_frame.grid_columnconfigure(0, weight=1)
        self.table_frame.grid_rowconfigure(0, weight=1)

        self.orders_table = None
        self._load_and_display_orders()
        logger.info("AdminOrdersScreen initialized and orders loaded.")

    def _load_and_display_orders(self):
        logger.debug("Loading all orders from database.")
        all_orders_from_db = Order.get_all_orders()

        # Filter out completed/cancelled orders before displaying
        active_orders = []
        if all_orders_from_db:
            for order_obj in all_orders_from_db:
                if order_obj.status.lower() not in ["delivered", "cancelled", "failed"]:
                    active_orders.append(order_obj)
        
        logger.info(f"Retrieved {len(all_orders_from_db) if all_orders_from_db else 0} orders, displaying {len(active_orders)} active orders.")

        self.current_orders_view = []
        table_values = [["Order ID", "Customer", "Restaurant", "Total (₹)", "Status", "Date", "Address", "Update Status"]]

        if active_orders:
            for order_obj in active_orders:
                customer_display = order_obj.customer_username if hasattr(order_obj, 'customer_username') and order_obj.customer_username else str(order_obj.user_id)
                
                self.current_orders_view.append({
                    'order_id': order_obj.order_id,
                    'customer_username': customer_display,
                    'restaurant_name': order_obj.restaurant_name,
                    'total_amount': f"{order_obj.total_amount:.2f}",
                    'status': order_obj.status,
                    'order_date': order_obj.order_date.strftime('%Y-%m-%d %H:%M') if hasattr(order_obj.order_date, 'strftime') else str(order_obj.order_date),
                    'delivery_address': order_obj.delivery_address if order_obj.delivery_address else 'N/A'
                })
                table_values.append([
                    order_obj.order_id,
                    customer_display,
                    order_obj.restaurant_name,
                    f"{order_obj.total_amount:.2f}",
                    order_obj.status,
                    order_obj.order_date.strftime('%Y-%m-%d %H:%M') if hasattr(order_obj.order_date, 'strftime') else str(order_obj.order_date),
                    order_obj.delivery_address if order_obj.delivery_address else 'N/A',
                    "Update"
                ])
        
        if self.orders_table and isinstance(self.orders_table, CTkTable):
            self.orders_table.destroy()
            self.orders_table = None
        elif self.orders_table:
             self.orders_table.destroy()
             self.orders_table = None

        if not active_orders:
            logger.info("No active orders found to display.")
            self.orders_table = ctk.CTkLabel(self.table_frame, text="No active orders found.", font=ctk.CTkFont(family=FONT_FAMILY, size=BODY_FONT_SIZE), text_color=ADMIN_TEXT_COLOR)
            self.orders_table.pack(expand=True, anchor="center")
            return

        header_font = ctk.CTkFont(family=FONT_FAMILY, size=BODY_FONT_SIZE+1, weight="bold")
        cell_font = ctk.CTkFont(family=FONT_FAMILY, size=BODY_FONT_SIZE)

        self.orders_table = CTkTable(
            master=self.table_frame,
            values=table_values,
            # font=cell_font, # Temporarily removed to diagnose deepcopy error
            # header_font=header_font, # Temporarily removed to diagnose deepcopy error
            header_color=ADMIN_TABLE_HEADER_BG_COLOR,
            hover_color=ADMIN_PRIMARY_ACCENT_COLOR,
            text_color=ADMIN_TABLE_TEXT_COLOR,
            colors=[ADMIN_TABLE_ROW_LIGHT_COLOR, ADMIN_TABLE_ROW_DARK_COLOR],
            corner_radius=8,
            border_width=1,
            border_color=ADMIN_TABLE_BORDER_COLOR,
            command=self._on_cell_click,
            wraplength=150  # Adjust wraplength for cell content
        )
        self.orders_table.pack(expand=True, fill="both", padx=10, pady=10)
        
        logger.debug(f"Displayed {len(self.current_orders_view)} orders.")

    def _on_cell_click(self, event_data):
        # event_data is expected to be a dict like: {'row': int, 'column': int, 'value': str}
        # 'row' is 0-indexed, where 0 is the header row.
        row_clicked = event_data["row"]
        column_clicked = event_data["column"]
        # value_clicked = event_data["value"] # The actual string value of the cell

        if row_clicked == 0:  # Clicked on header row
            logger.info(f"Header row clicked at Table Row {row_clicked}, Column {column_clicked}. Ignoring.")
            return

        # Convert table row index (1-based for data) to 0-based index for self.current_orders_view
        data_row_idx = row_clicked - 1
        
        logger.info(f"Order table cell clicked: Table Row {row_clicked} (Data Index {data_row_idx}), Column Index {column_clicked}")

        if not (0 <= data_row_idx < len(self.current_orders_view)):
            logger.warning(f"Clicked data_row_idx {data_row_idx} is out of bounds for current_orders_view (len {len(self.current_orders_view)}).")
            return
        
        order_data = self.current_orders_view[data_row_idx]
        order_id = order_data['order_id']

        # Determine if the "Update Status" column was clicked.
        # The header is ["Order ID", ..., "Update Status"]
        # Assuming self.orders_table.values[0] holds the header list
        if self.orders_table and self.orders_table.values:
            header_list = self.orders_table.values[0]
            update_status_column_index = len(header_list) - 1 # Last column

            if column_clicked == update_status_column_index:
                self._open_update_status_dialog(order_id, order_data['status'])
            else:
                logger.info(f"Clicked on non-interactive column {column_clicked} (value: '{event_data.get('value', 'N/A')}') for order ID {order_id}.")
        else:
            logger.warning("Could not determine header to identify 'Update Status' column.")

    def _open_update_status_dialog(self, order_id, current_status):
        # Use a compact, light-themed, visually consistent modal
        dialog = ctk.CTkToplevel(self)
        dialog.title(f"Update Order #{order_id} Status")
        dialog.resizable(False, False)
        dialog_width = 420
        dialog_height = 300
        
        # Center the dialog on screen
        center_window(dialog, dialog_width, dialog_height)
        
        dialog.transient(self.master)
        dialog.grab_set()
        
        # Set Swigato icon safely
        set_swigato_icon(dialog)

        # Main themed frame (no dark/black, no rounded dark corners)
        main_frame = ctk.CTkFrame(dialog, fg_color=ADMIN_BACKGROUND_COLOR, corner_radius=0)
        main_frame.pack(expand=True, fill="both", padx=0, pady=0)
        main_frame.grid_columnconfigure(0, weight=1)

        # Title
        ctk.CTkLabel(main_frame, text="Update Order Status", font=ctk.CTkFont(family=FONT_FAMILY, size=HEADING_FONT_SIZE, weight="bold"), text_color=ADMIN_PRIMARY_COLOR).pack(pady=(18, 6))
        # Order info
        ctk.CTkLabel(main_frame, text=f"Order ID: {order_id}", font=ctk.CTkFont(family=FONT_FAMILY, size=BODY_FONT_SIZE+2), text_color=ADMIN_TEXT_COLOR).pack(pady=(0, 2))
        ctk.CTkLabel(main_frame, text=f"Current Status: {current_status}", font=ctk.CTkFont(family=FONT_FAMILY, size=BODY_FONT_SIZE), text_color=ADMIN_TEXT_COLOR).pack(pady=(0, 10))

        status_options = ["Pending Confirmation", "Confirmed", "Preparing Food", "Out for Delivery", "Delivered", "Cancelled", "Failed"]
        if current_status not in status_options:
            status_options.insert(0, current_status)
        new_status_var = ctk.StringVar(value=current_status)
        status_menu = ctk.CTkOptionMenu(
            main_frame,
            variable=new_status_var,
            values=status_options,
            font=ctk.CTkFont(family=FONT_FAMILY, size=BODY_FONT_SIZE+1),
            dropdown_font=ctk.CTkFont(family=FONT_FAMILY, size=BODY_FONT_SIZE),
            fg_color=ADMIN_BUTTON_FG_COLOR,
            button_color=ADMIN_BUTTON_FG_COLOR,
            button_hover_color=ADMIN_BUTTON_HOVER_COLOR,
            text_color=ADMIN_BUTTON_TEXT_COLOR,
            width=260
        )
        status_menu.pack(pady=(0, 18))

        # Buttons: right-aligned, side by side
        buttons_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        buttons_frame.pack(side="bottom", anchor="e", pady=(0, 18), padx=18)
        save_btn = ctk.CTkButton(buttons_frame, text="Save Status", command=lambda: save_status(), corner_radius=8, fg_color=ADMIN_BUTTON_FG_COLOR, hover_color=ADMIN_BUTTON_HOVER_COLOR, text_color=ADMIN_BUTTON_TEXT_COLOR, font=ctk.CTkFont(family=FONT_FAMILY, size=BUTTON_FONT_SIZE), width=110)
        cancel_btn = ctk.CTkButton(buttons_frame, text="Cancel", command=dialog.destroy, corner_radius=8, fg_color=ADMIN_SECONDARY_ACCENT_COLOR, hover_color=ADMIN_PRIMARY_ACCENT_COLOR, text_color=ADMIN_TEXT_COLOR, font=ctk.CTkFont(family=FONT_FAMILY, size=BUTTON_FONT_SIZE), width=90)        
        cancel_btn.pack(side="right", padx=(0, 8))
        save_btn.pack(side="right")

        def save_status():
            new_status = new_status_var.get()
            parent_window = self.winfo_toplevel() if hasattr(self, 'winfo_toplevel') else self.master
            if new_status != current_status:
                if Order.update_status(order_id, new_status):
                    logger.info(f"Order #{order_id} status updated to '{new_status}'. Triggering table refresh.")
                    try:
                        messagebox.showinfo("Success", f"Order #{order_id} status updated to '{new_status}'.")
                    except Exception as e:
                        logger.error(f"Error showing info dialog after order status update: {e}")
                    self._load_and_display_orders()
                    dialog.destroy()
                else:
                    logger.error(f"Failed to update status for order #{order_id} via Order.update_status.")
                    try:
                        messagebox.showerror("Error", f"Failed to update status for order #{order_id}. Check logs.")
                    except Exception as e:
                        logger.error(f"Error showing error dialog after order status update: {e}")
            else:
                dialog.destroy()

        dialog.bind("<Return>", lambda event: save_status())
        dialog.bind("<Escape>", lambda event: dialog.destroy())
