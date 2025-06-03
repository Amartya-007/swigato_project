import customtkinter as ctk
from CTkTable import CTkTable
import logging
from gui_constants import (
    FONT_FAMILY, BODY_FONT_SIZE, HEADING_FONT_SIZE,
    ADMIN_BACKGROUND_COLOR, ADMIN_FRAME_FG_COLOR, ADMIN_TEXT_COLOR,
    ADMIN_PRIMARY_ACCENT_COLOR, ADMIN_SECONDARY_ACCENT_COLOR,
    ADMIN_TABLE_HEADER_BG_COLOR, ADMIN_TABLE_ROW_LIGHT_COLOR, ADMIN_TABLE_ROW_DARK_COLOR,
    ADMIN_TABLE_BORDER_COLOR, ADMIN_TABLE_TEXT_COLOR, ERROR_COLOR, ADMIN_PRIMARY_COLOR, ADMIN_BUTTON_TEXT_COLOR, ADMIN_BUTTON_HOVER_COLOR
)
from orders.models import Order

logger = logging.getLogger("swigato_app.admin_orders_screen")

class AdminOrdersScreen(ctk.CTkFrame):
    def __init__(self, master, app_callbacks, user, **kwargs):
        super().__init__(master, fg_color=ADMIN_BACKGROUND_COLOR, **kwargs)
        self.app_callbacks = app_callbacks
        self.loggedInUser = user
        self.current_orders = []
        self.current_view = "orders"  # 'orders' or 'history'

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)

        title_label = ctk.CTkLabel(self, text="Orders Management",
                                   font=ctk.CTkFont(family=FONT_FAMILY, size=HEADING_FONT_SIZE, weight="bold"),
                                   text_color=ADMIN_TEXT_COLOR)
        title_label.grid(row=0, column=0, padx=20, pady=(10, 10), sticky="nw")

        self.table_frame = ctk.CTkFrame(self, fg_color=ADMIN_FRAME_FG_COLOR, corner_radius=10)
        self.table_frame.grid(row=1, column=0, padx=20, pady=(0,20), sticky="nsew")
        self.table_frame.grid_columnconfigure(0, weight=1)
        self.table_frame.grid_rowconfigure(0, weight=1)

        self.orders_table = None
        self.show_orders()  # Default view
        logger.info("AdminOrdersScreen initialized and orders loaded.")

    def show_orders(self):
        self.current_view = "orders"
        self._load_and_display_orders(active_only=True)

    def show_order_history(self):
        self.current_view = "history"
        self._load_and_display_orders(active_only=False)

    def _load_and_display_orders(self, active_only=True):
        for widget in self.table_frame.winfo_children():
            widget.destroy()

        all_orders = Order.get_all_orders()
        if active_only:
            active_statuses = ("Pending Confirmation", "Preparing", "Out for Delivery", "Confirmed")
            orders = [o for o in all_orders if o.status in active_statuses]
            orders.sort(key=lambda o: o.order_date, reverse=True)
        else:
            orders = list(all_orders)
            orders.sort(key=lambda o: o.order_date)

        from orders.models import get_order_items_for_order
        for o in orders:
            if not hasattr(o, 'items') or not o.items:
                o.items = get_order_items_for_order(o.order_id)

        self.current_orders = orders

        # Add 'Actions' column only for active orders
        if active_only:
            headers = ["Order ID", "User", "Restaurant", "Date", "Total (₹)", "Status", "Address", "Items", "Actions"]
        else:
            headers = ["Order ID", "User", "Restaurant", "Date", "Total (₹)", "Status", "Address", "Items"]
        table_data = [headers]
        for order in orders:
            user_display = order.customer_username if hasattr(order, 'customer_username') else str(order.user_id)
            date_str = order.order_date.strftime('%Y-%m-%d %H:%M') if hasattr(order.order_date, 'strftime') else str(order.order_date)
            items_str = ", ".join([f"{item.name} x{item.quantity}" for item in getattr(order, 'items', [])])
            if len(items_str) > 60:
                items_str = items_str[:57] + "..."
            address_str = order.delivery_address or "N/A"
            if len(address_str) > 30:
                address_str = address_str[:27] + "..."
            row = [
                order.order_id,
                user_display,
                order.restaurant_name,
                date_str,
                f"{order.total_amount:.2f}",
                order.status,
                address_str,
                items_str
            ]
            if active_only:
                row.append("Change Status")
            table_data.append(row)

        if len(table_data) == 1:
            ctk.CTkLabel(self.table_frame, text="No orders found.",
                         font=ctk.CTkFont(family=FONT_FAMILY, size=BODY_FONT_SIZE),
                         text_color=ADMIN_TEXT_COLOR).pack(expand=True, anchor="center", padx=20, pady=20)
            return

        cell_font = ctk.CTkFont(family=FONT_FAMILY, size=BODY_FONT_SIZE - 1)
        # Use a scrollable frame for order history (not for active orders, which are usually fewer)
        if not active_only:
            scroll_frame = ctk.CTkScrollableFrame(self.table_frame, fg_color=ADMIN_FRAME_FG_COLOR, corner_radius=10)
            scroll_frame.pack(expand=True, fill="both", padx=0, pady=0)
            table_parent = scroll_frame
        else:
            table_parent = self.table_frame
        self.orders_table = CTkTable(
            master=table_parent,
            values=table_data,
            font=cell_font,
            header_color=ADMIN_TABLE_HEADER_BG_COLOR,
            text_color=ADMIN_TABLE_TEXT_COLOR,
            hover_color=ADMIN_PRIMARY_ACCENT_COLOR,
            colors=[ADMIN_TABLE_ROW_LIGHT_COLOR, ADMIN_TABLE_ROW_DARK_COLOR],
            corner_radius=8,
            border_width=1,
            border_color=ADMIN_TABLE_BORDER_COLOR,
            wraplength=180,
            command=self._on_cell_click if active_only else None
        )
        self.orders_table.pack(expand=True, fill="both", padx=10, pady=10)
        if active_only:
            self.actions_column_index = 8

    def _on_cell_click(self, event_data):
        row_clicked = event_data["row"]
        column_clicked = event_data["column"]
        if row_clicked == 0:
            return
        order_index = row_clicked - 1
        if not (0 <= order_index < len(self.current_orders)):
            return
        order = self.current_orders[order_index]
        if column_clicked == getattr(self, 'actions_column_index', -1):
            self._open_status_change_dialog(order)

    def _open_status_change_dialog(self, order):
        dialog = ctk.CTkToplevel(self)
        dialog.title(f"Change Status for Order {order.order_id}")
        dialog.geometry("420x280")
        dialog.configure(fg_color=ADMIN_BACKGROUND_COLOR)
        dialog.grab_set()
        ctk.CTkLabel(dialog, text=f"Order ID: {order.order_id}", font=ctk.CTkFont(family=FONT_FAMILY, size=18, weight="bold"), text_color=ADMIN_PRIMARY_COLOR, fg_color="transparent").pack(pady=(24,8))
        ctk.CTkLabel(dialog, text=f"Current Status: {order.status}", font=ctk.CTkFont(family=FONT_FAMILY, size=15), text_color=ADMIN_TEXT_COLOR, fg_color="transparent").pack(pady=6)
        status_options = ["Pending Confirmation", "Preparing", "Out for Delivery", "Confirmed", "Delivered", "Cancelled", "Failed"]
        status_var = ctk.StringVar(value=order.status)
        status_menu = ctk.CTkOptionMenu(dialog, variable=status_var, values=status_options, font=ctk.CTkFont(family=FONT_FAMILY, size=15), fg_color=ADMIN_PRIMARY_COLOR, text_color=ADMIN_BUTTON_TEXT_COLOR, dropdown_fg_color=ADMIN_PRIMARY_ACCENT_COLOR, dropdown_text_color=ADMIN_TEXT_COLOR)
        status_menu.pack(pady=12)
        status_label = ctk.CTkLabel(dialog, text="", font=ctk.CTkFont(family=FONT_FAMILY, size=13), text_color=ERROR_COLOR, fg_color="transparent")
        status_label.pack(pady=5)
        def save_status():
            new_status = status_var.get()
            if new_status == order.status:
                status_label.configure(text="No change.")
                return
            from orders.models import Order as OrderModel
            if OrderModel.update_status(order.order_id, new_status):
                status_label.configure(text="Status updated!", text_color="#43A047")
                dialog.after(700, dialog.destroy)
                self._load_and_display_orders(active_only=True)
            else:
                status_label.configure(text="Failed to update status.", text_color=ERROR_COLOR)
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.pack(pady=16)
        save_btn = ctk.CTkButton(btn_frame, text="Save", command=save_status, fg_color=ADMIN_PRIMARY_COLOR, hover_color=ADMIN_BUTTON_HOVER_COLOR, text_color=ADMIN_BUTTON_TEXT_COLOR, font=ctk.CTkFont(family=FONT_FAMILY, size=14), width=110)
        save_btn.pack(side="left", padx=10)
        cancel_btn = ctk.CTkButton(btn_frame, text="Cancel", command=dialog.destroy, fg_color=ADMIN_SECONDARY_ACCENT_COLOR, hover_color=ADMIN_PRIMARY_ACCENT_COLOR, text_color=ADMIN_TEXT_COLOR, font=ctk.CTkFont(family=FONT_FAMILY, size=14), width=110)
        cancel_btn.pack(side="left", padx=10)
