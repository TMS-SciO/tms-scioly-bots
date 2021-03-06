from __future__ import annotations

import asyncio

import discord
from discord import app_commands
from discord.app_commands import checks, command, describe, Group, guilds
from discord.ext import commands
from utils import Role, SERVER_ID, is_staff, Channel
from typing import Union, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from bot import TMS


class Suggest(Group):
    def __init__(self, bot: TMS):
        super().__init__(name="suggestion", guild_ids=[SERVER_ID])
        self.bot = bot

    @property
    def cog(self) -> commands.Cog:
        return self.bot.get_cog("Staff")

    @command()
    @checks.has_any_role(Role.SERVERLEADER, Role.FORMER_SL)
    @describe(message="Message link or ID")
    async def deny(self, interaction: discord.Interaction, message: str):
        """Denies a suggestion, is not reversible"""
        message = await commands.MessageConverter().convert(
            await self.bot.get_context(interaction), message
        )
        if message.channel.id == Channel.SUGGESTIONS:
            embed_obj = message.embeds[0]
            embed = embed_obj.copy()
            description = embed.description
            embed.description = description + "\n ```This suggestion has been denied```"
            embed.colour = discord.Colour.brand_red()
            await message.edit(embed=embed)
            await message.clear_reactions()
            await interaction.response.send_message("Successfully denied suggestion")
        else:
            await interaction.response.send_message(
                "That is not a valid suggestion message"
            )

    @command()
    @checks.has_any_role(Role.SERVERLEADER, Role.FORMER_SL)
    @describe(message="Message link or ID")
    async def approve(self, interaction: discord.Interaction, message: str):
        """Approves a suggestion, is not reversible"""
        message = await commands.MessageConverter().convert(
            await self.bot.get_context(interaction), message
        )
        if message.channel.id == Channel.SUGGESTIONS:
            embed_obj = message.embeds[0]
            embed = embed_obj.copy()
            description = embed.description
            embed.description = (
                description + "\n ```This suggestion has been approved```"
            )
            embed.colour = discord.Colour.brand_green()
            await message.edit(embed=embed)
            await interaction.response.send_message("Successfully approved suggestion")
        else:
            await interaction.response.send_message(
                "That is not a valid suggestion message"
            )

    @command()
    @checks.has_any_role(Role.SERVERLEADER, Role.FORMER_SL)
    @describe(message="Message link or ID")
    async def delete(self, interaction: discord.Interaction, message: str):
        """Deletes a suggestion message"""
        message = await commands.MessageConverter().convert(
            await self.bot.get_context(interaction), message
        )
        if message.channel.id == Channel.SUGGESTIONS:
            msg = await interaction.response.send_message(
                "Deleting suggestion in `5` seconds"
            )
            await asyncio.sleep(1)
            for i in range(4, 0, -1):
                await msg.edit(f"Deleting suggestion in `{i}` seconds")
                await asyncio.sleep(1)
            await message.delete()
            await msg.edit(content="Deleted suggestion")
        else:
            await interaction.response.send_message("Not a valid suggestion message")


class Staff(commands.Cog):
    """Commands used by staff"""

    print("Staff Commands Loaded")

    def __init__(self, bot: TMS):
        self.bot = bot
        self.__cog_app_commands__.append(Suggest(bot))

    async def cog_check(self, ctx: commands.Context):
        return await is_staff(ctx)

    @property
    def display_emoji(self) -> discord.PartialEmoji:
        return discord.PartialEmoji(name="mod_badge", id=900488706748731472)

    @commands.command()
    @commands.is_owner()
    async def sudo(
        self,
        ctx: commands.Context,
        who: Union[discord.Member, discord.User],
        *,
        command: str,
        channel: Optional[discord.TextChannel],
    ):
        """Run a command as another user optionally in another channel."""
        msg = ctx.message
        msg.author = who
        msg.channel = channel or ctx.channel
        msg.content = ctx.prefix + command
        new_context: commands.Context = await self.bot.get_context(msg, cls=type(ctx))
        await self.bot.invoke(new_context)
        await ctx.send("sent command", ephemeral=True)


async def setup(bot: TMS):
    await bot.add_cog(Staff(bot))
