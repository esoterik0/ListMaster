"classes that define formulas for dicing tables"


class Formula:
    "Indicates that the list of lists is a formula and not a recursive list"
    def __init__(self, lst: list[list], labels: list[str], name: str, split: int = 6):
        self.formula: list[list] = lst
        self.labels = labels
        self.name = name
        self.split = split


class MetaFormula(Formula):
    "indicates this is a list of formulas"
    def __init__(self, forms: list[list], labels: list[str], name: str, split: int = 6):
        super().__init__([Formula(form, labels, name) for form in forms], labels, name, split)
