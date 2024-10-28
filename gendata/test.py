# test.py

class formula:
    def __init__(self, lst: list[list]):
        self.formula: list[list] = lst


def testmatch(foo):
    match foo:
        case formula():
            print("i am a formula")
        case list():
            print("i am a list")
        case str():
            print("i am a string")


if __name__ == "__main__":
    form = formula([[]])
    form.formula.append([1])
    form.formula.append([2])

    testmatch(form)
    testmatch(["woot"])
    testmatch("string")
