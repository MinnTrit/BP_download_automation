import discord
import os
import asyncio
from discord import Intents, Client, Message

channel_id = int(os.getenv('DISCORD_CHANNEL_ID'))
discord_token = os.getenv('DISCORD_TOKEN')

class MyClient(discord.Client):
    def __init__(self, message, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.message = message

    async def on_ready(self):
        print(f'Logged in as {self.user}')
        channel = self.get_channel(channel_id)
        if channel:
            await self.send_message(channel)
            await self.close()
        else:
            print(f"Could not find channel with ID {channel_id}")

    async def send_message(self, channel):
        await channel.send(self.message)

def create_discord_client(client_message):
    intents = Intents.default()
    return MyClient(message=client_message, intents=intents)

async def run_discord_client(client):
    await client.start(discord_token)
