from collections import deque
from os import getenv
from dotenv import load_dotenv
import discord
from discord.ext import commands
import numpy as np
from random import shuffle


class Blobby(commands.Bot):
    prefix: str = "#!"
    players_started_platformer: dict[str, int] = {}
    _board: str = f"{'◽'*4}\n{'◼️'*3}◽\n👺{'◽'*3}\n{'◼️'*4}"
    _board_size: int = 6
    _movement: dict[str, tuple[int, int]] = {
        "⬆️": (-1, 0),
        "⬇️": (1, 0),
        "⬅️": (0, -1),
        "➡️": (0, 1),
    }
    _player_location: tuple[int, int] = (2, 0)

    def __init__(self, intents: discord.Intents | None = None):
        if not intents:
            intents = discord.Intents.default()
        _ = load_dotenv()
        self._TOKEN: str | None = getenv("DISCORD_TOKEN")
        intents.messages = True
        intents.message_content = True
        super().__init__(self.prefix, intents=intents)

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
        # Read reactions under message
        # If user who started added reaction
        # take the first one and move
        # then reset reactions
        # and loop again
        reaction = await self.wait_for(
            "reaction_add", check=lambda _, user: user.id == member.id
        )

        await self._move(reaction[0])
        # Redraw the board now
        self._build_platformer_board()
        # await channel.send(f"{member} reacted with {reaction[0]}")

    async def _start_platformer(self, member, channel):
        board = self._build_platformer_board()
        embedVar = discord.Embed(
            title=f"Platformer game {member.global_name}",
            description=board,
            color=0xFF0808,
        )
        return await channel.send(embed=embedVar)

    def _build_platformer_board(self):
        # Randomize platform but make it possible to finish?
        # start in some random spot on the border
        # then check neighbors in random order
        # if they're within boundaries and are a wall
        # go there
        # if not, remove current pos from stack
        # and continue

        starting_positions: list[tuple[int, int]] = [
            (0, x) for x in range(self._board_size)
        ]
        starting_positions.append([(y, 0) for y in range(self._board_size)])
        shuffle(starting_positions)

        # Start in starting_positions[0]
        # go dfs
        queue = deque()
        queue.append(starting_positions[0])
        random_directions = self._movement.values()
        shuffle(random_directions)
        # dfs try to reach the player
        # only move if that tile is a wall - 1
        while queue:
            x, y = queue.pop()
            for rx, ry in random_directions:
                nx, ny = x + rx, y + ry
                if nx not in range(self._board_size) or ny not in range(
                    self._board_size
                ):
                    continue
                if self.board[nx][ny] == 1:
                    queue.append((nx, ny))
            pass
        return self._board

    async def _add_movement_keys(self, message):
        await message.add_reaction(str("⬅️"))
        await message.add_reaction(str("➡️"))
        await message.add_reaction(str("⬆️"))
        await message.add_reaction(str("⬇️"))

    async def _move(self, emoji):
        move = self._movement.get(emoji, None)
        if not move:
            return False

        # Move player
        # Need to know where player is
        # if move will be out of bounds
        # if yes re-render the message with no move
        temp = np.add(self._player_location, move)
        if temp[0] not in range(0, len(self._board)) or temp[1] not in range(
            0, len(self._board[0])
        ):
            return False
        self._player_location = temp

    def run(self):
        super().run(self._TOKEN)


def main():
    print("Hello from blobby!")
    client = Blobby()
    client.run()


if __name__ == "__main__":
    main()
