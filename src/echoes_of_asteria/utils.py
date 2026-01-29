"""Utility functions for the game."""

import os
import sys
import time
import textwrap
from collections import namedtuple

Position = namedtuple("Position", ["x", "y"])


def clear_screen():
    """Clear the terminal screen."""
    os.system("cls" if os.name == "nt" else "clear")


def slow_print(text, delay=0.01):
    """Print text character by character for effect."""
    for ch in text:
        print(ch, end="", flush=True)
        time.sleep(delay)
    print()


def wrap_text(text, width=70):
    """Wrap text to specified width."""
    return "\n".join(textwrap.wrap(text, width=width))


def input_prompt(prompt_text="> "):
    """Get user input with prompt."""
    return input(prompt_text).strip()


def choose_option(options):
    """Present numbered options and return chosen index."""
    for i, opt in enumerate(options, 1):
        print(f"{i}. {opt}")
    while True:
        choice = input_prompt("Choose number: ")
        if choice.isdigit() and 1 <= int(choice) <= len(options):
            return int(choice) - 1
