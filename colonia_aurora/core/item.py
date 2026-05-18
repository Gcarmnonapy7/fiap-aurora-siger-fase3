from functools import total_ordering


@total_ordering
class Item:
    def __init__(self, name: str):
        self.name = name

    def __eq__(self, other: "Item") -> bool:
        raise NotImplementedError

    def __lt__(self, other: "Item") -> bool:
        raise NotImplementedError

    def do(self):
        raise NotImplementedError

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.name}>"
