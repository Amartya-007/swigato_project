from rich.console import Console
from rich.table import Table
from utils.logger import log
from utils.database import initialize_database  # Import for database initialization
from users.auth import sign_up, log_in, log_out, get_current_user
from users.models import User  # To get user address
from restaurants.models import Restaurant, populate_sample_restaurant_data  # Import Restaurant for type hinting and populate_sample_restaurant_data
from cart.models import Cart, add_item_to_cart, view_cart as display_cart_contents  # Renamed for clarity
from delivery.tracker import track_order
from orders.models import create_order, get_orders_by_user_id, get_order_by_id  # New order imports
from reviews.models import add_review as submit_review, populate_sample_reviews  # Import review functions
from utils.validation import get_validated_input  # Added import
from admin.actions import (
    view_all_users, view_all_orders, delete_user_by_admin, 
    view_all_restaurants_admin, add_restaurant_admin, 
    edit_restaurant_admin, delete_restaurant_admin,
    manage_restaurant_menu_items_admin, update_order_status_admin, delete_review_admin # Added new imports
)

active_cart = Cart()  # Initialize a global cart for the session
active_cart_restaurant_id = None  # Store the restaurant ID from which items are being added to the cart
active_cart_restaurant_name = None  # Store the restaurant name for the cart context

console = Console()  # Initialize Rich Console

def initial_data_setup():
    """Populates initial sample data. This will be adapted for database persistence."""
    log("Initial data setup: Populating sample restaurant data.")
    populate_sample_restaurant_data()  # Call to populate restaurant data
    log("Initial data setup: Populating sample reviews.")
    populate_sample_reviews()  # Call to populate review data

def list_restaurants():
    """Lists all available restaurants with dynamic ratings using Rich Table."""
    log("Fetching list of restaurants...")
    all_restaurants = Restaurant.get_all()  # Use Restaurant.get_all()
    if not all_restaurants:
        console.print("[bold red]No restaurants available at the moment.[/bold red]")
        return None

    table = Table(title="Available Restaurants", show_header=True, header_style="bold magenta")
    table.add_column("#", style="dim", width=3)
    table.add_column("Name", min_width=20)
    table.add_column("Cuisine Type", min_width=15)
    table.add_column("Rating", justify="right")

    for i, restaurant in enumerate(all_restaurants):
        table.add_row(
            str(i + 1),
            restaurant.name,
            restaurant.cuisine_type,
            f"{restaurant.rating:.1f}"
        )
    
    console.print(table)
    return all_restaurants

def select_restaurant_and_actions(all_restaurants):
    """Allows user to select a restaurant, view menu, view reviews, or add a review."""
    if not all_restaurants:
        return

    while True:
        console.print()  # Added line break
        choice_str = get_validated_input(
            prompt="[bold cyan]Enter restaurant number (or 0 to go back):[/bold cyan] ",
            validation_type="integer",
            options={"min_val": 0, "max_val": len(all_restaurants)}
        )
        choice_num = int(choice_str)

        if choice_num == 0:
            return
        selected_restaurant = all_restaurants[choice_num - 1]
        log(f"Selected: {selected_restaurant.name}")
        
        while True:
            console.print()  # Added line break
            console.print(f"--- [bold green]{selected_restaurant.name}[/bold green] ({selected_restaurant.rating:.1f} stars) ---")
            action = get_validated_input(
                prompt="Choose action: (1) View Menu, (2) View Reviews, (3) Add Review, (0) Back to Restaurants: ",
                validation_type="choice",
                options={"choices": ['1', '2', '3', '0']}
            )
            if action == '1':
                selected_restaurant.display_menu(console)
                console.print()  # Added line break after menu display
                handle_menu_actions(selected_restaurant) 
            elif action == '2':
                selected_restaurant.display_reviews(console)
            elif action == '3':
                handle_add_review(selected_restaurant)
            elif action == '0':
                break

def handle_add_review(restaurant: Restaurant):
    """Handles adding a review for a given restaurant."""
    current_user = get_current_user()
    if not current_user:
        console.print("[yellow]You must be logged in to add a review.[/yellow]")
        return

    console.print()  # Added line break
    console.print(f"--- [bold]Add Review for {restaurant.name}[/bold] ---")
    rating_str = get_validated_input(
        prompt="Enter your rating (1-5): ",
        validation_type="integer",
        options={"min_val": 1, "max_val": 5}
    )
    rating = int(rating_str)
    
    comment = console.input("Enter your comment (optional): ")
    
    review = submit_review(
        user_id=current_user.user_id,
        username=current_user.username,
        restaurant_id=restaurant.restaurant_id,
        rating=rating,
        comment=comment
    )
    if review:
        console.print("[green]Review submitted successfully![/green]")
    else:
        console.print("[red]Failed to submit review.[/red]")

def handle_menu_actions(restaurant):
    """Handles actions after viewing a restaurant's menu (e.g., add to cart)."""
    global active_cart, active_cart_restaurant_id, active_cart_restaurant_name
    if not restaurant or not restaurant.menu:
        console.print("[yellow]No menu items to select from.[/yellow]")
        return

    if active_cart_restaurant_id is not None and active_cart_restaurant_id != restaurant.restaurant_id and active_cart.items:
        console.print(f"[yellow]Your cart contains items from {active_cart_restaurant_name}.[/yellow]")
        clear_choice = get_validated_input(
            prompt="Starting a new order will clear your current cart. Continue? (yes/no): ",
            validation_type="yes_no"
        )
        if clear_choice == 'yes':  # Changed from `in ['yes', 'y']` to match get_validated_input output
            active_cart.clear_cart()
            active_cart_restaurant_id = None
            active_cart_restaurant_name = None
            log("Cart cleared for new restaurant.")
        else:
            log("Returning to restaurant list. Your current cart is preserved.")
            return
    
    active_cart_restaurant_id = restaurant.restaurant_id
    active_cart_restaurant_name = restaurant.name

    valid_item_ids = [str(item.item_id) for item in restaurant.menu]

    while True:
        console.print()  # Added line break
        action = get_validated_input(
            prompt=f"Menu for [bold]{restaurant.name}[/bold] - Enter item ID to add, 'v' to view cart, or 'b'/'0' to go back: ",
            validation_type="custom",  # Using custom validation
            error_message="Invalid input. Please enter a valid item ID, 'v', 'b', or '0'.",
            options={"pattern": r"^(v|b|0|[1-9][0-9]*)$"}  # Regex for v, b, 0, or positive integer
        ).lower()

        if action is None:  # User failed validation multiple times
            continue

        if action == 'b' or action == '0':
            break
        elif action == 'v':
            current_cart_total = active_cart.get_total_price()
            display_cart_contents(active_cart, console)
            if active_cart.items:
                checkout_choice = get_validated_input(
                    prompt="Proceed to checkout? (yes/no): ",
                    validation_type="yes_no"
                )
                if checkout_choice == 'yes':  # Changed from `in ['yes', 'y']`
                    handle_checkout()
        elif action.isdigit() and action in valid_item_ids:
            selected_item = next((item for item in restaurant.menu if str(item.item_id) == action), None)
            if not selected_item:  # Should not happen if action in valid_item_ids, but good for safety
                console.print("[red]Error: Item not found despite valid ID. Please try again.[/red]")
                continue
            
            quantity_str = get_validated_input(
                prompt=f"How many '[cyan]{selected_item.name}[/cyan]' would you like to add? (default 1, press Enter): ",
                validation_type="integer",
                options={"min_val": 1},
                optional=True,
                default_value="1"
            )
            # quantity_str will be default_value if user presses Enter, or their input
            quantity = int(quantity_str) 

            add_item_to_cart(active_cart, selected_item, quantity)
            console.print(f"[green]Added {quantity} x {selected_item.name} to cart.[/green]")
        else:
            # This case handles if the input was a number but not a valid_item_id, 
            # or if the regex allowed something unexpected (though it shouldn't with the current pattern).
            console.print("[red]Invalid item ID. Please choose from the menu or enter 'v', 'b', or '0'.[/red]")

def handle_checkout():
    """Handles the checkout process."""
    global active_cart, active_cart_restaurant_id, active_cart_restaurant_name
    current_user = get_current_user()

    if not active_cart.items:
        console.print("[yellow]Your cart is empty. Nothing to checkout.[/yellow]")
        return

    console.print()  # Added line break
    console.print("--- [bold]Checkout[/bold] ---")
    display_cart_contents(active_cart, console)
    total_amount = active_cart.get_total_price()
    console.print(f"Total amount to pay: [bold green]₹{total_amount}[/bold green]")

    confirm = get_validated_input(
        prompt="Confirm order? (yes/no): ",
        validation_type="yes_no"
    )
    if confirm not in ['yes', 'y']:
        console.print("[yellow]Checkout cancelled.[/yellow]")
        return

    user_id_for_order = None
    delivery_address = None
    if current_user:
        user_id_for_order = current_user.user_id
        if current_user.address:
            use_saved_address = get_validated_input(
                prompt=f"Use saved address: {current_user.address}? (yes/no): ",
                validation_type="yes_no"
            )
            if use_saved_address in ['yes', 'y']:
                delivery_address = current_user.address
        if not delivery_address:
            delivery_address = get_validated_input("Enter delivery address: ", "not_empty")
    else:
        log("Guest checkout. No user information will be saved with the order directly unless manually entered.")
        delivery_address = get_validated_input("Enter delivery address for guest order: ", "not_empty")

    if not delivery_address:
        console.print("[red]Delivery address is required. Checkout cancelled.[/red]")
        return

    if active_cart_restaurant_id is None or active_cart_restaurant_name is None:
        log("Error: Restaurant information for the cart is missing. Cannot proceed with checkout.")
        console.print("[bold red]There was an issue with your cart. Please try adding items again.[/bold red]")
        return

    new_order = create_order(
        user_id=user_id_for_order,
        restaurant_id=active_cart_restaurant_id,
        restaurant_name=active_cart_restaurant_name,
        cart_items=active_cart.items,
        total_amount=total_amount,
        user_address=delivery_address
    )

    if new_order:
        console.print(f"[bold green]Order #{new_order.order_id} placed successfully![/bold green]")
        console.print(track_order(new_order.order_id))
        active_cart.clear_cart()
        active_cart_restaurant_id = None
        active_cart_restaurant_name = None
        log(f"Cart cleared after order {new_order.order_id}.")
    else:
        console.print("[bold red]There was an issue placing your order. Please try again.[/bold red]")

def view_order_history():
    """Displays the order history for the logged-in user using Rich Table."""
    current_user = get_current_user()
    if not current_user:
        console.print("[yellow]You need to be logged in to view order history.[/yellow]")
        return

    console.print()  # Added line break
    log(f"Fetching order history for {current_user.username}...")
    user_orders = get_orders_by_user_id(current_user.user_id)

    if not user_orders:
        console.print("[yellow]You have no past orders.[/yellow]")
        return

    table = Table(title=f"Order History for {current_user.username}", show_header=True, header_style="bold blue")
    table.add_column("Order ID", style="dim", width=10)
    table.add_column("Restaurant", min_width=20)
    table.add_column("Date", min_width=16)
    table.add_column("Total (₹)", justify="right")
    table.add_column("Status")
    table.add_column("Items")
    table.add_column("Address")

    for order in user_orders:
        items_str = "\n".join([f"- {item.name} x{item.quantity} @ ₹{item.price}" for item in order.items])
        table.add_row(
            str(order.order_id),
            order.restaurant_name,
            order.order_date.strftime('%Y-%m-%d %H:%M'),
            f"{order.total_amount:.2f}",
            order.status,
            items_str,
            order.delivery_address
        )
    console.print(table)

def admin_menu(user):
    if not user.is_admin:
        console.print("[red]Access Denied. Admin privileges required.[/red]")
        return

    from admin.actions import (
        view_all_users, view_all_orders, delete_user_by_admin, 
        view_all_restaurants_admin, add_restaurant_admin, 
        edit_restaurant_admin, delete_restaurant_admin,
        manage_restaurant_menu_items_admin, update_order_status_admin, delete_review_admin
    )

    while True:
        console.print()  # Added line break
        console.print("[bold cyan]Admin Panel[/bold cyan]")
        console.print("1. View All Users")
        console.print("2. View All Orders")
        console.print("3. Update Order Status")
        console.print("--- Restaurant Management ---")
        console.print("4. Add New Restaurant")
        console.print("5. Edit Restaurant")
        console.print("6. Delete Restaurant")
        console.print("7. Manage Menu Items for a Restaurant")
        console.print("--- Review Management ---")
        console.print("8. Delete Review")
        console.print("9. Back to Main Menu")

        admin_choice = get_validated_input(
            prompt="Enter your choice: ",
            validation_type="choice",
            options={"choices": ['1', '2', '3', '4', '5', '6', '7', '8', '9']}
        )

        if admin_choice == '1':
            view_all_users(user)
        elif admin_choice == '2':
            view_all_orders(user)
        elif admin_choice == '3':
            update_order_status_admin()
        elif admin_choice == '4':
            add_restaurant_admin(user)
        elif admin_choice == '5':
            edit_restaurant_admin(user)
        elif admin_choice == '6':
            delete_restaurant_admin(user)
        elif admin_choice == '7':
            manage_restaurant_menu_items_admin(user)
        elif admin_choice == '8':
            delete_review_admin()
        elif admin_choice == '9':
            break
        else:
            console.print("[red]Invalid choice. Please try again.[/red]")

def run_app():
    log("App started")
    initialize_database()  # Initialize the database and tables
    initial_data_setup()  # Call to populate sample data (restaurants and reviews)
    global active_cart, active_cart_restaurant_id, active_cart_restaurant_name

    while True:
        current_user = get_current_user()
        cart_item_count = len(active_cart.items)
        cart_total_price = active_cart.get_total_price()
        cart_info = f"(Cart: {cart_item_count} item{'s' if cart_item_count != 1 else ''}, [green]₹{cart_total_price:.2f}[/green])"
        
        console.print()  # Added line break before main welcome/menu
        if current_user:
            console.print(f"Welcome, [bold cyan]{current_user.username}[/bold cyan]! {cart_info}")
            if current_user.is_admin:
                console.print("[bold yellow]Admin user logged in.[/bold yellow]")
                while True:
                    console.print()  # Added line break
                    admin_or_user_choice = get_validated_input(
                        prompt="Go to [1] Admin Panel or [2] User Menu? ",
                        validation_type="choice",
                        options={"choices": ['1', '2']}
                    )
                    if admin_or_user_choice == '1':
                        admin_menu(current_user)
                        console.print()  # Added line break
                        post_admin_choice = get_validated_input(
                            prompt="Go to [1] User Menu or [2] Logout? ",
                            validation_type="choice",
                            options={"choices": ['1', '2']}
                        )
                        if post_admin_choice == '1':
                            break
                        else:
                            log_out()
                            current_user = None
                            break
                    elif admin_or_user_choice == '2':
                        break
            console.print()  # Added line break
            action = get_validated_input(
                prompt="Choose: (1) List Restaurants, (2) View Cart, (3) Order History, (4) Track Order, (5) Logout, (6) Exit: ",
                validation_type="choice",
                options={"choices": ['1', '2', '3', '4', '5', '6']}
            )
            if action == '1':
                all_restaurants = list_restaurants()
                if all_restaurants:
                    select_restaurant_and_actions(all_restaurants)
            elif action == '2':
                display_cart_contents(active_cart, console)
                if active_cart.items:
                    checkout_choice = get_validated_input(
                        prompt="Proceed to checkout? (yes/no): ",
                        validation_type="yes_no"
                    )
                    if checkout_choice in ['yes', 'y']:
                        handle_checkout()
            elif action == '3':
                view_order_history()
            elif action == '4':
                order_id_input = get_validated_input(
                    prompt="Enter your order ID to track: ",
                    validation_type="integer",
                    options={"min_val": 1}
                )
                order_id_to_track = int(order_id_input)
                order_object = get_order_by_id(order_id_to_track)
                if order_object:
                    console.print(f"Order #[bold]{order_object.order_id}[/bold] Status: [yellow]{order_object.status}[/yellow] (via Order object)")
                    console.print(track_order(order_id_to_track))
                else:
                    console.print(f"[red]Order ID {order_id_to_track} not found in our records.[/red]")
            elif action == '5':
                log_out()
                active_cart.clear_cart()
                active_cart_restaurant_id = None
                active_cart_restaurant_name = None
                log("Logged out. Cart has been reset.")
                console.print("[green]Logged out successfully. Your cart has been reset.[/green]")
            elif action == '6':
                break
        else:
            console.print(f"Welcome to Swigato! {cart_info}")
            console.print()  # Added line break
            action = get_validated_input(
                prompt="Choose: (1) Sign Up, (2) Log In, (3) List Restaurants (Guest), (4) View Cart (Guest), (5) Exit: ",
                validation_type="choice",
                options={"choices": ['1', '2', '3', '4', '5']}
            )
            if action == '1':
                username = get_validated_input("Enter username: ", "not_empty")
                password = get_validated_input("Enter password: ", "not_empty", options={"is_password": True})
                address = console.input("Enter address (optional): ")
                new_user = sign_up(username, password, address if address else None)
                if new_user:
                    console.print(f"[green]User {new_user.username} signed up successfully![/green]")
            elif action == '2':
                username = get_validated_input("Enter username: ", "not_empty")
                password = get_validated_input("Enter password: ", "not_empty", options={"is_password": True})
                user = log_in(username, password)
                if user:
                    console.print(f"[green]Logged in as {user.username} successfully![/green]")
                    if user.is_admin:
                        console.print("[bold yellow]Admin user logged in.[/bold yellow]")
                        while True:
                            admin_or_user_choice = get_validated_input(
                                prompt="Go to [1] Admin Panel or [2] User Menu? ",
                                validation_type="choice",
                                options={"choices": ['1', '2']}
                            )
                            if admin_or_user_choice == '1':
                                admin_menu(user)
                                post_admin_choice = get_validated_input(
                                    prompt="Go to [1] User Menu or [2] Logout? ",
                                    validation_type="choice",
                                    options={"choices": ['1', '2']}
                                )
                                if post_admin_choice == '1':
                                    break
                            else:
                                log_out()
                                break
            elif action == '3':
                all_restaurants = list_restaurants()
                if all_restaurants:
                    select_restaurant_and_actions(all_restaurants)
            elif action == '4':
                display_cart_contents(active_cart, console)
                if active_cart.items:
                    checkout_choice = get_validated_input(
                        prompt="Proceed to checkout? (yes/no): ",
                        validation_type="yes_no"
                    )
                    if checkout_choice in ['yes', 'y']:
                        handle_checkout()
            elif action == '5':
                break

    log("App finished")
    console.print("[bold blue]Thank you for using Swigato![/bold blue]")

if __name__ == "__main__":
    run_app()
