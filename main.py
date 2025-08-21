from os import getenv
from typing import Callable
from dotenv import load_dotenv
import discord
from discord.ext import commands


class Blobby(discord.Client):
    _TOKEN: str | None
    prefix: str = "#!"

    def __init__(self, intents=discord.Intents.default()):
        load_dotenv()
        self._TOKEN = getenv("DISCORD_TOKEN")
        intents.messages = True
        intents.message_content = True
        super().__init__(intents=intents)

    async def on_ready(self):
        print(f"{super().user} connected!")

    async def on_message(self, message):
        if message.author == super().user:
            return

        if not message.content.startswith(self.prefix):
            return
        await self._handle_command(message)

    async def _handle_command(self, message):
        command = message.content.split(self.prefix)[-1]

        if command == "ping":
            await message.channel.send("Pong!")

        if command.startswith("kick"):
            if len(command.split()) == 3:
                command, member, reason = command.split()
                await self.kick(member, reason)
                return
            command, member = command.split()
            await self.kick(member)

        if command.startswith("ban"):
            if len(command.split()) == 3:
                command, member, reason = command.split()
                await self.ban(member, reason)
                return
            command, member = command.split()
            await self.ban(member)

        return

    @commands.has_permissions(kick_members=True)
    async def kick(self, member, reason: str | None = None):
        await bot.kick(member, reason)

    @commands.has_permissions(ban_members=True)
    async def ban(self, member, reason: str | None = None):
        await bot.ban(member, reason)

    def run(self):
        super().run(self._TOKEN)


# client = discord.Client(intents=discord.Intents.default())


def main():
    print("Hello from blobby!")
    client = Blobby()
    client.run()


if __name__ == "__main__":
    main()
