from utils.database import get_db_connection
from utils.logger import log
from rich.table import Table
from rich.text import Text
import sqlite3

class MenuItem:
    def __init__(self, item_id, restaurant_id, name, description, price, category, image_filename=None, created_at=None):
        self.item_id = item_id
        self.restaurant_id = restaurant_id
        self.name = name
        self.description = description
        self.price = price
        self.category = category
        self.image_filename = image_filename
        self.created_at = created_at

    def __repr__(self):
        return f"<MenuItem {self.name} (ID: {self.item_id}, RestaurantID: {self.restaurant_id}, Price: ₹{self.price}, Img: {self.image_filename})>"

    @staticmethod
    def create(restaurant_id, name, description, price, category, image_filename=None):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO menu_items (restaurant_id, name, description, price, category, image_filename)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (restaurant_id, name, description, price, category, image_filename))
            conn.commit()
            item_id = cursor.lastrowid
            log(f"MenuItem '{name}' created with ID {item_id}, image: {image_filename}.")
            return MenuItem.get_by_id(item_id)
        except sqlite3.Error as e:
            log(f"SQLite error creating MenuItem '{name}': {e}")
            if "no such column: image_filename" in str(e).lower():
                log("Hint: The 'image_filename' column might be missing in the 'menu_items' table. Consider adding it: ALTER TABLE menu_items ADD COLUMN image_filename TEXT;")
            conn.rollback()
            return None
        except Exception as e:
            log(f"General error creating MenuItem '{name}': {e}")
            conn.rollback()
            return None
        finally:
            conn.close()

    @staticmethod
    def get_by_id(item_id):
        conn = get_db_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM menu_items WHERE item_id = ?", (item_id,))
            row = cursor.fetchone()
            if row:
                return MenuItem(**dict(row))
            return None
        except sqlite3.Error as e:
            log(f"SQLite error fetching MenuItem ID {item_id}: {e}")
            if "no such column: image_filename" in str(e).lower():
                log("Hint: The 'image_filename' column might be missing in the 'menu_items' table.")
            return None
        except Exception as e:
            log(f"General error fetching MenuItem ID {item_id}: {e}")
            return None
        finally:
            conn.close()

    @staticmethod
    def get_for_restaurant(restaurant_id):
        log(f"MenuItem.get_for_restaurant called for restaurant_id: {restaurant_id}") # ADDED LOG
        conn = get_db_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        menu = []
        try:
            cursor.execute("SELECT * FROM menu_items WHERE restaurant_id = ? ORDER BY category, name", (restaurant_id,))
            rows = cursor.fetchall()
            log(f"Found {len(rows)} menu items for restaurant_id: {restaurant_id}") # ADDED LOG
            for row in rows:
                menu.append(MenuItem(**dict(row)))
            return menu
        except sqlite3.Error as e:
            log(f"SQLite error fetching menu for restaurant ID {restaurant_id}: {e}")
            if "no such column: image_filename" in str(e).lower():
                log("Hint: The 'image_filename' column might be missing in the 'menu_items' table.")
            return []
        except Exception as e:
            log(f"General error fetching menu for restaurant ID {restaurant_id}: {e}")
            return []
        finally:
            conn.close()

    def update(self, name=None, description=None, price=None, category=None, image_filename=None):
        if not any([name, description, price, category, image_filename]):
            log(f"No update parameters provided for menu item ID {self.item_id}.")
            return False

        conn = get_db_connection()
        cursor = conn.cursor()
        fields_to_update = []
        parameters = []

        if name:
            fields_to_update.append("name = ?")
            parameters.append(name)
        if description:
            fields_to_update.append("description = ?")
            parameters.append(description)
        if price is not None:
            fields_to_update.append("price = ?")
            parameters.append(price)
        if category:
            fields_to_update.append("category = ?")
            parameters.append(category)
        if image_filename:
            fields_to_update.append("image_filename = ?")
            parameters.append(image_filename)

        if not fields_to_update:
            return False

        parameters.append(self.item_id)

        try:
            sql = f"UPDATE menu_items SET {', '.join(fields_to_update)} WHERE item_id = ?"
            cursor.execute(sql, tuple(parameters))
            conn.commit()
            log(f"MenuItem ID {self.item_id} updated successfully. Changed fields: {fields_to_update}")
            if name: self.name = name
            if description: self.description = description
            if price is not None: self.price = price
            if category: self.category = category
            if image_filename: self.image_filename = image_filename
            return True
        except sqlite3.Error as e:
            log(f"SQLite error updating MenuItem ID {self.item_id}: {e}")
            if "no such column: image_filename" in str(e).lower():
                log("Hint: The 'image_filename' column might be missing.")
            conn.rollback()
            return False
        except Exception as e:
            log(f"General error updating MenuItem ID {self.item_id}: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def delete(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM menu_items WHERE item_id = ?", (self.item_id,))
            conn.commit()
            log(f"MenuItem ID {self.item_id} ('{self.name}') deleted successfully.")
            return True
        except Exception as e:
            log(f"Error deleting MenuItem ID {self.item_id}: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

class Restaurant:
    def __init__(self, restaurant_id, name, cuisine_type, address, description=None, image_filename=None, created_at=None):
        self.restaurant_id = restaurant_id
        self.id = restaurant_id  # Add alias for compatibility if needed, or update all usages
        self.name = name
        self.cuisine_type = cuisine_type
        self.address = address
        self.description = description
        self.image_filename = image_filename
        self.created_at = created_at

    @property
    def menu(self):
        log(f"Accessing menu for restaurant: {self.name} (ID: {self.restaurant_id})") # ADDED LOG
        retrieved_menu = MenuItem.get_for_restaurant(self.restaurant_id)
        log(f"Restaurant.menu property for '{self.name}' returning {len(retrieved_menu)} items.") # ADDED LOG
        return retrieved_menu

    @property
    def rating(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT AVG(rating) FROM reviews WHERE restaurant_id = ?", (self.restaurant_id,))
            result = cursor.fetchone()
            return result[0] if result and result[0] is not None else 0.0
        except Exception as e:
            log(f"Error calculating rating for restaurant ID {self.restaurant_id}: {e}")
            return 0.0
        finally:
            conn.close()

    def get_review_count(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT COUNT(*) FROM reviews WHERE restaurant_id = ?", (self.restaurant_id,))
            result = cursor.fetchone()
            return result[0] if result else 0
        except Exception as e:
            log(f"Error getting review count for restaurant ID {self.restaurant_id}: {e}")
            return 0
        finally:
            conn.close()

    def __repr__(self):
        return f"<Restaurant {self.name} (ID: {self.restaurant_id}, Cuisine: {self.cuisine_type}, Img: {self.image_filename}) - {self.rating:.1f} stars>"

    def get_menu_by_category(self, category):
        return [item for item in self.menu if item.category.lower() == category.lower()]

    def display_menu(self, console):
        current_menu = self.menu
        table = Table(title=f"Menu for {self.name}", show_header=True, header_style="bold cyan")
        avg_rating = self.rating
        review_count = self.get_review_count()
        table.caption = f"Average Rating: {avg_rating:.1f} stars ({review_count} review{'s' if review_count != 1 else ''})"
        
        table.add_column("ID", style="dim", width=6)
        table.add_column("Name", min_width=20)
        table.add_column("Description", min_width=30, overflow="fold")
        table.add_column("Price (₹)", justify="right")
        table.add_column("Category", min_width=12)

        if not current_menu:
            console.print(Text(f"This restaurant currently has no items on the menu.", style="yellow"))
            return

        for item in sorted(current_menu, key=lambda x: (x.category, x.name)):
            table.add_row(
                str(item.item_id),
                item.name,
                item.description,
                f"{item.price:.2f}",
                item.category
            )
        console.print(table)

    def display_reviews(self, console):
        from reviews.models import get_reviews_for_restaurant as get_reviews_db

        all_reviews = get_reviews_db(self.restaurant_id)

        table = Table(title=f"Reviews for {self.name}", show_header=True, header_style="bold yellow")
        table.add_column("User", min_width=15)
        table.add_column("Rating", width=8)
        table.add_column("Date", width=12)
        table.add_column("Comment", min_width=30, overflow="fold")

        if not all_reviews:
            console.print(Text(f"No reviews yet for this restaurant.", style="italic yellow"))
            return

        for review_obj in all_reviews:
            table.add_row(
                review_obj.username,
                f"{review_obj.rating}/5",
                review_obj.review_date.strftime('%Y-%m-%d') if review_obj.review_date else "N/A",
                review_obj.comment if review_obj.comment else "-"
            )
        console.print(table)

    def update(self, name=None, cuisine_type=None, address=None, description=None, image_filename=None):
        if not any([name, cuisine_type, address, description, image_filename]):
            log("No update parameters provided for restaurant.")
            return False

        conn = get_db_connection()
        cursor = conn.cursor()
        fields_to_update = []
        parameters = []

        if name:
            fields_to_update.append("name = ?")
            parameters.append(name)
        if cuisine_type:
            fields_to_update.append("cuisine_type = ?")
            parameters.append(cuisine_type)
        if address:
            fields_to_update.append("address = ?")
            parameters.append(address)
        if description:
            fields_to_update.append("description = ?")
            parameters.append(description)
        if image_filename:
            fields_to_update.append("image_filename = ?")
            parameters.append(image_filename)

        parameters.append(self.restaurant_id)

        try:
            sql = f"UPDATE restaurants SET {', '.join(fields_to_update)} WHERE restaurant_id = ?"
            cursor.execute(sql, tuple(parameters))
            conn.commit()
            log(f"Restaurant ID {self.restaurant_id} updated successfully. Changed fields: {fields_to_update}")
            if name: self.name = name
            if cuisine_type: self.cuisine_type = cuisine_type
            if address: self.address = address
            if description: self.description = description
            if image_filename: self.image_filename = image_filename
            return True
        except sqlite3.Error as e:
            log(f"SQLite error updating restaurant ID {self.restaurant_id}: {e}")
            if "no such column: image_filename" in str(e).lower() or "no such column: description" in str(e).lower():
                log("Hint: The 'image_filename' or 'description' column might be missing.")
            conn.rollback()
            return False
        except Exception as e:
            log(f"Error updating restaurant ID {self.restaurant_id}: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def delete(self):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM reviews WHERE restaurant_id = ?", (self.restaurant_id,))
            log(f"Deleted reviews for restaurant ID {self.restaurant_id}.")

            cursor.execute("DELETE FROM menu_items WHERE restaurant_id = ?", (self.restaurant_id,))
            log(f"Deleted menu items for restaurant ID {self.restaurant_id}.")
            
            cursor.execute("DELETE FROM restaurants WHERE restaurant_id = ?", (self.restaurant_id,))
            conn.commit()
            log(f"Restaurant ID {self.restaurant_id} and its associated data deleted successfully.")
            return True
        except Exception as e:
            log(f"Error deleting restaurant ID {self.restaurant_id}: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    @staticmethod
    def create(name, cuisine_type, address, description=None, image_filename=None):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO restaurants (name, cuisine_type, address, description, image_filename)
                VALUES (?, ?, ?, ?, ?)
            """, (name, cuisine_type, address, description, image_filename))
            conn.commit()
            restaurant_id = cursor.lastrowid
            log(f"Restaurant '{name}' created with ID {restaurant_id}, description: {description}, image: {image_filename}.")
            return Restaurant.get_by_id(restaurant_id)
        except sqlite3.Error as e:
            log(f"SQLite error creating restaurant '{name}': {e}")
            if "no such column: description" in str(e).lower() or "no such column: image_filename" in str(e).lower():
                log("Hint: The 'description' or 'image_filename' column might be missing in the 'restaurants' table.")
            conn.rollback()
            return None
        except Exception as e:
            log(f"Error creating restaurant '{name}': {e}")
            conn.rollback()
            return None
        finally:
            conn.close()

    @staticmethod
    def get_by_id(restaurant_id):
        conn = get_db_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM restaurants WHERE restaurant_id = ?", (restaurant_id,))
            row = cursor.fetchone()
            if row:
                return Restaurant(**dict(row))
            return None
        except sqlite3.Error as e:
            log(f"SQLite error fetching restaurant ID {restaurant_id}: {e}")
            if "no such column: image_filename" in str(e).lower() or "no such column: description" in str(e).lower():
                log("Hint: The 'image_filename' or 'description' column might be missing.")
            return None
        except Exception as e:
            log(f"Error fetching restaurant ID {restaurant_id}: {e}")
            return None
        finally:
            conn.close()

    @staticmethod
    def get_all():
        conn = get_db_connection()
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        restaurants = []
        try:
            cursor.execute("SELECT * FROM restaurants ORDER BY name")
            rows = cursor.fetchall()
            for row in rows:
                restaurants.append(Restaurant(**dict(row)))
            return restaurants
        except sqlite3.Error as e:
            log(f"SQLite error fetching all restaurants: {e}")
            if "no such column: image_filename" in str(e).lower() or "no such column: description" in str(e).lower():
                log("Hint: The 'image_filename' or 'description' column might be missing.")
            return []
        except Exception as e:
            log(f"Error fetching all restaurants: {e}")
            return []
        finally:
            conn.close()

def populate_sample_restaurant_data():
    log("Attempting to populate sample restaurant data...")
    
    restaurants_to_add = [
        {"name": "Paradise Biryani", "cuisine": "Hyderabadi", "address": "Secunderabad, Hyderabad", "description": "Famous for authentic Hyderabadi biryani.", "image_filename": "restaurent_a.jpeg", "menu": [
            {"name": "Hyderabadi Chicken Biryani", "desc": "Aromatic basmati rice cooked with tender chicken and spices.", "price": 350, "cat": "Main Course", "image_filename": "menu_1.jpeg"},
            {"name": "Mutton Biryani", "desc": "Rich and flavorful mutton cooked with fragrant rice.", "price": 450, "cat": "Main Course", "image_filename": "menu_2.jpeg"},
            {"name": "Veg Biryani", "desc": "Mixed vegetables and basmati rice cooked in Hyderabadi style.", "price": 280, "cat": "Main Course", "image_filename": "menu_3.jpeg"},
            {"name": "Masala Chai", "desc": "Traditional Indian spiced tea.", "price": 50, "cat": "Drinks", "image_filename": "menu_default.jpg"},
            {"name": "Lassi (Sweet)", "desc": "Refreshing yogurt-based drink.", "price": 80, "cat": "Drinks", "image_filename": "menu_default.jpg"},
            {"name": "Qubani ka Meetha", "desc": "Apricot dessert, a Hyderabadi specialty.", "price": 150, "cat": "Desserts", "image_filename": "menu_default.jpg"}
        ]},
        {"name": "Cafe Coffee Day", "cuisine": "Cafe", "address": "Multiple Locations", "description": "Popular cafe chain serving coffee and snacks.", "image_filename": "restaurent_b.jpeg", "menu": [
            {"name": "Cold Coffee", "desc": "Classic cold coffee.", "price": 180, "cat": "Drinks", "image_filename": "menu_4.jpeg"},
            {"name": "Cappuccino", "desc": "Espresso with steamed milk foam.", "price": 150, "cat": "Drinks", "image_filename": "menu_5.jpeg"},
            {"name": "Cafe Latte", "desc": "Espresso with steamed milk.", "price": 160, "cat": "Drinks", "image_filename": "menu_default.jpg"},
            {"name": "Chocolate Brownie", "desc": "Warm chocolate brownie.", "price": 120, "cat": "Desserts", "image_filename": "menu_default.jpg"}
        ]},
        {"name": "Punjabi Tadka", "cuisine": "North Indian", "address": "Koramangala, Bangalore", "description": "Authentic Punjabi cuisine with rich flavors.", "image_filename": "restaurent_c.jpeg", "menu": [
            {"name": "Butter Chicken", "desc": "Creamy and rich chicken curry.", "price": 400, "cat": "Main Course", "image_filename": "menu_default.jpg"},
            {"name": "Dal Makhani", "desc": "Black lentils and kidney beans cooked in a creamy sauce.", "price": 300, "cat": "Main Course", "image_filename": "menu_default.jpg"},
            {"name": "Paneer Tikka Masala", "desc": "Grilled paneer in a spiced curry.", "price": 350, "cat": "Main Course", "image_filename": "menu_default.jpg"},
            {"name": "Gulab Jamun", "desc": "Soft, deep-fried milk solids soaked in sugar syrup.", "price": 100, "cat": "Desserts", "image_filename": "menu_default.jpg"},
            {"name": "Sweet Lassi", "desc": "Traditional Punjabi sweet yogurt drink.", "price": 90, "cat": "Drinks", "image_filename": "menu_default.jpg"}
        ]},
        {"name": "The Great Hall Baluchi", "cuisine": "Indian", "address": "The Lalit, New Delhi", "description": "Fine dining with exquisite Indian dishes.", "image_filename": "baluchi-the-great-hall.jpg", "menu": [
            {"name": "Dal Baluchi", "desc": "Signature slow-cooked black lentils.", "price": 650, "cat": "Main Course", "image_filename": "menu_default.jpg"},
            {"name": "Subz Biryani", "desc": "Vegetable biryani with aromatic spices.", "price": 750, "cat": "Main Course", "image_filename": "menu_default.jpg"}
        ]},
        {"name": "Badkul Restaurant", "cuisine": "Multi-cuisine", "address": "Civil Lines, Jabalpur", "description": "A mix of Indian and international cuisines.", "image_filename": "badkul.jpeg", "menu": [
            {"name": "Special Thali", "desc": "A complete meal with multiple dishes.", "price": 300, "cat": "Main Course", "image_filename": "menu_default.jpg"},
            {"name": "Chilli Paneer", "desc": "Spicy Indo-Chinese paneer dish.", "price": 250, "cat": "Starters", "image_filename": "menu_default.jpg"}
        ]}
    ]

    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        for r_data in restaurants_to_add:
            cursor.execute("SELECT restaurant_id FROM restaurants WHERE name = ?", (r_data["name"],))
            existing_r_row = cursor.fetchone() # Renamed to avoid conflict
            restaurant_id_to_use = None

            if not existing_r_row:
                log(f"Adding restaurant: {r_data['name']} with image {r_data.get('image_filename')}")
                new_r = Restaurant.create(
                    r_data["name"], 
                    r_data["cuisine"], 
                    r_data["address"], 
                    description=r_data.get("description"), 
                    image_filename=r_data.get("image_filename")
                )
                if new_r:
                    restaurant_id_to_use = new_r.restaurant_id
            else:
                log(f"Restaurant '{r_data['name']}' already exists. Checking/adding its menu items.")
                restaurant_id_to_use = existing_r_row[0] # Get ID from existing restaurant

            if restaurant_id_to_use:
                for item_data in r_data["menu"]:
                    # Check if this specific menu item already exists for this restaurant
                    cursor.execute("SELECT item_id FROM menu_items WHERE restaurant_id = ? AND name = ?", 
                                   (restaurant_id_to_use, item_data["name"]))
                    existing_item = cursor.fetchone()
                    if not existing_item:
                        log(f"Adding menu item '{item_data['name']}' to restaurant ID {restaurant_id_to_use}") # ADDED LOG
                        MenuItem.create(
                            restaurant_id_to_use, 
                            item_data["name"], 
                            item_data["desc"], 
                            item_data["price"], 
                            item_data["cat"],
                            image_filename=item_data.get("image_filename")
                        )
                    else:
                        log(f"Menu item '{item_data['name']}' already exists for restaurant ID {restaurant_id_to_use}. Skipping.")
            else:
                log(f"Could not obtain restaurant_id for '{r_data['name']}', skipping menu item population for it.")

        log("Sample restaurant data population check complete.")
    except Exception as e:
        log(f"Error during sample restaurant data population: {e}")
    finally:
        conn.close()
