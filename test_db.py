# Store the order details in the database
from datetime import datetime
from sqlalchemy.orm import Session
from database import Order, SessionLocal


PIZZA_TYPES = ["margherita", "supreme", "pesto and sun-dried tomato", "pepperoni", "seafood", "bbq chicken"]
VEGETARIAN_PIZZA_TYPES = ["margherita", "supreme", "pesto and sun-dried tomato"]
NON_VEGETARIAN_PIZZA_TYPES = ["pepperoni", "bbq chicken", "seafood"]

PIZZA_SIZES = {"small": 8, "medium": 12, "large": 16}
PIZZA_QUANTITY = ["one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"]
PIZZA_QUANTITY_ABBR = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]

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

RESTAURANT_PHONE_NUMBER = "+XX-XXX-XXX-XXXX"
RESTAURANT_OPENING_HOURS = {
    "Opening": "12:00 PM",
    "Closing": "11:59 PM"
}

AVAILABLE_POSSIBLE_TOPPINGS = [
    "mozzarella cheese",
    "feta cheese",
    "tomato sauce"
    "pesto sauce",
    "bbq sauce",
    "grilled chicken",
    "tomatoes",
    "sun-dried tomatoes",
    "spinach",
    "basil leaves",
    "pepperoni slices",
    "mushrooms",
    "onions",
    "red onions",
    "olives",
    "prosciutto",
    "artichokes",
    "anchovies",
    "bell peppers",
    "cilantro",
    "shrimp",
    "mussels",
    "clams"
]

# db: Session = SessionLocal()

# try:
#     new_order = Order(
#         order_number=str(order_number),
#         order_list=order_list,
#         total_price=total_price,
#         preparation_time=order_preparation_time,
#         pickup_time=datetime.strptime(order_pickup_time, "%Y-%m-%d %H:%M")
#     )
#     db.add(new_order)
#     db.commit()
# except Exception as e:
#     db.rollback()
#     print(f"An error occurred: {e}")
# finally:
#     db.close()

# connect to the database
db: Session = SessionLocal()

# get all the orders from the database
orders = db.query(Order).all()
print(len(orders))

from collections import defaultdict


def process_orders(orders):
    vegetarian_pizzas = defaultdict(int)
    non_vegetarian_pizzas = defaultdict(int)

    VEGETARIAN_PIZZA_TYPES = ["margherita", "supreme", "pesto and sun-dried tomato"]
    NON_VEGETARIAN_PIZZA_TYPES = ["pepperoni", "bbq chicken", "seafood"]

    for order in orders:
        for pizza in order.order_list:
            pizza_type = pizza['type']
            pizza_toppings = tuple(sorted(pizza['topping']))

            # convert the quantity to a number using the index from the PIZZA_QUANTITY list
            quantity = PIZZA_QUANTITY.index(pizza['quantity']) + 1

            pizza_key = (pizza_type, pizza_toppings)

            if pizza_type in VEGETARIAN_PIZZA_TYPES:
                vegetarian_pizzas[pizza_key] += quantity
            elif pizza_type in NON_VEGETARIAN_PIZZA_TYPES:
                non_vegetarian_pizzas[pizza_key] += quantity

    return vegetarian_pizzas, non_vegetarian_pizzas


def get_top_pizzas_with_toppings(pizzas_dict, top_n=2):
    sorted_pizzas = sorted(pizzas_dict.items(), key=lambda x: x[1], reverse=True)
    return sorted_pizzas[:top_n]


def veg_pizza_recommendation(vegetarian_pizzas):
    # get the top vegetarian pizzas
    top_vegetarian_pizzas = get_top_pizzas_with_toppings(vegetarian_pizzas)
    recommendation_1 = {top_vegetarian_pizzas[0][0][0]: list(top_vegetarian_pizzas[0][0][1])}
    recommendation_2 = {top_vegetarian_pizzas[1][0][0]: list(top_vegetarian_pizzas[1][0][1])}

    return recommendation_1, recommendation_2


def non_veg_pizza_recommendation(non_vegetarian_pizzas):
    # get the top non-vegetarian pizzas
    top_non_vegetarian_pizzas = get_top_pizzas_with_toppings(non_vegetarian_pizzas)

    recommendation_1 = {top_non_vegetarian_pizzas[0][0][0]: list(top_non_vegetarian_pizzas[0][0][1])}
    recommendation_2 = {top_non_vegetarian_pizzas[1][0][0]: list(top_non_vegetarian_pizzas[1][0][1])}

    return recommendation_1, recommendation_2

vegetarian_pizzas, non_vegetarian_pizzas = process_orders(orders)
print("Top 2 Vegetarian Pizzas:")
vegetarian_pizzas_recommendations = veg_pizza_recommendation(vegetarian_pizzas)
for recommendation in vegetarian_pizzas_recommendations:
    print(recommendation)

print("\nTop 2 Non-Vegetarian Pizzas:")
non_vegetarian_pizzas_recommendations = non_veg_pizza_recommendation(non_vegetarian_pizzas)
for recommendation in non_vegetarian_pizzas_recommendations:
    print(recommendation)
