"ListPanelLambda"

from collections.abc import Callable

from ListTitlePanelABC import ListTitlePanelABC

class ListPanelLambda(ListTitlePanelABC):
    "Allows external functions to be called on events"
    def __init__(
        self,
        parent,
        sel_foo: Callable[[int], None] | None = None,
        double_foo: Callable[[int], None] | None = None,
        drag_foo: Callable[[int, int], None] | None = None,
        **kwargs
    ):
        super().__init__(parent, drag=True, **kwargs)
        self.lbox.bind("<Double-1>", self.double)

        self.sel_foo: Callable[[int], None] | None = sel_foo
        self.double_foo: Callable[[int], None] | None = double_foo
        self.drag_foo: Callable[[int, int], None] | None = drag_foo

    def accept_edit(self, *args, **kwargs):
        "unused in this subclass"
        #we won't start an edit so we won't end one either
        return None

    def do_lbox_sel(self, *args, **kwargs):
        "callend on single clicks"
        self._sel()
        if self.sel_foo:
            self.sel_foo(self.last_selection)

    def double(self):
        "called on double clicks"
        self._sel()
        if self.double_foo:
            self.double_foo(self.last_selection)

    def drag(self, start, end):
        "called on drags"
        if self.drag_foo:
            self.drag_foo(start, end)
