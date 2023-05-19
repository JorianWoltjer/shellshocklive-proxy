"""
Creates games with titles of Rick Astley's "Never Gonna Give You Up" lyrics.
"""

from protocol import Game


def mod(games):
    with open("mods/rickroll-titles.txt", "r") as f:
        titles = [line.strip() for line in f]

    games = [Game(title=title, host="Rick Astley") for title in titles]

    return games
