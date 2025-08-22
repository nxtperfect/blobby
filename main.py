from os import getenv
from dotenv import load_dotenv
import discord
from discord.ext import commands


class Blobby(discord.Client):
    _TOKEN: str | None
    prefix: str = "#!"
    players_started_platformer: dict[str, int] = {}

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
        whole_command = message.content.split(self.prefix)[-1]
        command = whole_command.split()[0]

        if command == "ping":
            await message.channel.send("Pong!")

        if command == "kick":
            if len(whole_command.split()) == 3:
                whole_command, member, reason = whole_command.split()
                await self.kick(member, reason)
                return
            whole_command, member = whole_command.split()
            await self.kick(member)

        if command == "ban":
            if len(whole_command.split()) == 3:
                whole_command, member, reason = whole_command.split()
                await self.ban(member, reason)
                return
            whole_command, member = whole_command.split()
            await self.ban(member)

        if command == "platformer":
            await self.platformer(message.author, message.channel)

        return

    @commands.has_permissions(kick_members=True)
    async def kick(self, member, reason: str | None = None):
        await bot.kick(member, reason)

    @commands.has_permissions(ban_members=True)
    async def ban(self, member, reason: str | None = None):
        await bot.ban(member, reason)

    async def platformer(self, member, channel):
        # Initialize the game if not already started
        if member.id in self.players_started_platformer:
            await channel.send("You already started platformer!")
            return
        self.players_started_platformer[member.id] = 1
        embed = await self._start_platformer(member, channel)
        await self._add_movement_keys(embed)
        # If already started read movements

    async def _start_platformer(self, member, channel):
        board = self._build_platformer_board()
        embedVar = discord.Embed(
            title=f"Platformer game {member.global_name}",
            description=board,
            color=0xFF0808,
        )
        return await channel.send(embed=embedVar)

    def _build_platformer_board(self):
        return f"{'◽'*4}\n{'◼️'*3}◽\n👺{'◽'*3}\n{'◼️'*4}"

    async def _add_movement_keys(self, message):
        await message.add_reaction(str("⬅️"))
        await message.add_reaction(str("➡️"))
        await message.add_reaction(str("⬆️"))
        await message.add_reaction(str("⬇️"))

    def run(self):
        super().run(self._TOKEN)


def main():
    print("Hello from blobby!")
    client = Blobby()
    client.run()


if __name__ == "__main__":
    main()
