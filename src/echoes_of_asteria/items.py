"""Item definitions and management."""


class Item:
    """Represents an item in the game world."""
    
    def __init__(self, id_, name, desc, kind="misc", power=0, value=0):
        self.id = id_
        self.name = name
        self.desc = desc
        self.kind = kind  # weapon, armor, consumable, key, misc
        self.power = power
        self.value = value

    def __str__(self):
        return f"{self.name} ({self.kind})"

    def __repr__(self):
        return f"Item({self.id!r}, {self.name!r})"

    def to_dict(self):
        """Convert item to dictionary for serialization."""
        return {
            "id": self.id, 
            "name": self.name, 
            "desc": self.desc, 
            "kind": self.kind, 
            "power": self.power, 
            "value": self.value
        }

    @staticmethod
    def from_dict(data):
        """Create item from dictionary."""
        return Item(
            data["id"], 
            data["name"], 
            data["desc"], 
            data.get("kind", "misc"), 
            data.get("power", 0), 
            data.get("value", 0)
        )
