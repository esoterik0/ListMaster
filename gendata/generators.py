# generator functions that return a function that returns a generartor.

from math import ceil
from random import choice, sample, shuffle
from typing import Callable, Generator, Any

from .formula import formula, meta_formula


def gen3(form: formula | meta_formula | list | str | tuple) -> list[str] | str | formula | tuple:
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
    match (form):
        case meta_formula() as meta:
            return gen3(choice(meta.formula))  # choose a formula from the meta formula list
        case formula():  # formula creates a list based on the formula
            ret = []
            for f in form.formula:
                match(f):
                    case formula():
                        ret += gen3(f)
                    case _:
                        ret.append(gen3(f))
            return ret
        case list() as lst:
            return gen3(choice(lst))  # choose something from the list
        case str() as st:
            return st  # just return the string
        case tuple() as t:  # creates a string based on a tuple
            def conv(obj: list | str | formula | meta_formula) -> str | formula:
                "sub function to match tuple elements"
                match (obj):
                    case meta_formula():
                        return conv(choice(obj.formula))
                    case formula():
                        return gen3(obj).join(" & ")
                    case list():
                        return gen3(obj)
                    case str():
                        return obj

            return [conv(o) for o in t].join("")


def gen_form(form: meta_formula | formula) -> list[str]:
    """
    Wrapper function to hide all the intermediary types that gen3 can return

    Generates a formula or meta_formual
    """
    return gen3(form)


def gen(lst: list | tuple) -> str:
    """
    Wrapper function to hide all the intermediary types that gen3 can return

    Generates a list or tuple
    """
    return gen3(lst)


def general_generator(
    form: formula,
    split: int = 6,
    lines: int = 50
) -> Callable[[], Generator[list[str], Any, None]]:
    """
    Generates a generator for a general formula.

    If the size (based on labels) is smaller than split, we try to fit as many multiples
    on one line as we can.

    If the size is larger than the split then it takes more than one line. We try to
    fit as many full sets of lines as we can without a partial set.
    """

    def food():
        size = len(form.labels)  # first get the size of the formula;
        headlines = ceil(size/split)
        loop = (lines-headlines)//headlines  # total lines

        # yield the header first provided by formual.labels
        if size < split:
            rep = split//size  # calculate any repatitions that are needed.
            loop *= rep  # increase the count by the multiple
            yield form.labels * rep  # yield the correct label
        else:
            loop = loop//ceil(size/split)  # reduce the loop for larger formulas
            yield form.labels  # yield the label

        for _ in loop:
            yield gen_form(form)  # yield the content

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
                    "({0} + {1})".format(draw[x], draw[x+1])
                    for x in range(0, len(draw), 2)
                ]

    return food


def genjump(n, t=60, sp=6):  # jumpstart
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
                out.append("({0} + {1})".format(draw[0], draw[1]))
                out.append("({0} + {1})".format(draw[2], draw[3]))
            yield out

    return food


def genstart(n, t=60, sp=8):
    return lambda: start(n, t, sp)
