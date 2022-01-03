import discord
from discord.ext import commands

from utils.variables import *


class Listeners(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_update(
            self, before, after
    ) -> None:

        if after.nick is None:
            return
        censor_cog = self.bot.get_cog("Censor")
        censor_found = censor_cog.censor_needed(after.nick)
        if censor_found:
            # If name contains a censored link
            reporter_cog = self.bot.get_cog('Reporter')
            await reporter_cog.create_inappropriate_username_report(member=after, offending_username=after.nick)

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

    @commands.Cog.listener()
    async def on_raw_message_edit(self, payload):
        await self.log_edit_message_payload(payload)

    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload):
        return await self.log_delete_message_payload(payload)

    async def log_edit_message_payload(self, payload):
        """
        Logs a payload for the 'Edit Message' event.
        """
        # Get the required resources for logging
        channel = self.bot.get_channel(payload.channel_id)
        guild = self.bot.get_guild(SERVER_ID) if channel.type == discord.ChannelType.private else channel.guild
        edited_channel = discord.utils.get(guild.text_channels, id=CHANNEL_DELETEDM)

        # Ignore payloads for events in logging channels (which would cause recursion)
        if channel.type != discord.ChannelType.private and channel.id in [
            CHANNEL_EDITEDM,
            CHANNEL_DELETEDM,
            CHANNEL_DMLOG
        ]:
            return

        # Attempt to log from the cached message if found, else just report on what is available
        try:
            message = payload.cached_message
            if (discord.utils.utcnow() - message.created_at).total_seconds() < 2:
                # No need to log edit event for a message that was just created
                return

            if message.author.id == self.bot.user.id:
                return

            message_now = await channel.fetch_message(message.id)
            channel_name = f"{message.author.mention}'s DM" if channel.type == discord.ChannelType.private else message.channel.mention

            embed = discord.Embed(
                title=":pencil: Edited Message",
                color=discord.Color.blurple()
            )
            fields = [
                {
                    "name": "Author",
                    "value": message.author,
                    "inline": "True"
                },
                {
                    "name": "Channel",
                    "value": channel_name,
                    "inline": "True"
                },
                {
                    "name": "Message ID",
                    "value": f"{payload.message_id} ([jump!]({message_now.jump_url}))",
                    "inline": "True"
                },
                {
                    "name": "Created At",
                    "value": discord.utils.format_dt(message.created_at, 'R'),
                    "inline": "True"
                },
                {
                    "name": "Edited At",
                    "value": discord.utils.format_dt(message_now.edited_at, 'R'),
                    "inline": "True"
                },
                {
                    "name": "Attachments",
                    "value": " | ".join([f"**{a.filename}**: [Link]({a.url})" for a in message.attachments]) if len(
                        message.attachments) > 0 else "None",
                    "inline": "False"
                },
                {
                    "name": "Past Content",
                    "value": message.content[:1024] if len(message.content) > 0 else "None",
                    "inline": "False"
                },
                {
                    "name": "New Content",
                    "value": message_now.content[:1024] if len(message_now.content) > 0 else "None",
                    "inline": "False"
                },
                {
                    "name": "Embed",
                    "value": "\n".join([str(e.to_dict()) for e in message.embeds]) if len(
                        message.embeds) > 0 else "None",
                    "inline": "False"
                }
            ]
            for field in fields:
                embed.add_field(
                    name=field['name'],
                    value=field['value'],
                    inline=field['inline']
                )

            await edited_channel.send(embed=embed)

        except Exception:  # No cached message is available
            message_now = await channel.fetch_message(payload.message_id)
            embed = discord.Embed(
                title=":pencil: Edited Message",
                color=discord.Color.blurple()
            )

            fields = [
                {
                    "name": "Channel",
                    "value": self.bot.get_channel(payload.channel_id).mention,
                    "inline": "True"
                },
                {
                    "name": "Message ID",
                    "value": f"{payload.message_id} ([jump!]({message_now.jump_url}))",
                    "inline": "True"
                },
                {
                    "name": "Author",
                    "value": message_now.author,
                    "inline": "True"
                },
                {
                    "name": "Created At",
                    "value": discord.utils.format_dt(message_now.created_at, 'R'),
                    "inline": "True"
                },
                {
                    "name": "Edited At",
                    "value": discord.utils.format_dt(message_now.edited_at, 'R'),
                    "inline": "True"
                },
                {
                    "name": "New Content",
                    "value": message_now.content[:1024] if len(message_now.content) > 0 else "None",
                    "inline": "False"
                },
                {
                    "name": "Current Attachments",
                    "value": " | ".join([f"**{a.filename}**: [Link]({a.url})" for a in message_now.attachments]) if len(
                        message_now.attachments) > 0 else "None",
                    "inline": "False"
                },
                {
                    "name": "Current Embed",
                    "value": "\n".join([str(e.to_dict()) for e in message_now.embeds])[:1024] if len(
                        message_now.embeds) > 0 else "None",
                    "inline": "False"
                }
            ]
            for field in fields:
                embed.add_field(
                    name=field['name'],
                    value=field['value'],
                    inline=field['inline']
                )

            await edited_channel.send(embed=embed)

    async def log_delete_message_payload(self, payload):
        """
        Logs a message payload that came from a 'Delete Message' payload.
        """
        # Get the required resources
        channel = self.bot.get_channel(payload.channel_id)
        guild = self.bot.get_guild(SERVER_ID) if channel.type == discord.ChannelType.private else channel.guild
        deleted_channel = discord.utils.get(guild.text_channels, id=CHANNEL_DELETEDM)

        if channel.type != discord.ChannelType.private and channel.id in [CHANNEL_DELETEDM,
                                                                          CHANNEL_REPORTS,
                                                                          CHANNEL_CLOSED_REPORTS,
                                                                          CHANNEL_DMLOG,
                                                                          CHANNEL_EDITEDM]:
            return

        try:
            message = payload.cached_message
            if message.author == discord.User.bot:
                return
            if message.author == self.bot:
                return
            channel_name = (f"{message.author.mention}'s DM"
                            if channel.type == discord.ChannelType.private
                            else message.channel.mention)
            embed = discord.Embed(
                title=":fire: Deleted Message",
                color=discord.Color.brand_red()
            )
            fields = [
                {
                    "name": "Author",
                    "value": message.author,
                    "inline": "True"
                },
                {
                    "name": "Channel",
                    "value": channel_name,
                    "inline": "True"
                },
                {
                    "name": "Message ID",
                    "value": payload.message_id,
                    "inline": "True"
                },
                {
                    "name": "Created At",
                    "value": discord.utils.format_dt(message.created_at, 'R'),
                    "inline": "True"
                },
                {
                    "name": "Deleted At",
                    "value": discord.utils.format_dt(discord.utils.utcnow(), 'R'),
                    "inline": "True"
                },
                {
                    "name": "Attachments",
                    "value": " | ".join([f"**{a.filename}**: [Link]({a.url})" for a in message.attachments]) if len(
                        message.attachments) > 0 else "None",
                    "inline": "False"
                },
                {
                    "name": "Content",
                    "value": str(message.content)[:1024] if len(message.content) > 0 else "None",
                    "inline": "False"
                },
                {
                    "name": "Embed",
                    "value": "\n".join([str(e.to_dict()) for e in message.embeds])[:1024] if len(
                        message.embeds) > 0 else "None",
                    "inline": "False"
                }
            ]
            for field in fields:
                embed.add_field(
                    name=field['name'],
                    value=field['value'],
                    inline=field['inline']
                )

            await deleted_channel.send(embed=embed)

        except Exception as _:

            embed = discord.Embed(
                title=":fire: Deleted Message",
                description="Because this message was not cached, I was unable to retrieve its content before it was deleted.",
                color=discord.Color.brand_red()
            )
            fields = [
                {
                    "name": "Channel",
                    "value": self.bot.get_channel(payload.channel_id).mention,
                    "inline": "True"
                },
                {
                    "name": "Message ID",
                    "value": payload.message_id,
                    "inline": "True"
                }
            ]
            for field in fields:
                embed.add_field(
                    name=field['name'],
                    value=field['value'],
                    inline=field['inline']
                )

            await deleted_channel.send(embed=embed)


def setup(bot):
    bot.add_cog(Listeners(bot))
