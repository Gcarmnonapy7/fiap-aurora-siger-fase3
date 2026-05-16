"""Node — generic N-ary tree class.

Used to build the colony's two hierarchies:
functional (Energy, Life Support, Command, Operations) and
criticality (Vital, Sustenance, Expansion).

Internal nodes carry `module=None`; leaves reference a module dict
(from `colony.modules.MODULES`).
"""

from collections import deque


class Node:

    def __init__(self, name, module=None):
        self.name = name
        self.module = module
        self.children = []

    def add_child(self, child):
        self.children.append(child)
        return child

    def is_leaf(self):
        return len(self.children) == 0

    def traverse_dfs(self):
        """Depth-first traversal (pre-order). Generator."""
        yield self
        for child in self.children:
            yield from child.traverse_dfs()

    def traverse_bfs(self):
        """Breadth-first traversal (by level). Generator."""
        queue = deque([self])
        while queue:
            current = queue.popleft()
            yield current
            for child in current.children:
                queue.append(child)

    def find(self, name):
        """DFS search by name. Returns the Node or None."""
        for node in self.traverse_dfs():
            if node.name == name:
                return node
        return None

    def leaves(self):
        """Returns the list of modules referenced by leaf nodes."""
        return [node.module for node in self.traverse_dfs() if node.is_leaf()]

    def depth(self):
        """Depth of the subtree (lone root = 1)."""
        if self.is_leaf():
            return 1
        return 1 + max(child.depth() for child in self.children)

    def aggregate(self, leaf_value, initial, combine):
        """Recursive aggregation over leaves.

        leaf_value: callable receiving the leaf's `module` and returning a value
        initial: neutral aggregator value (0 for sum, 1 for product, ...)
        combine: callable (a, b) -> c
        """
        if self.is_leaf():
            return leaf_value(self.module)
        result = initial
        for child in self.children:
            result = combine(result, child.aggregate(leaf_value, initial, combine))
        return result

    def pretty_print(self, indent=0):
        """Returns a pretty-printed string of the subtree."""
        lines = ["  " * indent + ("- " if indent > 0 else "") + self.name]
        for child in self.children:
            lines.append(child.pretty_print(indent + 1))
        return "\n".join(lines)
