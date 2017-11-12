import requests
import configparser


# Configure the Library
config = configparser.RawConfigParser()
config.read("config.conf")
api_key = config.get("RiotAPI", "api_key")

# Configure API URLs
api_root = "https://americas.api.riotgames.com{}?api_key=" + api_key
match_api_root = "https://na1.api.riotgames.com{}?api_key=" + api_key


def create_provider(callback_url, region="NA"):
    """
    Uses the Tournament API to create a tournament provider and return ID
    :param callback_url: the callback URL where game results will be sent
    :param region: the LoL region
    :return: int provider_id
    """
    request_body = {
        "region": region,
        "url": callback_url
    }

    request_url = "/lol/tournament/v3/providers"
    full_url = api_root.format(request_url)
    result = requests.post(full_url, json=request_body)
    return result.json()


def create_tournament(name, provider_id):
    """
    Uses the Tournament API to create a Tournament and return its ID
    :param name: The name of the tournament
    :param provider_id: the tournament provider_id
    :return: int tournament_id
    """
    request_body = {
        "name": name,
        "providerId": provider_id
    }

    request_url = "/lol/tournament/v3/tournaments"
    full_url = api_root.format(request_url)
    result = requests.post(full_url, json=request_body)
    return result.json()


def create_tournament_code(tournament_id, map_type="SUMMONERS_RIFT", metadata="", pick_type="DRAFT_MODE", spectator_type="ALL", team_size=5):
    """
    Uses the Tournament API to get tournament codes
    :param tournament_id: tournament_id
    :param map_type: The map type of the game. (Legal values: SUMMONERS_RIFT, TWISTED_TREELINE, HOWLING_ABYSS)
    :param metadata: Optional string that may contain any data in any format, if specified at all. Used to denote any custom information about the game.
    :param pick_type: The pick type of the game. (Legal values: BLIND_PICK, DRAFT_MODE, ALL_RANDOM, TOURNAMENT_DRAFT)
    :param spectator_type: The spectator type of the game. (Legal values: NONE, LOBBYONLY, ALL)
    :param team_size: The team size of the game. Valid values are 1-5.
    :return: list of tournament codes
    """
    request_body = {
        "mapType": map_type,
        "metadata": metadata,
        "pickType": pick_type,
        "spectatorType": spectator_type,
        "teamSize": team_size
    }

    request_url = "/lol/tournament/v3/codes"
    full_url = api_root.format(request_url) + "&tournamentId={}".format(tournament_id)
    result = requests.post(full_url, json=request_body)
    return result


def get_lobby_events(tournament_code):
    """
    Uses the Tournament API to get lobby events
    :param tournament_code: the tournament code
    :return:
    """
    request_url = "/lol/tournament/v3/lobby-events/by-code/{}".format(tournament_code)
    full_url = api_root.format(request_url)
    result = requests.get(full_url)
    return result.json()


def get_match(match_id, tournament_code):
    """
    Return a match DTO from a match ID + tournament code
    :param match_id:
    :param tournament_code:
    :return:
    """
    request_url = '/lol/match/v3/matches/{}/by-tournament-code/{}'.format(match_id, tournament_code)
    full_url = match_api_root.format(request_url)
    result = requests.get(full_url)

    if result.status_code != 200:
        return None
    else:
        return result.json()


def get_match_id_list(tournament_code):
    """
    Takes a tournament code and returns a list of match IDs
    :param tournament_code:
    :return:
    """
    request_url = '/lol/match/v3/matches/by-tournament-code/{}/ids'.format(tournament_code)
    full_url = match_api_root.format(request_url)
    result = requests.get(full_url)

    if result.status_code != 200:
        return []
    else:
        return result.json()


def get_tournament_code_dto():
    pass


def update_tournament_code():
    pass


def stub_create_provider(callback_url, region="NA"):
    """
    Uses the Tournament stub API to create a mock provider and return ID
    :param callback_url: the callback URL where game results will be sent
    :param region: the LoL region
    :return: int provider_id
    """
    request_body = {
        "region": region,
        "url": callback_url
    }

    request_url = "/lol/tournament-stub/v3/providers"
    full_url = api_root.format(request_url)
    result = requests.post(full_url, json=request_body)
    return result.json()


def stub_create_tournament(name, provider_id):
    """
    Uses the Tournament stub API to create a mock Tournament and return its ID
    :param name: The name of the tournament
    :param provider_id: the tournament provider_id
    :return: int tournament_id
    """
    request_body = {
        "name": name,
        "providerId": provider_id
    }

    request_url = "/lol/tournament-stub/v3/tournaments"
    full_url = api_root.format(request_url)
    result = requests.post(full_url, json=request_body)
    return result.json()


def stub_create_tournament_code(tournament_id, map_type="SUMMONERS_RIFT", metadata="", pick_type="DRAFT_MODE", spectator_type="ALL", team_size=5):
    """
    Uses the Tournament stub API to get mock tournament codes
    :param tournament_id: tournament_id
    :param map_type: The map type of the game. (Legal values: SUMMONERS_RIFT, TWISTED_TREELINE, HOWLING_ABYSS)
    :param metadata: Optional string that may contain any data in any format, if specified at all. Used to denote any custom information about the game.
    :param pick_type: The pick type of the game. (Legal values: BLIND_PICK, DRAFT_MODE, ALL_RANDOM, TOURNAMENT_DRAFT)
    :param spectator_type: The spectator type of the game. (Legal values: NONE, LOBBYONLY, ALL)
    :param team_size: The team size of the game. Valid values are 1-5.
    :return: list of tournament codes
    """
    request_body = {
      "mapType": map_type,
      "metadata": metadata,
      "pickType": pick_type,
      "spectatorType": spectator_type,
      "teamSize": team_size
    }

    request_url = "/lol/tournament-stub/v3/codes"
    full_url = api_root.format(request_url) + "&tournamentId={}".format(tournament_id)
    result = requests.post(full_url, json=request_body)
    return result


def stub_get_lobby_events(tournament_code):
    """
    Uses the Tournament stub API to get mock lobby events
    :param tournament_code: the tournament code
    :return:
    """
    request_url = "/lol/tournament-stub/v3/lobby-events/by-code/{}".format(tournament_code)
    full_url = api_root.format(request_url)
    result = requests.get(full_url)
    return result.json()

