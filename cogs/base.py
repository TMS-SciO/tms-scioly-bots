import discord
from discord import ExtensionError, ExtensionNotLoaded, Permission, permissions
from discord.ext import commands
from utils.checks import is_dev
import io
import textwrap
from contextlib import redirect_stdout
import traceback

from utils.variables import SERVER_ID


class Core(commands.Cog):
    '''Bot/Module Management (requires owner)'''

    print('Core Cog Loaded')

    @property
    def display_emoji(self) -> discord.PartialEmoji:
        return discord.PartialEmoji(name='\U0001f4bb')

    def __init__(self, bot):
        self.bot = bot
        self._last_result = None

    async def cog_check(self, ctx):
        return await is_dev(ctx)

    module = discord.SlashCommandGroup(
        "module",
        "Manage the bot's modules",
        [SERVER_ID],
        permissions=[Permission(
            747126643587416174,
            2,
            True
        )],
        default_permission=False
    )

    @module.command()
    @permissions.is_owner()
    async def load(self, ctx, *, module):
        """Loads a module."""
        try:
            self.bot.load_extension(module)
        except ExtensionError as e:
            await ctx.respond(f'{e.__class__.__name__}: {e}')
        else:
            await ctx.respond('<:greenTick:899466945672392704> ')

    @module.command()
    @permissions.is_owner()
    async def unload(self, ctx, *, module):
        """Unloads a module."""
        try:
            self.bot.unload_extension(module)
        except ExtensionError as e:
            await ctx.respond(f'{e.__class__.__name__}: {e}')
        else:
            await ctx.respond('<:greenTick:899466945672392704>')

    @module.command()
    @permissions.is_owner()
    async def reload(self, ctx, *, module):
        """Reloads a module."""
        try:
            self.bot.reload_extension(module)
        except ExtensionError as e:
            await ctx.respond(f'{e.__class__.__name__}: {e}')
        else:
            await ctx.respond('<:greenTick:899466945672392704>')

    def reload_or_load_extension(self, module):
        try:
            self.bot.reload_extension(module)
        except ExtensionNotLoaded:
            self.bot.load_extension(module)

    @staticmethod
    def cleanup_code(content):
        """Automatically removes code blocks from the code."""
        # remove ```py\n```
        if content.startswith('```') and content.endswith('```'):
            return '\n'.join(content.split('\n')[1:-1])

        # remove `foo`
        return content.strip('` \n')

    @commands.command()
    @commands.is_owner()
    async def eval(self, ctx, *, body: str):
        """Evaluates a code"""
        env = {
            'bot': self.bot,
            'ctx': ctx,
            'channel': ctx.channel,
            'author': ctx.author,
            'guild': ctx.guild,
            'message': ctx.message,
            '_': self._last_result
        }

        env.update(globals())

        body = self.cleanup_code(body)
        stdout = io.StringIO()

        to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'

        try:
            exec(to_compile, env)
        except Exception as e:
            return await ctx.respond(f'```py\n{e.__class__.__name__}: {e}\n```')

        func = env['func']
        try:
            with redirect_stdout(stdout):
                ret = await func()
        except Exception as e:
            value = stdout.getvalue()
            await ctx.respond(f'```py\n{value}{traceback.format_exc()}\n```')
        else:
            value = stdout.getvalue()
            try:
                await ctx.message.add_reaction('\u2705')
            except:
                pass

            if ret is None:
                if value:
                    await ctx.respond(f'```py\n{value}\n```')
            else:
                self._last_result = ret
                await ctx.respond(f'```py\n{value}{ret}\n```')


def setup(bot):
    bot.add_cog(Core(bot))
