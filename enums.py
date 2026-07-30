"enums.py contains enums and constants for the ListMaster program"
from enum import Enum
import gendata

table = gendata.table # type alias pylint: disable=C0103

# valuse for tkinter; I don't know what these are supposed to be the doc and setup says they should
# be in pixels, or what ever we set, but it seems to ignore the setting (or we set it wrong, or the
# documentation is wrong.) ... These appear to be based on the current font size, even though the
# docs say that pixels are the default, seems that they arent.
WIDTH = 200
HEIGHT = 20
SINGLE = 1
TEXTSIZE = 12
MENUSIZE = 12
LOG = "rolls.log"

# weights describe relative movement so bigger movement is shrinking and growing faster smaller
COLWEIGHT = (1,1,1) # numbers stay larger at smaller sizes


class State(Enum):
    "defines for what state the program is in"
    ROLL = "ROLL"
    EDIT = "EDIT"


class ItemType(Enum):
    "Defines for item types"
    META = "Meta"
    FORM = "Form"
    LIST = "List"
    NONE = "None"


class ItemColor(Enum):
    "Defines a color for a type"
    META = "#FFAAAA"
    FORM = "#FFAAFF"
    LIST = "#AAAAFF"
