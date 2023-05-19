"""
Changes the Friends Only and Level Difference settings to allow you to join any game, regardless of protection settings.
- Puts [FRIENDS] in the title if Friends Only was bypassed
- Puts [LEVEL] in the title if Level Difference was bypassed
"""

from protocol import Game


def allow_join(game: Game):
    CURRENT_LEVEL = 70  # Used to tell if you should be able to join a game or not

    if game.friends == b"True":
        game.friends = False
        game.title += b" [FRIENDS]"
        return
    if abs(int(game.avglvl) - CURRENT_LEVEL) > int(game.lvldiff):
        game.lvldiff = 100
        game.title += b" [LEVEL]"
        return


def mod(games):
    for game in games:
        allow_join(game)

    return games
