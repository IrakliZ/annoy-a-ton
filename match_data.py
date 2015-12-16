import os
import decimal
import requests
import json
import boto3
import time
from league_api import Summoner, Game

table_name = 'league_data'
attribute_name = 'summoner_name'


class DataCollector:

    def __init__(self, summoner_name):
        self.summoner_name = summoner_name.lower()
        self.game = Game()
        self.dynamo_controller = DynamoData()
        self.table = None

    def get_existing_summoner_data(self):
        try:
            self.table = self.dynamo_controller.get_table(table_name)
        except ValueError:
            self.table = self.dynamo_controller.setup_table(table_name, attribute_name)

        summoner_data = self.table.get_item(Key=dict(summoner_name=self.summoner_name))
        print(summoner_data)

        if 'Item' not in summoner_data: #Check if item already exists in dynamodb
            summoner_data = self.initial_setup()
        else:
            summoner_data = summoner_data['Item']

        return summoner_data

    def initial_setup(self):
        initial_data = {
            'summoner_name': self.summoner_name,
            'game_ids': [],
            'games': []
        }

        self.table.put_item(Item=initial_data)
        return initial_data

    def start_tracking(self):
        summoner = Summoner()
        summoner_info = summoner.get_summoners_info_by_names([self.summoner_name])
        summoner_id = summoner_info[self.summoner_name]['id']
        current_match_id = None

        while True:
            print('Traking in outter loop')
            try:
                current_match = self.game.get_current_match(summoner_id)
                current_match_id = current_match['gameId']
                self.track_in_game(current_match_id, summoner_id)
            except ValueError:
                time.sleep(600)



    def track_in_game(self, match_id, summoner_id):
        match_id_temp = match_id
        current_match = None
        while match_id_temp == match_id:
            print('Tracking the match %d' % match_id)
            try:
                current_match = self.game.get_current_match(summoner_id)
                match_id_temp = current_match['gameId']
            except ValueError:
                break
            
            time.sleep(60)
        
        match_info = self.game.get_match_info(match_id)
        stored_data = self.get_existing_summoner_data()
        stored_data['game_ids'].append(match_id)
        stored_data['games'].append(match_info)

        self.table.put_item(Item=stored_data)


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
            AttributeDefinitions=[dict(AttributeName=attribute_name, AttributeType='S')],
            ProvisionedThroughput=dict(ReadCapacityUnits=5, WriteCapacityUnits=5)
        )

        return table
