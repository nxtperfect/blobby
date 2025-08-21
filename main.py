from os import getenv
from dotenv import load_dotenv
import discord


class Blobby(discord.Client):
    _TOKEN: str | None

    def __init__(self, intents=discord.Intents.default()):
        load_dotenv()
        self._TOKEN = getenv("DISCORD_TOKEN")
        super().__init__(intents=intents)

    async def on_ready(self):
        print(f"{super().user} connected!")

    def run(self):
        super().run(self._TOKEN)


# client = discord.Client(intents=discord.Intents.default())


def main():
    print("Hello from blobby!")
    client = Blobby()
    client.run()


if __name__ == "__main__":
    main()
