from utils.database import get_db_connection
from utils.logger import log
from rich.table import Table
from rich.text import Text
import sqlite3

class MenuItem:
    def __init__(self, item_id, restaurant_id, name, description, price, category, created_at=None):
        self.item_id = item_id
        self.restaurant_id = restaurant_id
        self.name = name
        self.description = description
        self.price = price
        self.category = category
        self.created_at = created_at

    def __repr__(self):
        return f"<MenuItem {self.name} (ID: {self.item_id}, RestaurantID: {self.restaurant_id}, Price: ₹{self.price})>"

    @staticmethod
    def create(restaurant_id, name, description, price, category):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO menu_items (restaurant_id, name, description, price, category)
                VALUES (?, ?, ?, ?, ?)
            """, (restaurant_id, name, description, price, category))
            conn.commit()
            item_id = cursor.lastrowid
            log(f"MenuItem '{name}' created with ID {item_id} for restaurant ID {restaurant_id}.")
            return MenuItem.get_by_id(item_id)
        except Exception as e:
            log(f"Error creating MenuItem '{name}': {e}")
            conn.rollback()
            return None
        finally:
            conn.close()

    @staticmethod
    def get_by_id(item_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM menu_items WHERE item_id = ?", (item_id,))
            row = cursor.fetchone()
            if row:
                return MenuItem(**row)
            return None
        except Exception as e:
            log(f"Error fetching MenuItem ID {item_id}: {e}")
            return None
        finally:
            conn.close()

    @staticmethod
    def get_for_restaurant(restaurant_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        menu = []
        try:
            cursor.execute("SELECT * FROM menu_items WHERE restaurant_id = ? ORDER BY category, name", (restaurant_id,))
            rows = cursor.fetchall()
            for row in rows:
                menu.append(MenuItem(**row))
            return menu
        except Exception as e:
            log(f"Error fetching menu for restaurant ID {restaurant_id}: {e}")
            return []
        finally:
            conn.close()

    def update(self, name=None, description=None, price=None, category=None):
        """Updates the menu item's details in the database."""
        if not any([name, description, price, category]):
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
        if price is not None: # Price can be 0, so check for None
            fields_to_update.append("price = ?")
            parameters.append(price)
        if category:
            fields_to_update.append("category = ?")
            parameters.append(category)

        if not fields_to_update:
            log(f"No valid fields to update for menu item ID {self.item_id}.") # Should be caught by initial check, but good to have
            return False

        parameters.append(self.item_id)

        try:
            sql = f"UPDATE menu_items SET {', '.join(fields_to_update)} WHERE item_id = ?"
            cursor.execute(sql, tuple(parameters))
            conn.commit()
            log(f"MenuItem ID {self.item_id} updated successfully. Changed fields: {fields_to_update}")
            # Update instance attributes
            if name: self.name = name
            if description: self.description = description
            if price is not None: self.price = price
            if category: self.category = category
            return True
        except Exception as e:
            log(f"Error updating MenuItem ID {self.item_id}: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def delete(self):
        """Deletes the menu item from the database."""
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
    def __init__(self, restaurant_id, name, cuisine_type, address, created_at=None):
        self.restaurant_id = restaurant_id
        self.name = name
        self.cuisine_type = cuisine_type
        self.address = address
        self.created_at = created_at

    @property
    def menu(self):
        return MenuItem.get_for_restaurant(self.restaurant_id)

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
        return f"<Restaurant {self.name} (ID: {self.restaurant_id}, Cuisine: {self.cuisine_type}) - {self.rating:.1f} stars>"

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

    def update(self, name=None, cuisine_type=None, address=None):
        """Updates the restaurant's details in the database."""
        if not any([name, cuisine_type, address]):
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

        parameters.append(self.restaurant_id)

        try:
            sql = f"UPDATE restaurants SET {', '.join(fields_to_update)} WHERE restaurant_id = ?"
            cursor.execute(sql, tuple(parameters))
            conn.commit()
            log(f"Restaurant ID {self.restaurant_id} updated successfully. Changed fields: {fields_to_update}")
            # Update instance attributes
            if name: self.name = name
            if cuisine_type: self.cuisine_type = cuisine_type
            if address: self.address = address
            return True
        except Exception as e:
            log(f"Error updating restaurant ID {self.restaurant_id}: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()

    def delete(self):
        """Deletes the restaurant and its associated menu items and reviews from the database."""
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            # Delete associated reviews
            cursor.execute("DELETE FROM reviews WHERE restaurant_id = ?", (self.restaurant_id,))
            log(f"Deleted reviews for restaurant ID {self.restaurant_id}.")

            # Delete associated menu items
            cursor.execute("DELETE FROM menu_items WHERE restaurant_id = ?", (self.restaurant_id,))
            log(f"Deleted menu items for restaurant ID {self.restaurant_id}.")
            
            # Delete the restaurant itself
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
    def create(name, cuisine_type, address):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO restaurants (name, cuisine_type, address)
                VALUES (?, ?, ?)
            """, (name, cuisine_type, address))
            conn.commit()
            restaurant_id = cursor.lastrowid
            log(f"Restaurant '{name}' created with ID {restaurant_id}.")
            return Restaurant.get_by_id(restaurant_id)
        except Exception as e:
            log(f"Error creating restaurant '{name}': {e}")
            conn.rollback()
            return None
        finally:
            conn.close()

    @staticmethod
    def get_by_id(restaurant_id):
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM restaurants WHERE restaurant_id = ?", (restaurant_id,))
            row = cursor.fetchone()
            if row:
                return Restaurant(restaurant_id=row['restaurant_id'], name=row['name'],
                                  cuisine_type=row['cuisine_type'], address=row['address'],
                                  created_at=row['created_at'])
            return None
        except Exception as e:
            log(f"Error fetching restaurant ID {restaurant_id}: {e}")
            return None
        finally:
            conn.close()

    @staticmethod
    def get_all():
        """Retrieves all restaurants from the database."""
        conn = get_db_connection()
        cursor = conn.cursor()
        restaurants = []
        try:
            cursor.execute("SELECT * FROM restaurants ORDER BY name")
            rows = cursor.fetchall()
            for row in rows:
                restaurants.append(Restaurant(restaurant_id=row['restaurant_id'], 
                                            name=row['name'],
                                            cuisine_type=row['cuisine_type'], 
                                            address=row['address'],
                                            created_at=row['created_at']))
            return restaurants
        except Exception as e:
            log(f"Error fetching all restaurants: {e}")
            return []
        finally:
            conn.close()

def populate_sample_restaurant_data():
    log("Attempting to populate sample restaurant data...")
    
    restaurants_to_add = [
        {"name": "Paradise Biryani", "cuisine": "Hyderabadi", "address": "Secunderabad, Hyderabad", "menu": [
            {"name": "Hyderabadi Chicken Biryani", "desc": "Aromatic basmati rice cooked with tender chicken and spices.", "price": 350, "cat": "Main Course"},
            {"name": "Mutton Biryani", "desc": "Rich and flavorful mutton cooked with fragrant rice.", "price": 450, "cat": "Main Course"},
            {"name": "Veg Biryani", "desc": "Mixed vegetables and basmati rice cooked in Hyderabadi style.", "price": 280, "cat": "Main Course"},
            {"name": "Masala Chai", "desc": "Traditional Indian spiced tea.", "price": 50, "cat": "Drinks"},
            {"name": "Lassi (Sweet)", "desc": "Refreshing yogurt-based drink.", "price": 80, "cat": "Drinks"},
            {"name": "Qubani ka Meetha", "desc": "Apricot dessert, a Hyderabadi specialty.", "price": 150, "cat": "Desserts"}
        ]},
        {"name": "Cafe Coffee Day", "cuisine": "Cafe", "address": "Multiple Locations", "menu": [
            {"name": "Cold Coffee", "desc": "Classic cold coffee.", "price": 180, "cat": "Drinks"},
            {"name": "Cappuccino", "desc": "Espresso with steamed milk foam.", "price": 150, "cat": "Drinks"},
            {"name": "Cafe Latte", "desc": "Espresso with steamed milk.", "price": 160, "cat": "Drinks"},
            {"name": "Chocolate Brownie", "desc": "Warm chocolate brownie.", "price": 120, "cat": "Desserts"}
        ]},
        {"name": "Punjabi Tadka", "cuisine": "North Indian", "address": "Koramangala, Bangalore", "menu": [
            {"name": "Butter Chicken", "desc": "Creamy and rich chicken curry.", "price": 400, "cat": "Main Course"},
            {"name": "Dal Makhani", "desc": "Black lentils and kidney beans cooked in a creamy sauce.", "price": 300, "cat": "Main Course"},
            {"name": "Paneer Tikka Masala", "desc": "Grilled paneer in a spiced curry.", "price": 350, "cat": "Main Course"},
            {"name": "Gulab Jamun", "desc": "Soft, deep-fried milk solids soaked in sugar syrup.", "price": 100, "cat": "Desserts"},
            {"name": "Sweet Lassi", "desc": "Traditional Punjabi sweet yogurt drink.", "price": 90, "cat": "Drinks"}
        ]}
    ]

    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        for r_data in restaurants_to_add:
            cursor.execute("SELECT restaurant_id FROM restaurants WHERE name = ?", (r_data["name"],))
            existing_r = cursor.fetchone()
            if not existing_r:
                log(f"Adding restaurant: {r_data['name']}")
                new_r = Restaurant.create(r_data["name"], r_data["cuisine"], r_data["address"])
                if new_r:
                    for item_data in r_data["menu"]:
                        cursor.execute("SELECT item_id FROM menu_items WHERE restaurant_id = ? AND name = ?", 
                                       (new_r.restaurant_id, item_data["name"]))
                        existing_item = cursor.fetchone()
                        if not existing_item:
                            MenuItem.create(new_r.restaurant_id, item_data["name"], item_data["desc"], 
                                            item_data["price"], item_data["cat"])
                        else:
                            log(f"Menu item '{item_data['name']}' already exists for '{new_r.name}'. Skipping.")
            else:
                log(f"Restaurant '{r_data['name']}' already exists. Skipping.")
        log("Sample restaurant data population check complete.")
    except Exception as e:
        log(f"Error during sample restaurant data population: {e}")
    finally:
        conn.close()
