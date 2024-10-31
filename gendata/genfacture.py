
from typing import Any, Callable, Generator

import openpyxl as pyxl
from openpyxl.styles import Border, Font, Side
from openpyxl.styles.colors import Color
from openpyxl.styles.fills import PatternFill


def CalcMargin(left=None):
    "Calculate the margin for left, right, or single=none"
    lt = 0.25
    rt = 0.25

    if left is not None:
        if left is True:
            lt = .75
        else:
            rt = .75

    return lt, rt


# these are used by generate to the excell column names
letters = [chr(ord('A')+i) for i in range(26)]
double = ['{}{}'.format(b, a) for b in letters for a in letters]
cols = letters + double  # excel cols


def Generate(
    foo: Callable[[], Generator[list[str], Any, None]],  # generator function
    outname: str | None = None,  # filename
    split: int = 6,  # split
    left_margin: bool | None = None,  # margins: left:True, right:False, center:None
    Thick: Side = Side(border_style="thick", color="FF000000"),  # cel border
    font: Font = Font("Crimson Text SemiBold"),  # font to use, must be in current directory, or path to file
    gray: PatternFill = PatternFill(patternType='solid', fgColor=Color(rgb="FFE8E8E8"))  # pattern for header bg
):
    "generate a page, with a name, and margin, default = single"
    # global cols  # excel cols n.b. we don't write to this so it doesn't need to be global.
    width: float = 94.0  # width of a sheet, this may change if the paper size or orientation changes etc.

    if not outname:
        outname = "foo.xlsx"  # default filename

    wb: pyxl.Workbook = pyxl.Workbook()
    ws = wb.active
    left, right = CalcMargin(left_margin)

    ws.page_margins.left = left
    ws.page_margins.right = right
    ws.page_margins.top = 0.25
    ws.page_margins.bottom = 0.25
    ws.page_margins.header = 0.0
    ws.page_margins.footer = 0.0

    # set the width of all the colums we are using
    for i in range(split):
        key = cols[i]
        ws.column_dimensions[key].width = width/split

    def top_border(x):
        "creates the top border for row x"
        for i in range(split):
            key = cols[i] + str(x)
            ws[key].border = Border(top=Thick)

    def bot_border(x):
        "creates the botom border for row x"
        for i in range(split):
            key = cols[i] + str(x)
            top = ws[key].border.top
            left = ws[key].border.left
            right = ws[key].border.right
            ws[key].border = Border(bottom=Thick, left=left, right=right, top=top)

    def side_border(x):
        "creates the side border for row x"
        key1 = cols[0] + str(x)
        key2 = cols[split-1] + str(x)
        top1 = ws[key1].border.top
        top2 = ws[key2].border.top
        ws[key1].border = Border(top=top1, left=Thick)
        ws[key2].border = Border(top=top2, right=Thick)

    x = 1  # excel row
    fill = gray

    # fil out the page
    for things in foo():  # each entry ...
        top_border(x)  # ... needs a top boarder

        # start inserting things into the row(s)
        while len(things):  # while we have entries in to insert
            part = things[:split]  # break off a full size row or whats left
            things = things[split:]  # break off any remaining
            side_border(x)  # each row needs side boarders

            # insert into the row, use enumerate to count the ojects
            for j, thing in enumerate(part):
                y = cols[j]  # get the column index
                idx = "{}{}".format(y, x)  # make our cel index
                ws[idx].value = thing  # insert our value
                ws[idx].font = font  # and font
                if fill:  # fill is for the header only
                    ws[idx].fill = fill  # and fill if we have it

            x = x + 1  # increment the row, entries can be multiple rows

        fill = None  # turn off the fill after the header (first row)

    bot_border(x-1)  # bottom border only used once; top of next is also the bottom of prev.

    wb.save(outname)  # save the file


def Manufacture(
    # callable that returns a callable that return's a generator
    gentoo: Callable[[], Callable[[], Generator[list[str], Any, None]]],
    prefix: str = "gen",  # file template prefix
    p: int = 5,  # number of pages
    split: int = 6,
    le: bool | None = True,
    rt: bool | None = True
):
    "Make double sided pages left and right."
    filename = prefix + "{}{}.xlsx"
    for i in range(2*p):
        odd = i % 2
        Generate(
            gentoo(),
            filename.format("L" if odd else "R", i//2 + 1),
            split,
            le if odd else rt
        )
