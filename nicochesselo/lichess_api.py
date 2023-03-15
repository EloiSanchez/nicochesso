import json
import requests
import chess.pgn as pgn
from chess import IllegalMoveError
import io


DEFAULT_GAME_TYPES = ('classical', 'rapid', 'blitz', 'bullet')


def _resp_to_json(response):
    """Parse an API text response to JSON

    Returns:
        json dict: API response as JSON dict
    """
    return json.loads(response.text)


def _get_field(json_list, field = 'username'):
    """Gets a field from a list of JSON dicts

    Args:
        json_list (list): list of JSON dicts containing the `field` key
        field (str, optional): the field to be recovered from each item in the
        list. Defaults to 'username'.

    Returns:
        set: a set with the values of the `field` of each element of the list
    """
    return set(x[field] for x in json_list)


def get_leaderboard(
    game_modes = ('classical', 'rapid', 'blitz', 'bullet'), n=200
    ):
    """Get the `n` top players of the requested game modes

    Args:
        game_modes (tuple, optional): Strings identifying the different game
        mode leaderboards to get the players.
        Defaults to ('classical', 'rapid', 'blitz', 'bullet').
        n (int, optional): Number of players to take from each leaderboard.
        Defaults to 200.

    Returns:
        set: a set of players found in the leaderboards
    """
    users = set()
    for game_mode in game_modes:
        users = users.union(_get_field(_resp_to_json(
            requests.get(f'https://lichess.org/api/player/top/{n}/{game_mode}')
            )['users']))
    return users


def get_streamers():
    """gets the currently streaming players in lichess

    Returns:
        set: a set of players found in the leaderboards
    """
    return set(_get_field(_resp_to_json(
        requests.get(f'https://lichess.org/api/streamer/live')
        ), 'name'))


# TODO: Get game by ID
def get_games(usernames, n = 100):
    """Gets `n` or all games of the players passed.

    Args:
        usernames (iterable | str): usernames that played the games to
        be downloaded
        n (int, optional): number of games to be downloaded. If not a positive
        number, it will be set to download all games of the players.
        Defaults to 100.

    Returns:
        _type_: _description_
    """
    usernames = [usernames] if type(usernames) == str else usernames
    n = n if n > 0 else ''

    game_info_params = {
        'max' : f'{n}',
        'perfType' : ','.join(DEFAULT_GAME_TYPES),
        'evals' : 'false',
        'opening': 'true'
    }

    games = []
    for user in usernames:
        print(f'getting {user}')
        games += _parse_games(
            requests.get(f'https://lichess.org/api/games/user/{user}',
                         params = game_info_params)
        )
    return games


def _parse_games(response):
    games = []
    with io.StringIO(response.text) as games_text:
        while True:
            # TODO: Silence errors
            game = pgn.read_game(games_text)

            if game is None:
                break

            if len(game.errors) > 0:
                continue

            games.append(game)
    return games


def get_default_games(n_users=200, n_games=100):
    return get_games(
        get_leaderboard(n=n_users),
        n=n_games
        )


def get_player_info(username):
    return _resp_to_json(requests.get(f'https://lichess.org/api/user/{username}'))