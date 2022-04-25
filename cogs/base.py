from __future__ import annotations

from typing import TYPE_CHECKING

import discord
from discord.app_commands import Group, command
from discord.ext import commands
import io
import textwrap
from contextlib import redirect_stdout
import traceback
import custom


if TYPE_CHECKING:
    from bot import TMS


class Core(commands.Cog):
    """Bot/Module Management (requires owner)"""

    @property
    def display_emoji(self) -> discord.PartialEmoji:
        return discord.PartialEmoji(name='\U0001f4bb')

    def __init__(self, bot: TMS):
        print("Core Cog Loaded")
        self.bot = bot
        self._last_result = None
        self.__cog_app_commands__.append(Module(bot))

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
    async def eval(self, ctx: custom.Context, *, body: str):
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
            return await ctx.send(f'```py\n{e.__class__.__name__}: {e}\n```')

        func = env['func']
        try:
            with redirect_stdout(stdout):
                ret = await func()
        except Exception as e:
            value = stdout.getvalue()
            await ctx.send(f'```py\n{value}{traceback.format_exc()}\n```')
        else:
            value = stdout.getvalue()
            try:
                await ctx.message.add_reaction('\u2705')
            except:
                pass

            if ret is None:
                if value:
                    await ctx.send(f'```py\n{value}\n```')
            else:
                self._last_result = ret
                await ctx.send(f'```py\n{value}{ret}\n```')

    @commands.hybrid_command(name="sync-commands")
    @commands.is_owner()
    async def _sync_commands(self, ctx: custom.Context, guild: int | discord.Guild | None = None):
        await ctx.defer()
        await self.bot.tree.sync(guild=guild)
        await ctx.reply(f"Synced commands to {guild.name}")

    @commands.command(name="profile")
    async def _profile(self, ctx, user_id: discord.User):
        await ctx.send(user_id.avatar)


class Module(Group):
    def __init__(self, bot: TMS):
        self.bot = bot
        super().__init__(
            name="module",
            description="Manages the bot's modules",
        )

    @property
    def cog(self) -> commands.Cog:
        return self.bot.get_cog("Core")

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if not interaction.user.id == self.bot.owner_id:
            return False
        return True

    @command()
    async def load(self, interaction: discord.Interaction, *, module: str):
        """Loads a module."""
        try:
            await self.bot.load_extension(module)
        except commands.ExtensionError as e:
            await interaction.response.send_message(f'{e.__class__.__name__}: {e}')
        else:
            await interaction.response.send_message('<:greenTick:899466945672392704> ')

    @command()
    async def unload(self, interaction: discord.Interaction, *, module: str):
        """Unloads a module."""
        try:
            await self.bot.unload_extension(module)
        except commands.ExtensionError as e:
            await interaction.response.send_message(f'{e.__class__.__name__}: {e}')
        else:
            await interaction.response.send_message('<:greenTick:899466945672392704>')

    @command()
    async def reload(self, interaction: discord.Interaction, *, module: str):
        """Reloads a module."""
        try:
            await self.bot.reload_extension(module)
        except commands.ExtensionError as e:
            await interaction.response.send_message(f'{e.__class__.__name__}: {e}')
        else:
            await interaction.response.send_message('<:greenTick:899466945672392704>')

    async def _reload_or_load_extension(self, module):
        try:
            await self.bot.reload_extension(module)
        except commands.ExtensionNotLoaded:
            await self.bot.load_extension(module)


async def setup(bot: TMS):
    await bot.add_cog(Core(bot))
