"""
For debugging. Adds a number to the beginning of each game's title.
"""

from protocol import Game


def mod(games):
    for i, game in enumerate(games):
        game.title = f"{i+1}) ".encode() + game.title

    return games
