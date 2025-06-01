import sqlite3
import os
from .logger import log

DATABASE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
DATABASE_NAME = os.path.join(DATABASE_DIR, 'swigato.db')

def get_db_connection():
    """Establishes a connection to the SQLite database."""
    if not os.path.exists(DATABASE_DIR):
        os.makedirs(DATABASE_DIR)
        log(f"Created database directory: {DATABASE_DIR}")
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row # Access columns by name
    log(f"Database connection established to {DATABASE_NAME}")
    return conn

def initialize_database():
    """Initializes all tables in the database if they don't exist."""
    log("Initializing database tables...")
    init_users_table()
    init_restaurants_table()
    init_menu_items_table()
    init_reviews_table()
    init_orders_table()
    init_order_items_table()
    log("Database initialization complete.")

    # Create a default admin user if one doesn't exist
    create_default_admin_user()

def init_users_table():
    """Initializes the users table."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            address TEXT,
            is_admin BOOLEAN DEFAULT FALSE, -- Added is_admin field
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()
    log("Users table initialized.")

def init_restaurants_table():
    """Initializes the restaurants table."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS restaurants (
            restaurant_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            cuisine_type TEXT,
            address TEXT,
            description TEXT, -- Added description column
            image_filename TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()
    log("Restaurants table initialized (with description).")

def init_menu_items_table():
    """Initializes the menu_items table."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS menu_items (
            item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            restaurant_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL,
            category TEXT,
            image_filename TEXT, -- Added image_filename column
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (restaurant_id) REFERENCES restaurants (restaurant_id)
        )
    ''')
    # Add an index for faster lookups by restaurant_id
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_menu_items_restaurant_id ON menu_items (restaurant_id);
    ''')
    conn.commit()
    conn.close()
    log("Menu items table initialized.")

def init_reviews_table():
    """Initializes the reviews table."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reviews (
            review_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            restaurant_id INTEGER NOT NULL,
            rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
            comment TEXT,
            username TEXT, -- Denormalized for easier display, could also join with users
            review_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id),
            FOREIGN KEY (restaurant_id) REFERENCES restaurants (restaurant_id)
        )
    ''')
    # Add indexes
    cursor.execute('''CREATE INDEX IF NOT EXISTS idx_reviews_user_id ON reviews (user_id);''')
    cursor.execute('''CREATE INDEX IF NOT EXISTS idx_reviews_restaurant_id ON reviews (restaurant_id);''')
    conn.commit()
    conn.close()
    log("Reviews table initialized.")

def init_orders_table():
    """Initializes the orders table."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            order_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER, -- Can be NULL for guest orders
            restaurant_id INTEGER NOT NULL,
            restaurant_name TEXT, -- Denormalized for convenience
            total_amount REAL NOT NULL,
            status TEXT DEFAULT 'Pending',
            order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            delivery_address TEXT,
            FOREIGN KEY (user_id) REFERENCES users (user_id),
            FOREIGN KEY (restaurant_id) REFERENCES restaurants (restaurant_id) 
        )
    ''')
    # Add indexes
    cursor.execute('''CREATE INDEX IF NOT EXISTS idx_orders_user_id ON orders (user_id);''')
    cursor.execute('''CREATE INDEX IF NOT EXISTS idx_orders_restaurant_id ON orders (restaurant_id);''')
    conn.commit()
    conn.close()
    log("Orders table initialized.")

def init_order_items_table():
    """Initializes the order_items table to store items for each order."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS order_items (
            order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            item_id INTEGER, -- Renamed from menu_item_id to item_id
            name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL, -- Price at the time of order
            FOREIGN KEY (order_id) REFERENCES orders (order_id)
            -- FOREIGN KEY (item_id) REFERENCES menu_items (item_id) -- Optional
        )
    ''')
    # Add index
    cursor.execute('''CREATE INDEX IF NOT EXISTS idx_order_items_order_id ON order_items (order_id);''')
    conn.commit()
    conn.close()
    log("Order items table initialized.")

def create_default_admin_user():
    """Creates a default admin user if no admin users exist."""
    from users.models import User # Local import to avoid circular dependency if User model imports from database directly
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT user_id FROM users WHERE is_admin = TRUE LIMIT 1")
        admin_exists = cursor.fetchone()
        if not admin_exists:
            default_admin_username = os.environ.get('SWIGATO_ADMIN_USER', 'admin')
            default_admin_password = os.environ.get('SWIGATO_ADMIN_PASS', 'admin123')
            # Use User.create to ensure hashing and correct insertion
            admin_user = User.create(username=default_admin_username, password=default_admin_password, address="Admin HQ", is_admin=True)
            if admin_user:
                log(f"Default admin user '{default_admin_username}' created successfully.")
            else:
                log(f"Failed to create default admin user '{default_admin_username}'.")
        else:
            log("Admin user already exists. Skipping default admin creation.")
    except sqlite3.Error as e:
        log(f"Database error during default admin user creation check: {e}")
    except Exception as e:
        log(f"Unexpected error during default admin creation: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    # This allows running the script directly to initialize the database
    log("Running database setup directly...")
    initialize_database()
    log("Database setup script finished.")
