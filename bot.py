import discord
from discord.ext import commands
from utils.views import Ticket, Close, Role1, Role2, Role3, Role4, Role5, Pronouns, Allevents
from utils.secret import TOKEN
from utils.variables import *
import sys
import traceback

intents = discord.Intents.all()

INITIAL_EXTENSIONS = ["cogs.mod",
                      "cogs.fun",
                      "cogs.general",
                      "cogs.tasks",
                      "cogs.listeners"]


class PersistentViewBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned_or(BOT_PREFIX1, BOT_PREFIX),
                         case_insensitive=True,
                         help_command=None,
                         intents=intents,
                         slash_commands=True)

        self.persistent_views_added = False

        for extension in INITIAL_EXTENSIONS:
            try:
                self.load_extension(extension)
            except all:
                print(f'Failed to load extension {extension}.', file=sys.stderr)
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
            self.add_view(Ticket(bot))
            self.add_view(Close(bot))
            self.persistent_views_added = True
        print(f'{bot.user} has connected!')
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')
        print(discord.__version__)
        await bot.change_presence(status=discord.Status.dnd, activity=discord.Game("Minecraft"))


bot = PersistentViewBot()


bot.run(TOKEN)
