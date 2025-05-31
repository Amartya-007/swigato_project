from rich.text import Text

def track_order(order_id):
    # Simulate different order statuses based on order_id
    if order_id % 4 == 0:
        status = Text("Order Confirmed", style="bold blue")
    elif order_id % 4 == 1:
        status = Text("Preparing Food", style="bold yellow")
    elif order_id % 4 == 2:
        status = Text("Out for Delivery 🛵", style="bold orange3")
    else:
        status = Text("Delivered! Enjoy your meal! 🎉", style="bold green")
    
    base_text = Text(f"Order #{order_id}: ")
    base_text.append(status)
    return base_text
