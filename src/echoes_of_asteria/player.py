"""Player and entity definitions."""

from .items import Item
from .utils import slow_print, Position


class Entity:
    """Base class for all combat-capable entities."""
    
    def __init__(self, name, hp, atk, defense, dodge=5):
        self.name = name
        self.max_hp = hp
        self.hp = hp
        self.atk = atk
        self.defense = defense
        self.dodge = dodge

    def alive(self):
        """Check if entity is still alive."""
        return self.hp > 0

    def __repr__(self):
        return f"Entity({self.name!r}, hp={self.hp}/{self.max_hp})"


class Player(Entity):
    """The player character with inventory and progression."""
    
    def __init__(self, name="Hero"):
        super().__init__(name, hp=40, atk=6, defense=2, dodge=8)
        self.level = 1
        self.xp = 0
        self.xp_to_next = 30
        self.pos = Position(1, 1)
        self.gold = 30
        self.inventory = []
        self.equipped_weapon = None
        self.equipped_armor = None
        self.discovered = set()
        self.quests = {}
        self.save_slot = "savegame.json"

    def attack_power(self):
        """Calculate total attack power including weapon."""
        base = self.atk
        if self.equipped_weapon:
            base += self.equipped_weapon.power
        return base

    def defense_value(self):
        """Calculate total defense including armor."""
        base = self.defense
        if self.equipped_armor:
            base += self.equipped_armor.power
        return base

    def add_item(self, item):
        """Add an item to inventory."""
        self.inventory.append(item)
        slow_print(f"You received: {item.name}")

    def remove_item_by_id(self, id_):
        """Remove and return item by ID, or None if not found."""
        for i, it in enumerate(self.inventory):
            if it.id == id_:
                return self.inventory.pop(i)
        return None

    def find_item(self, name):
        """Find item by partial name match."""
        name = name.lower()
        for it in self.inventory:
            if name in it.name.lower():
                return it
        return None

    def gain_xp(self, amount):
        """Add experience points, potentially leveling up."""
        self.xp += amount
        slow_print(f"You gained {amount} XP.")
        while self.xp >= self.xp_to_next:
            self.xp -= self.xp_to_next
            self._level_up()

    def _level_up(self):
        """Handle leveling up."""
        self.level += 1
        self.max_hp += 8
        self.atk += 2
        self.defense += 1
        self.hp = self.max_hp
        self.xp_to_next = int(self.xp_to_next * 1.4)
        slow_print(f"*** LEVEL UP! Now level {self.level}. ***")

    def to_dict(self):
        """Serialize player to dictionary."""
        return {
            "name": self.name,
            "hp": self.hp,
            "max_hp": self.max_hp,
            "atk": self.atk,
            "defense": self.defense,
            "dodge": self.dodge,
            "level": self.level,
            "xp": self.xp,
            "xp_to_next": self.xp_to_next,
            "pos": (self.pos.x, self.pos.y),
            "gold": self.gold,
            "inventory": [it.to_dict() for it in self.inventory],
            "equipped_weapon": self.equipped_weapon.to_dict() if self.equipped_weapon else None,
            "equipped_armor": self.equipped_armor.to_dict() if self.equipped_armor else None,
            "quests": self.quests,
            "discovered": list(self.discovered)
        }

    @staticmethod
    def from_dict(data):
        """Deserialize player from dictionary."""
        p = Player(data.get("name", "Hero"))
        p.hp = data.get("hp", p.hp)
        p.max_hp = data.get("max_hp", p.max_hp)
        p.atk = data.get("atk", p.atk)
        p.defense = data.get("defense", p.defense)
        p.dodge = data.get("dodge", p.dodge)
        p.level = data.get("level", p.level)
        p.xp = data.get("xp", p.xp)
        p.xp_to_next = data.get("xp_to_next", p.xp_to_next)
        pos = data.get("pos", (1, 1))
        p.pos = Position(*pos)
        p.gold = data.get("gold", p.gold)
        p.inventory = [Item.from_dict(it) for it in data.get("inventory", [])]
        ew = data.get("equipped_weapon")
        ea = data.get("equipped_armor")
        p.equipped_weapon = Item.from_dict(ew) if ew else None
        p.equipped_armor = Item.from_dict(ea) if ea else None
        p.quests = data.get("quests", {})
        p.discovered = set(tuple(x) for x in data.get("discovered", []))
        return p
