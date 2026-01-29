"""World generation and room management."""

import random
from .items import Item
from .player import Entity
from .utils import Position


class Room:
    """Represents a location in the game world."""
    
    def __init__(self, name, desc, pos, items=None, enemy=None, locked=False, special=None):
        self.name = name
        self.desc = desc
        self.pos = pos
        self.items = items or []
        self.enemy = enemy
        self.locked = locked
        self.special = special

    def __str__(self):
        return f"{self.name}: {self.desc}"

    def __repr__(self):
        return f"Room({self.name!r}, pos={self.pos})"


class World:
    """The game world containing all rooms."""
    
    def __init__(self, width=5, height=5):
        self.width = width
        self.height = height
        self.rooms = {}
        self._generate()

    def _generate(self):
        """Generate the world map."""
        # Helper to create rooms
        def add_room(x, y, **kwargs):
            pos = (x, y)
            self.rooms[pos] = Room(
                kwargs.get("name", f"Unknown Area"),
                kwargs.get("desc", "An unremarkable place."),
                pos,
                items=kwargs.get("items", []),
                enemy=kwargs.get("enemy"),
                locked=kwargs.get("locked", False),
                special=kwargs.get("special")
            )

        # Define key locations
        add_room(1, 1, name="Crossroads", 
                 desc="A dusty crossroads with a weathered sign pointing in four directions.")
        
        add_room(1, 2, name="Merchant's Way", 
                 desc="A well-worn path where traders often rest.", 
                 special="merchant")
        
        add_room(2, 1, name="Whispering Trees", 
                 desc="Ancient trees that seem to whisper secrets when the wind blows.", 
                 enemy=self._create_enemy("Wolf"))
        
        add_room(2, 2, name="Old Ruins", 
                 desc="Crumbled stones from a long-forgotten civilization.", 
                 items=[Item("ancient_coin", "Ancient Coin", "A weathered coin from ages past.", "misc", value=100)])
        
        add_room(0, 1, name="Foggy Marsh", 
                 desc="Thick mist obscures your vision. The ground is soft and treacherous.", 
                 enemy=self._create_enemy("Marsh Slime"))
        
        add_room(1, 0, name="Sunlit Meadow", 
                 desc="Wildflowers sway in a gentle breeze. A peaceful place.", 
                 items=[Item("herb", "Healing Herb", "A medicinal plant that can heal wounds.", "consumable", power=15, value=5)])
        
        add_room(3, 1, name="Bandit Camp", 
                 desc="Remnants of a camp. Someone unfriendly lingers here.", 
                 enemy=self._create_enemy("Bandit"))
        
        add_room(3, 2, name="Mysterious Cave", 
                 desc="A dark cave entrance. Strange symbols are carved around the doorway.", 
                 locked=True, special="riddle")
        
        add_room(4, 1, name="Cliff Edge", 
                 desc="A stunning view of the sea far below. Something glints nearby.", 
                 items=[Item("strange_gem", "Strange Gem", "A gem pulsing with inner light.", "misc", value=200)])
        
        add_room(2, 3, name="Quiet Pond", 
                 desc="Crystal clear water reflects the sky. Fish swim lazily.", 
                 items=[Item("fish", "Lucky Fish", "A plump fish. Might restore some energy.", "consumable", power=8, value=3)])
        
        # Fill remaining spaces with wilderness
        for x in range(self.width):
            for y in range(self.height):
                if (x, y) not in self.rooms:
                    self.rooms[(x, y)] = Room("Wilderness", "Tall grass stretches in all directions.", (x, y))
        
        # Boss location
        self.rooms[(4, 4)].name = "Obsidian Keep"
        self.rooms[(4, 4)].desc = "A fortress of black glass looms before you. Dark energy radiates from within."
        self.rooms[(4, 4)].enemy = self._create_enemy("Obsidian Warden", hp=60, atk=10, defense=4, dodge=4)
        
        # Place key in ruins (high chance)
        if random.random() < 0.9:
            self.rooms[(2, 2)].items.append(
                Item("rusty_key", "Rusty Key", "An old iron key. Might fit an ancient lock.", "key", value=0)
            )

    def _create_enemy(self, kind, hp=None, atk=None, defense=None, dodge=None):
        """Create an enemy entity from template."""
        templates = {
            "Wolf": {"hp": 14, "atk": 5, "defense": 1, "dodge": 4, "xp": 12, "gold": 8},
            "Marsh Slime": {"hp": 12, "atk": 4, "defense": 0, "dodge": 2, "xp": 10, "gold": 6},
            "Bandit": {"hp": 18, "atk": 6, "defense": 1, "dodge": 5, "xp": 14, "gold": 12},
            "Obsidian Warden": {"hp": 60, "atk": 10, "defense": 4, "dodge": 4, "xp": 80, "gold": 50},
        }
        template = templates.get(kind, {"hp": 10, "atk": 3, "defense": 0, "dodge": 2, "xp": 5, "gold": 2})
        
        enemy = Entity(
            kind,
            hp or template["hp"],
            atk or template["atk"],
            defense or template["defense"],
            dodge or template["dodge"]
        )
        enemy.xp_reward = template.get("xp", 5)
        enemy.gold_reward = template.get("gold", 2)
        return enemy

    def get_room(self, pos):
        """Get room at position."""
        return self.rooms.get((pos.x, pos.y))

    def neighbors(self, pos):
        """Get valid neighboring positions."""
        directions = {
            "north": (pos.x, pos.y - 1),
            "south": (pos.x, pos.y + 1),
            "west": (pos.x - 1, pos.y),
            "east": (pos.x + 1, pos.y)
        }
        valid = {}
        for direction, (nx, ny) in directions.items():
            if 0 <= nx < self.width and 0 <= ny < self.height:
                valid[direction] = Position(nx, ny)
        return valid

    def ascii_minimap(self, player_pos, reveal_set=None):
        """Generate ASCII map showing explored areas."""
        reveal_set = reveal_set or set()
        lines = []
        
        for y in range(self.height):
            row = []
            for x in range(self.width):
                if (x, y) == (player_pos.x, player_pos.y):
                    row.append("@")
                elif (x, y) in reveal_set:
                    room = self.rooms[(x, y)]
                    if room.enemy and room.enemy.alive():
                        row.append("!")
                    elif room.locked:
                        row.append("#")
                    elif room.items:
                        row.append("*")
                    else:
                        row.append(".")
                else:
                    row.append(" ")
            lines.append("".join(row))
        
        return "\n".join(lines)
