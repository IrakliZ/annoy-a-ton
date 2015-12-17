#!/usr/bin/env python3
import json
from match_data import DataCollector
from random import choice
import slack_api
from threading import Thread


class Controller(object):
    def __init__(self):
        self.the_player = 'Synz0331'
        self.collector = DataCollector(self.the_player)

        self.slack = slack_api.Slack()
        self.channel = 'quinn-facts'
        self.lytes = [line.strip() for line in open('lyte.txt')]

        self.champs = json.load(open('champs.json'))
        self.champs = {int(k): v for k, v in self.champs.items()}

        self.thread = Thread(target=self.collector.start_tracking)
        self.thread.start()

    def run(self):
        while True:
            print("Waiting for game")
            match_info = self.collector.get_game()
            print("Got game")
            p_num = next(p['participantId'] for p in match_info['participantIdentities'] if p['player']['summonerName'] == self.the_player)
            participant = next(p for p in match_info['participants'] if p['participantId'] == p_num)
            team = participant['teamId']
            won = next(t for t in match_info['teams'] if t['teamId'] == team)

            if not won:
                stats = participant['stats']

                kills = stats['kills']
                deaths = stats['deaths']
                assists = stats['assists']
                champ = self.champs[participant['championId']]
                quote = choice(self.lytes)
                message = "Quinn lost a game as %d/%d/%d %s and lost. %s" % (kills, deaths, assists, champ, quote)

                self.slack.send_message(self.channel, message)


if __name__ == "__main__":
    c = Controller()
    c.run()
