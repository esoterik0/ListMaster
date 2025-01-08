"methods for random potion colors"
from .formulas import Formula

basic_colors = [
    "Red",
    "Orange",
    "Yellow",
    "Green",
    "Blue",
    "Purple",
    "Magenta",
    "Cyan",
    "White",
    "Gray",
]

special_colors = [
    ("Transparent ", basic_colors),
    ("Glowing ", basic_colors),
    ("Sparkling ", basic_colors),
    ("Dark ", basic_colors),
    ("Neon ", basic_colors),
    ("Metallic ", basic_colors),
]

secondary_colors = basic_colors + special_colors
double_secondary_colors = Formula([secondary_colors]*2, ["color"]*2, "Double secondary colors")

double_colors = [
    (double_secondary_colors, " Checker"),
    (double_secondary_colors, " Polka-dot"),
    (double_secondary_colors, " Swirled"),
    (double_secondary_colors, " Striped"),
]

potion_color = secondary_colors + double_colors
potion_colors = Formula([potion_color], ["Potion color"], "Potion color", 2)
