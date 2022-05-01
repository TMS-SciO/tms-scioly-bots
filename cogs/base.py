from __future__ import annotations

import subprocess
import sys
from threading import Thread

import discord
import io
import textwrap
import traceback
from contextlib import redirect_stdout
from typing import List, Literal, TYPE_CHECKING

from discord.app_commands import checks, command, Group
from discord.ext import commands

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
    async def _sync_commands(self, ctx: custom.Context, guild: str = None):
        await ctx.defer()
        await self.bot.tree.sync(guild=discord.Object(int(guild)) if guild else None)
        await ctx.reply(f"Synced commands to guild id: {guild}")

    @commands.command(name="profile")
    async def _profile(self, ctx, user_id: discord.User):
        await ctx.send(user_id.avatar)


class Module(Group):
    def __init__(self, bot: TMS):
        super().__init__(
            name="module",
            description="Manages the bot's modules",
        )
        self.bot = bot
        self.extensions: List[str] = [
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
            "jishaku"
        ]

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

    @staticmethod
    async def _force_restart(interaction: discord.Interaction, branch="master"):
        p = subprocess.run(
            "git status -uno", shell=True, text=True, capture_output=True, check=True
        )

        embed = discord.Embed(
            title="Restarting...",
            description="Doing GIT Operation (1/3)",
            color=discord.Color.brand_green(),
        )
        embed.add_field(
            name="Checking GIT (1/3)",
            value=f"**Git Output:**\n```shell\n{p.stdout}\n```",
        )

        msg = await interaction.channel.send(embed=embed)
        try:

            result = subprocess.run(
                f"cd && cd {branch}",
                shell=True,
                text=True,
                capture_output=True,
                check=True,
            )
            theproc = subprocess.Popen([sys.executable, "bot.py"])

            runThread = Thread(target=theproc.communicate)
            runThread.start()

            embed.add_field(
                name="Started Environment and Additional Process (2/3)",
                value="Executed `source` and `nohup`.",
                inline=False,
            )
            await msg.edit(embed=embed)

        except Exception as e:
            embed = discord.Embed(
                title="Operation Failed", description=e, color=discord.Color.brand_red()
            )
            embed.set_footer(text="Main bot process will be terminated.")

            await interaction.channel.send(embed=embed)

        else:
            embed.add_field(
                name="Killing Old Bot Process (3/3)",
                value="Executing `sys.exit(0)` now...",
                inline=False,
            )
            await msg.edit(embed=embed)
            sys.exit(0)

    @command()
    async def gitpull(
            self,
            interaction: discord.Interaction,
            mode: Literal["-a", "-c"] = "-a",
            sync_commands: bool = False,
    ) -> None:
        output = ""
        try:
            p = subprocess.run(
                "git fetch --all",
                shell=True,
                text=True,
                capture_output=True,
                check=True,
            )
            output += p.stdout
        except Exception as e:
            await interaction.response.send_message(
                f"⛔️ Unable to fetch the Current Repo Header!\n**Error:**\n{e}"
            )
        try:
            p = subprocess.run(
                f"git reset --hard `master`",
                shell=True,
                text=True,
                capture_output=True,
                check=True,
            )
            output += p.stdout
        except Exception as e:
            await interaction.response.send_message(
                f"⛔️ Unable to apply changes!\n**Error:**\n{e}"
            )

        embed = discord.Embed(
            title="GitHub Local Reset",
            description=f"Local Files changed to match `master`",
            color=discord.Color.brand_green(),
        )
        embed.add_field(name="Shell Output", value=f"```shell\n$ {output}\n```")
        if mode == "-a":
            embed.set_footer(text="Attempting to restart the bot...")
        elif mode == "-c":
            embed.set_footer(text="Attempting to reloading cogs...")

        await interaction.response.send_message(embed=embed)

        if mode == "-a":
            await self._force_restart(interaction)
        elif mode == "-c":
            try:
                embed = discord.Embed(
                    title="Cogs - Reload",
                    description="Reloaded all cogs",
                    color=discord.Color.brand_green(),
                )
                for extension in self.extensions:
                    await self.bot.reload_extension(extension)
                return await interaction.channel.send(embed=embed)
            except commands.ExtensionError:
                embed = discord.Embed(
                    title="Cogs - Reload",
                    description="Failed to reload cogs",
                    color=discord.Color.brand_red(),
                )
                return await interaction.channel.send(embed=embed)

        if sync_commands:
            await self.bot.tree.sync()


async def setup(bot: TMS):
    await bot.add_cog(Core(bot))
