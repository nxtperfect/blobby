from collections import deque
from os import getenv
from dotenv import load_dotenv
import discord
from discord.ext import commands
import numpy as np
from random import choice, randrange, shuffle

EMPTY_TILE = 0
WALL_TILE = 1
PLAYER_TILE = 2
EXIT_TILE = 3
END_GAME_EMOJI = str("❌")


class Blobby(commands.Bot):
    prefix: str = "#!"
    players_started_platformer: dict[str, int] = {}
    _board_size: int = 12
    board: list[list[int]]
    _movement: dict[str, tuple[int, int]] = {
        "⬆️": (-1, 0),
        "⬇️": (1, 0),
        "⬅️": (0, -1),
        "➡️": (0, 1),
    }
    _player_location: tuple[int, int] = (-1, -1)
    _exit_location: tuple[int, int] | None = None
    _is_game_finished = False

    def __init__(self, intents: discord.Intents | None = None):
        if not intents:
            intents = discord.Intents.default()
        _ = load_dotenv()
        self.board = [[WALL_TILE] * self._board_size for _ in range(self._board_size)]
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
        if self.players_started_platformer.get(member.id, 0):
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

        if str(reaction[0]) == END_GAME_EMOJI:
            self.players_started_platformer[member.id] = 0
            await channel.send("You quit platformer.")
            return
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
        starting_positions: list[tuple[int, int]] = [
            (0, x) for x in range(self._board_size)
        ]
        starting_positions = starting_positions + [
            (y, 0) for y in range(self._board_size)
        ]
        shuffle(starting_positions)

        queue = deque()
        queue.append(starting_positions[0])
        random_directions = list(self._movement.values())
        visited_cells: list[tuple[int, int]] = []

        while queue:
            x, y = queue.pop()
            visited_cells.append((x, y))
            shuffle(random_directions)
            self.board[x][y] = 0

            for rx, ry in random_directions:
                nx, ny = x + rx, y + ry
                if nx not in range(self._board_size) or ny not in range(
                    self._board_size
                ):
                    continue
                if self.board[nx][ny] == PLAYER_TILE:
                    continue
                if self.board[nx][ny] == WALL_TILE:
                    queue.append((nx, ny))
                    break
                if self.board[nx][ny] == EXIT_TILE:
                    queue.clear()
                    break
            if not queue:
                self._player_location = (x, y)
        # Pick exit and player from visited cells
        self._exit_location = choice(visited_cells)
        self._player_location = choice(visited_cells)

        while self._player_location == self._exit_location:
            self._player_location = choice(visited_cells)
        # Draw the board
        self.board[self._player_location[0]][self._player_location[1]] = PLAYER_TILE
        self.board[self._exit_location[0]][self._exit_location[1]] = EXIT_TILE
        # print(self.board)
        return self._convert_raw_board_to_emoji(self.board)

    async def _add_movement_keys(self, message):
        await message.add_reaction(str("⬅️"))
        await message.add_reaction(str("➡️"))
        await message.add_reaction(str("⬆️"))
        await message.add_reaction(str("⬇️"))
        await message.add_reaction(str("❌"))

    async def _move(self, emoji):
        move = self._movement.get(emoji, None)
        if not move:
            return False

        temp = np.add(self._player_location, move)
        if temp[0] not in range(0, len(self._board)) or temp[1] not in range(
            0, len(self._board[0])
        ):
            return False
        if temp[0] == self._exit_location[0] and temp[1] == self._exit_location[1]:
            self._is_game_finished = True
        self._player_location = temp

    def _convert_raw_board_to_emoji(self, board: list[list[int]]):
        final_board: list[list[int]] = []
        for row in board:
            new_row = []
            for cell in row:
                if cell == EXIT_TILE:
                    new_row.append("🚪")
                    continue
                if cell == PLAYER_TILE:
                    new_row.append("👺")
                    continue
                if cell == WALL_TILE:
                    new_row.append("◼️")
                    continue
                if cell == EMPTY_TILE:
                    new_row.append("◽")
                    continue
                print(f"Invalid cell in board {cell}")
            final_board.append(new_row)
        # self.board = ''.join(['\n'.join(x) for x in final_board])
        # return final_board
        return "\n".join(["".join(x) for x in final_board])

    def run(self):
        super().run(self._TOKEN)


def main():
    # print("Hello from blobby!")
    client = Blobby()
    client.run()


if __name__ == "__main__":
    main()
