import boto3
from league_api import Summoner, Game, NotFoundException
import pickle
import time
from queue import Queue


table_name = 'league_data'
attribute_name = 'match_id'


class DataCollector:

    def __init__(self, summoner_name):
        self.summoner_name = summoner_name.lower().replace(' ', '')
        self.game = Game()
        self.dynamo_controller = DynamoData()

        try:
            self.table = self.dynamo_controller.get_table(self.summoner_name)
        except ValueError:
            self.table = self.dynamo_controller.setup_table(self.summoner_name, attribute_name)

        self.output = Queue()

    def start_tracking(self):
        summoner = Summoner()
        summoner_info = summoner.get_summoners_info_by_names([self.summoner_name])
        summoner_id = summoner_info[self.summoner_name]['id']
        current_match_id = None

        while True:
            print('Tracking outer loop')
            try:
                current_match = self.game.get_current_match(summoner_id)
                self.track_in_game(current_match, summoner_id)
            except NotFoundException:
                time.sleep(600)

    def track_in_game(self, current_match, summoner_id):
        def player_mapper(p_id, participant):
            player = {'summonerId': participant['summonerId'],
                      'summonerName': participant['summonerName'],
                      'profileIcon': participant['profileIconId']}

            return {'participantId': p_id, 'player': player}
        match_id = current_match['gameId']
        match_id_temp = match_id
        while match_id_temp == match_id:
            print('Tracking inner %d' % match_id)
            try:
                current_match_temp = self.game.get_current_match(summoner_id)
                print('ANOTHER MATCH WAS FOUND')
                match_id_temp = current_match_temp['gameId']
            except NotFoundException:
                break

            time.sleep(60)

        print('TRACKING INNER DONE')
        print('CURRENT_MATCH %s' % str(current_match))

        counter = 0
        match_info = None
        while True:
            print('TRYING TO GET MOST RECENT ENDED GAME')
            try:
                match_info = self.game.get_match_info(match_id)
                break
            except NotFoundException:
                counter += 1
                time.sleep(10)
                if counter > 20:
                    return

        print('GOT MOST RECENT ENDED GAME')

        pickle.dump((current_match, match_info), open('saved.p', 'wb'))
        player_map = {(p['championId'], p['teamId']): p for p in current_match['participants']}

        game_data = {'match_id': match_id, 'match_info': match_info}
        self.table.put_item(Item=game_data)

        # populate participant identities, ruck fito
        match_info['participantIdentities'] = [player_mapper(p['participantId'], player_map[p['championId'], p['teamId']]) for p in match_info['participants']]

        self.table.put_item(Item=game_data)
        self.output.put(match_info)

    # TODO: Replace this a wait/notify method instead
    def get_game(self):
        while self.output.empty():
            time.sleep(10)
        return self.output.get()


class DynamoData:

    def __init__(self):
        self.dynamodb = boto3.resource('dynamodb')

    def get_table(self, table_name):
        table = self.dynamodb.Table(table_name)
        if table in self.dynamodb.tables.all():
            return table
        else:
            raise ValueError('Table %s not yet created' % table_name)

    def setup_table(self, table_name, attribute_name):
        table = self.dynamodb.create_table(
            TableName=table_name,
            KeySchema=[dict(AttributeName=attribute_name, KeyType='HASH')],
            AttributeDefinitions=[dict(AttributeName=attribute_name, AttributeType='N')],
            ProvisionedThroughput=dict(ReadCapacityUnits=5, WriteCapacityUnits=5)
        )

        return table
