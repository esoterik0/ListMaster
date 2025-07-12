"enums.py contains enums and constants for the ListMaster program"
from enum import Enum

WIDTH = 75
HEIGHT = 25
SINGLE = 1

class State(Enum):
    "Enums to define what state the program is in"
    ROLL = "ROLL"
    EDIT = "EDIT"
