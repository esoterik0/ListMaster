"classes that define formulas for dicing tables"
from enums import table

class Formula:  # pylint: disable=too-few-public-methods
    "Indicates that the list of lists is a formula and not a recursive list"
    def __init__(self, lst: table, labels: list[str], name: str, split: int = 6):
        self.formula: table = lst
        self.labels = labels
        self.name = name
        self.split = split

        # figure out of something like this could work to make it look like a list for most purposes
        # self.__getitem__ = self.formula.__getitem__
        # self.__setitem__ = self.formula.__setitem__

    def __len__(self):
        return len(self.formula)


class MetaFormula(Formula):  # pylint: disable=too-few-public-methods
    "indicates this is a list of formulas"
    def __init__(self, forms: list[table], labels: list[str], name: str, split: int = 6):
        super().__init__([Formula(form, labels, name, split) for form in forms], labels, name, split)
