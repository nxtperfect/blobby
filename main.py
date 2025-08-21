from os import getenv
from dotenv import load_dotenv
import discord

load_dotenv()
_TOKEN = getenv("DISCORD_TOKEN")

client = discord.Client(intents=discord.Intents.default())


@client.event
async def on_ready():
    print(f"{client.user} connected!")
    for guild in client.guilds:
        print(f"Connected to {guild.name}")


client.run(_TOKEN)


def main():
    print("Hello from blobby!")
    client.run()


if __name__ == "__main__":
    main()
