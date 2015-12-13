from functools import lru_cache
import json
import os
from retrying import retry
import requests
import util

with open('config.json') as f:
    config = json.load(f)

api_key = os.environ.get('LOL_API_KEY')
api_key = api_key[:-1] if '\r' == api_key[-1:] else api_key


class LeagueRequest:

    def get(url):
        url_auth = ('%s?api_key=%s' % (url, api_key))
        request_info = requests.get(url_auth)

        if request_info.status_code != 200:
            raise ValueError(request_info.json()['status']['message'])

        return request_info.json()


class Summoner:

    def __init__(self):
        self.base_url = '%s%s/v1.4/summoner/' % (config['base_url'], config['region'])

    def get_summoners_info_by_names(self, summoner_names):
        """Get info about summoners by summoner names

        Keyword arguments:
        summoner_names -- list of summoner names to query
        """

        results = []
        for subset in util.grouper(summoner_names, 40):
            url = self.base_url + 'by-name/' + ','.join(name for name in subset if name)
            print("by_names: %s" % url)
            results.append(LeagueRequest.get(url))

        return util.dict_merge(results)

    def get_summoners_info_by_ids(self, summoner_ids):
        """Get info about summoners by summoner ids

        Keyword arguments:
        summoner_ids -- list of summoner ids to query
        """

        results = []
        for subset in util.grouper(summoner_ids, 40):
            url = self.base_url + ','.join(str(summoner_id) for summoner_id in subset if summoner_id)
            print("by_ids: %s" % url)
            results.append(LeagueRequest.get(url))

        return util.dict_merge(results)

    def get_summoner_names_by_ids(self, summoner_ids):
        """Get summoner names by their ids

        Keyword arguments:
        summoner_ids -- list of summoner ids to query
        """
        results = []
        for subset in util.grouper(summoner_ids, 40):
            url = self.base_url + ','.join(str(summoner_id) for summoner_id in subset if summoner_id) + '/name'
            print("names_by_ids: %s" % url)
            results.append(LeagueRequest.get(url))

        return util.dict_merge(results)

class Game:

    def __init__(self):
        self.base_game_url = '%s%s/v1.3/game/by-summoner/%s/recent' % (config['base_url'], config['region'], '%d')
        self.base_match_url = '%s%s/v2.2/match/%s' % (config['base_url'], config['region'], '%d')

    def get_recent_games(self, summoner_id):
        """Get 10 most recent games of a summoner

        Keyword arguments:
        summoner_id -- summoner id for querying the recent games
        """
        url = self.base_game_url % summoner_id
        return LeagueRequest.get(url)

    def get_match_info(self, match_id):
        """Get detailed info about a match

        Keyword arguments:
        summoner_id -- id of the match
        """
        url = self.base_match_url % match_id
        return LeagueRequest.get(url)
