#

class formula:
    "Indicates that the list of lists is a formula and not a recursive list"
    def __init__(self, lst: list[list], labels: list[str], split: int = 6):
        self.formula: list[list] = lst
        self.labels = labels
        self.split = split


class meta_formula(formula):
    "indicates this is a list of formulas"
    def __init__(self, forms: list[list], labels: list[str], split: int = 6):
        super().__init__([formula(form, labels) for form in forms], labels, split)
