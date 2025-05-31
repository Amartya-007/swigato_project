from .models import User
from utils.logger import log
from rich.console import Console

console = Console()

# Global variable to store the currently logged-in user object
current_user_session = None 

def sign_up(username, password, address=None):
    global current_user_session
    if User.get_by_username(username):
        console.print(f"[yellow]Username '{username}' already exists.[/yellow]")
        log(f"Sign up failed: Username '{username}' already exists.")
        return None
    
    new_user = User.create(username, password, address)
    if new_user:
        current_user_session = new_user # Automatically log in after sign up
        log(f"User '{username}' (ID: {new_user.user_id}) created and logged in successfully.")
        return new_user
    else:
        log(f"Sign up failed: Could not create user '{username}'.")
        return None

def log_in(username, password):
    global current_user_session
    user = User.get_by_username(username)
    if user and user.verify_password(password):
        current_user_session = user
        log(f"User '{username}' (ID: {user.user_id}) logged in successfully.")
        return user
    console.print("[red]Invalid username or password.[/red]") # Added this line
    log(f"Login failed for '{username}': Invalid username or password.")
    return None

def log_out():
    global current_user_session
    if current_user_session:
        log(f"User '{current_user_session.username}' logged out.")
        current_user_session = None
    else:
        log("Logout attempt: No user currently logged in.")

def get_current_user():
    return current_user_session
