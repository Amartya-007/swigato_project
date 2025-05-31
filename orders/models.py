import datetime
from utils.logger import log
from utils.database import get_db_connection
import sqlite3

class OrderItem:
    """Represents an item within an order, capturing details at the time of order."""
    def __init__(self, item_id, name, price, quantity, order_item_id=None, order_id=None):
        self.order_item_id = order_item_id # Database primary key
        self.order_id = order_id # Foreign key to orders table
        self.item_id = item_id # Original menu_item_id
        self.name = name
        self.price = price # Price at the time of order
        self.quantity = quantity

    @property
    def total_price(self):
        return self.price * self.quantity

    def __repr__(self):
        return f"<OrderItem DB_ID:{self.order_item_id}, OrderID:{self.order_id} - {self.name} x{self.quantity} @ ₹{self.price}>"

    @staticmethod
    def _from_row(row):
        if row:
            return OrderItem(**row)
        return None

class Order:
    def __init__(self, user_id, restaurant_id, restaurant_name, total_amount, delivery_address, 
                 order_id=None, order_date=None, status=None, items=None):
        self.order_id = order_id # Database primary key
        self.user_id = user_id # Can be None for guest orders if DB schema allows
        self.restaurant_id = restaurant_id
        self.restaurant_name = restaurant_name # Denormalized for easy display
        self.items = items if items is not None else [] # List of OrderItem objects, loaded separately
        self.total_amount = total_amount
        
        if isinstance(order_date, str):
            try:
                # Attempt to parse common SQLite timestamp formats
                if '.' in order_date:
                    self.order_date = datetime.datetime.strptime(order_date, '%Y-%m-%d %H:%M:%S.%f')
                else:
                    self.order_date = datetime.datetime.strptime(order_date, '%Y-%m-%d %H:%M:%S')
            except ValueError as e:
                log(f"Warning: Could not parse order_date string '{order_date}' due to {e}. Falling back to current time.")
                self.order_date = datetime.datetime.now() # Fallback
        elif order_date is None:
            self.order_date = datetime.datetime.now()
        else: # Assuming it's already a datetime.datetime object
            self.order_date = order_date
            
        self.status = status if status else "Pending Confirmation" # Initial status
        self.delivery_address = delivery_address

    def __repr__(self):
        return f"<Order ID: {self.order_id} - User: {self.user_id} - Total: ₹{self.total_amount} - Status: {self.status}>"

    @staticmethod
    def _from_row(row):
        if row:
            # Items will be loaded separately
            return Order(order_id=row['order_id'], user_id=row['user_id'], restaurant_id=row['restaurant_id'],
                         restaurant_name=row['restaurant_name'], total_amount=row['total_amount'],
                         delivery_address=row['delivery_address'], order_date=row['order_date'],
                         status=row['status'])
        return None

    @staticmethod
    def get_all_orders():
        """Retrieves all orders from the database, ordered by date descending."""
        conn = get_db_connection()
        cursor = conn.cursor()
        orders = []
        try:
            cursor.execute("""
                SELECT o.order_id, o.user_id, o.restaurant_id, o.restaurant_name, 
                       o.total_amount, o.status, o.order_date, o.delivery_address,
                       u.username AS customer_username  -- Fetch username from users table
                FROM orders o
                LEFT JOIN users u ON o.user_id = u.user_id -- Join with users table
                ORDER BY o.order_date DESC
            """)
            rows = cursor.fetchall()
            for row_data in rows:
                row_dict = dict(row_data)
                order = Order(
                    order_id=row_dict['order_id'],
                    user_id=row_dict['user_id'],
                    restaurant_id=row_dict['restaurant_id'],
                    restaurant_name=row_dict['restaurant_name'],
                    total_amount=row_dict['total_amount'],
                    items=[], # Pass empty list as we don't fetch items here
                    status=row_dict['status'],
                    order_date=row_dict['order_date'],
                    delivery_address=row_dict['delivery_address']
                )
                order.customer_username = row_dict['customer_username'] if row_dict['customer_username'] else 'Guest'
                orders.append(order)
            return orders
        except Exception as e:
            log(f"Error fetching all orders: {e}")
            return []
        finally:
            conn.close()

    @staticmethod
    def update_status(order_id, new_status):
        """Updates the status of an order in the database."""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE orders SET status = ? WHERE order_id = ?", (new_status, order_id))
            conn.commit()
            if cursor.rowcount > 0:
                log(f"Order {order_id} status updated to {new_status}.")
                return True
            else:
                log(f"Order {order_id} not found for status update.")
                return False
        except Exception as e:
            log(f"Error updating order status for order {order_id}: {e}")
            return False
        finally:
            conn.close()

def create_order(user_id, restaurant_id, restaurant_name, cart_items, total_amount, user_address=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        current_time = datetime.datetime.now()
        cursor.execute("""
            INSERT INTO orders (user_id, restaurant_id, restaurant_name, total_amount, delivery_address, order_date, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user_id, restaurant_id, restaurant_name, total_amount, user_address, current_time, "Pending Confirmation"))
        
        order_id = cursor.lastrowid
        if not order_id:
            raise Exception("Failed to create order, no order_id returned.")

        log(f"Order {order_id} created in DB. Adding items...")

        created_order_items = []
        for cart_item_obj in cart_items.values(): # Assuming cart_items is the cart.items dictionary
            cursor.execute("""
                INSERT INTO order_items (order_id, item_id, name, price, quantity)
                VALUES (?, ?, ?, ?, ?)
            """, (order_id, cart_item_obj.menu_item.item_id, cart_item_obj.menu_item.name, 
                  cart_item_obj.menu_item.price, cart_item_obj.quantity))
            order_item_id = cursor.lastrowid
            created_order_items.append(
                OrderItem(
                    order_item_id=order_item_id,
                    order_id=order_id,
                    item_id=cart_item_obj.menu_item.item_id,
                    name=cart_item_obj.menu_item.name,
                    price=cart_item_obj.menu_item.price,
                    quantity=cart_item_obj.quantity
                )
            )
        
        conn.commit()
        log(f"Order {order_id} and its {len(created_order_items)} item(s) committed to database.")
        
        return Order(
            order_id=order_id,
            user_id=user_id,
            restaurant_id=restaurant_id,
            restaurant_name=restaurant_name,
            items=created_order_items,
            total_amount=total_amount,
            delivery_address=user_address,
            order_date=current_time,
            status="Pending Confirmation"
        )

    except Exception as e:
        log(f"Error creating order and saving to DB: {e}")
        conn.rollback()
        return None
    finally:
        conn.close()

def get_order_items_for_order(order_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    items = []
    try:
        cursor.execute("SELECT * FROM order_items WHERE order_id = ?", (order_id,))
        rows = cursor.fetchall()
        for row in rows:
            items.append(OrderItem._from_row(row))
        return items
    except Exception as e:
        log(f"Error fetching items for order ID {order_id}: {e}")
        return []
    finally:
        conn.close()

def get_orders_by_user_id(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    orders = []
    try:
        cursor.execute("SELECT * FROM orders WHERE user_id = ? ORDER BY order_date DESC", (user_id,))
        rows = cursor.fetchall()
        for row in rows:
            order = Order._from_row(row)
            if order:
                order.items = get_order_items_for_order(order.order_id) # Load items for each order
                orders.append(order)
        return orders
    except Exception as e:
        log(f"Error fetching orders for user ID {user_id}: {e}")
        return []
    finally:
        conn.close()

def get_order_by_id(order_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM orders WHERE order_id = ?", (order_id,))
        row = cursor.fetchone()
        order = Order._from_row(row)
        if order:
            order.items = get_order_items_for_order(order.order_id) # Load items
        return order
    except Exception as e:
        log(f"Error fetching order ID {order_id}: {e}")
        return None
    finally:
        conn.close()

# No sample data population for orders as they are transactional and user-specific.
