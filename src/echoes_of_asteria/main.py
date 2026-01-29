"""Main entry point for Echoes of Asteria."""

from .game import Game


def main():
    """Start the game."""
    game = Game()
    game.start()


if __name__ == "__main__":
    main()
