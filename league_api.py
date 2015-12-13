import os
import requests
import json
from functools import lru_cache
from retrying import retry

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
        self.lol_request = LeagueRequest()

    def get_summoners_info_by_names(self, summoner_names):
        """Get info about summoners by summoner names

        Keyword arguments:
        summoner_names -- list of summoner names to query
        """
        if len(summoner_names) > 40:
            raise ValueError('Too many summoners') #TODO: Add handling of request with more than 40 summoners

        url = self.base_url + 'by-name/' + ','.join(summoner_names)
        return LeagueRequest.get(url)

    def get_summoners_info_by_ids(self, summoner_ids):
        """Get info about summoners by summoner ids

        Keyword arguments:
        summoner_ids -- list of summoner ids to query
        """
        if len(summoner_ids) > 40:
            raise ValueError('Too many summoners') #TODO: Add handling of request with more than 40 summoners

        url = self.base_url + ','.join(str(summoner_id) for summoner_id in summoner_ids)
        return LeagueRequest.get(url)

    def get_summoner_names_by_ids(self, summoner_ids):
        """Get summoner names by their ids

        Keyword arguments:
        summoner_ids -- list of summoner ids to query
        """
        if len(summoner_ids) > 40:
            raise ValueError('Too many summoners') #TODO: Add handling of request with more than 40 summoners

        url = self.base_url + ','.join(str(summoner_id) for summoner_id in summoner_ids) + '/name'
        return LeagueRequest.get(url)
