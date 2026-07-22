"Interface class for main<->sub panel communications"
import gendata as dat
from enums import State, table


class PanelCom:
    """Abstract Interface base class for main panel and sub panels to communicate. The main panel
    implements the the interface, calling down to the sub panels where needed. Sub panels call the
    interface to pass information and commands between the panels. This way the sub panels only
    need to care about their parent, we could have had an interface per panel if we wanted or
    needed the the granularity.

    This allows breaking the circular import if we want to use type hints and the UI help that
    comes with that. Both main.py and the sub panels (what/page/results.py) can import this file
    and not have the sub panels 'from main import MainPanel' which causes a circular import loop.
    """
    def __init__(self):
        self.state: State = State.ROLL # we want an instance variable, not a class variable

    def set_state(self, state: State):
        "sets the internal state based on value"
        raise NotImplementedError

    def set_page(self, name: str, page: list[table]):
        "set page panel contents"
        raise NotImplementedError

    def set_result_item(self, form: tuple[str, dat.Formula] | tuple[str, table] = ("", [])):
        "set the table for the result page to use"
        raise NotImplementedError

    def get_name_index(self, name: str) -> tuple[int, table] | tuple[None,  None]:
        "returns the index of a table in all_tables"
        raise NotImplementedError

    def has_name(self, name) -> bool:
        "returns true if the name exists"
        raise NotImplementedError

    def name_available(self, name: str) -> bool:
        "returns true if a name is available"
        raise NotImplementedError

    def get_table(self, idx: int) -> tuple[str, table] | None:
        "returns a table from all_tables by index"
        raise NotImplementedError

    def get_table_index(self, tab: table) -> tuple[int | None, str]:
        "returns the index of a table in all_tables"
        raise NotImplementedError

    def add_to_all(self, tab: tuple[str, table]) -> bool:
        "adds a table to the all_tables category"
        raise NotImplementedError

    def get_name(self, item: dat.MetaFormula | dat.Formula | list | tuple | str) -> str:
        "get name of object, tabels encoded as {tableName}"
        raise NotImplementedError

    def rename(self, name: str, newname: str) -> bool:
        "renames a table"
        raise NotImplementedError

    def do_clipboard(self, out: str):
        "copy to the clipboard"
        raise NotImplementedError

    def check_delete_from_all(self, name):
        "returns trues if deleted from all"
        raise NotImplementedError
