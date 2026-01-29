# Echoes of Asteria

A turn-based terminal RPG written in Python. Explore the mystical land of Asteria, battle enemies, complete quests, and defeat the Obsidian Warden.

## Features

- **Exploration**: Navigate a 5x5 world with fog-of-war discovery
- **Turn-based Combat**: Strategic battles with attack, flee, and item usage options
- **RPG Mechanics**: Level up, gain stats, and grow stronger
- **Inventory System**: Collect, equip, and use weapons, armor, and consumables
- **Economy**: Buy and sell items at the merchant's shop
- **Quest System**: Help NPCs and solve riddles for rewards
- **Save/Load**: Persistent game state using JSON

## Getting Started

### Requirements

- Python 3.6+
- No external dependencies (uses standard library only)

### Running the Game

```bash
git clone https://github.com/yourusername/echoes-of-asteria.git
cd echoes-of-asteria
python3 run_game.py
```

## How to Play

### Controls

| Command | Description |
|---------|-------------|
| `n/s/e/w` | Move north, south, east, or west |
| `look` | Examine your current location |
| `map` | Display discovered areas |
| `inventory` | View your items |
| `take <item>` | Pick up an item |
| `drop <item>` | Drop an item |
| `equip <item>` | Equip a weapon or armor |
| `use <item>` | Use a consumable or key |
| `attack` | Start combat with an enemy |
| `talk` | Speak with NPCs |
| `shop` | Open the merchant interface |
| `stats` | View your character stats |
| `save` / `load` | Save or load your game |
| `help` | Show command list |
| `quit` | Exit the game |

### Combat

When you encounter an enemy and choose to attack, you enter combat mode:
- **(a)ttack**: Strike the enemy
- **(u)se item**: Use a potion or consumable
- **(f)lee**: Attempt to escape (50% chance)

### Tips

1. **Equip your starter gear immediately** - Type `equip knife` and `equip vest`
2. **Explore the meadow first** - Find the Healing Herb for a quest
3. **Visit the merchant** - Buy better equipment when you have gold
4. **Save often** - The dungeon can be unforgiving
5. **Find the Rusty Key** - It unlocks a special area

### Winning the Game

Defeat the **Obsidian Warden** in the Obsidian Keep at the far corner of the map to complete your adventure.

## Project Structure

```
echoes_of_asteria/
├── run_game.py                 # Entry point
├── README.md
├── requirements.txt
└── src/
    └── echoes_of_asteria/
        ├── __init__.py
        ├── main.py             # Main entry point
        ├── game.py             # Game loop and commands
        ├── player.py           # Player and Entity classes
        ├── world.py            # World generation and rooms
        ├── items.py            # Item system
        └── utils.py            # Helper functions
```

## License

MIT License - feel free to use and modify.
