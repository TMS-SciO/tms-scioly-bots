from __future__ import annotations

import asyncio
import collections
import logging
import os
import sys
import traceback
from typing import Any, List, Optional, Type, TYPE_CHECKING, Union

import aiohttp
import discord
import slate
from discord import app_commands
from discord.abc import Snowflake
from discord.ext import commands
from discord.ext.commands import errors
from dotenv import load_dotenv

import custom
import mongo
from custom import Context
from utils.variables import TMS_BOT_IDS
from utils.views import Close, Pronouns, ReportView, Role1, Role2, Role3, Role4, Role5, Ticket

if TYPE_CHECKING:
    from cogs.listeners import Listeners
    from cogs.spam import SpamManager
    from cogs.censor import Censor
    from cogs.embed import EmbedCommands

INITIAL_EXTENSIONS: List[str] = [
    "cogs.api",
    "cogs.mod",
    "cogs.fun",
    "cogs.general",
    "cogs.tasks",
    "cogs.meta",
    "cogs.embed",
    "cogs.base",
    "cogs.github",
    "cogs.google",
    "cogs.censor",
    "cogs.elements",
    "cogs.activities",
    "cogs.spam",
    "cogs.report",
    "cogs.listeners",
    "cogs.wikipedia",
    "cogs.config",
    "cogs.staff",
    "cogs.medals",
    "cogs.player",
    "cogs.music",
    "jishaku",
]

logging.basicConfig(level=logging.WARNING)

load_dotenv()


class TmsBotTree(app_commands.CommandTree):
    def __init__(self, client: 'TMS') -> None:
        super().__init__(client)

    async def sync(self, *, guild: Optional[Snowflake] = None) -> List[app_commands.AppCommand]:
        print(f"Synced to {guild}")
        return await super().sync(guild=guild)


class TMS(commands.Bot):
    def __init__(self) -> None:
        intents = discord.Intents.all()
        intents.message_content = True
        super().__init__(
            command_prefix=commands.when_mentioned_or("!", ),
            case_insensitive=True,
            slash_commands=True,
            intents=intents,
            status=discord.Status.dnd,
            tree_cls=TmsBotTree
        )
        self.persistent_views_added = False
        self.owner_id = 747126643587416174
        self.help_command = commands.DefaultHelpCommand()
        self.enable_debug_events = True
        self.mongo: mongo.MongoDatabase = mongo.MongoDatabase(self)
        self.socket_stats: collections.Counter[str] = collections.Counter()

    async def setup_hook(self) -> None:
        await self.mongo.setup()
        await self.connect_slate()
        for extension in INITIAL_EXTENSIONS:
            try:
                await self.load_extension(extension)
            except all:
                print(f'Failed to load extension {extension}', file=sys.stderr)
                traceback.print_exc()

    async def start(self, token: str, *, reconnect: bool = True) -> None:
        self.session = aiohttp.ClientSession()
        await super().start(token=token, reconnect=reconnect)

    async def on_ready(self):
        if not self.persistent_views_added:
            self.add_view(Role1())
            self.add_view(Role2())
            self.add_view(Role3())
            self.add_view(Role4())
            self.add_view(Role5())
            self.add_view(Pronouns())
            self.add_view(ReportView())
            self.add_view(Ticket(bot))
            self.add_view(Close(bot))
            self.persistent_views_added = True
        print(f'{bot.user} has connected!')
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print("discord.py v" + discord.__version__)

    async def on_message(
            self, message: discord.Message
    ) -> None:
        if type(message.channel) == discord.DMChannel:
            log: 'Listeners' | commands.Cog = self.get_cog("Listeners")
            return await log.send_to_dm_log(bot, message)

        if message.author.id in TMS_BOT_IDS:
            return

        censor_cog: 'Censor' | commands.Cog = self.get_cog("Censor")  # Censor
        await censor_cog.on_message(message)

        spam: 'SpamManager' | commands.Cog = self.get_cog("SpamManager")  # Spamming
        await spam.store_and_validate(message)

        listener_for_embed: 'EmbedCommands' | commands.Cog = self.get_cog("Embeds")
        await listener_for_embed.on_message(message)

        if not censor_cog.censor_needed(message.content):
            await super().on_message(message)

    async def close(self):
        await self.session.close()
        await super().close()

    async def connect_slate(self) -> None:
        self.slate: slate.Pool['TMS', custom.Player] = slate.Pool()
        node = await self.slate.create_node(
            provider=slate.Provider.LAVALINK,
            bot=self,
            identifier="slate",
            host=os.getenv("NODE_HOST"),
            port=os.getenv("NODE_PORT"),
            password=os.getenv("NODE_PASSWORD"),
            session=self.session,
            spotify_client_id=os.getenv("SPOTIFY_CLIENT_ID"),
            spotify_client_secret=os.getenv("SPOTIFY_TOKEN"),
        )
        print(f"Connected node {node}")

    async def get_context(
            self,
            origin: discord.Interaction | discord.Message,
            cls: Type[Context] = None,
    ) -> Optional[Union['Context', Any]]:
        return await super().get_context(origin, cls=Context)

    async def on_command_error(
            self,
            context: Context['TMS'],
            exception: errors.CommandError, /
    ) -> None:
        if isinstance(exception, custom.EmbedError):
            await context.reply(embed=exception.embed)
        await super().on_command_error(context, exception)


bot = TMS()


async def main() -> None:
    async with bot:
        await bot.start(os.getenv("TOKEN"), reconnect=True)


if __name__ == "__main__":
    asyncio.run(main())
