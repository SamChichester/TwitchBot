import os
from twitchio import Client
from twitchio.ext import pubsub
from obswebsockets import OBSWebsocket


class Config:
    def __init__(self):
        self.my_token = os.environ.get('ACCESS_TOKEN')
        self.users_oauth_token = os.environ.get('OAUTH_TOKEN')
        self.users_channel_id = int(os.environ.get('BROADCASTER_ID'))


class TwitchClient:
    def __init__(self, config):
        self.client = Client(token=config.my_token)
        self.pubsub_pool = pubsub.PubSubPool(client=self.client)
        self.config = config

        @self.client.event()
        async def event_pubsub_channel_points(event: pubsub.PubSubChannelPointsMessage):
            if event.reward.title == 'Move Pipe':
                print('--- Redeemed Pipe Reward ---')
                obs = OBSWebsocket()
                obs.pipe_animation(scene_name='Gaming', source_name1='Camera', source_name2='Pipe')
                obs.disconnect()
                print('\tRan pipe animation')

    async def main(self):
        topics = [
            pubsub.channel_points(self.config.users_oauth_token)[self.config.users_channel_id],
        ]
        await self.pubsub_pool.subscribe_topics(topics)
        await self.client.start()

    def run(self):
        self.client.loop.run_until_complete(self.main())


class Application:
    def __init__(self):
        self.config = Config()
        self.twitch_client = TwitchClient(config=self.config)

    def run(self):
        print('--- Running Twitch Client ---')
        self.twitch_client.run()
