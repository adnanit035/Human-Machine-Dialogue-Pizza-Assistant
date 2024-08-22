from rasa.shared.core.slots import Slot
from datetime import datetime


class OrderPickupDateTimeSlot(Slot):
    def __init__(self, name: str, *args, **kwargs):
        super().__init__(name, *args, **kwargs)

    def parse_value(self, value: str, tracker) -> datetime:
        """
        Parse the incoming string value to a datetime object.
        """
        # Define the possible datetime formats
        datetime_formats = [
            "%Y-%m-%d %H:%M",  # e.g., "2024-08-15 14:30"
            "%Y-%m-%d %I:%M %p",  # e.g., "2024-08-15 02:30 PM"
            "%Y-%m-%d",  # e.g., "2024-08-15"
            "%H:%M",  # e.g., "14:30"
            "%I:%M %p",  # e.g., "02:30 PM"
        ]

        for fmt in datetime_formats:
            try:
                return datetime.strptime(value, fmt)
            except ValueError:
                continue

        # If the value doesn't match any format, return None or handle it as invalid
        return None

    def set(self, tracker, value: str) -> datetime:
        """
        Override the set method to use the parse_value method.
        """
        datetime_value = self.parse_value(value, tracker)
        if datetime_value:
            return datetime_value
        else:
            return None

    def as_feature(self, value: datetime) -> float:
        """
        Convert the datetime value into a float feature.
        """
        if value is None:
            return 0.0
        # Example: Use the timestamp as a feature
        return value.timestamp()

    def persist(self, tracker):
        """
        Return the value as a string for persistence.
        """
        value = tracker.get_slot(self.name)
        if isinstance(value, datetime):
            return value.isoformat()
        return str(value)
