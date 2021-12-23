import asyncio

import discord
import webcolors
from discord import Permission, slash_command
from discord.commands import permissions
from discord.ext import commands
from utils.variables import *
from utils.checks import is_staff
from utils.autocomplete import CSS_COLORS
from discord.commands import Option
from typing import Union, Optional


class Staff(commands.Cog):
    '''Commands used by staff'''

    print("Staff Commands Loaded")

    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        return await is_staff(ctx)

    @property
    def display_emoji(self) -> discord.PartialEmoji:
        return discord.PartialEmoji(name='mod_badge', id=900488706748731472)

    suggestion = discord.SlashCommandGroup(
        "suggestion",
        "Managing suggestions",
        guild_ids=[SERVER_ID],
        permissions=[Permission(
            823929718717677568,
            1,
            True
        )],
        default_permission=False
    )

    @suggestion.command()
    @permissions.has_any_role(ROLE_SERVERLEADER, guild_id=SERVER_ID)
    async def deny(self, ctx, message: Option(str, description="Suggestion message id")):
        '''Denies a suggestion, is not reversible'''
        message = await commands.MessageConverter().convert(ctx, message)
        if message.channel.id == CHANNEL_SUGGESTIONS:
            embed_obj = message.embeds[0]
            embed = embed_obj.copy()
            description = embed.description
            embed.description = (description + "\n ```This suggestion has been denied```")
            embed.colour = discord.Colour.brand_red()
            await message.edit(embed=embed)
            await message.clear_reactions()
            await ctx.respond("Successfully denied suggestion")
        else:
            await ctx.respond("That is not a valid suggestion message")

    @suggestion.command()
    @permissions.has_any_role(ROLE_SERVERLEADER, guild_id=SERVER_ID)
    async def approve(self, ctx, message: Option(str, description="Suggestion message id")):
        '''Approves a suggestion, is not reversible'''
        message = await commands.MessageConverter().convert(ctx, message)
        if message.channel.id == CHANNEL_SUGGESTIONS:
            embed_obj = message.embeds[0]
            embed = embed_obj.copy()
            description = embed.description
            embed.description = (description + "\n ```This suggestion has been approved```")
            embed.colour = discord.Colour.brand_green()
            await message.edit(embed=embed)
            await ctx.respond("Successfully approved suggestion")
        else:
            await ctx.respond("That is not a valid suggestion message")

    @suggestion.command()
    @permissions.has_any_role(ROLE_SERVERLEADER, guild_id=SERVER_ID)
    async def delete(self, ctx, message: Option(str, description="Suggestion message id")):
        '''Deletes a suggestion message'''
        message = await commands.MessageConverter().convert(ctx, message)
        if message.channel.id == CHANNEL_SUGGESTIONS:
            msg = await ctx.respond("Deleting suggestion in `5` seconds")
            await asyncio.sleep(1)
            for i in range(4, 0, -1):
                await msg.edit(f"Deleting suggestion in `{i}` seconds")
                await asyncio.sleep(1)
            await message.delete()
            await msg.edit(content="Deleted suggestion")
        else:
            await ctx.respond("Not a valid suggestion message")

    @slash_command(guild_ids=[SERVER_ID])
    @permissions.has_any_role(ROLE_SERVERLEADER, guild_id=SERVER_ID)
    async def trial(self,
                    ctx,
                    user: Option(discord.Member, description="The user you wish promote to trial leader")):
        """Promotes/Trials a user."""
        member = ctx.author
        role = discord.utils.get(member.guild.roles, name=ROLE_TRIAL)
        await user.add_roles(role)
        await ctx.respond(
            f"Successfully added {role}. Congratulations {user.mention}! :partying_face: :partying_face: ")

    @slash_command(guild_ids=[SERVER_ID])
    @permissions.has_any_role(ROLE_SERVERLEADER, guild_id=SERVER_ID)
    async def untrial(self, ctx,
                      user: Option(discord.Member, description="The user you wish to demote")):
        """Demotes/unTrials a user."""
        member = ctx.author
        role = discord.utils.get(member.guild.roles, name=ROLE_TRIAL)
        await user.remove_roles(role)
        await ctx.respond(f"Successfully removed {role} from {user.mention}.")

    @commands.command()
    async def sudo(self, ctx, who: Union[discord.Member, discord.User], *,
                   command: str, channel: Optional[discord.TextChannel]):
        """Run a command as another user optionally in another channel."""
        msg = ctx.message
        msg.author = who
        msg.channel = channel or ctx.channel
        msg.content = ctx.prefix + command
        new_ctx = await self.bot.get_context(msg, cls=type(ctx))
        await self.bot.invoke(new_ctx)
        await ctx.respond('sent command', ephemeral=True)

    @slash_command(guild_ids=[SERVER_ID])
    @permissions.has_any_role(ROLE_SERVERLEADER, guild_id=SERVER_ID)
    async def embed(
            self,
            ctx,
            color: Option(str, autocomplete=discord.utils.basic_autocomplete(values=CSS_COLORS)),
            channel: Option(discord.TextChannel, description="The channel to send the embed to", required=False),
            title: Option(str, description="Embed title", required=False),
            description: Option(str, description="Embed description", required=False),
            title_url: Option(str, description="Title text link, type: url", required=False),
            thumbnail_url: Option(str, description="Thumbnail image link, type: url", required=False),
            author_url: Option(str, description="Author name link, type: url", required=False),
            footer_text: Option(str, description="Text displayed in embed footer", required=False),
            footer_url: Option(str, description="Footer text link, type: url", required=False),
            image_url: Option(str, description="Embed image, type: url", required=False)
    ) -> None:

        send_channel = channel if channel else ctx.channel
        title = title if title else ""
        description = description if description else ""
        title_url = title_url if title_url else ""
        thumbnail_url = thumbnail_url if thumbnail_url else ""
        author_url = author_url if author_url else ""
        footer_text = footer_text if footer_text else ""
        footer_url = footer_url if footer_url else ""
        image_url = image_url if image_url else ""
        author_name = ctx.author.name
        author_icon = ctx.author.display_avatar
        hexcolor = webcolors.name_to_hex(color)

        embed = discord.Embed(
            title=title,
            description=description,
            color=int(hexcolor, 16),
            url=title_url
        )
        embed.set_author(
            name=author_name,
            icon_url=author_icon,
            url=author_url
        )
        embed.set_image(
            url=image_url
        )
        embed.set_footer(
            text=footer_text,
            icon_url=footer_url
        )
        embed.set_thumbnail(
            url=thumbnail_url
        )

        await send_channel.send(embed=embed)
        await ctx.respond('Embed Sent', ephemeral=True)

    @slash_command(guild_ids=[SERVER_ID])
    @permissions.has_any_role(ROLE_SERVERLEADER, guild_id=SERVER_ID)
    async def vip(self,
                  ctx,
                  user: Option(discord.Member, description="The user you wish to VIP")):
        """Exalts/VIPs a user."""
        member = ctx.author
        role = discord.utils.get(member.guild.roles, name=ROLE_VIP)
        await user.add_roles(role)
        await ctx.respond(f"Successfully added VIP. Congratulations {user.mention}! :partying_face: :partying_face: ")

    @slash_command(guild_ids=[SERVER_ID])
    @permissions.has_any_role(ROLE_SERVERLEADER, guild_id=SERVER_ID)
    async def unvip(self,
                    ctx,
                    user: Option(discord.Member, description="The user you wish to unVIP")):
        """Unexalts/unVIPs a user."""
        member = ctx.author
        role = discord.utils.get(member.guild.roles, name=ROLE_VIP)
        await user.remove_roles(role)
        await ctx.respond(f"Successfully removed VIP from {user.mention}.")


def setup(bot):
    bot.add_cog(Staff(bot))
