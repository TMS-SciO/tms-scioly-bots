import discord
from discord.ext import commands
from utils.checks import is_dev


class Core(commands.Cog):
    '''Bot/Module Management (Requires Bot-Developer-Role)'''

    print('Core Cog Loaded')

    @property
    def display_emoji(self) -> discord.PartialEmoji:
        return discord.PartialEmoji(name='king', id=900800639989321799)

    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        return await is_dev(ctx)

    @commands.command()
    async def load(self, ctx, *, module):
        """Loads a module."""
        try:
            self.bot.load_extension(module)
        except commands.ExtensionError as e:
            await ctx.send(f'{e.__class__.__name__}: {e}')
        else:
            await ctx.send('<:greenTick:899466945672392704> ')

    @commands.command()
    async def unload(self, ctx, *, module):
        """Unloads a module."""
        try:
            self.bot.unload_extension(module)
        except commands.ExtensionError as e:
            await ctx.send(f'{e.__class__.__name__}: {e}')
        else:
            await ctx.send('<:greenTick:899466945672392704>')

    @commands.command()
    async def reload(self, ctx, *, module):
        """Reloads a module."""
        try:
            self.bot.reload_extension(module)
        except commands.ExtensionError as e:
            await ctx.send(f'{e.__class__.__name__}: {e}')
        else:
            await ctx.send('<:greenTick:899466945672392704>')

    def reload_or_load_extension(self, module):
        try:
            self.bot.reload_extension(module)
        except commands.ExtensionNotLoaded:
            self.bot.load_extension(module)


def setup(bot):
    bot.add_cog(Core(bot))
