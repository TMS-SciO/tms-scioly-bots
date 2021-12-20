import discord
from discord import slash_command
from discord.commands import permissions
from discord.ext import commands
from utils.variables import *
from utils.checks import is_staff
from utils.autocomplete import CSS_COLORS
from utils.functions import assemble_embed
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
    async def embed(self,
                    ctx,
                    color: Option(str, autocomplete=discord.utils.basic_autocomplete(values=CSS_COLORS)),
                    channel: Option(discord.TextChannel, description="The channel to send the embed to",
                                    required=False),
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
        author_icon = ctx.author.avatar
        embed = assemble_embed(title=title,
                               description=description,
                               title_url=title_url,
                               webcolor=color,
                               thumbnail_url=thumbnail_url,
                               author_name=author_name,
                               author_url=author_url,
                               author_icon=author_icon,
                               footer_text=footer_text,
                               footer_url=footer_url,
                               fields=None,
                               image_url=image_url)
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
