import os
import random
import json
import shutil
from .utils import clear_screen, slow_print, wrap_text, input_prompt, choose_option, Position
from .items import Item
from .player import Player, Entity
from .world import World

class Game:
    def __init__(self):
        self.world = World(width=5, height=5)
        self.player = Player()
        # Starter items
        self.player.inventory = [
            Item("knife","Traveler's Knife","A simple steel knife. Better than nothing.", "weapon", power=2, value=4),
            Item("leather_vest","Leather Vest","Light protection for the torso.", "armor", power=1, value=6),
            Item("bread","Stale Bread","Restores a bit of HP.", "consumable", power=8, value=2),
        ]
        # Shop items (could be in World but kept here for simplicity as per original)
        self.merchant_goods = [
            Item("iron_sword","Iron Sword","A solid blade.", "weapon", power=4, value=40),
            Item("chain_mail","Chain Mail","Better armor.", "armor", power=3, value=50),
            Item("potion","Minor Potion","Restores 25 HP.", "consumable", power=25, value=20),
        ]
        self.running = True
        self.intro_done = False
        self.player.discovered.add((self.player.pos.x, self.player.pos.y))
        self.turn_count = 0

    def start(self):
        clear_screen()
        slow_print("Welcome to Echoes of Asteria.\n", 0.008)
        slow_print("A terminal adventure of exploration and danger.\n", 0.008)
        self.intro_done = True
        self.help_text()
        
        # Initial offer to load
        slow_print("\nType 'load' to load a saved game or just press Enter to start.")
        choice = input_prompt().lower()
        if choice == 'load':
            self.load()

        while self.running:
            try:
                self.tick()
            except (KeyboardInterrupt, EOFError):
                slow_print("\nExiting game. Goodbye.")
                break

    def help_text(self):
        txt = """
Commands:
  Movement:   north/south/east/west (or n/s/e/w)
  Look:       look (or l) - examine current area
  Map:        map (or m) - show explored areas
  
  Items:      inventory (or i), take <item>, drop <item>
              equip <item>, unequip <weapon|armor>
              use <item>, inspect <item>
              
  Combat:     attack (or a) - engage enemy
              In combat: (a)ttack, (u)se item, (f)lee
              
  Social:     talk - speak to NPCs
              shop - buy/sell at merchant
              
  Quests:     quests - view active quests
              riddle - attempt puzzle
              
  System:     save, load, stats, help, quit
"""
        slow_print(txt.strip(), 0)


    def tick(self):
        cmd = input_prompt("\nWhat will you do? ").lower()
        if not cmd:
            return
        parts = cmd.split()
        verb = parts[0]
        args = parts[1:]
        
        if verb in ("help", "?"):
            self.help_text()
        elif verb in ("look","l"):
            self.cmd_look()
        elif verb in ("move","go"):
            if args:
                self.cmd_move(args[0])
            else:
                slow_print("Move where? north/south/east/west")
        elif verb in ("north","south","east","west"):
            self.cmd_move(verb)
        elif verb in ("n","s","e","w"):
             full_dirs = {'n':'north', 's':'south', 'e':'east', 'w':'west'}
             self.cmd_move(full_dirs[verb])
        elif verb in ("map","m"):
            self.cmd_map()
        elif verb in ("inventory","inv","i"):
            self.cmd_inventory()
        elif verb == "inspect":
            self.cmd_inspect(" ".join(args))
        elif verb == "equip":
            self.cmd_equip(" ".join(args))
        elif verb == "unequip":
            self.cmd_unequip(" ".join(args))
        elif verb == "use":
            self.cmd_use(" ".join(args))
        elif verb in ("attack", "a"):
            self.cmd_attack()
        elif verb == "stats":
            self.cmd_stats()
        elif verb == "save":
            self.save()
        elif verb == "load":
            self.load()
        elif verb in ("quit", "exit"):
            self.running = False
        elif verb in ("take", "get"):
            self.cmd_take(" ".join(args))
        elif verb == "drop":
            self.cmd_drop(" ".join(args))
        elif verb == "talk":
            self.cmd_talk()
        elif verb == "shop":
            self.cmd_shop()
        elif verb == "quests":
            self.cmd_quests()
        elif verb == "riddle":
            self.cmd_riddle()
        else:
            slow_print("I don't understand that command. Type 'help' for options.")

    # --- Commands ---

    def current_room(self):
        return self.world.get_room(self.player.pos)

    def reveal_current(self):
        self.player.discovered.add((self.player.pos.x, self.player.pos.y))

    def cmd_look(self):
        r = self.current_room()
        self.reveal_current()
        slow_print(f"You are at: {r.name}\n", 0.002)
        slow_print(wrap_text(r.desc), 0.002)
        if r.items:
            slow_print("\nYou notice the following items:")
            for it in r.items:
                slow_print(f"- {it.name}: {it.desc}")
        if r.enemy and r.enemy.alive():
            slow_print(f"\nA hostile {r.enemy.name} is here!")
        if r.locked:
            slow_print("\nThere is a locked door here.")
        if r.special:
            # Subtle hint
            pass

    def cmd_move(self, direction):
        if not direction:
            slow_print("Move where?")
            return
        direction = direction.strip().lower()
        dirs = self.world.neighbors(self.player.pos)
        if direction not in dirs:
            slow_print(f"You can't go {direction}. Available: {', '.join(dirs.keys())}")
            return
        new_pos = dirs[direction]
        r = self.world.get_room(new_pos)
        if r.locked:
            slow_print("The way is locked.")
            return
        self.player.pos = new_pos
        self.turn_count += 1
        self.reveal_current()
        self.cmd_look()
        self.random_event()

    def cmd_map(self):
        mm = self.world.ascii_minimap(self.player.pos, reveal_set=self.player.discovered)
        slow_print("Map ('@' is you):")
        slow_print(mm)

    def cmd_inventory(self):
        if not self.player.inventory:
            slow_print("Inventory empty.")
            return
        slow_print("Inventory:")
        for it in self.player.inventory:
            eq = ""
            if self.player.equipped_weapon and it.id == self.player.equipped_weapon.id:
                eq = " [equipped weapon]"
            if self.player.equipped_armor and it.id == self.player.equipped_armor.id:
                eq = " [equipped armor]"
            slow_print(f"- {it.name}{eq}: {it.desc}")

    def cmd_inspect(self, name):
        if not name:
            slow_print("Inspect what?")
            return
        name = name.strip()
        it = self.player.find_item(name)
        if it:
            slow_print(f"{it.name}: {it.desc} (Power: {it.power}, Value: {it.value})")
            return
        # Check room
        room = self.current_room()
        for r_it in room.items:
            if name in r_it.name.lower():
                slow_print(f"{r_it.name} (on ground): {r_it.desc}")
                return
        slow_print("Item not found.")

    def cmd_equip(self, name):
        if not name:
            slow_print("Equip what?")
            return
        it = self.player.find_item(name)
        if not it:
            slow_print("You don't have that.")
            return
        if it.kind == "weapon":
            self.player.equipped_weapon = it
            slow_print(f"Equipped {it.name}.")
        elif it.kind == "armor":
            self.player.equipped_armor = it
            slow_print(f"Equipped {it.name}.")
        else:
            slow_print("Cannot equip that.")

    def cmd_unequip(self, what):
        what = what.strip().lower()
        if what == "weapon":
            self.player.equipped_weapon = None
            slow_print("Weapon unequipped.")
        elif what == "armor":
            self.player.equipped_armor = None
            slow_print("Armor unequipped.")
        else:
            slow_print("Unequip 'weapon' or 'armor'.")

    def cmd_use(self, name):
        if not name:
             slow_print("Use what?")
             return
        it = self.player.find_item(name)
        if not it:
            slow_print("You don't have that.")
            return
        
        if it.kind == "consumable":
            old = self.player.hp
            heal = it.power
            self.player.hp = min(self.player.max_hp, self.player.hp + heal)
            self.player.remove_item_by_id(it.id)
            slow_print(f"Used {it.name}. HP {old} -> {self.player.hp}.")
        elif it.kind == "key":
            # Unlock nearby
            unlocked = False
            for pos, room in self.world.rooms.items():
                # Check distance implies adjacency (Manhattan dist)
                dist = abs(pos[0] - self.player.pos.x) + abs(pos[1] - self.player.pos.y)
                if room.locked and dist <= 1: # Only unlock adjacent
                     room.locked = False
                     unlocked = True
                     slow_print(f"You unlocked {room.name}.")
                     self.player.remove_item_by_id(it.id)
                     break
            if not unlocked:
                slow_print("Nothing nearby to unlock.")
        else:
            slow_print("Can't use that.")

    def cmd_take(self, name):
        if not name:
            slow_print("Take what?")
            return
        room = self.current_room()
        for i, it in enumerate(room.items):
            if name in it.name.lower():
                self.player.add_item(it)
                room.items.pop(i)
                return
        slow_print("Not found here.")

    def cmd_drop(self, name):
        if not name:
            slow_print("Drop what?")
            return
        it = self.player.find_item(name)
        if it:
            if (self.player.equipped_weapon == it) or (self.player.equipped_armor == it):
                slow_print("Unequip first.")
                return
            self.player.remove_item_by_id(it.id)
            self.current_room().items.append(it)
            slow_print(f"Dropped {it.name}.")
        else:
            slow_print("You don't have that.")

    def cmd_stats(self):
        p = self.player
        slow_print(f"Name: {p.name}")
        slow_print(f"Level: {p.level} (XP: {p.xp}/{p.xp_to_next})")
        slow_print(f"HP: {p.hp}/{p.max_hp}")
        slow_print(f"Atk: {p.attack_power()}  Def: {p.defense_value()}")
        slow_print(f"Gold: {p.gold}")
        
    def cmd_quests(self):
        if not self.player.quests:
             slow_print("No active quests.")
        else:
             for q_id, q_data in self.player.quests.items():
                 status = "Done" if q_data["done"] else "In Progress"
                 slow_print(f"- {q_data['desc']} ({status})")

    def random_event(self):
        roll = random.random()
        if roll < 0.08:
            slow_print("A cold wind blows through...")
        elif roll < 0.12:
            slow_print("You hear distant howling.")
        elif roll < 0.15:
            slow_print("A raven caws overhead.")
        elif roll < 0.18:
            # Small gold find
            found = random.randint(1, 5)
            self.player.gold += found
            slow_print(f"You found {found} gold coins on the ground!")
        elif roll < 0.20:
            slow_print("The shadows seem to move...")


    # --- Interaction ---
    
    def cmd_talk(self):
        r = self.current_room()
        if r.special == "merchant":
            slow_print("You meet a traveling merchant.")
            self.cmd_shop()
        elif r.enemy and r.enemy.alive():
            slow_print("The enemy attacks you as you try to speak!")
            self.cmd_attack()
        elif "lost_herb" not in self.player.quests:
            slow_print("A wanderer passes by.")
            slow_print("'I lost my healing herb in the meadow... could you find it?'")
            self.player.quests["lost_herb"] = {"desc": "Find herb for wanderer", "done": False}
        elif not self.player.quests["lost_herb"]["done"]:
            herb = self.player.find_item("herb")
            if herb:
                slow_print("'You found it! Thank you!'")
                slow_print("He gives you 15 gold.")
                self.player.gold += 15
                self.player.remove_item_by_id(herb.id)
                self.player.quests["lost_herb"]["done"] = True
            else:
                slow_print("'Please find my herb in the meadow.'")
        else:
            slow_print("The wanderer waves at you.")

    def cmd_shop(self):
        r = self.current_room()
        if r.special != "merchant":
            slow_print("There is no shop here.")
            return

        slow_print("Merchant: 'Welcome, traveler!'")
        
        while True:
            slow_print("\n(b)uy, (s)ell, or (l)eave?")
            choice = input_prompt("Shop> ").lower()
            
            if choice in ('l', 'leave', 'exit'):
                slow_print("Merchant: 'Come again!'")
                break
                
            elif choice in ('b', 'buy'):
                slow_print(f"\nYour gold: {self.player.gold}")
                for i, it in enumerate(self.merchant_goods):
                    price = int(it.value * 1.5)
                    slow_print(f"{i+1}. {it.name} - {price} gold")
                slow_print("Enter number to buy, or 0 to cancel.")
                c = input_prompt("Buy> ")
                if c.isdigit() and 1 <= int(c) <= len(self.merchant_goods):
                    idx = int(c) - 1
                    item = self.merchant_goods[idx]
                    price = int(item.value * 1.5)
                    if self.player.gold >= price:
                        self.player.gold -= price
                        new_item = Item.from_dict(item.to_dict())
                        self.player.add_item(new_item)
                        slow_print(f"Bought {item.name} for {price} gold.")
                    else:
                        slow_print("Not enough gold.")
                        
            elif choice in ('s', 'sell'):
                sellable = [it for it in self.player.inventory 
                           if it != self.player.equipped_weapon and it != self.player.equipped_armor]
                if not sellable:
                    slow_print("Nothing to sell.")
                    continue
                slow_print("\nSellable items:")
                for i, it in enumerate(sellable):
                    sell_price = int(it.value * 0.6)
                    slow_print(f"{i+1}. {it.name} - {sell_price} gold")
                slow_print("Enter number to sell, or 0 to cancel.")
                c = input_prompt("Sell> ")
                if c.isdigit() and 1 <= int(c) <= len(sellable):
                    idx = int(c) - 1
                    item = sellable[idx]
                    sell_price = int(item.value * 0.6)
                    self.player.remove_item_by_id(item.id)
                    self.player.gold += sell_price
                    slow_print(f"Sold {item.name} for {sell_price} gold.")
            else:
                slow_print("Invalid choice.")


    def cmd_riddle(self):
        r = self.current_room()
        if r.special != "riddle":
            slow_print("No puzzle here.")
            return
        if not r.locked:
            slow_print("The door is already open.")
            return
            
        slow_print("Inscription: 'I speak without a mouth and hear without ears. I have no body, but I come alive with wind. What am I?'")
        ans = input_prompt("Answer: ").lower()
        if "echo" in ans:
            slow_print("The stone door rumbles open!")
            r.locked = False
        else:
            slow_print("Nothing happens.")

    # --- Combat ---
    
    def cmd_attack(self):
        r = self.current_room()
        if not r.enemy or not r.enemy.alive():
            slow_print("No enemy here.")
            return
        
        enemy = r.enemy
        in_combat = True
        
        while in_combat and self.player.alive() and enemy.alive():
            slow_print(f"\n[{self.player.name}: {self.player.hp}/{self.player.max_hp} HP] vs [{enemy.name}: {enemy.hp}/{enemy.max_hp} HP]")
            slow_print("(a)ttack, (u)se item, (f)lee?")
            action = input_prompt("Combat> ").lower()
            
            if action in ('a', 'attack'):
                # Player attacks
                self._do_attack(self.player, enemy, use_player_stats=True)
                if not enemy.alive():
                    break
                # Enemy retaliates
                self._do_attack(enemy, self.player, use_player_stats=False)
                
            elif action in ('u', 'use'):
                slow_print("Use which item?")
                item_name = input_prompt("Item> ")
                self.cmd_use(item_name)
                # Enemy still attacks
                self._do_attack(enemy, self.player, use_player_stats=False)
                
            elif action in ('f', 'flee'):
                if random.random() < 0.5:
                    slow_print("You fled successfully!")
                    in_combat = False
                else:
                    slow_print("Couldn't escape!")
                    self._do_attack(enemy, self.player, use_player_stats=False)
            else:
                slow_print("Invalid action.")
        
        if not enemy.alive():
            slow_print(f"\nVictory! {enemy.name} defeated!")
            self.player.gain_xp(enemy.xp_reward)
            gold_found = enemy.gold_reward
            self.player.gold += gold_found
            slow_print(f"Found {gold_found} gold.")
            
            # Check for boss victory
            if enemy.name == "Obsidian Warden":
                self._victory_ending()
            return
            
        if not self.player.alive():
            slow_print("\nYou have been defeated...")
            self.player.hp = self.player.max_hp // 2
            lost_gold = int(self.player.gold * 0.2)
            self.player.gold -= lost_gold
            self.player.pos = Position(1,1)
            slow_print(f"You wake at the crossroads, having lost {lost_gold} gold.")

    def _do_attack(self, attacker, defender, use_player_stats=False):
        # Calculate attack and defense
        if use_player_stats and hasattr(attacker, 'attack_power'):
            atk_val = attacker.attack_power()
            def_val = defender.defense
        elif not use_player_stats and hasattr(defender, 'defense_value'):
            atk_val = attacker.atk
            def_val = defender.defense_value()
        else:
            atk_val = attacker.atk
            def_val = defender.defense
        
        # Dodge check
        dodge_roll = random.randint(1, 20)
        if dodge_roll <= defender.dodge:
            slow_print(f"{defender.name} dodged the attack!")
            return
        
        # Damage calculation
        base_dmg = max(1, atk_val - def_val + random.randint(-1, 2))
        
        # Critical hit
        is_crit = random.random() < 0.12
        if is_crit:
            base_dmg = int(base_dmg * 1.8)
            slow_print("CRITICAL HIT!")
        
        defender.hp -= base_dmg
        slow_print(f"{attacker.name} hits {defender.name} for {base_dmg} damage.")
        
    def _victory_ending(self):
        slow_print("\n" + "=" * 50)
        slow_print("CONGRATULATIONS!")
        slow_print("=" * 50)
        slow_print("\nYou have defeated the Obsidian Warden!")
        slow_print("The ancient keep trembles as peace returns to Asteria.")
        slow_print("Your name will be remembered in legends.")
        slow_print(f"\nFinal Stats: Level {self.player.level}, {self.player.gold} gold")
        slow_print("\nThank you for playing Echoes of Asteria!")
        slow_print("=" * 50)
        self.running = False


    # --- Persistence ---

    def save(self):
        try:
            data = {
                "version": "1.0",
                "player": self.player.to_dict(),
                "turn": self.turn_count
            }
            with open(self.player.save_slot, "w") as f:
                json.dump(data, f, indent=2)
            slow_print("Game saved.")
        except Exception as e:
            slow_print(f"Save failed: {e}")

    def load(self):
        if not os.path.exists(self.player.save_slot):
            slow_print("No save found.")
            return
        try:
            with open(self.player.save_slot, "r") as f:
                data = json.load(f)
            self.player = Player.from_dict(data["player"])
            self.turn_count = data.get("turn", 0)
            slow_print("Game loaded.")
        except Exception as e:
            slow_print(f"Load failed: {e}")
