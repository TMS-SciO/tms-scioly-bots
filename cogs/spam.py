from __future__ import annotations

import discord
import datetime
from discord.ext import commands
from utils import Role, SERVER_ID
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bot import TMS


class SpamManager(commands.Cog):
    recent_messages = []

    # Limits
    caps_limit = 15
    mute_limit = 8
    warning_limit = 3

    def __init__(self, bot: TMS):
        self.bot = bot
        self.recent_messages = []

    @staticmethod
    def has_caps(message: discord.Message) -> bool:
        """
        Returns true if the message has caps (more capitalized letters than lowercase letters)
        """
        caps = False
        upper_count = sum(1 for c in message.content if c.isupper())
        lower_count = sum(1 for c in message.content if c.islower())
        if upper_count > (lower_count + 3):
            caps = True

        return caps

    async def check_for_repetition(self, message: discord.Message):
        """
        Checks to see if the message has often been repeated, and takes action if action is needed.
        """
        matching_messages = filter(
            lambda m: m.author == message.author and m.content.lower() == message.content.lower(), self.recent_messages)
        matching_messages_count = len(list(matching_messages))

        if matching_messages_count >= self.mute_limit:
            await self.mute(message.author)

            # Send info message to channel about mute
            info_message = await message.channel.send(f"Successfully muted {message.author.mention} for 1 hour.")

            # Send info message to staff about mute
            staff_embed_message = discord.Embed(
                title=f"Automatic mute occurred",
                color=discord.Color.yellow(),
                description=f"""
                {message.author.mention} was automatically muted in {message.channel} for **repeatedly spamming 
                similar messages**. The user was **repeatedly warned**, and sent **{self.mute_limit} messages** 
                before a mute was applied. 
                Their mute will automatically expire in: {discord.utils.format_dt(discord.utils.utcnow() + datetime.timedelta(hours=1), 'R')}.
                No further action needs to be taken. To teleport to the issue, please [click here]({info_message.jump_url}). Please know that the offending messages may have been deleted by the author or staff. 
                """
            )
            reporter_cog = self.bot.get_cog('Reporter')
            await reporter_cog.create_staff_message(staff_embed_message)
        elif matching_messages_count >= self.warning_limit:
            await message.author.send(
                f"{message.author.mention}, please avoid spamming. Additional spam will lead to your account being "
                f"temporarily muted.")

    async def check_for_caps(self, message: discord.Message):
        """
        Checks the message to see if it and recent messages contain a lot of capital letters.
        """
        caps_messages = filter(lambda m: m.author == message.author and self.has_caps(m) and len(m.content) > 5,
                               self.recent_messages)
        caps_messages_count = len(list(caps_messages))

        if caps_messages_count >= self.caps_limit and self.has_caps(message):
            await self.mute(message.author)

            # Send info message to channel about mute
            info_message = await message.channel.send(f"Successfully muted {message.author.mention} for 1 hour.")

            # Send info message to staff about mute
            staff_embed_message = discord.Embed(
                title=f"Automatic mute occurred",
                color=discord.Color.yellow(),
                description=f"""
                {message.author.mention} was automatically muted in {message.channel} for **repeatedly using caps** in their messages. The user was **repeatedly warned**, and sent **{self.caps_limit} messages** before a mute was applied.
                Their mute will automatically expire in: {discord.utils.format_dt(discord.utils.utcnow() + datetime.timedelta(hours=1), 'R')}.
                No further action needs to be taken. To teleport to the issue, please [click here]({info_message.jump_url}). Please know that the offending messages may have been deleted by the author or staff.
                """
            )
            reporter_cog = self.bot.get_cog('Reporter')
            await reporter_cog.create_staff_message(staff_embed_message)
        elif caps_messages_count >= self.warning_limit and self.has_caps(message):
            await message.author.send(
                f"{message.author.mention}, please avoid using all caps in your messages. Repeatedly doing so will "
                f"cause your account to be temporarily muted.")

    async def mute(self, member: discord.Member):
        """
        Mutes the user and schedules an unmute for an hour later in CRON.
        """
        guild = self.bot.get_guild(SERVER_ID)
        muted_role = guild.get_role(Role.MUTED)
        unmute_time = datetime.datetime.now() + datetime.timedelta(hours=1)
        cron_cog = self.bot.get_cog("CronTasks")
        await cron_cog.schedule_unmute(member, unmute_time)
        await member.add_roles(muted_role)

    async def store_and_validate(self, message: discord.Message):
        """
        Stores a message in recent_messages and validates whether the message is spam or not.
        """
        # No need to take action for bots
        if message.author.bot:
            return
        if message.channel.id in (816809336113201193, 816806977723957278, 827537529162039326):
            # Ignore if message # in bot-spam
            return
        if message.author.id == self.bot.owner_id:
            # Ignore if is owner
            return
        if message.content.lower() in ("yea", "yeah", "ok",):
            return

        # Store message
        self.recent_messages.insert(0, message)
        self.recent_messages = self.recent_messages[:20]  # Only store 20 recent messages at once

        await self.check_for_repetition(message)
        await self.check_for_caps(message)


async def setup(bot: TMS):
    await bot.add_cog(SpamManager(bot))
