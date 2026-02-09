# generator functions that return a function that returns a generartor.

from functools import reduce
from math import ceil
from operator import add
from random import choice, sample, shuffle
from typing import Any, Callable, Generator

from .formulas import Formula, MetaFormula


def gen3(form: Formula | MetaFormula | list | str | tuple) -> list[str] | str | Formula | tuple:
    """
    Recursive work function.

    Generates the formulas;
        meta->formula
        formala->list[str]
        list->list|tuple|str
        tuple->str
        str->str

    Returns the list of choices from a formula or meta formula. Formulas inside formulas are expanded
        or the single choice from a list. It has a few intermediary return types but the final return
        type should be str or list[str]
    """
    if not form:
        return ""
    match (form):
        case MetaFormula() as meta:
            return gen3(choice(meta.formula))  # choose a formula from the meta formula list
        case Formula():  # formula creates a list based on the formula
            ret = []
            for f in form.formula:
                match(f):
                    case Formula():
                        ret += gen3(f)
                    case _:
                        ret.append(gen3(f))
            return ret
        case list() as lst:
            return gen3(choice(lst))  # choose something from the list
        case str() as st:
            return st  # just return the string
        case tuple() as t:  # creates a string based on a tuple
            def conv(obj: list | str | Formula | MetaFormula) -> str | Formula:
                "sub function to match tuple elements"
                match (obj):
                    case MetaFormula():
                        return conv(choice(obj.formula))
                    case Formula():
                        return " & ".join(gen3(obj))
                    case _:
                        return gen3(obj)

            return "".join([conv(o) for o in t])


def gen_form(form: MetaFormula | Formula) -> list[str]:
    """
    Wrapper function to hide all the intermediary types that gen3 can return

    Generates a formula or meta_formuala
    """
    return gen3(form)


def gen_list(lst: list | tuple) -> str:
    """
    Wrapper function to hide all the intermediary types that gen3 can return

    Generates a list or tuple
    """
    return gen3(lst)


def general_generator(
    form: Formula,
    lines: int = 50,
    half: bool = False
) -> Callable[[], Generator[list[str], Any, None]]:
    """
    Generates a generator for a general formula.

    If the size (based on labels) is smaller than split, we try to fit as many multiples
    on one line as we can.

    If the size is larger than the split then it takes more than one line. We try to
    fit as many full sets of lines as we can without a partial set.
    """
    split = form.split

    if half:
        split /= 2
        lines /= 2

    def food():
        size = len(form.labels)  # first get the size of the formula;
        headlines = ceil(size/split)
        loop = (lines-headlines)//headlines  # total lines
        rep = 1

        # yield the header first provided by formula.labels
        if size < split:
            rep = split//size  # calculate any repetitions that are needed.
            yield form.labels * rep  # yield the correct label
        else:
            yield form.labels  # yield the label

        for _ in range(loop):
            yield reduce(add, [gen_form(form) for _ in range(rep)])  # yield the content

    return food


def jump(n, total=60, sp=6):  # jumpstart
    "makes a list of unique pairings exhaustivly."
    def food():
        yield ["Player One", "Player Two"]*sp//2
        for _ in range(n):
            nums = [x+1 for x in range(total)]
            shuffle(nums)
            while (len(nums)):
                draw = nums[:sp*2]
                nums = nums[sp*2:]
                yield [
                    f"({draw[x]} + {draw[x+1]})"
                    for x in range(0, len(draw), 2)
                ]

    return food


def genjump(n, t=60, sp=6):  # jumpstart
    "helper for jumpstart"
    return lambda: jump(n, t, sp)


def start(n, t=60, sp=8):
    "makes pairs of unique parings."
    def food():
        yield ["Player One", "Player Two"]*sp//2
        nums = [x+1 for x in range(t)]
        for _ in range(n):
            out = []
            for _ in range(sp//2):
                draw = sample(nums, 4)
                out.append(f"({draw[0]} + {draw[1]})")
                out.append(f"({draw[2]} + {draw[3]})")
            yield out

    return food


def genstart(n, t=60, sp=8):
    "generator start"
    return lambda: start(n, t, sp)
