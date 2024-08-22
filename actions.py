import random
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, Text, Any, List, Optional

from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.events import SlotSet, FollowupAction, ActiveLoop, AllSlotsReset
from rasa_sdk.executor import CollectingDispatcher
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

RESTAURANT_DETAILS = {
    "name": "The Champ's Pizza",
    "address": "1234 Pizza Street, Pizza City",
    "phone_number": "+XX-XXX-XXX-XXXX",
    "opening_hours": {
        "Opening": "12:00 PM",
        "Closing": "11:59 PM"
    },
    "final_order_time": "11:59 PM"
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


def process_orders(orders):
    vegetarian_pizzas = defaultdict(int)
    non_vegetarian_pizzas = defaultdict(int)

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


def generate_pizza_menu():
    menu = " Here's Our Menu :\n\n"

    menu += "- Vegetarian Pizzas:\n"
    for pizza_type in VEGETARIAN_PIZZA_TYPES:
        menu += f"  - {pizza_type.capitalize()}: {', '.join(PIZZA_TOPPINGS_STD[pizza_type])}. "
        menu += f"Price: ${PIZZA_PRICES[pizza_type]['medium']} (Medium)\n"

    menu += "\n- Non-Vegetarian Pizzas:\n"
    for pizza_type in NON_VEGETARIAN_PIZZA_TYPES:
        menu += f"  - {pizza_type.capitalize()}: {', '.join(PIZZA_TOPPINGS_STD[pizza_type])}. "
        menu += f"Price: ${PIZZA_PRICES[pizza_type]['medium']} (Medium)\n"

    menu += "\n-------------------------------------------\n"

    return menu


def generate_vegetarian_pizza_menu():
    # menu = " Here's Our Vegetarian Pizza Menu :\n\n"
    #
    # menu += "- Vegetarian Pizzas:\n"
    # for pizza_type in VEGETARIAN_PIZZA_TYPES:
    #     menu += f"  - {pizza_type.capitalize()}: {', '.join(PIZZA_TOPPINGS_STD[pizza_type])}. "
    #     menu += f"Price: ${PIZZA_PRICES[pizza_type]['medium']} (Medium)\n"
    #
    # menu += "\n-------------------------------------------\n"
    #
    # return menu
    menu = " Our Vegetarian Pizza are: "

    menu += ""
    for pizza_type in VEGETARIAN_PIZZA_TYPES:
        menu += f" {pizza_type.capitalize()}, "

    menu += "."

    return menu


def generate_non_vegetarian_pizza_menu():
    menu = " Here's Our Non-Vegetarian Pizza Menu :\n\n"

    menu += "- Non-Vegetarian Pizzas:\n"
    for pizza_type in NON_VEGETARIAN_PIZZA_TYPES:
        menu += f"  - {pizza_type.capitalize()}: {', '.join(PIZZA_TOPPINGS_STD[pizza_type])}. "
        menu += f"Price: ${PIZZA_PRICES[pizza_type]['medium']} (Medium)\n"

    menu += "\n-------------------------------------------\n"

    return menu


def generate_pizza_sizes():
    # sizes = " We offer the following sizes for our pizzas:\n\n"
    #
    # for size in PIZZA_SIZES.keys():
    #     sizes += f"  - {size.capitalize()}: {PIZZA_SIZES[size]} inches\n"
    #
    # return sizes
    sizes = " We offer the following sizes for our pizzas:"

    for size in PIZZA_SIZES.keys():
        sizes += f" {size.capitalize()}, "

    return sizes


def generate_recommended_pizzas_menu():
    # get the current session
    session = SessionLocal()

    # get all the orders from the database
    orders = session.query(Order).all()

    # process the orders to get the vegetarian and non-vegetarian pizzas
    vegetarian_pizzas, non_vegetarian_pizzas = process_orders(orders)

    # get the top recommended pizzas
    veg_recommendation_1, veg_recommendation_2 = veg_pizza_recommendation(vegetarian_pizzas)
    non_veg_recommendation_1, non_veg_recommendation_2 = non_veg_pizza_recommendation(non_vegetarian_pizzas)

    # close the session
    session.close()

    # first recommended veg pizza
    pizza_type = list(veg_recommendation_1.keys())[0]
    toppings = list(veg_recommendation_1.values())[0]
    price_medium = PIZZA_PRICES[pizza_type]['medium']

    # generate the recommended pizzas menu
    menu = " Here's Our Recommended Pizzas Menu :\n"
    menu += "  (Based on Our Customers' Most Buying)\n\n"

    menu += "- Recommended Vegetarian Pizzas:\n"
    menu += f"  - {pizza_type.capitalize()}: {', '.join(toppings)}. Price: ${price_medium} (Medium)\n"

    # second recommended veg pizza
    pizza_type = list(veg_recommendation_2.keys())[0]
    toppings = list(veg_recommendation_2.values())[0]
    price_medium = PIZZA_PRICES[pizza_type]['medium']

    menu += f"  - {pizza_type.capitalize()}: {', '.join(toppings)}. Price: ${price_medium} (Medium)\n"

    # first recommended non-veg pizza
    pizza_type = list(non_veg_recommendation_1.keys())[0]
    toppings = list(non_veg_recommendation_1.values())[0]
    price_medium = PIZZA_PRICES[pizza_type]['medium']

    menu += "\n- Recommended Non-Vegetarian Pizzas:\n"
    menu += f"  - {pizza_type.capitalize()}: {', '.join(toppings)}. Price: ${price_medium} (Medium)\n"

    # second recommended non-veg pizza
    pizza_type = list(non_veg_recommendation_2.keys())[0]
    toppings = list(non_veg_recommendation_2.values())[0]
    price_medium = PIZZA_PRICES[pizza_type]['medium']

    menu += f"  - {pizza_type.capitalize()}: {', '.join(toppings)}. Price: ${price_medium} (Medium)\n"

    menu += "\n-------------------------------------------\n"

    return menu


def generate_recommended_vegetarian_pizzas_menu():
    # get the current session
    session = SessionLocal()

    # get all the orders from the database
    orders = session.query(Order).all()

    # process the orders to get the vegetarian and non-vegetarian pizzas
    vegetarian_pizzas, _ = process_orders(orders)

    # get the top recommended pizzas
    veg_recommendation_1, veg_recommendation_2 = veg_pizza_recommendation(vegetarian_pizzas)

    # close the session
    session.close()

    # first recommended veg pizza
    pizza_type = list(veg_recommendation_1.keys())[0]
    toppings = list(veg_recommendation_1.values())[0]
    price_medium = PIZZA_PRICES[pizza_type]['medium']

    # generate the recommended pizzas menu
    menu = " Here's Our Recommended Vegetarian Pizzas Menu :\n"
    menu += "       (Based on Our Customers' Most Buying)       \n\n"

    menu += "- Recommended Vegetarian Pizzas:\n"
    menu += f"  - {pizza_type.capitalize()}: {', '.join(toppings)}. Price: ${price_medium} (Medium)\n"

    # second recommended veg pizza
    pizza_type = list(veg_recommendation_2.keys())[0]
    toppings = list(veg_recommendation_2.values())[0]
    price_medium = PIZZA_PRICES[pizza_type]['medium']

    menu += f"  - {pizza_type.capitalize()}: {', '.join(toppings)}. Price: ${price_medium} (Medium)\n"

    menu += "\n-------------------------------------------\n"

    return menu


def generate_recommended_non_vegetarian_pizzas_menu():
    # get the current session
    session = SessionLocal()

    # get all the orders from the database
    orders = session.query(Order).all()

    # process the orders to get the vegetarian and non-vegetarian pizzas
    _, non_vegetarian_pizzas = process_orders(orders)

    # get the top recommended pizzas
    non_veg_recommendation_1, non_veg_recommendation_2 = non_veg_pizza_recommendation(non_vegetarian_pizzas)

    # close the session
    session.close()

    # first recommended non-veg pizza
    pizza_type = list(non_veg_recommendation_1.keys())[0]
    toppings = list(non_veg_recommendation_1.values())[0]
    price_medium = PIZZA_PRICES[pizza_type]['medium']

    # generate the recommended pizzas menu
    menu = " Here's Our Recommended Non-Vegetarian Pizzas Menu :\n"
    menu += "        (Based on Our Customers' Most Buying)          \n\n"

    menu += "- Recommended Non-Vegetarian Pizzas:\n"
    menu += f"  - {pizza_type.capitalize()}: {', '.join(toppings)}. Price: ${price_medium} (Medium)\n"

    # second recommended non-veg pizza
    pizza_type = list(non_veg_recommendation_2.keys())[0]
    toppings = list(non_veg_recommendation_2.values())[0]
    price_medium = PIZZA_PRICES[pizza_type]['medium']

    menu += f"  - {pizza_type.capitalize()}: {', '.join(toppings)}. Price: ${price_medium} (Medium)\n"

    menu += "\n-------------------------------------------\n"

    return menu


class ActionResetAllSlots(Action):
    def name(self) -> Text:
        return "action_reset_all_slots"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        return [AllSlotsReset()]


class ActionResponseToAskRestaurantAddress(Action):
    def name(self) -> Text:
        return "action_response_to_ask_restaurant_address"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        address = RESTAURANT_DETAILS["address"]
        dispatcher.utter_message(text=f"The restaurant address is: {address}")
        return []


class ActionResponseToAskRestaurantContactNumber(Action):
    def name(self) -> Text:
        return "action_response_to_ask_restaurant_contact_number"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        phone_number = RESTAURANT_DETAILS["phone_number"]
        dispatcher.utter_message(text=f"The restaurant contact number is: {phone_number}")
        return []


class ActionResponseToAskRestaurantName(Action):
    def name(self) -> Text:
        return "action_response_to_ask_restaurant_name"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        name = RESTAURANT_DETAILS["name"]
        dispatcher.utter_message(text=f"The restaurant name is: {name}")
        return []


class ActionResponseToAskRestaurantDetails(Action):
    def name(self) -> Text:
        return "action_response_to_ask_restaurant_details"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        name = RESTAURANT_DETAILS["name"]
        address = RESTAURANT_DETAILS["address"]
        phone_number = RESTAURANT_DETAILS["phone_number"]
        opening_hours = RESTAURANT_DETAILS["opening_hours"]
        final_order_time = RESTAURANT_DETAILS["final_order_time"]

        message = " Here are the details of the restaurant:\n"
        message += f"  - Name: {name}\n"
        message += f"  - Address: {address}\n"
        message += f"  - Phone Number: {phone_number}\n"
        message += f"  - Opening Hours: {opening_hours['Opening']} to {opening_hours['Closing']}\n"
        message += f"  - Final Order Time: {final_order_time}\n"

        dispatcher.utter_message(text=message)
        return []


class ActionDefaultFallback(Action):
    def name(self) -> str:
        return "action_default_fallback"

    def run(self, dispatcher, tracker, domain):
        dispatcher.utter_message(text="I'm sorry, I didn't understand that. Could you please rephrase?")
        return []


class ActionInformRecommendationsMenu(Action):
    def name(self) -> Text:
        return "action_inform_recommendations_menu"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        menu_message = generate_recommended_pizzas_menu()
        dispatcher.utter_message(text=menu_message, response="utter_ask_pizza_type")
        return []


class ActionInformVegRecommendationsMenu(Action):
    def name(self) -> Text:
        return "action_inform_veg_recommendations_menu"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        menu_message = generate_recommended_vegetarian_pizzas_menu()
        dispatcher.utter_message(text=menu_message, response="utter_ask_pizza_type")
        return []


class ActionInformNonVegRecommendationsMenu(Action):
    def name(self) -> Text:
        return "action_inform_non_veg_recommendations_menu"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        menu_message = generate_recommended_non_vegetarian_pizzas_menu()
        dispatcher.utter_message(text=menu_message, response="utter_ask_pizza_type")
        return []


class ActionInformMenu(Action):
    def name(self) -> Text:
        return "action_inform_menu"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        menu_message = generate_pizza_menu()
        dispatcher.utter_message(text=menu_message, response="utter_ask_pizza_type")
        return []


class ActionInformVegetarianMenu(Action):
    def name(self) -> Text:
        return "action_inform_vegetarian_menu"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        menu_message = generate_vegetarian_pizza_menu()
        dispatcher.utter_message(text=menu_message, response="utter_ask_pizza_type")
        return []


class ActionInformNonVegetarianMenu(Action):
    def name(self) -> Text:
        return "action_inform_non_vegetarian_menu"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        menu_message = generate_non_vegetarian_pizza_menu()
        dispatcher.utter_message(text=menu_message, response="utter_ask_pizza_type")
        return []


class ActionUtterGreet(Action):
    def name(self) -> Text:
        return "action_utter_greet"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        current_time = datetime.now().strftime("%I:%M %p")
        opening_time = RESTAURANT_DETAILS["opening_hours"]["Opening"]
        final_order_time = RESTAURANT_DETAILS["final_order_time"]

        # check if the current time is within the opening hours of the restaurant by comparing the time objects
        opening_time = datetime.strptime(opening_time, "%I:%M %p").time()
        final_order_time = datetime.strptime(final_order_time, "%I:%M %p").time()
        current_time = datetime.strptime(current_time, "%I:%M %p").time()

        if opening_time <= current_time <= final_order_time:
            dispatcher.utter_message(response="utter_greet")
            return [SlotSet("restaurant_opened", True)]
        else:
            # set slot 'restaurant_opened' to False
            dispatcher.utter_message(response="utter_greet_closed")
            return [SlotSet("restaurant_opened", False)]


class ActionAskPizzaSize(Action):
    def name(self) -> Text:
        return "action_ask_pizza_size"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        size_message = generate_pizza_sizes()

        size_message += "\n Which size would you like to order?"

        dispatcher.utter_message(text=size_message)
        return []


class ActionAskPizzaQuantity(Action):
    def name(self) -> Text:
        return "action_ask_pizza_quantity"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(response="utter_ask_pizza_quantity")
        return []


class ActionAskPizzaTopping(Action):
    def name(self) -> Text:
        return "action_ask_pizza_topping"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        pizza_type = tracker.get_slot("pizza_type").lower()

        pizza_topping = PIZZA_TOPPINGS_STD[pizza_type]
        for i, topping in enumerate(pizza_topping):
            if topping.startswith("and "):
                pizza_topping[i] = topping[4:]

        if len(pizza_topping) > 1:
            pizza_topping[-1] = "and " + pizza_topping[-1]

        pizza_topping = ", ".join(pizza_topping)

        if pizza_type:
            dispatcher.utter_message(
                text="The standard toppings for {} are: {}. "
                     "\n Would you like to go with the standard toppings or customize your own toppings?".format(
                    pizza_type, pizza_topping))

            return [ActiveLoop(None), FollowupAction("action_listen")]
        else:
            dispatcher.utter_message(
                text="Sorry, I didn't get that. Please choose a pizza type from the available menu.",
                response="utter_inform_menu")
            return []


class ActionUtterAskToppingConfirmation(Action):
    def name(self) -> Text:
        return "action_utter_ask_topping_confirmation"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(response="utter_ask_topping_confirmation")

        return []


class ActionInformAvailableToppings(Action):
    def name(self) -> Text:
        return "action_inform_available_toppings"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        available_possible_toppings = AVAILABLE_POSSIBLE_TOPPINGS
        message = " We offer the following topping options: {}.".format(", ".join(available_possible_toppings))
        dispatcher.utter_message(text=message)
        return []


class ActionActivateToppingsForm(Action):
    def name(self) -> Text:
        return "action_activate_toppings_form"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        return [ActiveLoop(None)]


class ActionAskPizzaCustomToppings(Action):
    def name(self) -> Text:
        return "action_ask_pizza_custom_toppings"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        # get current selected pizza_topping for the current pizza_type
        pizza_type = tracker.get_slot("pizza_type").lower()
        # get the current selected pizza_type's toppings
        pizza_topping = PIZZA_TOPPINGS_STD[pizza_type]

        # get the available possible toppings
        available_possible_toppings = AVAILABLE_POSSIBLE_TOPPINGS[0:5]

        # remove the standard toppings from the available possible toppings
        for topping in pizza_topping:
            if topping.lower() in available_possible_toppings:
                available_possible_toppings.remove(topping.lower())

        # if pizza_topping list has any item with 'and' then remove 'and' from the items.
        # Then add 'and' before the last topping if there are more than one topping.
        for i, topping in enumerate(pizza_topping):
            if topping.startswith("and "):
                pizza_topping[i] = topping[4:]

        if len(pizza_topping) > 1:
            pizza_topping[-1] = "and " + pizza_topping[-1]

        # add 'and' before the last topping if there are more than one topping
        if len(available_possible_toppings) > 1:
            available_possible_toppings[-1] = "and " + available_possible_toppings[-1]

        message = " Current Selected Toppings for Your '{}' Pizza are: {}".format(
            tracker.get_slot("pizza_type"), ", ".join(pizza_topping)
        )
        message += "\n We offer the following topping options: {}.".format(", ".join(available_possible_toppings))
        message += "\n\n Please make your own custom toppings selection(s)..."

        dispatcher.utter_message(text=message)

        return []


class ActionAskToppingSatisfaction(Action):
    def name(self) -> Text:
        return "action_ask_topping_satisfaction"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        dispatcher.utter_message(response="utter_ask_topping_satisfaction")
        return []


class ValidatePizzaOrderForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_pizza_order_form"

    async def validate_pizza_type(self, slot_value: Any, dispatcher: CollectingDispatcher, tracker: Tracker,
                                  domain: Dict[Text, Any]) -> Dict[Text, Any]:
        """Validate pizza_type value."""
        last_intent = tracker.get_intent_of_latest_message(skip_fallback_intent=True)
        latest_intent = tracker.latest_message["intent"].get("name")
        if latest_intent == "pizza_standard_topping_confirm":
            pizza_type = tracker.get_slot("pizza_type").lower()
            pizza_topping = PIZZA_TOPPINGS_STD[pizza_type]
            dispatcher.utter_message(text="Noted! your pizza will have the standard toppings")
            return {"pizza_type": pizza_type, "pizza_topping": pizza_topping, "topping_satisfaction": True}

        if slot_value.lower() in PIZZA_TYPES:
            # acknowledge the pizza type randomly
            acknowledgements = ["Great Choice!", "Nice Selection!", "Awesome!", "Yummy Choice!"]
            acknowledgement = random.choice(acknowledgements)
            dispatcher.utter_message(text=f"{acknowledgement} You have selected {slot_value.capitalize()} Pizza.")
            return {"pizza_type": slot_value}
        else:
            dispatcher.utter_message(
                text="Sorry, we don't have that pizza: {}. Please choose from the available menu.".format(slot_value),
                response="utter_inform_menu")
            return {"pizza_type": None}

    async def validate_pizza_topping(self, slot_value: Any, dispatcher: CollectingDispatcher, tracker: Tracker,
                                     domain: Dict[Text, Any]) -> Dict[Text, Any]:
        """Validate pizza_topping value."""
        pizza_topping = tracker.get_slot("pizza_topping")

        # check the intent of customer
        if pizza_topping:
            return {"pizza_topping": pizza_topping}
        else:
            dispatcher.utter_message(
                text="Sorry, I didn't get that. Please choose a pizza type from the available menu.",
                response="utter_inform_menu")
            return {"pizza_topping": None}

    async def validate_pizza_size(self, slot_value: Any, dispatcher: CollectingDispatcher, tracker: Tracker,
                                  domain: Dict[Text, Any]) -> Dict[Text, Any]:
        """Validate pizza_size value."""
        if slot_value.lower() in PIZZA_SIZES.keys():
            # acknowledge the pizza size
            dispatcher.utter_message(text=f"Great! You have selected {slot_value.capitalize()} size.")
            return {"pizza_size": slot_value}
        else:
            dispatcher.utter_message(
                text="Sorry, we don't have that size: {}. Please choose from the available sizes.".format(slot_value),
                response="utter_pizza_size")
            return {"pizza_size": None}

    async def validate_pizza_quantity(self, slot_value: Any, dispatcher: CollectingDispatcher, tracker: Tracker,
                                      domain: Dict[Text, Any]) -> Dict[Text, Any]:
        """Validate pizza_quantity value."""
        if slot_value.lower() in ["a", "A", "an", "An"]:
            slot_value = "one"
        if slot_value.lower() in PIZZA_QUANTITY:
            return {"pizza_quantity": slot_value}
        else:
            dispatcher.utter_message(
                text="Sorry, if you want to order more than 10 pizzas, then please contact us on +XX-XXX-XXX-XXXX")
            return {"pizza_quantity": None}

    async def extract_order_list(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict) -> Dict[
        Text, Any]:
        order_list = tracker.get_slot("order_list") or []
        return {"order_list": order_list}


class ActionSubmitPizzaOrderForm(Action):
    def name(self) -> Text:
        return "action_submit_pizza_order_form"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        pizza_type = tracker.get_slot("pizza_type").lower()
        pizza_size = tracker.get_slot("pizza_size").lower()
        pizza_quantity = tracker.get_slot("pizza_quantity").lower()
        pizza_topping = tracker.get_slot("pizza_topping")

        if pizza_type and pizza_size and pizza_quantity:
            order_list = tracker.get_slot("order_list") or []

            # if order_list is not empty, then remove all the items from the order_list which are not dict type
            order_list = [item for item in order_list if isinstance(item, dict)]

            # calculate the total price of current selected items
            current_item_price = PIZZA_PRICES[pizza_type][pizza_size] * PIZZA_QUANTITY.index(pizza_quantity) + 1

            # if order_list is not empty, then calculate the total price of all items
            if order_list:
                total_price = sum([item["price"] for item in order_list]) + current_item_price
            else:
                total_price = current_item_price

            # add the current selected item to the order_list
            order_list.append({
                "type": pizza_type,
                "size": pizza_size,
                "topping": pizza_topping,
                "quantity": pizza_quantity,
                "price": current_item_price
            })

            # Display Order Summary with the total price in a nice format
            message = "Here's Your Order Summary:\n"
            for i, item in enumerate(order_list):
                message += "{}. {} {} Pizza\n".format(i + 1, item["size"].capitalize(), item["type"].capitalize())
                message += "   - Toppings: {}\n".format(", ".join(item["topping"]))
                message += "   - Quantity: {}\n".format(item["quantity"].capitalize())
                message += "   - Price: ${:.2f}\n".format(item["price"])

            message += "\nTotal Price: ${:.2f}".format(total_price)

            # prompt to ask if the customer wants to add more items to the order
            message += "\n\nWould you like to add another Pizza to your order? or Proceed to Pickup?"

            dispatcher.utter_message(text=message)

            # set pizza_order_form slots to None so that the form can be filled again for the next order item
            return [
                SlotSet("pizza_type", None),
                SlotSet("pizza_topping", None),
                SlotSet("pizza_size", None),
                SlotSet("pizza_quantity", None),
                SlotSet("topping_satisfaction", None),
                SlotSet("pizza_custom_toppings", None),
                SlotSet("order_list", order_list),
                FollowupAction("action_listen")
            ]
        else:
            dispatcher.utter_message(text="Sorry, I didn't get that. Please provide all the required information.")
            return [FollowupAction("action_restart")]


# action_show_order_summary
class ActionShowOrderSummary(Action):
    def name(self) -> Text:
        return "action_show_order_summary"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        order_list = tracker.get_slot("order_list") or []

        if not order_list:
            dispatcher.utter_message(text="You don't have any active orders.")
            return []

        # calculate the total price of all items
        total_price = sum([item["price"] for item in order_list])

        # Display Order Summary with the total price in a nice format
        message = "Here's Your Order Summary:\n"
        for i, item in enumerate(order_list):
            message += "{}. {} {} Pizza\n".format(i + 1, item["size"].capitalize(), item["type"].capitalize())
            message += "   - Toppings: {}\n".format(", ".join(item["topping"]))
            message += "   - Quantity: {}\n".format(item["quantity"].capitalize())
            message += "   - Price: ${:.2f}\n".format(item["price"])

        message += "\nTotal Price: ${:.2f}".format(total_price)

        # prompt to ask if the customer wants to add more items to the order
        message += "\n\nWould you like to add another Pizza to your order? or Proceed to Pickup?"

        dispatcher.utter_message(text=message)

        return [
            SlotSet("pizza_type", None),
            SlotSet("pizza_topping", None),
            SlotSet("pizza_size", None),
            SlotSet("pizza_quantity", None),
            SlotSet("topping_satisfaction", None),
            SlotSet("pizza_custom_toppings", None),
            SlotSet("order_list", order_list),
            FollowupAction("action_listen")
        ]


class ActionRemoveItemFromOrder(Action):
    def name(self) -> Text:
        return "action_remove_item_from_order"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        order_list = tracker.get_slot("order_list") or []
        pizza_type = tracker.get_slot("pizza_type").lower()

        if not order_list:
            dispatcher.utter_message(text="You don't have any active orders.")
            return []

        if pizza_type not in [item["type"] for item in order_list]:
            dispatcher.utter_message(text="You don't have any {} Pizza in your order.".format(pizza_type.capitalize()))
            return []

        # remove the dict from the order_list which has the same pizza_type as the current selected pizza_type
        order_list = [item for item in order_list if item["type"] != pizza_type]

        # give message to the customer that the item has been removed from the order
        dispatcher.utter_message(text="The {} Pizza has been removed from your order.".format(pizza_type.capitalize()))

        # if order list becomes empty, then inform the customer that there are no active orders
        if not order_list:
            dispatcher.utter_message(text="You don't have any active orders. "
                                          "Is there anything else I can help you with?")

            # reset all the slots and call the action_listen
            return [AllSlotsReset(), FollowupAction("action_listen")]

        # calculate the total price of all items
        total_price = sum([item["price"] for item in order_list])

        # Display Order Summary with the total price in a nice format
        message = "Here's Your Updated Order Summary:\n"
        for i, item in enumerate(order_list):
            message += "{}. {} {} Pizza\n".format(i + 1, item["size"].capitalize(), item["type"].capitalize())
            message += "   - Toppings: {}\n".format(", ".join(item["topping"]))
            message += "   - Quantity: {}\n".format(item["quantity"].capitalize())
            message += "   - Price: ${:.2f}\n".format(item["price"])

        message += "\nTotal Price: ${:.2f}".format(total_price)

        # prompt to ask if the customer wants to add more items to the order
        message += "\n\n Would you like to add another Pizza to your order? or Proceed to Pickup?"

        dispatcher.utter_message(text=message)

        # set pizza_order_form slots to None so that the form can be filled again for the next order item
        return [
            SlotSet("pizza_type", None),
            SlotSet("pizza_topping", None),
            SlotSet("pizza_size", None),
            SlotSet("pizza_quantity", None),
            SlotSet("topping_satisfaction", None),
            SlotSet("pizza_custom_toppings", None),
            SlotSet("order_list", order_list),
            FollowupAction("action_listen")
        ]


class ValidatePizzaCustomToppingForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_pizza_custom_topping_form"

    async def required_slots(self, slots_mapped_in_domain: List[Text], dispatcher: CollectingDispatcher,
                             tracker: Tracker, domain: Dict[Text, Any]) -> Optional[List[Text]]:
        if tracker.get_slot("topping_satisfaction"):
            return []
        else:
            return ["pizza_custom_toppings", "topping_satisfaction"]

    async def validate_pizza_custom_toppings(self, slot_value: Any, dispatcher: CollectingDispatcher, tracker: Tracker,
                                             domain: Dict[Text, Any]) -> Dict[Text, Any]:
        """Validate pizza_custom_toppings value."""
        pizza_type = tracker.get_slot("pizza_type").lower()

        # if pizza_topping slot is empty, then get the standard toppings for the selected pizza_type
        if not tracker.get_slot("pizza_topping"):
            pizza_topping = PIZZA_TOPPINGS_STD[pizza_type]
        else:
            pizza_topping = tracker.get_slot("pizza_topping")

        # if pizza_topping list has any item with 'and' then remove 'and' from the items
        for i, topping in enumerate(pizza_topping):
            if topping.startswith("and "):
                pizza_topping[i] = topping[4:]

        pizza_topping = [topping.strip() for topping in pizza_topping]

        pizza_custom_toppings = tracker.get_slot("pizza_custom_toppings")
        if pizza_custom_toppings:
            if pizza_custom_toppings.__contains__(","):
                pizza_custom_toppings = pizza_custom_toppings.split(",")
            else:
                pizza_custom_toppings = [pizza_custom_toppings]

            # check the intent of customer
            latest_intent = tracker.latest_message["intent"].get("name")
            if latest_intent == "add_pizza_custom_toppings":
                pizza_custom_toppings = [topping.strip() for topping in pizza_custom_toppings]
            elif latest_intent == "remove_pizza_custom_toppings":
                pizza_custom_toppings = [topping.strip() for topping in pizza_custom_toppings]

                # remove the custom toppings from the standard toppings list
                for topping in pizza_custom_toppings:
                    if topping in pizza_topping:
                        pizza_topping.remove(topping)

            if pizza_custom_toppings:
                # add the custom toppings to the standard toppings list
                if latest_intent == "add_pizza_custom_toppings":
                    pizza_topping.extend(pizza_custom_toppings)

                    # add 'and' before the last topping if there are more than one topping
                    if len(pizza_topping) > 1:
                        pizza_topping[-1] = "and " + pizza_topping[-1]
                    pizza_topping = ", ".join(pizza_topping)  # pizza toppings string

                    dispatcher.utter_message(text="We have added {} to your toppings. You now have: {}.".format(
                        pizza_custom_toppings, pizza_topping)
                    )
                elif latest_intent == "remove_pizza_custom_toppings":
                    # add 'and' before the last topping if there are more than one topping
                    if len(pizza_topping) > 1:
                        pizza_topping[-1] = "and " + pizza_topping[-1]
                    pizza_topping = ", ".join(pizza_topping)

                    dispatcher.utter_message(text="We have removed {} from your toppings. You now have: {}.".format(
                        pizza_custom_toppings, pizza_topping)
                    )

                # remove the 'and' from any item in the list
                pizza_topping = pizza_topping.split(", ")
                for j, topping in enumerate(pizza_topping):
                    if topping.startswith("and "):
                        pizza_topping[j] = topping[4:]

            return {"pizza_topping": pizza_topping, "pizza_custom_toppings": pizza_custom_toppings}
        else:
            return {"pizza_topping": pizza_topping, "pizza_custom_toppings": None}

    async def validate_topping_satisfaction(self, slot_value: Any, dispatcher: CollectingDispatcher, tracker: Tracker,
                                            domain: Dict[Text, Any]) -> Dict[Text, Any]:
        """Validate topping_satisfaction value."""
        latest_intent = tracker.latest_message["intent"].get("name")
        if latest_intent == "pizza_custom_toppings_happy" or latest_intent == "pizza_standard_topping_confirm":
            return {"topping_satisfaction": True}
        else:
            return {"topping_satisfaction": None}


class ActionSubmitPizzaCustomToppingForm(Action):
    def name(self) -> Text:
        return "action_submit_pizza_custom_topping_form"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        pizza_topping = tracker.get_slot("pizza_topping")
        pizza_topping = [topping.strip() for topping in pizza_topping]

        return [
            SlotSet("pizza_topping", pizza_topping),  # set the slot value
            FollowupAction("pizza_order_form")  # go back to the pizza_order_form
        ]


class ActionCalculatePreparationTime(Action):
    def name(self) -> Text:
        return "action_calculate_preparation_time"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        order_list = tracker.get_slot("order_list") or []

        # calculate the total preparation time
        preparation_time = 0
        for item in order_list:
            preparation_time += PIZZA_PREPARATION_TIME[item["size"]]

        # set the preparation_time slot
        return [SlotSet("preparation_time", preparation_time)]


class ValidateOrderPickupForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_order_pickup_form"

    def extract_time(self, time_str: str):
        """
        Tries to extract a time from the given string using common time formats.
        """
        time_formats = [
            "%I:%M %p",  # e.g., "5:30 PM"
            "%I %p",  # e.g., "5 PM"
            "%H:%M",  # e.g., "17:30"
            "%H",  # e.g., "17"
            "%I:%M",  # e.g., "8:15"
            "%I",  # e.g., "8"
            "%I%p",  # e.g., "5PM"
            "%I:%M%p",  # e.g., "5:30PM"
            "%I o'clock %p",  # e.g., "5 o'clock PM"
            "%I o'clock"  # e.g., "5 o'clock""
        ]

        for fmt in time_formats:
            try:
                # today date
                today = datetime.now().date()
                # convert time string to datetime object
                time_obj = datetime.strptime(time_str, fmt)

                # combine today date and time object
                return datetime.combine(today, time_obj.time())
            except ValueError:
                continue

        return None

    async def validate_order_pickup_time(self, slot_value: Any, dispatcher: CollectingDispatcher, tracker: Tracker,
                                         domain: Dict[Text, Any]) -> Dict[Text, Any]:
        """Validate order_pickup_time value."""
        pickup_time_str = tracker.get_slot('pickup_time')

        times_in_english_words = [
            'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten',
            'eleven', 'twelve', 'thirteen', 'fourteen', 'fifteen', 'sixteen', 'seventeen', 'eighteen', 'nineteen',
            'twenty', 'twenty one', 'twenty two', 'twenty three', 'twenty four'
        ]

        # replace the sting time with the numeric time
        for i, time in enumerate(times_in_english_words):
            pickup_time_str = pickup_time_str.replace(time, str(i + 1))

        # remove . from the time string
        pickup_time_str = pickup_time_str.replace(".", "")
        print(pickup_time_str)

        parsed_time = self.extract_time(pickup_time_str)  # parse the date time object


        if parsed_time:
            # Assuming you want to store the time as a string in 24-hour format

            # format the time to 24-hour format with date
            formatted_time = parsed_time.strftime("%Y-%m-%d %H:%M")

            # if the time is in the past, then ask the user to provide a future time
            if parsed_time < datetime.now():
                dispatcher.utter_message(
                    text=f"I'm sorry, your pickup time has already been passed. "
                         f"Please provide us your pickup in coming time. "
                         f"We're open till {RESTAURANT_DETAILS['opening_hours']['Closing']} "
                         f"and accepting orders till {RESTAURANT_DETAILS['final_order_time']}."
                )
                return {"pickup_time": None, "order_pickup_time": None}

            # if the date is not today, then ask the user to provide a time for today
            if parsed_time.date() != datetime.now().date():
                dispatcher.utter_message(
                    text=f"I'm sorry, we only accept orders for today. "
                         f"Please provide us your pickup time for today."
                         f"Please remember, Today, we're open till {RESTAURANT_DETAILS['opening_hours']['Closing']}."
                         f" And accepting orders till {RESTAURANT_DETAILS['final_order_time']}."
                )
                return {"pickup_time": None, "order_pickup_time": None}

            # if the time is after the closing time, then ask the user to provide a time before the closing time
            if parsed_time.time() > datetime.strptime(RESTAURANT_DETAILS['opening_hours']['Closing'], "%I:%M %p").time():
                dispatcher.utter_message(
                    text=f"I'm sorry, we're closed at {RESTAURANT_DETAILS['opening_hours']['Closing']}. "
                         f"Please provide us your pickup time before the closing time. "
                         f"We're open till {RESTAURANT_DETAILS['opening_hours']['Closing']}."
                )
                return {"pickup_time": None, "order_pickup_time": None}

            # if the time is before the opening time, then ask the user to provide a time after the opening time
            if parsed_time.time() < datetime.strptime(RESTAURANT_DETAILS['opening_hours']['Opening'], "%I:%M %p").time():
                dispatcher.utter_message(
                    text=f"I'm sorry, we're open at {RESTAURANT_DETAILS['opening_hours']['Opening']}. "
                         f"Please provide us your pickup time after the opening time."
                )
                return {"pickup_time": None, "order_pickup_time": None}

            # If the preparation time is more than the time provided,
            preparation_time = tracker.get_slot("preparation_time")
            if preparation_time:
                if parsed_time < datetime.now() + timedelta(minutes=preparation_time):
                    # earliest possible pickup time
                    earliest_pickup_time = datetime.now() + timedelta(minutes=preparation_time) + timedelta(minutes=5)
                    formatted_earliest_pickup_time = earliest_pickup_time.strftime("%Y-%m-%d %H:%M")

                    dispatcher.utter_message(
                        text=f"I'm sorry, the preparation time for your order is {preparation_time} minutes. "
                             f"Your earliest pickup time can be {formatted_earliest_pickup_time} or after that. "
                             f"Would you like to provide us a new pickup time? Thank you."
                    )

                    return {"pickup_time": None, "order_pickup_time": None}

            # if reached here, then the time is valid. Show the selected time to the customer for confirmation
            dispatcher.utter_message(
                text=f"Great! Your pickup time is set to {formatted_time}. "
                     f"Would you like to confirm the pickup time?"
            )

            # return {"pickup_time": formatted_time, "order_pickup_time": formatted_time}
            # update the slots and call the listen action for the user to confirm the time
            return {"pickup_time": formatted_time, "order_pickup_time": formatted_time, "within_business_hours": True}
        else:
            dispatcher.utter_message(
                text="I'm sorry, I couldn't understand the time you provided. "
                     "Could you please specify the exact pickup time again?")

            # set order_pickup_time and pickup_time slots to None
            return {"pickup_time": None, "order_pickup_time": None}

    async def validate_pickup_confirmation(self, slot_value: Any, dispatcher: CollectingDispatcher, tracker: Tracker,
                                           domain: Dict[Text, Any]) -> Dict[Text, Any]:
        """Validate pickup_confirmation value."""
        latest_intent = tracker.latest_message["intent"].get("name")
        if latest_intent == "approve_pickup_time" or latest_intent == "affirm":
            order_number = random.randint(1000, 9999)
            dispatcher.utter_message(
                text=f"Great! Thank you for confirming the pickup time. Your order is confirmed. \n\n"
                     f"Your order number is #{order_number}. Please note down your order number for future reference. "
            )
            return {"pickup_confirmation": True, "order_number": order_number}
        elif latest_intent == "deny_pickup_time" or latest_intent == "deny_pickup_time":
            # if customer denies while confirming the pickup time, then ask customer to provide a new pickup time which
            # is closer to the estimated delivery time.
            preparation_time = tracker.get_slot("preparation_time")

            # earliest possible pickup time
            earliest_pickup_time = datetime.now() + timedelta(minutes=preparation_time) + timedelta(minutes=5)
            formatted_earliest_pickup_time = earliest_pickup_time.strftime("%Y-%m-%d %H:%M")

            dispatcher.utter_message(
                text=f"I'm sorry, the preparation time for your order is {preparation_time} minutes. "
                     f"Your earliest pickup time can be {formatted_earliest_pickup_time} or after that. "
                     f"Would you like to provide us a new pickup time? Thank you."
            )

            return {
                "pickup_time": None, "order_pickup_time": None, "within_business_hours": None,
                "pickup_confirmation": None
            }


class ActionSubmitOrderPickupForm(Action):
    def name(self) -> Text:
        return "action_submit_order_pickup_form"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        order_list = tracker.get_slot("order_list") or []
        order_pickup_time = tracker.get_slot("order_pickup_time")
        order_preparation_time = tracker.get_slot("preparation_time")
        order_number = tracker.get_slot("order_number")

        # calculate the total price
        total_price = sum([item["price"] for item in order_list])

        # message = f"Order Confirmation: #{order_number}\n\n"
        # message += "Here's Your Final Order Summary:\n"
        # for i, item in enumerate(order_list):
        #     message += "{}. {} {} Pizza\n".format(i + 1, item["size"].capitalize(), item["type"].capitalize())
        #     message += "   - Toppings: {}\n".format(", ".join(item["topping"]))
        #     message += "   - Quantity: {}\n".format(item["quantity"].capitalize())
        #     message += "   - Price: ${:.2f}\n".format(item["price"])
        #
        # message += "\nTotal Price: ${:.2f}".format(total_price)
        # message += "\nPreparation Time: {} minutes".format(order_preparation_time)
        # message += "\nPickup Time: {}".format(order_pickup_time)

        # Add an ending line for pickup

        message = f"Thank you for your order! We’ll see you at Champ Pizza Hut on {order_pickup_time} for pickup. \n\n"

        # Add Restaurant Address
        # message += f"Our Address: {RESTAURANT_DETAILS['address']}\n"

        # Add a contact number for the restaurant
        # message += f"If you have any questions, please call us at {RESTAURANT_DETAILS['address']}.\n\n"

        # Add the opening hours of the restaurant
        # message += f"We are open from {RESTAURANT_DETAILS['opening_hours']['Opening']} to {RESTAURANT_DETAILS['opening_hours']['Closing']}."

        # Store the order details in the database
        db: Session = SessionLocal()

        # remove 'and' from the last item in the list
        for i, item in enumerate(order_list):
            if item["topping"][-1].startswith("and "):
                order_list[i]["topping"][-1] = item["topping"][-1][4:]

        try:
            new_order = Order(
                order_number=order_number,
                order_list=order_list,
                total_price=total_price,
                preparation_time=order_preparation_time,
                pickup_time=datetime.strptime(order_pickup_time, "%Y-%m-%d %H:%M")
            )
            db.add(new_order)
            db.commit()
        except Exception as e:
            db.rollback()
            dispatcher.utter_message(text="An error occurred while saving your order. Please try again.")
            return [FollowupAction("action_restart")]
        finally:
            db.close()

        dispatcher.utter_message(text=message)

        # Reset all the slots after the order is confirmed
        return [
            SlotSet("pizza_type", None),
            SlotSet("pizza_topping", None),
            SlotSet("pizza_custom_toppings", None),
            SlotSet("topping_satisfaction", None),
            SlotSet("pizza_size", None),
            SlotSet("pizza_quantity", None),
            SlotSet("order_list", None),
            SlotSet("pickup_time", None),
            SlotSet("order_pickup_time", None),
            SlotSet("preparation_time", None),
            SlotSet("within_business_hours", None),
            SlotSet("order_number", None),
            FollowupAction("utter_end_greet")
        ]
