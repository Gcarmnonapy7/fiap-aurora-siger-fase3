class GenericManager:
    def __init__(self):
        self._items = []

    def add(self, item):
        self._items.append(item)

    def remove(self, item):
        if item in self._items:
            self._items.remove(item)

    def find(self, name: str):
        for item in self._items:
            if item.name == name:
                return item
        return None

    def find_by_index(self, i: int):
        if 0 <= i < len(self._items):
            return self._items[i]
        return None

    def order_by(self, key_fn):
        return sorted(self._items, key=key_fn)

    def do_all(self):
        for item in self._items:
            item.do()

    def __len__(self):
        return len(self._items)

    def __iter__(self):
        return iter(self._items)
