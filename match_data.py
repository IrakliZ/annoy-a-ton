import os
import requests
import json
import boto3
from league_api import Summoner, Game

table_name = 'league_data'
attribute_name = 'summoner_name'


class DataCollector:

    def __init__(self, summoner_name):
        self.summoner_name = summoner_name
        self.summoner = Summoner()
        self.game = Game()
        self.dynamo_controller = DynamoData()

    def track_summoner(self):
        try:
            table = self.dynamo_controller.get_table(table_name)
        except ValueError:
            table = self.initial_setup()

    def initial_setup(self):
        return self.dynamo_controller.setup_table(table_name, attribute_name)



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
