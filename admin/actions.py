# filepath: g:\\swigato_project\\admin\\actions.py
from datetime import datetime
from rich.console import Console
from rich.table import Table
from users.models import User
from orders.models import Order
from reviews.models import Review
from restaurants.models import Restaurant, MenuItem
from utils.logger import log
from utils.validation import get_validated_input

console = Console()

def view_all_users(admin_user):
    if not admin_user or not admin_user.is_admin:
        console.print("[red]Permission denied. Admin access required.[/red]")
        return

    users = User.get_all_users()
    if not users:
        console.print("[yellow]No users found in the system.[/yellow]")
        return

    table = Table(title="All Registered Users")
    table.add_column("User ID", style="dim", width=12)
    table.add_column("Username")
    table.add_column("Address")
    table.add_column("Is Admin", justify="center")
    table.add_column("Created At")

    for user in users:
        table.add_row(
            str(user.user_id),
            user.username,
            user.address if user.address else "N/A",
            "Yes" if user.is_admin else "No",
            str(user.created_at)
        )
    console.print(table)
    log(f"Admin '{admin_user.username}' viewed all users.")

def view_all_orders(admin_user):
    if not admin_user or not admin_user.is_admin:
        console.print("[red]Permission denied. Admin access required.[/red]")
        return

    all_orders = Order.get_all_orders()
    if not all_orders:
        console.print("[yellow]No orders found in the system.[/yellow]")
        return

    table = Table(title="All Orders")
    table.add_column("Order ID", style="dim")
    table.add_column("User ID")
    table.add_column("Username")
    table.add_column("Restaurant Name")
    table.add_column("Total Amount", justify="right")
    table.add_column("Status")
    table.add_column("Order Date")

    for order in all_orders:
        customer_username = "N/A"
        if order.user_id:
            customer = User.get_by_id(order.user_id)
            if customer:
                customer_username = customer.username
        
        table.add_row(
            str(order.order_id),
            str(order.user_id) if order.user_id else "Guest",
            customer_username,
            order.restaurant_name,
            f"{order.total_amount:.2f}",
            order.status,
            order.order_date.strftime("%Y-%m-%d %H:%M:%S") if order.order_date else "N/A"
        )
    console.print(table)
    log(f"Admin '{admin_user.username}' viewed all orders.")

def update_order_status_admin():
    """Allows admin to update the status of an order."""
    console.print("\n[bold cyan]Update Order Status[/bold cyan]")
    orders = Order.get_all_orders()
    if not orders:
        console.print("[yellow]No orders available to update.[/yellow]")
        return

    console.print("\n[bold]Available Orders:[/bold]")
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Order ID", style="dim")
    table.add_column("User ID")
    table.add_column("Restaurant Name")
    table.add_column("Total Amount")
    table.add_column("Status")
    table.add_column("Order Date")

    for order in orders:
        table.add_row(
            str(order.order_id),
            str(order.user_id),
            order.restaurant_name,
            f"${order.total_amount:.2f}",
            order.status,
            order.order_date.strftime('%Y-%m-%d %H:%M') if isinstance(order.order_date, datetime) else order.order_date
        )
    console.print(table)

    order_id = get_validated_input(
        prompt="Enter the ID of the order to update status: ",
        validation_type="integer",
        custom_error_message="Invalid Order ID format. Please enter a number."
    )
    if order_id is None:
        return

    # Ensure both o.order_id and order_id are compared as integers
    selected_order = next((o for o in orders if int(o.order_id) == int(order_id)), None)

    if not selected_order:
        console.print(f"[red]Order with ID {order_id} not found.[/red]")
        return

    console.print(f"Current status of order {order_id}: [yellow]{selected_order.status}[/yellow]")
    new_status = get_validated_input(
        prompt="Enter the new status (e.g., Processing, Shipped, Delivered, Cancelled): ",
        validation_type="not_empty",
        custom_error_message="Status cannot be empty."
    )
    if not new_status:
        return

    if Order.update_status(order_id, new_status):
        console.print(f"[green]Order {order_id} status updated to {new_status} successfully![/green]")
        log(f"Admin updated order {order_id} status to {new_status}.")
    else:
        console.print(f"[red]Failed to update status for order {order_id}.[/red]")

def delete_review_admin():
    """Allows admin to delete a review."""
    console.print("\n[bold cyan]Delete a Review[/bold cyan]")
    reviews = Review.get_all_reviews()
    if not reviews:
        console.print("[yellow]No reviews available to delete.[/yellow]")
        return

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Review ID", style="dim")
    table.add_column("User")
    table.add_column("Restaurant")
    table.add_column("Rating")
    table.add_column("Comment")
    table.add_column("Date")

    for review in reviews:
        date_display = ""
        if isinstance(review.review_date, datetime):
            date_display = review.review_date.strftime('%Y-%m-%d %H:%M')
        elif review.review_date is not None:
            date_display = str(review.review_date)

        table.add_row(
            str(review.review_id),
            review.username,
            review.restaurant_name,
            str(review.rating),
            review.comment,
            date_display
        )
    console.print(table)

    review_id = get_validated_input(
        prompt="Enter the ID of the review to delete: ",
        validation_type="integer",
        custom_error_message="Invalid Review ID format. Please enter a number."
    )
    if review_id is None:
        return

    confirm = get_validated_input(
        prompt=f"Are you sure you want to delete review {review_id}? (yes/no): ",
        validation_type="yes_no",
        custom_error_message="Please enter 'yes' or 'no'."
    )

    if confirm == 'yes':
        if Review.delete_review(review_id):
            console.print(f"[green]Review {review_id} deleted successfully![/green]")
            log(f"Admin deleted review {review_id}.")
        else:
            console.print(f"[red]Failed to delete review {review_id}. It might not exist.[/red]")
    else:
        console.print("[yellow]Review deletion cancelled.[/yellow]")

def delete_user_by_admin(admin_user, username_to_delete):
    if not admin_user or not admin_user.is_admin:
        console.print("[red]Permission denied. Admin access required.[/red]")
        return False

    user_to_delete = User.get_by_username(username_to_delete)
    if not user_to_delete:
        console.print(f"[yellow]User '{username_to_delete}' not found.[/yellow]")
        return False
    
    if user_to_delete.is_admin and user_to_delete.username == admin_user.username:
        console.print("[red]Admin users cannot delete themselves.[/red]")
        return False

    if User.delete_by_username(username_to_delete):
        console.print(f"[green]User '{username_to_delete}' and their associated data (reviews) deleted successfully.[/green]")
        log(f"Admin '{admin_user.username}' deleted user '{username_to_delete}'.")
        return True
    else:
        console.print(f"[red]Failed to delete user '{username_to_delete}'. Check logs.[/red]")
        return False

def view_all_restaurants_admin(admin_user):
    if not admin_user or not admin_user.is_admin:
        console.print("[red]Permission denied. Admin access required.[/red]")
        return
    restaurants = Restaurant.get_all()
    if not restaurants:
        console.print("[yellow]No restaurants found.[/yellow]")
        return
    table = Table(title="All Restaurants")
    table.add_column("ID", style="dim")
    table.add_column("Name")
    table.add_column("Cuisine")
    table.add_column("Address")
    for r in restaurants:
        table.add_row(str(r.restaurant_id), r.name, r.cuisine_type, r.address)
    console.print(table)
    log(f"Admin '{admin_user.username}' viewed all restaurants.")

def add_restaurant_admin(admin_user):
    if not admin_user or not admin_user.is_admin:
        console.print("[red]Permission denied. Admin access required.[/red]")
        return

    console.print("\n[bold]Add New Restaurant[/bold]")
    name = get_validated_input(
        prompt="Enter restaurant name: ",
        validation_type="non_empty_string",
        custom_error_message="Restaurant name cannot be empty."
    )
    if not name: return

    cuisine_type = get_validated_input(
        prompt="Enter cuisine type: ",
        validation_type="non_empty_string",
        custom_error_message="Cuisine type cannot be empty."
    )
    if not cuisine_type: return

    address = get_validated_input(
        prompt="Enter address: ",
        validation_type="non_empty_string",
        custom_error_message="Address cannot be empty."
    )
    if not address: return

    new_restaurant = Restaurant.create(name, cuisine_type, address)
    if new_restaurant:
        console.print(f"[green]Restaurant '{new_restaurant.name}' added successfully with ID {new_restaurant.restaurant_id}.[/green]")
        log(f"Admin '{admin_user.username}' added new restaurant: {new_restaurant.name}")
    else:
        console.print("[red]Failed to add restaurant. Check logs for details.[/red]")

def edit_restaurant_admin(admin_user):
    if not admin_user or not admin_user.is_admin:
        console.print("[red]Permission denied. Admin access required.[/red]")
        return

    view_all_restaurants_admin(admin_user)
    restaurant_id = get_validated_input(
        prompt="Enter ID of the restaurant to edit (or 0 to cancel): ",
        validation_type="integer_or_cancel",
        custom_error_message="Invalid ID. Please enter a number or 0 to cancel.",
        cancel_value=0
    )
    if restaurant_id is None or restaurant_id == 0:
        if restaurant_id == 0: console.print("[yellow]Edit restaurant cancelled.[/yellow]")
        return
    
    restaurant_to_edit = Restaurant.get_by_id(restaurant_id)

    if not restaurant_to_edit:
        console.print(f"[red]Restaurant with ID {restaurant_id} not found.[/red]")
        return

    console.print(f"\n[bold]Editing Restaurant: {restaurant_to_edit.name}[/bold] (ID: {restaurant_id})")
    
    new_name = get_validated_input(
        prompt=f"Enter new name (current: {restaurant_to_edit.name}): ",
        validation_type="optional_string",
        default_value=restaurant_to_edit.name
    )
    
    new_cuisine_type = get_validated_input(
        prompt=f"Enter new cuisine type (current: {restaurant_to_edit.cuisine_type}): ",
        validation_type="optional_string",
        default_value=restaurant_to_edit.cuisine_type
    )

    new_address = get_validated_input(
        prompt=f"Enter new address (current: {restaurant_to_edit.address}): ",
        validation_type="optional_string",
        default_value=restaurant_to_edit.address
    )

    if restaurant_to_edit.update(name=new_name, cuisine_type=new_cuisine_type, address=new_address):
        console.print(f"[green]Restaurant '{new_name}' updated successfully.[/green]")
        log(f"Admin '{admin_user.username}' edited restaurant ID {restaurant_id}.")
    else:
        console.print("[red]Failed to update restaurant. Check logs for details.[/red]")

def delete_restaurant_admin(admin_user):
    if not admin_user or not admin_user.is_admin:
        console.print("[red]Permission denied. Admin access required.[/red]")
        return

    view_all_restaurants_admin(admin_user)
    restaurant_id = get_validated_input(
        prompt="Enter ID of the restaurant to DELETE (or 0 to cancel): ",
        validation_type="integer_or_cancel",
        custom_error_message="Invalid ID. Please enter a number or 0 to cancel.",
        cancel_value=0
    )
    if restaurant_id is None or restaurant_id == 0:
        if restaurant_id == 0: console.print("[yellow]Restaurant deletion cancelled.[/yellow]")
        return
    
    restaurant_to_delete = Restaurant.get_by_id(restaurant_id)

    if not restaurant_to_delete:
        console.print(f"[red]Restaurant with ID {restaurant_id} not found.[/red]")
        return

    confirm = get_validated_input(
        prompt=f"[bold red]Are you sure you want to delete '{restaurant_to_delete.name}' (ID: {restaurant_id})? This will also delete all its menu items and reviews. (yes/no): [/bold red]",
        validation_type="yes_no",
        custom_error_message="Please enter 'yes' or 'no'."
    )

    if confirm == 'yes':
        if restaurant_to_delete.delete():
            console.print(f"[green]Restaurant '{restaurant_to_delete.name}' and all associated data deleted successfully.[/green]")
            log(f"Admin '{admin_user.username}' deleted restaurant ID {restaurant_id} ('{restaurant_to_delete.name}').")
        else:
            console.print("[red]Failed to delete restaurant. Check logs for details.[/red]")
    else:
        console.print("[yellow]Restaurant deletion cancelled.[/yellow]")

def manage_restaurant_menu_items_admin(admin_user):
    if not admin_user or not admin_user.is_admin:
        console.print("[red]Permission denied. Admin access required.[/red]")
        return

    view_all_restaurants_admin(admin_user)
    restaurant_id = get_validated_input(
        prompt="Enter ID of the restaurant whose menu you want to manage (or 0 to cancel): ",
        validation_type="integer_or_cancel",
        custom_error_message="Invalid ID. Please enter a number or 0 to cancel.",
        cancel_value=0
    )
    if restaurant_id is None or restaurant_id == 0:
        if restaurant_id == 0: console.print("[yellow]Menu management cancelled.[/yellow]")
        return
    
    selected_restaurant = Restaurant.get_by_id(restaurant_id)

    if not selected_restaurant:
        console.print(f"[red]Restaurant with ID {restaurant_id} not found.[/red]")
        return

    while True:
        console.print(f"\n[bold cyan]Managing Menu for: {selected_restaurant.name}[/bold cyan]")
        selected_restaurant.display_menu(console)
        console.print("\nMenu Item Actions:")
        console.print("1. Add New Menu Item")
        console.print("2. Edit Menu Item")
        console.print("3. Delete Menu Item")
        console.print("0. Back to Admin Panel")
        
        choice = get_validated_input(
            prompt="Choose an action: ",
            validation_type="integer_range",
            custom_error_message="Invalid choice. Please enter a number between 0 and 3.",
            min_value=0,
            max_value=3
        )
        if choice is None:
            continue

        if choice == 1:
            add_menu_item_admin(admin_user, selected_restaurant)
        elif choice == 2:
            edit_menu_item_admin(admin_user, selected_restaurant)
        elif choice == 3:
            delete_menu_item_admin(admin_user, selected_restaurant)
        elif choice == 0:
            break

def add_menu_item_admin(admin_user, restaurant: Restaurant):
    console.print(f"\n[bold]Add New Menu Item to {restaurant.name}[/bold]")
    name = get_validated_input(
        prompt="Enter item name: ",
        validation_type="non_empty_string",
        custom_error_message="Item name cannot be empty."
    )
    if not name: return

    description = get_validated_input(
        prompt="Enter item description: ",
        validation_type="non_empty_string",
        custom_error_message="Description cannot be empty."
    )
    if not description: return

    price = get_validated_input(
        prompt="Enter item price: ",
        validation_type="float_positive",
        custom_error_message="Invalid price. Please enter a positive number."
    )
    if price is None: return

    category = get_validated_input(
        prompt="Enter item category (e.g., Main Course, Appetizer, Drinks): ",
        validation_type="non_empty_string",
        custom_error_message="Category cannot be empty."
    )
    if not category: return

    new_item = MenuItem.create(restaurant.restaurant_id, name, description, price, category)
    if new_item:
        console.print(f"[green]Menu item '{new_item.name}' added successfully to {restaurant.name}.[/green]")
        log(f"Admin '{admin_user.username}' added menu item '{new_item.name}' to restaurant ID {restaurant.restaurant_id}.")
    else:
        console.print("[red]Failed to add menu item. Check logs.[/red]")

def edit_menu_item_admin(admin_user, restaurant: Restaurant):
    console.print(f"\n[bold]Menu Items for {restaurant.name}:[/bold]")
    restaurant.display_menu(console)

    item_id = get_validated_input(
        prompt="Enter ID of the menu item to edit (or 0 to cancel): ",
        validation_type="integer_or_cancel",
        custom_error_message="Invalid ID. Please enter a number or 0 to cancel.",
        cancel_value=0
    )
    if item_id is None or item_id == 0:
        if item_id == 0: console.print("[yellow]Edit menu item cancelled.[/yellow]")
        return
        
    menu_item_to_edit = MenuItem.get_by_id(item_id)

    if not menu_item_to_edit or menu_item_to_edit.restaurant_id != restaurant.restaurant_id:
        console.print(f"[red]Menu item with ID {item_id} not found in {restaurant.name}.[/red]")
        return

    console.print(f"\n[bold]Editing Menu Item: {menu_item_to_edit.name}[/bold] (ID: {item_id})")
    console.print(f"Current Name: {menu_item_to_edit.name}")
    new_name = get_validated_input(
        prompt="Enter new name (or press Enter to keep current): ",
        validation_type="optional_string",
        default_value=menu_item_to_edit.name
    )

    console.print(f"Current Description: {menu_item_to_edit.description}")
    new_description = get_validated_input(
        prompt="Enter new description (or press Enter to keep current): ",
        validation_type="optional_string",
        default_value=menu_item_to_edit.description
    )

    console.print(f"Current Price: {menu_item_to_edit.price}")
    new_price = get_validated_input(
        prompt="Enter new price (or press Enter to keep current): ",
        validation_type="optional_float_positive",
        custom_error_message="Invalid price. Must be a positive number.",
        default_value=menu_item_to_edit.price
    )
    
    console.print(f"Current Category: {menu_item_to_edit.category}")
    new_category = get_validated_input(
        prompt="Enter new category (or press Enter to keep current): ",
        validation_type="optional_string",
        default_value=menu_item_to_edit.category
    )

    if menu_item_to_edit.update(name=new_name, description=new_description, price=new_price, category=new_category):
        console.print(f"[green]Menu item '{new_name}' updated successfully.[/green]")
        log(f"Admin '{admin_user.username}' edited menu item ID {item_id} in restaurant ID {restaurant.restaurant_id}.")
    else:
        console.print("[red]Failed to update menu item. Check logs.[/red]")

def delete_menu_item_admin(admin_user, restaurant: Restaurant):
    console.print(f"\n[bold]Menu Items for {restaurant.name}:[/bold]")
    restaurant.display_menu(console)

    item_id = get_validated_input(
        prompt="Enter ID of the menu item to DELETE (or 0 to cancel): ",
        validation_type="integer_or_cancel",
        custom_error_message="Invalid ID. Please enter a number or 0 to cancel.",
        cancel_value=0
    )
    if item_id is None or item_id == 0:
        if item_id == 0: console.print("[yellow]Menu item deletion cancelled.[/yellow]")
        return

    menu_item_to_delete = MenuItem.get_by_id(item_id)

    if not menu_item_to_delete or menu_item_to_delete.restaurant_id != restaurant.restaurant_id:
        console.print(f"[red]Menu item with ID {item_id} not found in {restaurant.name}.[/red]")
        return

    confirm = get_validated_input(
        prompt=f"[bold red]Are you sure you want to delete '{menu_item_to_delete.name}' (ID: {item_id}) from {restaurant.name}? (yes/no): [/bold red]",
        validation_type="yes_no",
        custom_error_message="Please enter 'yes' or 'no'."
    )
    if confirm == 'yes':
        if menu_item_to_delete.delete():
            console.print(f"[green]Menu item '{menu_item_to_delete.name}' deleted successfully from {restaurant.name}.[/green]")
            log(f"Admin '{admin_user.username}' deleted menu item ID {item_id} ('{menu_item_to_delete.name}') from restaurant ID {restaurant.restaurant_id}.")
        else:
            console.print("[red]Failed to delete menu item. Check logs.[/red]")
    else:
        console.print("[yellow]Menu item deletion cancelled.[/yellow]")
