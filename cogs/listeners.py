import discord
from discord.ext import commands

from utils.variables import *


class Listeners(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message_edit(
            self, before, after
    ) -> None:
        if after.author.id in TMS_BOT_IDS:
            return
        if after.author.discriminator == "0000":
            return
        censor_cog = self.bot.get_cog("Censor")
        censor_found = censor_cog.censor_needed(after.content)
        if censor_found:
            await after.delete()
            await after.author.send(
                "You recently edited a message, but it **contained a censored word**! Therefore, I unfortunately had "
                "to delete it.")

        message_embed = discord.Embed(
            title="\U0000270f Edited Message",
            color=discord.Color.fuchsia()
        )
        message_embed.add_field(name="Author", value=after.author.mention, inline=True)
        message_embed.add_field(name="Message ID", value=after.id, inline=True)
        message_embed.add_field(name="Message Link", value=f"[Here!]({after.jump_url})", inline=False)
        message_embed.add_field(name="Before", value=f"{before.content}", inline=True)
        message_embed.add_field(name="After", value=f"{after.content}", inline=True)
        message_embed.add_field(name="Attachments", value=" | ".join(
            [f"**{a.filename}**: [Link]({a.url})" for a in after.attachments]) if len(
            after.attachments) > 0 else "None", inline=False)

        message_embed.add_field(name="Sent", value=discord.utils.format_dt(before.created_at, 'R'), inline=True)
        message_embed.add_field(name="Edited", value=discord.utils.format_dt(after.created_at, 'R'), inline=True)

        guild = self.bot.get_guild(SERVER_ID)
        moderation_log = discord.utils.get(guild.text_channels, id=CHANNEL_EDITEDM)

        await moderation_log.send(embed=message_embed)

    @commands.Cog.listener()
    async def on_message_delete(
            self, message
    ):
        if message.author.id in TMS_BOT_IDS:
            return
        message_embed = discord.Embed(
            title="\U0001f525 Deleted Message",
            color=discord.Color.brand_red()
        )
        message_embed.add_field(name="Author", value=message.author.mention, inline=True)
        message_embed.add_field(name="Message ID", value=message.id, inline=True)
        message_embed.add_field(name="Content", value=f"{message.content}", inline=False)
        message_embed.add_field(name="Attachments", value=" | ".join(
            [f"**{a.filename}**: [Link]({a.url})" for a in message.attachments]) if
        message.attachments else "None", inline=False)
        message_embed.add_field(name="Created", value=discord.utils.format_dt(message.created_at, 'R'), inline=False)

        guild = self.bot.get_guild(SERVER_ID)
        moderation_log = discord.utils.get(guild.text_channels, id=CHANNEL_DELETEDM)
        await moderation_log.send(embed=message_embed)

    @commands.Cog.listener()
    async def on_member_update(
            self, before, after
    ) -> None:

        if after.nick is None:
            return
        name = after.nick
        censor_cog = self.bot.get_cog('Censor')
        if censor_cog.censor_needed(name):
            # If name contains a censored link
            reporter_cog = self.bot.get_cog('Reporter')
            await reporter_cog.create_inappropriate_username_report(member=after, offending_username=name)

    @commands.Cog.listener()
    async def on_member_join(
            self, member: discord.Member
    ):
        if member.guild.id != SERVER_ID:
            return

        name = member.name
        censor_cog = self.bot.get_cog('Censor')
        if censor_cog.censor_needed(name):
            reporter_cog: commands.Cog = self.bot.get_cog('Reporter')
            await reporter_cog.create_inappropriate_username_report(member, member.name)

        role: discord.Role = discord.utils.get(member.guild.roles, name=ROLE_MR)
        join_channel: discord.TextChannel = discord.utils.get(member.guild.text_channels, id=WELCOME_CHANNEL)
        await member.add_roles(role)
        embed = discord.Embed(
            title="Welcome!",
            description=f"{member.mention}! Welcome to the TMS Scio Discord. If you need any help "
                        "feel free to open a ticket in <#848996283288518718> or use `/help` for "
                        "bot-command help! Please state your name, JV or Varsity, and add your "
                        "events in <#863054629787664464> ! ",
            timestamp=discord.utils.utcnow(),
            color=discord.Color.fuchsia()
        )
        await join_channel.send(
            embed=embed, content=f"{member.mention}"
        )


def setup(bot):
    bot.add_cog(Listeners(bot))
