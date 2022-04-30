from __future__ import annotations

import asyncio
import datetime
import json
import mongo

import discord
from discord.app_commands import Group, command, guilds, describe, checks
from discord.ext import commands

from utils.checks import is_staff
from utils.variables import *
from utils.views import Confirm, CronView, ReportView, Nuke

from typing import Literal, Optional, TYPE_CHECKING, Union

if TYPE_CHECKING:
    from bot import TMS

STOPNUKE = datetime.datetime.utcnow()


class CensorGroup(Group):
    def __init__(self, bot: TMS):
        self.bot = bot
        super().__init__(name="censor", guild_ids=[SERVER_ID])

    @property
    def cog(self) -> commands.Cog:
        return self.bot.get_cog("Moderation")

    @command()
    @checks.has_any_role(Role.SERVERLEADER, Role.FORMER_SL)
    @describe(phrase="The word/phrase to add to the censor list")
    async def add(
            self,
            interaction: discord.Interaction,
            phrase: str
    ):
        '''Adds a word to the censor'''
        from cogs.censor import CENSORED
        phrase = phrase.lower()
        if phrase in CENSORED['words']:
            return await interaction.response.send_message(
                f"`{phrase}` is already in the censored words list. Operation cancelled.")
        else:
            CENSORED['words'].append(phrase)
            await mongo.update("bot", "censor", CENSORED['_id'], {"$push": {"words": phrase}})
            return await interaction.response.send_message(f"Added Word to censored list")

    @command()
    @checks.has_any_role(Role.SERVERLEADER, Role.FORMER_SL)
    @describe(phrase="The word/phrase to remove from the censor list")
    async def remove(
            self,
            interaction: discord.Interaction,
            phrase: str
    ):
        '''Removes a word from the censor'''
        from cogs.censor import CENSORED
        phrase = phrase.lower()
        if phrase not in CENSORED["words"]:
            return await interaction.response.send_message(f"`{phrase}` is not in the list of censored words.")
        else:
            CENSORED["words"].remove(phrase)
            await mongo.update("bot", "censor", CENSORED['_id'], {"$pull": {"words": phrase}})
            return await interaction.response.send_message(f"Removed {phrase} from list of censored words")


class Moderation(commands.Cog):
    """Commands used for moderation"""
    print('Moderation Cog Loaded')

    def __init__(self, bot: TMS):
        self.bot = bot
        self.__cog_app_commands__.append(CensorGroup(bot))

    async def cog_check(self, interaction: commands.Context):
        return await is_staff(interaction)

    @property
    def display_emoji(self) -> discord.PartialEmoji:
        return discord.PartialEmoji(name='mod_badge', id=900488706748731472)

    @staticmethod
    async def send_closed_report(interaction: discord.Interaction, embed: discord.Embed):
        closed_reports: discord.abc.MessageableChannel = interaction.guild.get_channel(Channel.CLOSED_REPORTS)
        await closed_reports.send(embed=embed)

    @command()
    @guilds(SERVER_ID)
    @checks.has_any_role(Role.SERVERLEADER, Role.FORMER_SL)
    async def cron(self, interaction: discord.Interaction):
        """
        Allows staff to manipulate the CRON list.
        Steps:
            1. Parse the cron list.
            2. Create relevant action rows.
            3. Perform steps as staff request.
        """

        cron_list = await mongo.get_cron()
        if len(cron_list) == 0:
            return await interaction.response.send_message("No items currently in CRON list")

        cron_embed = discord.Embed(
            title="Managing the CRON list",
            color=discord.Color.fuchsia(),
            description=f'Hello! Managing the CRON list gives you the power to change when or how TMS-Bot '
                        'automatically executes commands. \n\n**Completing a task:** Do you want to instantly unmute '
                        'a user who is '
                        'scheduled to be unmuted later? Sure, select the CRON entry from the dropdown, and then '
                        'select *"Complete '
                        'Now"*! \n\n**Removing a task:** Want to completely remove a task so TMS-Bot will never '
                        'execute it? No worries, '
                        'select the CRON entry from the dropdown and select *Remove*!'
        )

        await interaction.response.send_message(
            "See information below for how to manage the CRON list.",
            view=CronView(cron_list, self.bot, interaction),
            embed=cron_embed
        )

    @command()
    @guilds(SERVER_ID)
    @checks.has_any_role(Role.SERVERLEADER, Role.FORMER_SL)
    @describe(delay="Slowmode delay in seconds")
    async def slowmode(
            self,
            interaction: discord.Interaction,
            mode: Literal["remove", "set"],
            delay: int,
            channel: Optional[discord.TextChannel]
    ):
        true_channel = channel or interaction.channel
        if mode == "remove":
            await true_channel.edit(slowmode_delay=0)
            await interaction.response.send_message("The slowmode was removed.")
        elif mode == "set":
            await true_channel.edit(slowmode_delay=delay)
            await interaction.response.send_message(f"Enabled a slowmode delay of {delay} seconds.")

    @command()
    @guilds(SERVER_ID)
    @checks.has_any_role(Role.SERVERLEADER, Role.FORMER_SL)
    @describe(
        member="The user to ban",
        reason="Why you are banning this user",
        ban_length="The amount of time the user is banned",
        delete_message_days="The number of days of messages the user has sent to be deleted"
    )
    async def ban(
            self,
            interaction: discord.Interaction,
            member: discord.User,
            reason: str,
            ban_length: Literal[
                "10 minutes", "30 minutes",
                "1 hour", "2 hours",
                "8 hours", "1 day",
                "4 days", "7 days",
                "1 month", "1 year",
                "Indefinitely"
            ],
            delete_message_days: Literal["Previous 24 hours", "Previous 7 days", "None"]
    ):
        """Bans a user."""
        times = {
            "10 minutes": discord.utils.utcnow() + datetime.timedelta(minutes=10),
            "30 minutes": discord.utils.utcnow() + datetime.timedelta(minutes=30),
            "1 hour": discord.utils.utcnow() + datetime.timedelta(hours=1),
            "2 hours": discord.utils.utcnow() + datetime.timedelta(hours=2),
            "4 hours": discord.utils.utcnow() + datetime.timedelta(hours=4),
            "8 hours": discord.utils.utcnow() + datetime.timedelta(hours=8),
            "1 day": discord.utils.utcnow() + datetime.timedelta(days=1),
            "4 days": discord.utils.utcnow() + datetime.timedelta(days=4),
            "7 days": discord.utils.utcnow() + datetime.timedelta(days=7),
            "1 month": discord.utils.utcnow() + datetime.timedelta(days=30),
            "1 year": discord.utils.utcnow() + datetime.timedelta(days=365),
        }
        delete_length = {
            "Previous 24 hours": 1,
            "Previous 7 days": 7,
            "None": 0
        }
        delete_message = delete_length[delete_message_days]
        if ban_length == "Indefinitely":
            time_statement = f"They will never be automatically unbanned."
        else:
            time_statement = f"They will be banned until {discord.utils.format_dt(times[ban_length], 'F')}."

        original_shown_embed = discord.Embed(
            title="Ban Confirmation",
            color=discord.Color.brand_red(),
            description=f"""
                    {member.mention} will be banned from the entire server. 
                    \n They will not be able to re-enter the server until the ban is lifted or the time expires.
                    \n {time_statement}
                    """
        )

        view = Confirm(interaction)
        await interaction.response.send_message("Please confirm that you would like to ban this user.", view=view,
                                                embed=original_shown_embed,
                                                ephemeral=False)

        message = f"""
        You have been banned from the TMS Scioly Discord server for {reason}. \n
        If you would like to appeal please DM `pandabear#8652`
        """

        reports_channel = interaction.guild.get_channel(Channel.REPORTS)

        await view.wait()
        if view.value is True:
            if member in interaction.guild.members:
                original_shown_embed.colour = discord.Color.brand_green()
                original_shown_embed.title = "Successfully Banned"
                original_shown_embed.description = f"member: `{member}` \n id: `{member.id}`\n\n was successfully banned"
                original_shown_embed.timestamp = discord.utils.utcnow()
                embed = discord.Embed(title=" ", description=message)
                embed.colour = discord.Color.brand_red()

                await member.send(embed=embed)
                await interaction.guild.ban(member, reason=reason, delete_message_days=delete_message)
                await interaction.edit_original_message(embed=original_shown_embed, content=None)
                await reports_channel.send(embed=original_shown_embed)
                if ban_length != "Indefinitely":
                    cron_cog = self.bot.get_cog("CronTasks")
                    await cron_cog.schedule_unban(member, times[ban_length])

            elif member not in interaction.guild.members:
                original_shown_embed.colour = discord.Color.brand_green()
                original_shown_embed.title = "Successfully Banned"
                original_shown_embed.description = f"member: `{member}` \n id: `{member.id}`\n\n was successfully banned"
                original_shown_embed.timestamp = discord.utils.utcnow()
                await interaction.edit_original_message(embed=original_shown_embed, content=None)
                await reports_channel.send(embed=original_shown_embed)
                await interaction.guild.ban(member, reason=reason, delete_message_days=delete_message)
                if ban_length != "Indefinitely":
                    cron_cog = self.bot.get_cog("CronTasks")
                    await cron_cog.schedule_unban(member, times[ban_length])
            else:
                await interaction.edit_original_message(
                    content="The user was not successfully banned because of an error. They remain in the server.",
                    embed=None, view=None)
        else:
            original_shown_embed.colour = discord.Colour.brand_green()
            original_shown_embed.description = f"`{member.name}` was not banned"
            original_shown_embed.title = "Ban Cancelled"
            await interaction.response.send_message(embed=original_shown_embed, view=None, content=None)

    @command()
    @guilds(SERVER_ID)
    @checks.has_any_role(Role.SERVERLEADER, Role.FORMER_SL)
    @describe(channel="The channel to sync permissions with")
    async def sync(self, interaction: discord.Interaction, channel: discord.TextChannel):
        """Syncs permissions to channel category"""

        if channel is None:
            await interaction.channel.edit(sync_permissions=True)
            await interaction.response.send_message(
                f'Permissions for {interaction.channel.mention} synced with {interaction.channel.category}')
        else:
            await channel.edit(sync_permissions=True)
            await interaction.response.send_message(f'Permissions for {channel.mention} synced with {channel.category}')

    @command()
    @guilds(SERVER_ID)
    @checks.has_any_role(Role.SERVERLEADER, Role.FORMER_SL)
    async def kick(
            self,
            interaction: discord.Interaction,
            member: discord.Member,
            reason: str
    ):
        view = Confirm(interaction)

        await interaction.response.send_message(f"Are you sure you want to kick `{member}` for `{reason}`", view=view)
        await view.wait()
        if view.value is False:
            await interaction.response.send_message('Aborting...')
        if view.value is True:

            if reason is None:
                await interaction.response.send_message("Please specify a reason why you want to kick this user!")
            if member.id in TMS_BOT_IDS:
                return await interaction.response.send_message("Hey! You can't kick me!!")
            await member.kick(reason=reason)

            em6 = discord.Embed(title="",
                                description=f"{member.mention} was kicked for {reason}.",
                                color=0xFF0000)

            await interaction.response.send_message(embed=em6)
        return view.value

    @command()
    @guilds(SERVER_ID)
    @checks.has_any_role(Role.SERVERLEADER, Role.FORMER_SL)
    @describe(user="The user to mute", reason="Reason for muting this user",
              mute_length="How long to mute the user for")
    async def mute(
            self,
            interaction: discord.Interaction,
            user: discord.Member,
            reason: str,
            mute_length: Literal[
                "10 minutes", "30 minutes", "1 hour",
                "2 hours", "8 hours", "1 day",
                "4 days", "7 days", "1 month",
                "1 year", "Indefinitely"
            ]
    ):

        times = {
            "10 minutes": discord.utils.utcnow() + datetime.timedelta(minutes=10),
            "30 minutes": discord.utils.utcnow() + datetime.timedelta(minutes=30),
            "1 hour": discord.utils.utcnow() + datetime.timedelta(hours=1),
            "2 hours": discord.utils.utcnow() + datetime.timedelta(hours=2),
            "4 hours": discord.utils.utcnow() + datetime.timedelta(hours=4),
            "8 hours": discord.utils.utcnow() + datetime.timedelta(hours=8),
            "1 day": discord.utils.utcnow() + datetime.timedelta(days=1),
            "4 days": discord.utils.utcnow() + datetime.timedelta(days=4),
            "7 days": discord.utils.utcnow() + datetime.timedelta(days=7),
            "1 month": discord.utils.utcnow() + datetime.timedelta(days=30),
            "1 year": discord.utils.utcnow() + datetime.timedelta(days=365),
        }

        if mute_length == "Indefinitely":
            time_statement = "The user will never be automatically unmuted."
        else:
            time_statement = f"The user will be muted until {discord.utils.format_dt(times[mute_length], 'F')}."

        original_shown_embed = discord.Embed(
            title="Mute Confirmation",
            color=discord.Color.brand_red(),
            description=f"""
            {user.mention} will be muted across the entire server. 
            The user will no longer be able to communicate in any channels they can read.
            {time_statement}
            """
        )

        view = Confirm(interaction)
        await interaction.response.send_message("Please confirm that you would like to mute this user.", view=view,
                                                embed=original_shown_embed)

        message = f"You have been muted from the TMS Scioly Discord server for {reason}."

        await view.wait()
        role = interaction.guild.get_role(Role.MUTED)
        if view.value is True:
            await user.add_roles(role)
            await user.send(message)
            if mute_length != "Indefinitely":
                cron_cog = self.bot.get_cog("CronTasks")
                await cron_cog.schedule_unmute(user, times[mute_length])

            original_shown_embed.colour = discord.Colour.brand_green()
            original_shown_embed.title = "Successfully Muted"
            original_shown_embed.description = f"{user.name} was successfully muted"
            original_shown_embed.timestamp = discord.utils.utcnow()
            await interaction.edit_original_message(embed=original_shown_embed, view=None, content=None)
            close_embed = discord.Embed(
                title=f"Successfully Muted {user}",
                description=f"{user.mention} was successfully muted until "
                            f"{discord.utils.format_dt(times[mute_length], 'F')} \n\n"
                            f"Use `/cron` to modify this mute.",
                timestamp=discord.utils.utcnow(),
                color=discord.Color.brand_green()
            )
            await self.send_closed_report(interaction, close_embed)

        else:
            original_shown_embed.colour = discord.Colour.brand_green()
            original_shown_embed.title = "Mute Canceled"
            original_shown_embed.description = f"Mute of `{user.name}` was canceled"
            original_shown_embed.timestamp = discord.utils.utcnow()
            await interaction.edit_original_message(embed=original_shown_embed, view=None, content=None)

    @command()
    @guilds(SERVER_ID)
    @checks.has_any_role(Role.SERVERLEADER, Role.FORMER_SL)
    @describe(count="The amount of messages to delete")
    async def nuke(self, interaction: discord.Interaction, count: int):
        """Nukes (deletes) a specified amount of messages."""
        global STOPNUKE
        max_delete = 100
        if int(count) > max_delete:
            return await interaction.response.send_message("Chill. No more than deleting 100 messages at a time.")
        channel = interaction.channel
        if int(count) < 0:
            history = await channel.history(limit=105).flatten()
            message_count = len(history)
            if message_count > 100:
                count = 100
            else:
                count = message_count + int(count) - 1
            if count <= 0:
                return await interaction.response.send_message(
                    "Sorry, you can not delete a negative amount of messages. This is likely because you are asking "
                    "to save more messages than there are in the channel.")

        original_shown_embed = discord.Embed(
            title="NUKE COMMAND PANEL",
            color=discord.Color.brand_red(),
            description=f"""
            {count} messages will be deleted from {channel.mention} in `10` seconds...
            To stop this nuke, press the red button below!
            """
        )
        view = Nuke(interaction)
        await interaction.response.send_message(embed=original_shown_embed, view=view)
        await asyncio.sleep(1)

        for i in range(9, 0, -1):
            if view.stopped:
                break
            original_shown_embed.description = f"""
            {count} messages will be deleted from {channel.mention} in `{i}` seconds...
            To stop this nuke, press the red button below!
            """
            await interaction.edit_original_message(embed=original_shown_embed, view=view)
            await asyncio.sleep(1)

        if not view.stopped:
            original_shown_embed.description = f"""
            Now nuking {count} messages from the channel...
            """
            await interaction.edit_original_message(embed=original_shown_embed, view=None)

            # Nuke has not been stopped, proceed with deleting messages
            def nuke_check(msgs: discord.Message) -> bool:
                return not msgs.pinned

            new_embed = discord.Embed(
                title="NUKE COMMAND PANEL",
                color=discord.Color.brand_green(),
                description=f"""
                        {count} messages have been deleted from {channel.mention} 
                        """
            )

            await channel.purge(limit=count + 3, check=nuke_check)
            await channel.send(embed=new_embed)

    @command()
    @guilds(SERVER_ID)
    @checks.has_any_role(Role.SERVERLEADER, Role.FORMER_SL)
    @describe(channel="The channel you want to lock")
    async def lock(self, interaction: discord.Interaction, channel: discord.TextChannel):
        """
        Locks a channel to Member access.
        """
        member = interaction.user
        if channel is None:
            member_role = interaction.guild.get_role(Role.M)
            await interaction.channel.set_permissions(member_role, add_reactions=False, send_messages=False,
                                                      read_messages=True)
            SL = interaction.guild.get_role(Role.SERVERLEADER)
            await interaction.channel.set_permissions(SL, add_reactions=True, send_messages=True, read_messages=True)
            await interaction.response.send_message(f"Locked :lock: {interaction.channel.mention} to Member access.")
        else:
            member_role = interaction.guild.get_role(Role.M)
            await channel.set_permissions(member_role, add_reactions=False, send_messages=False, read_messages=True)
            SL = interaction.guild.get_role(Role.SERVERLEADER)
            await channel.set_permissions(SL, add_reactions=True, send_messages=True, read_messages=True)
            await interaction.response.send_message(f"Locked :lock: {channel.mention} to Member access.")

    @command()
    @guilds(SERVER_ID)
    @checks.has_any_role(Role.SERVERLEADER, Role.FORMER_SL)
    @describe(channel="The channel to unlock")
    async def unlock(
            self,
            interaction: discord.Interaction,
            channel: Optional[discord.TextChannel]
    ):
        """Unlocks a channel to Member access."""
        member = interaction.user
        if channel is None:
            member_role = interaction.guild.get_role(Role.M)
            await interaction.channel.set_permissions(member_role, add_reactions=True, send_messages=True,
                                                      read_messages=True)
            SL = interaction.guild.get_role(Role.SERVERLEADER)
            await interaction.channel.set_permissions(SL, add_reactions=True, send_messages=True, read_messages=True)
            await interaction.response.send_message(
                f"Unlocked :unlock: {interaction.channel.mention} to Member access. Please check if permissions need to be synced.")
        else:
            member_role = interaction.guild.get_role(Role.M)
            await channel.set_permissions(member_role, add_reactions=True, send_messages=True, read_messages=True)
            SL = interaction.guild.get_role(Role.SERVERLEADER)
            await channel.set_permissions(SL, add_reactions=True, send_messages=True, read_messages=True)
            await interaction.response.send_message(
                f"Unlocked :unlock: {channel.mention} to Member access. Please check if permissions need to be synced.")

    @command()
    @guilds(SERVER_ID)
    @checks.has_any_role(Role.SERVERLEADER, Role.FORMER_SL)
    @describe(reason="The reason you are warning this user", member="The user you are warning")
    async def warn(self, interaction: discord.Interaction, member: discord.Member, reason: str):
        '''Warns a user'''
        server = self.bot.get_guild(SERVER_ID)
        reports_channel = interaction.guild.get_channel(Channel.REPORTS)
        mod = interaction.user
        avatar = mod.avatar
        avatar1 = member.avatar.url

        if member is interaction.user:
            return await interaction.response.send_message("You cannot warn yourself :rolling_eyes:")
        if member.id in TMS_BOT_IDS:
            return await interaction.response.send_message(
                f"Hey {interaction.user.mention}! You can't warn {member.mention}")
        embed = discord.Embed(title="Warning Given",
                              description=f"Warning issued to {member.mention} \n id: `{member.id}`",
                              color=0xFF0000)
        embed.add_field(name="Reason:", value=f"`{reason}`")
        embed.add_field(name="Responsible Moderator:", value=f"{mod.mention}")
        embed.set_author(name=f"{member}",
                         icon_url=avatar1)

        embed1 = discord.Embed(title=" ", description=f"{member} has been warned", color=0x2E66B6)

        embed2 = discord.Embed(title=f"Warning",
                               description=f"You have been given a warning by {mod.mention} for `{reason}`. \n Please follow the rules of the server",
                               color=0xFF0000)
        embed2.set_author(name=f"{mod}",
                          icon_url=avatar)

        await reports_channel.send(embed=embed, view=ReportView())
        await interaction.response.send_message(embed=embed1)
        await member.send(embed=embed2)

    @command()
    @guilds(SERVER_ID)
    @checks.has_any_role(Role.SERVERLEADER, Role.FORMER_SL)
    @describe(member="The member you want to blacklist from using commands")
    async def blacklist(self, interaction: discord.Interaction, member: discord.Member):
        '''Blacklist a user from using commands'''
        if member.id == self.bot.owner_id:
            return await interaction.response.send_message("You can't blacklist the owner of the bot :rolling_eyes:")
        try:
            with open("blacklist.json") as f:
                data = json.load(f)
            if member.id in data['blacklisted_ids']:
                return await interaction.response.send_message(
                    f'{member.mention} is already blacklisted from using commands!')
            else:
                data["blacklisted_ids"].append(member.id)
                with open("blacklist.json", 'w') as f:
                    json.dump(data, f)
                await interaction.response.send_message(f'Blacklisted {member.mention} from using commands!')
        except Exception:
            await interaction.response.send_message(f'Failed to blacklist {member.mention}!')

    @command()
    @guilds(SERVER_ID)
    @checks.has_any_role(Role.SERVERLEADER, Role.FORMER_SL)
    async def unblacklist(self, interaction: discord.Interaction, member: discord.Member):
        '''Un-Blacklist a user from using commands'''
        id = member.id
        with open("blacklist.json") as f:
            data = json.load(f)
        if member.id in data['blacklisted_ids']:
            # try:
            index = data["blacklisted_ids"].index(id)
            del data["blacklisted_ids"][index]
            with open('blacklist.json', 'w') as f:
                json.dump(data, f)

                await interaction.response.send_message(f"Successfully removed command blacklist from {member.mention}")
            #
            # except Exception: await interaction.response.send_message(f"Couldn't remove command blacklist from {
            # member.mention}", ephemeral=True)
        else:
            await interaction.response.send_message(f"{member.mention} is not blacklisted from using commands")


async def setup(bot: TMS):
    await bot.add_cog(Moderation(bot))
