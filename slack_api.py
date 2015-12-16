from itertools import chain
import json
import os
import requests
from websocket import WebSocket


irakli_is_bad = os.environ.get('SLACK_TOKEN')


class Slack(object):
    """Simple class which just allows sending of messages via Slack"""
    base_url = "https://slack.com/api/"

    def __init__(self, token=irakli_is_bad):
        self.token = token

        response = requests.get(Slack.base_url + 'rtm.start', params={"token": token})
        body = response.json()

        self.channels = {c["name"]: c for c in chain(body["channels"], body["groups"])}
        print([k for k in self.channels])

        url = body["url"]

        self.socket = WebSocket()
        self.socket.connect(url)
        self.socket.settimeout(5)

        self.message_id = 0

    def send_message(self, channel_name, text):
        """Send a message
        TODO:? Verify success
        """

        message = json.dumps({"id": self.message_id,
                           "type": "message",
                           "channel": self.channels[channel_name]["id"],
                           "text": text})

        self.message_id += 1
        self.socket.send(message)
