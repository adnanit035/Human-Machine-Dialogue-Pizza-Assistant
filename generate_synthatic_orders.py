import random
from datetime import datetime, timedelta
from datetime import datetime
from sqlalchemy.orm import Session
from database import Order, SessionLocal

PIZZA_TYPES = ["margherita", "supreme", "pesto and sun-dried tomato", "pepperoni", "seafood", "bbq chicken"]
VEGETARIAN_PIZZA_TYPES = ["margherita", "supreme", "pesto and sun-dried tomato"]
NON_VEGETARIAN_PIZZA_TYPES = ["pepperoni", "bbq chicken", "seafood"]

PIZZA_SIZES = {"small": 8, "medium": 12, "large": 16}
PIZZA_QUANTITY = ["one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"]

PIZZA_TOPPINGS_STD = {
    "margherita": ["Mozzarella Cheese", "Tomato Sauce", "Basil Leaves"],
    "supreme": ["Mushrooms", "Bell Peppers", "Onions", "Olives", "Tomatoes"],
    "pesto and sun-dried tomato": ["Pesto Sauce", "Sun-dried Tomatoes", "Feta Cheese", "Spinach"],
    "pepperoni": ["Pepperoni Slices", "Mozzarella Cheese", "Tomato Sauce"],
    "bbq chicken": ["BBQ Sauce", "Grilled Chicken", "Red Onions", "Cilantro", "Mozzarella Cheese"],
    "seafood": ["Shrimp", "Mussels", "Clams", "Tomato Sauce", "Mozzarella Cheese"]
}

PIZZA_PRICES = {
    "margherita": {"small": 9.99, "medium": 12.99, "large": 15.99},
    "supreme": {"small": 11.99, "medium": 14.99, "large": 17.99},
    "pesto and sun-dried tomato": {"small": 10.99, "medium": 13.99, "large": 16.99},
    "pepperoni": {"small": 10.99, "medium": 13.99, "large": 16.99},
    "bbq chicken": {"small": 12.99, "medium": 15.99, "large": 18.99},
    "seafood": {"small": 13.99, "medium": 16.99, "large": 19.99}
}

PIZZA_PREPARATION_TIME = {
    "small": 7,  # in minutes
    "medium": 10,
    "large": 15
}


def generate_synthetic_order(order_number: int):
    num_items = random.randint(1, 5)  # Randomly decide how many items in the order
    order_list = []
    total_price = 0
    max_preparation_time = 0

    for _ in range(num_items):
        pizza_type = random.choice(PIZZA_TYPES)
        size = random.choice(list(PIZZA_SIZES.keys()))
        quantity = random.choice(PIZZA_QUANTITY)
        # Convert quantity string to number using the index of the quantity in the list
        quantity_num = PIZZA_QUANTITY.index(quantity) + 1
        toppings = PIZZA_TOPPINGS_STD[pizza_type]

        price_per_pizza = PIZZA_PRICES[pizza_type][size]
        item_total_price = price_per_pizza * quantity_num
        total_price += item_total_price

        preparation_time = PIZZA_PREPARATION_TIME[size] * quantity_num
        max_preparation_time = max(max_preparation_time, preparation_time)

        order_list.append({
            "type": pizza_type,
            "size": size,
            "topping": toppings,
            "quantity": quantity,
            "price": item_total_price
        })

    # Simulate a pickup time within the next 4 hours
    pickup_time = datetime.now() + timedelta(minutes=random.randint(30, 240))
    pickup_time_str = pickup_time.strftime('%Y-%m-%d %H:%M')

    order_data = {
        'order_number': order_number,
        'order_list': order_list,
        'total_price': total_price,
        'preparation_time': max_preparation_time,
        'pickup_time': pickup_time_str
    }

    return order_data


# Generate 100 synthetic orders
synthetic_orders = [generate_synthetic_order(i + 72423) for i in range(100)]

db: Session = SessionLocal()

for order in synthetic_orders:
    print(order)
    order_number = order['order_number']
    order_list = order['order_list']
    total_price = order['total_price']
    order_preparation_time = order['preparation_time']
    order_pickup_time = order['pickup_time']
    try:
        new_order = Order(
            order_number=str(order_number),
            order_list=order_list,
            total_price=total_price,
            preparation_time=order_preparation_time,
            pickup_time=datetime.strptime(order_pickup_time, "%Y-%m-%d %H:%M")
        )
        db.add(new_order)
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"An error occurred: {e}")
    finally:
        db.close()
