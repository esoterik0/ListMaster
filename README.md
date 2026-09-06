# ListMaster
Create, maintain, and roll random tables for RPG or other use. Single or group choices. Makes printable pages. Import from pdf or txt files.

# Usage
- Install python 3.12.6 or later
- Open a command prompt and pick or make a folder ex. `md PyApps`  and enter it `cd PyApps`
- create and enter a virtual environment (optional)

    `python -m venv ./venv/ListMaster`

    `./venv/ListMaster/Scripts/activate`
- Clone into a folder ListMaster

    `git clone git@github.com:esoterik0/ListMaster.git ListMaster`
- enter the ListMaster folder

    `cd ListMaster`
- install libraries

    `pip install -r LM.pip`
- start the program

    `python start.py`

Once installed, One can create a shortcut to a script to start the program. Start in pyapps or what ever folder you installed ListMaster into.

    .\venv\ListMaster\Scripts\Activate.bat

or


    .\venv\ListMaster\Scripts\Activate.ps1

    cd ListMaster
    pythonw start.py

## Features

- Roll on random tables, formulas and metaformulas.
- Save set of table
- Export a single collection
- Load set of tables
- Import set of tables
- Create random tables.
- Create random formulas; a set of tables to roll at once.
- Create random metaformulas; a table of similar formulas to choose from.
- Edit random tables.
- Import tables from pdf.
- Import tables from txt.
- Export table to txt.
- Drag to reorder items in the what, and results column whilst in edit mode
- Generate .xls files of pages of random rolls, for printing and future use
- Log rolls to save for later

## Basic Usage
There are three main columns to the program:
- What collection
- Select page
- Results

There are two modes:
- Dice Tables: Roll mode
- Add/Edit Tables: Edit Mode

There are three types of tables
- List
- Formula
- Meta formula

### Table types

#### list
a basic list. a list can contain
- text
- {ref} to another table
- text with a {ref} inserted or {ref_two}

References to other tables must be surrounded by {}, Page has a copy item functon to help with this.

#### Formula
A named collection of tables to roll all at once, i.e. a NPC; entries may be any type of table.

Entries look like 'Name ;{Table}'

#### Meta formula
A collection of similar formulas, that share a set of names, one formula is chosen to be used.

The top line in edit mode will have a ';' separated list of names. Each other entry is a '`' (backtick) separated list of tables.

### What collection
What book/collection to choose from.

There is a special collection at the top called 'All Tables', this contains all tables in the data base. The other collections pull from this. When you add a table, it gets added to all tables.

There are some builtin tables and formulas from mazerats, and formuals I made. The two collections built in are:
- Maze Rats Pages
- Formulas

When you select a collection its contents will be displayed in the page column.

#### Edit mode

In edit mode you can:
- add a collection
- edit a collection - double click or F2 to edit
- drag to move items

### Select page
This column lists the 'pages' in the 'book'/collection.

You can choose which 'page' to roll, some are lists, some are formuals, etc. you can filter the pages by list, formula, metaformula, or no filter.

When you choose what table to roll it is sent to the results panel and rolled.

#### Edit Mode
In edit mode there are buttons to:
- Add a new List
- Add a new Formula
- add a new metaformula
- Edit an Item - also press F2
- Copy an Item name
- Insert an Item into the collocetion by name
- Delete an item - edit its name to nothing "" - can choose to delete from all
- Double click to edit table in results column

### Results

Displays the results of the roll on the Table, if it is a Formula or MetaFormula there will be multiple entries. Or if on a list it can roll it multiple times

There are buttons, etc. to:
- Re-Roll the result
- Copy Result to Clipboard
- Choose path for xls file
- Set number of pages to generate for the .xls file & times to roll on basic tables
- Generate an .xls file. -- You may need to install the included `CrimsonText-SemiBold.ttf` for the .xls files to work, the paging and spacing might not work with another font.
- Set the log file
- Re-roll and log
- Log the roll

#### Edit Mode
edit mode has:
- Add item
- you can add '{tables}' or '{table} element' etc.
- Edit item - also double click and F2
- delete an item; edit it to nothing ""
- Finish Editing; closes the panel
- Drag to move items
- Pressing enter while the panel has focus will add a new entry

### Menus

#### File
- New / Clear database - gives you an empty database
- Reset to defaults - replace the contents with the mazerats deafults
- Load database - load a previously saved data base
- Import database - import and merge databases
- Save - Save the database to default name
- Save as - Save the database to specified name
- Save & Quit - Save the data base and quit
- Just Quit (No prompt) - just quit no save no prompt.

#### Import
Only works in Edit mode, disabled in roll mode.

- import list (txt)

imports a list from text, the filename is the title. it will show you the list to verify and edit before saving.

- import list (pdf)

imports lists from a pdf. Choose a page or pages, and press parse, the middle column will have all
the text blocks from the page or pages. Each block starts with the number of newlines in the block, and the first line or part thereof. Every time you hit parse it will erase everything in the other two columns.

The title can be separate from the list or on top of the list. If the title is separate there are buttons to set or add to the title. The title can also be edited manuallly.

Double click on a block to add it to the list. If the list is one block per entry, you can drag to add all the blocks dragged through.

the third column contains the list it can be edited or added to.

Save will save the table to the currently open collection, and clear the third column.
Save & Quit will save the table to the currenly open collection, and close the dialog.

one could set a page, pase, save lists, set a new page parse, ...

#### Export

- Export list (txt)

Exports the currently seleceted list, only works in roll mode. A path is given and the filename will be the 'tablename.txt'.
- export collection

Exports the currently seleceted collection, only works in roll mode. A file name is given to write out the .dat file.

#### About
has the about command
shows the about dialog.

# Misc
## Known issues
- when adding new items or editing existing items, backspace won't work until the entry box is clicked in, or a left or right arrow key is pressed. This seems to be a bug in TK or TKinter; all the other keys work, it has keyboard focus.
- I have not been able change the font size for popup messages. Nothing works, things the documentation and people/forums say should work just dont; as far as I can tell I should have been able to change the size. This seems to be an issue with TK or TKinter.

I have tried to research these issues but the have had no luck finding an answer.

#### Content used under license
mazedat.py contains content used under the CC-BY 4.0 License from Maze Rats by Ben Milton.

Crimson Text Font under SIL
