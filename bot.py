import json
import os
from abc import ABC

import aiohttp
import discord
from discord.ext import commands

from utils.functions import send_to_dm_log
from utils.views import ReportView, Ticket, Close, Role1, Role2, Role3, Role4, Role5, Pronouns, Allevents
from utils.variables import *

import sys
import traceback

INITIAL_EXTENSIONS = [
    "cogs.mod",
    "cogs.fun",
    "cogs.general",
    "cogs.tasks",
    "cogs.meta",
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
    "jishaku"
]


class TMS(commands.Bot, ABC):
    def __init__(self):
        intents = discord.Intents.all()
        super().__init__(
            command_prefix=commands.when_mentioned_or("!"),
            case_insensitive=True,
            slash_commands=True,
            intents=intents,
            status=discord.Status.dnd
        )
        self.persistent_views_added = False
        self.session = aiohttp.ClientSession(loop=self.loop)
        self.owner_id = 747126643587416174

        for extension in INITIAL_EXTENSIONS:
            try:
                self.load_extension(extension)
            except all:
                print(f'Failed to load extension {extension}', file=sys.stderr)
                traceback.print_exc()

    async def on_ready(self):
        if not self.persistent_views_added:
            self.add_view(Role1())
            self.add_view(Role2())
            self.add_view(Role3())
            self.add_view(Role4())
            self.add_view(Role5())
            self.add_view(Allevents())
            self.add_view(Pronouns())
            self.add_view(ReportView())
            self.add_view(Ticket(bot))
            self.add_view(Close(bot))
            self.persistent_views_added = True
        print(f'{bot.user} has connected!')
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print("discord.py v" + discord.__version__)

    async def on_error(
            self, event, *args, **kwargs
    ) -> None:
        print(traceback.format_exc())

    async def on_application_command_error(
            self, ctx: discord.ApplicationContext, exception: discord.DiscordException
    ) -> None:
        print(exception)
        try:
            await ctx.defer()
            await ctx.respond(exception)
        except all:
            pass

    async def on_interaction(
            self,  interaction
    ) -> None:
        ctx = await self.get_application_context(interaction)
        member = ctx.author.id
        f = open('blacklist.json')
        data = json.load(f)
        if member in data['blacklisted_ids']:
            return await ctx.respond("You have been blacklisted from using commands", ephemeral=True)
        else:
            await self.process_application_commands(interaction)

    async def on_message(
            self, message
    ):
        if type(message.channel) == discord.DMChannel:
            await send_to_dm_log(bot, message)

        if message.author.id in TMS_BOT_IDS:
            return

        censor_cog = bot.get_cog("Censor")  # Censor
        await censor_cog.on_message(message)

        spam = bot.get_cog("SpamManager")  # Spamming
        await spam.store_and_validate(message)

    def run(self):
        super().run(os.environ['TOKEN'], reconnect=True)

    async def close(self):
        await self.session.close()
        await super().close()


bot = TMS()


def main():
    bot.run()


if __name__ == "__main__":
    main()
