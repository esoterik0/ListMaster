"enums.py contains enums and constants for the ListMaster program"
from enum import Enum

#type alias
table = list[str | list | tuple]  # pylint: disable=invalid-name

WIDTH = 75
HEIGHT = 25
SINGLE = 1


class State(Enum):
    "Enums to define what state the program is in"
    ROLL = "ROLL"
    EDIT = "EDIT"


class ItemType(Enum):
    "enum for item type"
    META = "Meta"
    FORM = "Form"
    LIST = "List"
    NONE = "None"


class ItemColor(Enum):
    "Enum to define a color for a type"
    META = "#FFAAAA",
    FORM = "#FFAAFF",
    LIST = "#AAAAFF",
