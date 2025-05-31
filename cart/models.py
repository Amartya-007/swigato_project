from utils.logger import log
from rich.table import Table
from rich.text import Text

class CartItem:
    def __init__(self, menu_item, quantity):
        self.menu_item = menu_item # This will be a MenuItem object
        self.quantity = quantity

    def __repr__(self):
        return f"<CartItem: {self.menu_item.name} x{self.quantity}>"

    @property
    def item_total(self):
        return self.menu_item.price * self.quantity

class Cart:
    def __init__(self, user_id=None): # user_id can be None for guest carts
        self.user_id = user_id
        self.items = {} # Using a dictionary for easier quantity updates: {item_id: CartItem}

    def add_item(self, menu_item, quantity=1):
        if quantity <= 0:
            log("Quantity must be positive.")
            return False

        if menu_item.item_id in self.items:
            self.items[menu_item.item_id].quantity += quantity
            log(f"Updated quantity for {menu_item.name} to {self.items[menu_item.item_id].quantity}.")
        else:
            self.items[menu_item.item_id] = CartItem(menu_item, quantity)
            log(f"Added {quantity} of {menu_item.name} to cart.")
        return True

    def remove_item(self, item_id, quantity=None):
        if item_id not in self.items:
            log(f"Item ID {item_id} not found in cart.")
            return False

        if quantity is None or quantity >= self.items[item_id].quantity:
            # Remove all quantity or if quantity to remove is more than available
            del self.items[item_id]
            log(f"Removed item ID {item_id} from cart.")
        else:
            self.items[item_id].quantity -= quantity
            log(f"Reduced quantity for item ID {item_id} by {quantity}. New quantity: {self.items[item_id].quantity}.")
        return True

    def get_total_price(self):
        return sum(item.item_total for item in self.items.values())

    def clear_cart(self):
        self.items = {}
        log("Cart cleared.")

    def __repr__(self):
        return f"<Cart (User: {self.user_id if self.user_id else 'Guest'}) - Items: {len(self.items)}, Total: ₹{self.get_total_price()}>"

# --- Cart Management Functions (could be expanded) ---

# For simplicity, we might have a global current cart in main.py or pass cart objects around.
# These functions operate on a passed cart object.

def add_item_to_cart(cart, menu_item, quantity=1):
    return cart.add_item(menu_item, quantity)

def remove_item_from_cart(cart, item_id, quantity=None):
    return cart.remove_item(item_id, quantity)

def view_cart(cart, console): # Add console parameter
    """Displays the shopping cart contents using Rich Table."""
    table = Table(title="Your Shopping Cart", show_header=True, header_style="bold green")
    table.add_column("#", style="dim", width=3)
    table.add_column("Item Name", min_width=20)
    table.add_column("Item ID", width=10)
    table.add_column("Unit Price (₹)", justify="right")
    table.add_column("Quantity", justify="center")
    table.add_column("Total Price (₹)", justify="right")

    if not cart.items:
        console.print(Text("Your cart is empty.", style="yellow"))
    else:
        for i, cart_item in enumerate(cart.items.values()):
            table.add_row(
                str(i + 1),
                cart_item.menu_item.name,
                str(cart_item.menu_item.item_id),
                f"{cart_item.menu_item.price:.2f}",
                str(cart_item.quantity),
                f"{cart_item.item_total:.2f}"
            )
        console.print(table)
    
    console.print(f"Total Cart Value: [bold green]₹{cart.get_total_price():.2f}[/bold green]")

def get_current_cart(user_id=None):
    # In a more complex app, this might fetch/create a cart from a DB based on user_id
    # For now, we assume a cart object is managed elsewhere (e.g., in main.py)
    # This function is more of a placeholder for future expansion.
    log("get_current_cart called. Cart management is currently session-based in main.py.")
    return Cart(user_id) # Returns a new empty cart, assuming main handles the active one
