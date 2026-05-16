"""Builds the two N-ary trees over the flat MODULES list.

Functional tree: groups by function (Energy, Life Support, Command, Operations).
Criticality tree: groups by level (Vital, Sustenance, Expansion).

Both trees reference the SAME module dicts — changing `module["current_mode"]`
in one is automatically visible from the other.
"""

from colony.tree import Node
from colony.modules import find_module


def build_functional_tree():
    root = Node("Aurora Siger Colony")

    energy = root.add_child(Node("Energy"))
    energy.add_child(Node("Solar Power", module=find_module(4)))
    energy.add_child(Node("Nuclear Power", module=find_module(5)))
    energy.add_child(Node("Wind Power", module=find_module(13)))

    life_support = root.add_child(Node("Life Support"))
    life_support.add_child(Node("Life Support (ECLSS)", module=find_module(2)))
    life_support.add_child(Node("Habitat", module=find_module(3)))
    life_support.add_child(Node("Medical Support", module=find_module(7)))
    life_support.add_child(Node("Food Production", module=find_module(8)))

    command = root.add_child(Node("Command"))
    command.add_child(Node("Command and Control", module=find_module(1)))
    command.add_child(Node("Communications", module=find_module(6)))

    operations = root.add_child(Node("Operations"))
    operations.add_child(Node("Logistics and Storage", module=find_module(9)))
    operations.add_child(Node("ISRU (Local Resources)", module=find_module(10)))
    operations.add_child(Node("Workshop and Maintenance", module=find_module(11)))
    operations.add_child(Node("Science Lab", module=find_module(12)))

    return root


def build_criticality_tree():
    root = Node("Aurora Siger Colony")

    vital = root.add_child(Node("Vital"))
    vital.add_child(Node("Command and Control", module=find_module(1)))
    vital.add_child(Node("Life Support (ECLSS)", module=find_module(2)))
    vital.add_child(Node("Medical Support", module=find_module(7)))
    vital.add_child(Node("Habitat", module=find_module(3)))

    sustenance = root.add_child(Node("Sustenance"))
    sustenance.add_child(Node("Solar Power", module=find_module(4)))
    sustenance.add_child(Node("Nuclear Power", module=find_module(5)))
    sustenance.add_child(Node("Wind Power", module=find_module(13)))
    sustenance.add_child(Node("Food Production", module=find_module(8)))
    sustenance.add_child(Node("Communications", module=find_module(6)))
    sustenance.add_child(Node("ISRU (Local Resources)", module=find_module(10)))

    expansion = root.add_child(Node("Expansion"))
    expansion.add_child(Node("Logistics and Storage", module=find_module(9)))
    expansion.add_child(Node("Workshop and Maintenance", module=find_module(11)))
    expansion.add_child(Node("Science Lab", module=find_module(12)))

    return root
