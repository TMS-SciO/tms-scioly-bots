from __future__ import annotations

import asyncio
import os
from typing import TYPE_CHECKING

import aiohttp
import discord
from discord import app_commands
from discord.ext import commands

import mongo

from utils.views import ReportView, Ticket, Close, Role1, Role2, Role3, Role4, Role5, Pronouns
from utils.variables import TMS_BOT_IDS

import sys
import traceback

INITIAL_EXTENSIONS = [
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
    "jishaku"
]


class TmsBotTree(app_commands.CommandTree):
    def __init__(self, client: 'TMS'):
        super().__init__(client)


class TMS(commands.Bot):
    def __init__(self):
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
        # self.session = aiohttp.ClientSession()

    async def setup_hook(self) -> None:
        for extension in INITIAL_EXTENSIONS:
            try:
                await self.load_extension(extension)
            except all:
                print(f'Failed to load extension {extension}', file=sys.stderr)
                traceback.print_exc()
        await self.db_start()

    async def db_start(self):
        await mongo.setup()

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
            self, message
    ) -> None:
        if type(message.channel) == discord.DMChannel:
            log = bot.get_cog("Listeners")
            return await log.send_to_dm_log(bot, message)

        if message.author.id in TMS_BOT_IDS:
            return

        censor_cog = bot.get_cog("Censor")  # Censor
        await censor_cog.on_message(message)

        spam = bot.get_cog("SpamManager")  # Spamming
        await spam.store_and_validate(message)

        listener_for_embed = bot.get_cog("Embeds")
        await listener_for_embed.on_message(message)

    async def close(self):
        await self.session.close()
        await super().close()


bot = TMS()


async def main() -> None:
    async with bot:
        await bot.start(os.getenv("TOKEN"), reconnect=True)


if __name__ == "__main__":
    asyncio.run(main())
