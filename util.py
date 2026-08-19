"utilities"

# utility candidate
def int_nun(s: str) -> int | None:
    "returns the string representation of the int or None if it cannot be converted"
    try:
        return int(s)
    except ValueError:
        return None
    except TypeError:
        return None
