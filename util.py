"utilities"

def int_nun(s: str) -> int | None:
    "returns the string representation of the int or None if it cannot be converted"
    try:
        return int(s)
    except ValueError:
        return None
    except TypeError:
        return None

def get_title_path_ext_from_file(fname: str) -> tuple[str, str, str]:
    "gets the title from a filename"
    path = ""
    if (x := max(fname.rfind('/'), fname.rfind('\\'))) >= 0:
        path = fname[0:x]
        fname = fname[x+1:]

    ext = ""
    if (x := fname.rfind('.')) >= 0:
        ext = fname[x+1:]
        fname = fname[0:x]

    return fname, path, ext