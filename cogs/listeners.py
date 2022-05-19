from __future__ import annotations

from typing import TYPE_CHECKING

import discord
import slate
from discord.ext import commands

import custom
from custom import enums
from utils import Channel, Role, SERVER_ID, TMS_BOT_IDS

if TYPE_CHECKING:
    from bot import TMS
    from cogs.censor import Censor
    from cogs.report import Reporter


class Listeners(commands.Cog):
    def __init__(self, bot: TMS):
        self.bot = bot

    @commands.Cog.listener("on_socket_event_type")
    async def _increment_socket_event_counter(self, event_type: str) -> None:
        self.bot.socket_stats[event_type] += 1

    @commands.Cog.listener()
    async def on_member_update(self, before, after) -> None:

        if after.nick is None:
            return
        censor_cog: "Censor" | commands.Cog = self.bot.get_cog("Censor")
        censor_found = censor_cog.censor_needed(after.nick)
        if censor_found:
            # If name contains a censored link
            reporter_cog: "Reporter" | commands.Cog = self.bot.get_cog("Reporter")
            await reporter_cog.create_inappropriate_username_report(
                member=after, offending_username=after.nick
            )

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        if member.guild.id != SERVER_ID:
            return

        name = member.name
        censor_cog: "Censor" | commands.Cog = self.bot.get_cog("Censor")
        if censor_cog.censor_needed(name):
            reporter_cog: "Reporter" | commands.Cog = self.bot.get_cog("Reporter")
            await reporter_cog.create_inappropriate_username_report(member, member.name)

        role: discord.Role = member.guild.get_role(Role.MEMBER)
        join_channel: discord.TextChannel = self.bot.get_channel(Channel.WELCOME)
        await member.add_roles(role)
        embed = discord.Embed(
            title="Welcome!",
            description=f"{member.mention}! Welcome to the TMS Scio Discord. If you need any help "
            "feel free to open a ticket in <#848996283288518718> or use `/help` for "
            "bot-command help! Please state your name, JV or Varsity, and add your "
            "events in <#863054629787664464> ! ",
            timestamp=discord.utils.utcnow(),
            color=discord.Color.fuchsia(),
        )
        await join_channel.send(embed=embed, content=f"{member.mention}")

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if after.author.id in TMS_BOT_IDS:
            return
        if not after.guild.id == SERVER_ID:
            return
        if after.channel.type != discord.ChannelType.private and after.channel.id in (
            Channel.EDITEDM,
            Channel.DELETEDM,
            Channel.DELETEDM,
        ):
            return
        censor_cog: "Censor" | commands.Cog = self.bot.get_cog("Censor")
        censor_found = censor_cog.censor_needed(after.content)
        if censor_found:
            await after.delete()
        message_embed = discord.Embed(
            title="\U0000270f Edited Message", color=discord.Color.blurple()
        )
        message_embed.add_field(name="Author", value=after.author.mention, inline=True)
        message_embed.add_field(name="Message ID", value=after.id, inline=True)
        message_embed.add_field(
            name="Message Link", value=f"[Here!]({after.jump_url})", inline=False
        )
        message_embed.add_field(
            name="Before",
            value=before.content[:1024] if len(before.content) > 0 else "None",
            inline=True,
        )
        message_embed.add_field(
            name="After",
            value=after.content[:1024] if len(after.content) > 0 else "None",
            inline=True,
        )
        message_embed.add_field(
            name="Attachments",
            value=" | ".join(
                [f"**{a.filename}**: [Link]({a.url})" for a in after.attachments]
            )
            if len(after.attachments) > 0
            else "None",
            inline=False,
        )
        message_embed.add_field(
            name="Embeds",
            value="\n".join([str(e.to_dict()) for e in after.embeds])
            if len(after.embeds) > 0
            else "None",
            inline=False,
        )
        message_embed.add_field(
            name="Created",
            value=discord.utils.format_dt(before.created_at, "R"),
            inline=True,
        )
        message_embed.add_field(
            name="Edited",
            value=discord.utils.format_dt(after.created_at, "R"),
            inline=True,
        )
        moderation_log = self.bot.get_channel(Channel.DELETEDM)
        await moderation_log.send(embed=message_embed)

    @staticmethod
    async def send_to_dm_log(bot: TMS, message: discord.Message):
        dm_channel = bot.get_channel(Channel.DELETEDM)

        if message.author.id == bot.user.id:
            title = ":speech_balloon: Outgoing Direct Message"
            color = discord.Color.fuchsia()
        else:
            title = ":speech_balloon: Incoming Direct Message to TMS-Bot"
            color = discord.Color.brand_green()

        # Create an embed containing the direct message info and send it to the log channel
        message_embed = discord.Embed(
            title=title,
            description=message.content
            if len(message.content) > 0
            else "This message contained no content.",
            color=color,
        )
        message_embed.add_field(
            name="Author", value=message.author.mention, inline=True
        )
        message_embed.add_field(name="Message ID", value=message.id, inline=True)
        message_embed.add_field(
            name="Sent",
            value=discord.utils.format_dt(message.created_at, "R"),
            inline=True,
        )
        message_embed.add_field(
            name="Attachments",
            value=" | ".join(
                [f"**{a.filename}**: [Link]({a.url})" for a in message.attachments]
            )
            if len(message.attachments) > 0
            else "None",
            inline=True,
        )
        await dm_channel.send(embed=message_embed)

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if message.author.id in TMS_BOT_IDS:
            return
        if not message.guild.id == SERVER_ID:
            return
        if (
            message.channel.type != discord.ChannelType.private
            and message.channel.id
            in (Channel.EDITEDM, Channel.DELETEDM, Channel.DELETEDM)
        ):
            return
        message_embed = discord.Embed(
            title="\U0001f525 Deleted Message", color=discord.Color.brand_red()
        )
        message_embed.add_field(
            name="Author", value=message.author.mention, inline=True
        )
        message_embed.add_field(name="Message ID", value=message.id, inline=True)
        message_embed.add_field(
            name="Content",
            value=str(message.content)[:1024] if len(message.content) > 0 else "None",
            inline=False,
        )
        message_embed.add_field(
            name="Attachments",
            value=" | ".join(
                [f"**{a.filename}**: [Link]({a.url})" for a in message.attachments]
            )
            if message.attachments
            else "None",
            inline=False,
        )
        message_embed.add_field(
            name="Created",
            value=discord.utils.format_dt(message.created_at, "R"),
            inline=False,
        )
        message_embed.add_field(
            name="Deleted",
            value=discord.utils.format_dt(discord.utils.utcnow(), "R"),
            inline=False,
        )
        message_embed.add_field(
            name="Embed",
            value="\n".join([str(e.to_dict()) for e in message.embeds])[:1024]
            if len(message.embeds) > 0
            else "None",
            inline=False,
        )
        moderation_log = self.bot.get_channel(Channel.EDITEDM)
        await moderation_log.send(embed=message_embed)

    # Voice events

    @commands.Cog.listener("on_voice_state_update")
    async def _handle_voice_client_disconnect(
        self,
        member: discord.Member,
        before: discord.VoiceState,
        after: discord.VoiceState,
    ) -> None:

        assert self.bot.user is not None

        if member.id != self.bot.user.id:
            return

        if (
            before.channel is not None
            and after.channel is None
            and before.channel.guild.voice_client is not None
        ):
            await before.channel.guild.voice_client.disconnect(force=True)

    @commands.Cog.listener("on_slate_track_start")
    async def _handle_track_start(
        self, player: custom.Player, _: slate.TrackStart
    ) -> None:
        await player.handle_track_start()

    @commands.Cog.listener("on_slate_track_end")
    async def _handle_track_end(
        self, player: custom.Player, event: slate.TrackEnd
    ) -> None:

        if event.reason == "REPLACED":
            return

        await player.handle_track_end(enums.TrackEndReason.NORMAL)

    @commands.Cog.listener("on_slate_track_stuck")
    async def _handle_track_stuck(
        self, player: custom.Player, _: slate.TrackStuck
    ) -> None:
        await player.handle_track_end(enums.TrackEndReason.STUCK)

    @commands.Cog.listener("on_slate_track_exception")
    async def _handle_track_exception(
        self, player: custom.Player, _: slate.TrackException
    ) -> None:
        await player.handle_track_end(enums.TrackEndReason.EXCEPTION)


async def setup(bot: TMS):
    await bot.add_cog(Listeners(bot))
