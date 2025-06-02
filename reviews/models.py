import datetime
from utils.logger import log
from utils.database import get_db_connection
import sqlite3

class Review:
    def __init__(self, user_id, username, restaurant_id, rating, comment="", review_id=None, review_date=None, restaurant_name=None): # Added restaurant_name
        self.review_id = review_id
        self.user_id = user_id
        self.username = username # Store username for easier display
        self.restaurant_id = restaurant_id
        self.restaurant_name = restaurant_name # Added this line
        if not 1 <= rating <= 5:
            raise ValueError("Rating must be between 1 and 5.")
        self.rating = rating
        self.comment = comment
        
        if isinstance(review_date, str):
            try:
                # Attempt to parse ISO format, common for SQLite timestamps
                self.review_date = datetime.datetime.fromisoformat(review_date)
            except ValueError:
                # Fallback or handle other string formats if necessary, or raise error
                log(f"Warning: Could not parse review_date string '{review_date}'. Using current time.")
                self.review_date = datetime.datetime.now()
        elif review_date is None:
            self.review_date = datetime.datetime.now()
        else: # Assuming it's already a datetime object
            self.review_date = review_date

    def __repr__(self):
        return f"<Review ID: {self.review_id} - Restaurant: {self.restaurant_name} - User: {self.username} - Rating: {self.rating}>"

    @staticmethod
    def get_all_reviews():
        """Fetches all reviews from the database including restaurant name, ordered by review_id ASC."""
        conn = get_db_connection()
        cursor = conn.cursor()
        reviews = []
        try:
            cursor.execute("""
                SELECT r.review_id, r.user_id, r.username, r.restaurant_id, res.name AS restaurant_name,
                       r.rating, r.comment, r.review_date 
                FROM reviews r
                JOIN restaurants res ON r.restaurant_id = res.restaurant_id
                ORDER BY r.review_id ASC
            """)
            rows = cursor.fetchall()
            for row in rows:
                reviews.append(Review._from_row(row)) # Use existing helper
            return reviews
        except Exception as e:
            log(f"Error fetching all reviews: {e}")
            return []
        finally:
            conn.close()

    @staticmethod
    def _from_row(row):
        """Helper to create a Review object from a database row."""
        if row:
            return Review(**row)
        return None

    @staticmethod
    def delete_review(review_id):
        """Deletes a review from the database by its ID."""
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM reviews WHERE review_id = ?", (review_id,))
            conn.commit()
            if cursor.rowcount > 0:
                log(f"Review {review_id} deleted successfully.")
                return True
            else:
                log(f"Review {review_id} not found.")
                return False
        except Exception as e:
            log(f"Error deleting review {review_id}: {e}")
            return False
        finally:
            conn.close()

def add_review(user_id, username, restaurant_id, rating, comment=""):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Ensure rating is an integer
        if not isinstance(rating, int) or not (1 <= rating <= 5):
            log(f"Invalid rating value: {rating}. Must be an integer between 1 and 5.")
            raise ValueError("Rating must be an integer between 1 and 5.")

        current_time = datetime.datetime.now()
        cursor.execute("""
            INSERT INTO reviews (user_id, username, restaurant_id, rating, comment, review_date)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, username, restaurant_id, rating, comment, current_time))
        conn.commit()
        review_id = cursor.lastrowid
        log(f"Review {review_id} added for restaurant {restaurant_id} by user {username}.")
        return Review(
            review_id=review_id, 
            user_id=user_id, 
            username=username, 
            restaurant_id=restaurant_id, 
            rating=rating, 
            comment=comment, 
            review_date=current_time
        )
    except ValueError as ve: # Catch specific ValueError for rating
        log(f"Error adding review (ValueError): {ve}")
        conn.rollback()
        return None
    except sqlite3.Error as e:
        log(f"Database error adding review: {e}")
        conn.rollback()
        return None
    except Exception as e:
        log(f"Unexpected error adding review: {e}")
        conn.rollback()
        return None
    finally:
        conn.close()

def get_reviews_for_restaurant(restaurant_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    reviews = []
    try:
        cursor.execute("""
            SELECT r.review_id, r.user_id, r.username, r.restaurant_id, res.name AS restaurant_name,
                   r.rating, r.comment, r.review_date 
            FROM reviews r
            JOIN restaurants res ON r.restaurant_id = res.restaurant_id
            WHERE r.restaurant_id = ? 
            ORDER BY r.review_id ASC
        """, (restaurant_id,))
        rows = cursor.fetchall()
        for row in rows:
            reviews.append(Review._from_row(row))
        return reviews
    except Exception as e:
        log(f"Error fetching reviews for restaurant {restaurant_id}: {e}")
        return []
    finally:
        conn.close()

def populate_sample_reviews():
    log("Attempting to populate sample review data...")
    conn = get_db_connection()
    cursor = conn.cursor()

    sample_reviews_data = [
        # Reviews for Paradise Biryani (assuming restaurant_id=1 from populate_sample_restaurant_data)
        {"user_id": 1, "username": "Alice", "restaurant_name": "Paradise Biryani", "rating": 5, "comment": "Absolutely delicious Hyderabadi Biryani! Best in town."},
        {"user_id": 2, "username": "Bob", "restaurant_name": "Paradise Biryani", "rating": 4, "comment": "Good biryani, but a bit spicy for me."},
        # Reviews for Cafe Coffee Day (assuming restaurant_id=2)
        {"user_id": 1, "username": "Alice", "restaurant_name": "Cafe Coffee Day", "rating": 3, "comment": "Coffee was okay, place was a bit crowded."},
        # Reviews for Punjabi Tadka (assuming restaurant_id=3)
        {"user_id": 2, "username": "Bob", "restaurant_name": "Punjabi Tadka", "rating": 5, "comment": "Butter chicken was amazing! Highly recommend."},
        {"user_id": 1, "username": "Alice", "restaurant_name": "Punjabi Tadka", "rating": 4, "comment": "Great North Indian food. The lassi was also good."}
    ]

    users_to_check_or_create = {
        1: {"username": "Alice", "password": "password123", "address": "123 Wonderland"},
        2: {"username": "Bob", "password": "password456", "address": "456 Builder Street"}
    }

    for user_id, user_data in users_to_check_or_create.items():
        try:
            cursor.execute("SELECT user_id FROM users WHERE username = ?", (user_data["username"],)) # Check by username
            existing_user_row = cursor.fetchone()
            
            actual_user_id = None
            if existing_user_row:
                actual_user_id = existing_user_row['user_id']
                log(f"Sample user '{user_data['username']}' already exists with ID {actual_user_id}.")
            else:
                # Use User.create() which handles hashing and insertion
                from users.models import User # Local import
                created_user = User.create(user_data["username"], user_data["password"], user_data["address"])
                if created_user:
                    actual_user_id = created_user.user_id
                    log(f"Sample user '{user_data['username']}' created with ID {actual_user_id} for reviews.")
                else:
                    log(f"Failed to create sample user '{user_data['username']}' using User.create().")
                    continue # Skip to next user if creation failed

            # Update the user_id in sample_reviews_data if it was different or newly created
            # This is important if the predefined user_id (1 or 2) doesn't match the actual ID in the DB
            # or if the user was just created.
            if actual_user_id is not None:
                for review_template in sample_reviews_data:
                    if review_template["username"] == user_data["username"]:
                        review_template["user_id"] = actual_user_id
            
        except Exception as e:
            log(f"Could not create or verify sample user {user_data['username']} for reviews: {e}")
            # conn.rollback() # User.create handles its own transaction for user creation part

    for review_data in sample_reviews_data:
        try:
            cursor.execute("SELECT restaurant_id FROM restaurants WHERE name = ?", (review_data["restaurant_name"],))
            restaurant_row = cursor.fetchone()
            if not restaurant_row:
                log(f"Restaurant '{review_data['restaurant_name']}' not found. Skipping review.")
                continue
            
            restaurant_id = restaurant_row['restaurant_id']

            cursor.execute("""
                SELECT review_id FROM reviews 
                WHERE user_id = ? AND restaurant_id = ? AND SUBSTR(comment, 1, 20) = SUBSTR(?, 1, 20) AND rating = ?
            """, (review_data["user_id"], restaurant_id, review_data["comment"], review_data["rating"]))
            
            existing_review = cursor.fetchone()

            if not existing_review:
                added_review = add_review(
                    user_id=review_data["user_id"], 
                    username=review_data["username"],
                    restaurant_id=restaurant_id,
                    rating=review_data["rating"],
                    comment=review_data["comment"]
                )
                if added_review:
                    log(f"Added sample review for '{review_data['restaurant_name']}' by '{review_data['username']}'.")
                else:
                    log(f"Failed to add sample review for '{review_data['restaurant_name']}' by '{review_data['username']}'.")
            else:
                log(f"Sample review for '{review_data['restaurant_name']}' by '{review_data['username']}' (comment starting with '{review_data['comment'][:20]}...') already exists. Skipping.")

        except Exception as e:
            log(f"Error adding sample review for {review_data.get('restaurant_name', 'Unknown Restaurant')}: {e}")
    
    log("Sample review data population check complete.")
    conn.close()

# No need for get_average_rating_for_restaurant, as Restaurant.rating property handles this.
