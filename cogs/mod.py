import asyncio
import datetime
import json

import discord
from discord import ApplicationContext, Permission
from discord.commands import slash_command, permissions
from discord.commands.commands import Option
from discord.ext import commands

from cogs.censor import CENSORED
from utils.checks import is_staff
from utils.variables import *
from utils.views import Confirm, CronView, ReportView, Nuke

STOPNUKE = datetime.datetime.utcnow()


class Moderation(commands.Cog):
    """Commands used for moderation"""
    print('Moderation Cog Loaded')

    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        return await is_staff(ctx)

    @property
    def display_emoji(self) -> discord.PartialEmoji:
        return discord.PartialEmoji(name='mod_badge', id=900488706748731472)

    @slash_command(guild_ids=[SERVER_ID])
    @permissions.has_any_role(ROLE_SERVERLEADER, guild_id=SERVER_ID)
    async def cron(self, ctx):
        """
        Allows staff to manipulate the CRON list.
        Steps:
            1. Parse the cron list.
            2. Create relevant action rows.
            3. Perform steps as staff request.
        """

        cron_list = CRON_LIST
        if len(CRON_LIST) == 0:
            return await ctx.respond("No items currently in CRON_LIST")

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

        await ctx.respond("See information below for how to manage the CRON list.",
                          view=CronView(cron_list, self.bot, ctx),
                          embed=cron_embed)

    censor = discord.SlashCommandGroup(
        "censor",
        "Managing the bot's censor system",
        guild_ids=[SERVER_ID],
        permissions=[Permission(
            823929718717677568,
            1,
            True
        )],
        default_permission=False
    )

    @censor.command()
    @permissions.has_any_role(ROLE_SERVERLEADER, guild_id=SERVER_ID)
    async def add(
            self,
            ctx,
            phrase: Option(str, description="The new word to add. For the new word, type the word")
    ):
        '''Adds a word to the censor'''
        phrase = phrase.lower()
        if phrase in CENSORED['words']:
            return await ctx.respond(f"`{phrase}` is already in the censored words list. Operation cancelled.")
        else:
            CENSORED['words'].append(phrase)
            self.bot.reload_extension("cogs.censor")
            return await ctx.respond(f"Added Word to censored list")

    @censor.command()
    @permissions.has_any_role(ROLE_SERVERLEADER, guild_id=SERVER_ID)
    async def remove(
            self,
            ctx,
            phrase: Option(str, description="The word to remove from the censor list.")
    ):
        '''Removes a word from the censor'''
        phrase = phrase.lower()
        if phrase not in CENSORED["words"]:
            return await ctx.respond(f"`{phrase}` is not in the list of censored words.")
        else:
            CENSORED["words"].remove(phrase)
            self.bot.reload_extension("cogs.censor")
            return await ctx.respond(f"Removed {phrase} from list of censored words")

    @slash_command(guild_ids=[SERVER_ID])
    @permissions.has_any_role(ROLE_SERVERLEADER, guild_id=SERVER_ID)
    async def slowmode(self,
                       ctx: ApplicationContext,
                       mode: Option(str,
                                    choices=["remove", "set"],
                                    description="How to change the slowmode in the channel."),
                       delay: Option(int,
                                     description="Slowmode delay in seconds"),
                       channel: Option(discord.TextChannel,
                                       description="The channel to edit slowmode",
                                       required=False)
                       ):
        true_channel = channel or ctx.channel
        if mode == "remove":
            await true_channel.edit(slowmode_delay=0)
            await ctx.respond("The slowmode was removed.")
        elif mode == "set":
            await true_channel.edit(slowmode_delay=delay)
            await ctx.respond(f"Enabled a slowmode delay of {delay} seconds.")

    @slash_command(guild_ids=[SERVER_ID])
    @permissions.has_any_role(ROLE_SERVERLEADER, guild_id=SERVER_ID)
    async def ban(self,
                  ctx,
                  member: Option(discord.User, description='the member to ban'),
                  reason: Option(str, description='the reason to ban this member'),
                  ban_length: Option(str, choices=["10 minutes",
                                                   "30 minutes",
                                                   "1 hour",
                                                   "2 hours",
                                                   "8 hours",
                                                   "1 day",
                                                   "4 days",
                                                   "7 days",
                                                   "1 month",
                                                   "1 year",
                                                   "Indefinitely"
                                                   ],
                                     description='the amount of time banned'),
                  delete_message_days: Option(str,
                                              description="The number of days of messages the user has sent to be "
                                                          "deleted",
                                              choices=["Previous 24 hours", "Previous 7 days", "None"]
                                              )
                  ):
        """Bans a user."""
        times = {
            "10 minutes": datetime.datetime.now() + datetime.timedelta(minutes=10),
            "30 minutes": datetime.datetime.now() + datetime.timedelta(minutes=30),
            "1 hour": datetime.datetime.now() + datetime.timedelta(hours=1),
            "2 hours": datetime.datetime.now() + datetime.timedelta(hours=2),
            "4 hours": datetime.datetime.now() + datetime.timedelta(hours=4),
            "8 hours": datetime.datetime.now() + datetime.timedelta(hours=8),
            "1 day": datetime.datetime.now() + datetime.timedelta(days=1),
            "4 days": datetime.datetime.now() + datetime.timedelta(days=4),
            "7 days": datetime.datetime.now() + datetime.timedelta(days=7),
            "1 month": datetime.datetime.now() + datetime.timedelta(days=30),
            "1 year": datetime.datetime.now() + datetime.timedelta(days=365),
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

        view = Confirm(ctx)
        await ctx.respond("Please confirm that you would like to ban this user.", view=view,
                          embed=original_shown_embed,
                          ephemeral=False)

        message = f"""
        You have been banned from the TMS Scioly Discord server for {reason}. \n
        If you would like to appeal please DM `pandabear#0001`
        """

        guild = ctx.author.guild
        server = self.bot.get_guild(SERVER_ID)
        reports_channel = discord.utils.get(server.text_channels, id=CHANNEL_REPORTS)

        await view.wait()
        if view.value is True:
            if member in guild.members:
                original_shown_embed.colour = discord.Color.brand_green()
                original_shown_embed.title = "Successfully Banned"
                original_shown_embed.description = f"member: `{member}` \n id: `{member.id}`\n\n was successfully banned"
                original_shown_embed.timestamp = discord.utils.utcnow()
                embed = discord.Embed(title=" ", description=message)
                embed.colour = discord.Color.brand_red()

                await member.send(embed=embed)
                await ctx.guild.ban(member, reason=reason, delete_message_days=delete_message)
                await ctx.interaction.edit_original_message(embed=original_shown_embed, content=None)
                await reports_channel.send(embed=original_shown_embed)
                if ban_length != "Indefinitely":
                    cron_cog = self.bot.get_cog("CronTasks")
                    await cron_cog.schedule_unban(member, times[ban_length])

            elif member not in guild.members:
                original_shown_embed.colour = discord.Color.brand_green()
                original_shown_embed.title = "Successfully Banned"
                original_shown_embed.description = f"member: `{member}` \n id: `{member.id}`\n\n was successfully banned"
                original_shown_embed.timestamp = discord.utils.utcnow()
                await ctx.interaction.edit_original_message(embed=original_shown_embed, content=None)
                await reports_channel.send(embed=original_shown_embed)
                await ctx.guild.ban(member, reason=reason, delete_message_days=delete_message)
                if ban_length != "Indefinitely":
                    cron_cog = self.bot.get_cog("CronTasks")
                    await cron_cog.schedule_unban(member, times[ban_length])
            else:
                await ctx.interaction.edit_original_message(
                    content="The user was not successfully banned because of an error. They remain in the server.",
                    embed=None, view=None)
        else:
            original_shown_embed.colour = discord.Colour.brand_green()
            original_shown_embed.description = "f`{member.name}` was not banned"
            original_shown_embed.title = "Ban Cancelled"
            await ctx.respond(embed=original_shown_embed, view=None, content=None)

    @slash_command(guild_ids=[SERVER_ID])
    @permissions.has_any_role(ROLE_SERVERLEADER, guild_id=SERVER_ID)
    async def dm(self, ctx,
                 member: Option(discord.Member, description="The member you want to send the message to"),
                 message: Option(str, description="The message you wish to send to the member")):
        em1 = discord.Embed(title=f" ",
                            description=f"> {message}",
                            color=0x2F3136)
        em1.set_author(name=f"Message from {ctx.author}", icon_url=ctx.author.avatar)
        await ctx.respond(f"Message sent to `{member}`")
        await member.send(embed=em1)

    @slash_command(guild_ids=[SERVER_ID])
    @permissions.has_any_role(ROLE_SERVERLEADER, guild_id=SERVER_ID)
    async def sync(self, ctx,
                   channel: Option(discord.TextChannel, description="The channel to sync permissions with",
                                   required=False)):
        '''Syncs permmissions to channel category'''

        if channel is None:
            await ctx.channel.edit(sync_permissions=True)
            await ctx.respond(f'Permissions for {ctx.channel.mention} synced with {ctx.channel.category}')
        else:
            await channel.edit(sync_permissions=True)
            await ctx.respond(f'Permissions for {channel.mention} synced with {channel.category}')

    @slash_command(guild_ids=[SERVER_ID])
    @permissions.has_any_role(ROLE_SERVERLEADER, guild_id=SERVER_ID)
    async def kick(
            self,
            ctx,
            member: Option(discord.Member, description="Which user to kick"),
            reason: Option(str, description="Why you're kicking this user")
    ):
        view = Confirm(ctx)

        await ctx.respond(f"Are you sure you want to kick `{member}` for `{reason}`", view=view)
        await view.wait()
        if view.value is False:
            await ctx.respond('Aborting...')
        if view.value is True:

            if reason is None:
                await ctx.respond("Please specify a reason why you want to kick this user!")
            if member.id in TMS_BOT_IDS:
                return await ctx.respond("Hey! You can't kick me!!")
            await member.kick(reason=reason)

            em6 = discord.Embed(title="",
                                description=f"{member.mention} was kicked for {reason}.",
                                color=0xFF0000)

            await ctx.respond(embed=em6)
        return view.value

    @slash_command(guild_ids=[SERVER_ID])
    @permissions.has_any_role(ROLE_SERVERLEADER, guild_id=SERVER_ID)
    async def mute(
            self,
            ctx,
            user: Option(discord.Member, description="The user to mute."),
            reason: Option(str, description="The reason to mute the user."),
            mute_length: Option(str, description="How long to mute the user for.",
                                choices=[
                                    "10 minutes",
                                    "30 minutes",
                                    "1 hour",
                                    "2 hours",
                                    "8 hours",
                                    "1 day",
                                    "4 days",
                                    "7 days",
                                    "1 month",
                                    "1 year",
                                    "Indefinitely"
                                ])
    ):

        times = {
            "10 minutes": datetime.datetime.now() + datetime.timedelta(minutes=10),
            "30 minutes": datetime.datetime.now() + datetime.timedelta(minutes=30),
            "1 hour": datetime.datetime.now() + datetime.timedelta(hours=1),
            "2 hours": datetime.datetime.now() + datetime.timedelta(hours=2),
            "4 hours": datetime.datetime.now() + datetime.timedelta(hours=4),
            "8 hours": datetime.datetime.now() + datetime.timedelta(hours=8),
            "1 day": datetime.datetime.now() + datetime.timedelta(days=1),
            "4 days": datetime.datetime.now() + datetime.timedelta(days=4),
            "7 days": datetime.datetime.now() + datetime.timedelta(days=7),
            "1 month": datetime.datetime.now() + datetime.timedelta(days=30),
            "1 year": datetime.datetime.now() + datetime.timedelta(days=365),
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

        view = Confirm(ctx)
        await ctx.respond("Please confirm that you would like to mute this user.", view=view,
                          embed=original_shown_embed)

        message = f"You have been muted from the TMS Scioly Discord server for {reason}."

        await view.wait()
        role = discord.utils.get(user.guild.roles, name=ROLE_MUTED)
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
            await ctx.interaction.edit_original_message(embed=original_shown_embed, view=None, content=None)

        else:
            original_shown_embed.colour = discord.Colour.brand_green()
            original_shown_embed.title = "Mute Canceled"
            original_shown_embed.description = f"Mute of `{user.name}` was canceled"
            original_shown_embed.timestamp = discord.utils.utcnow()
            await ctx.interaction.edit_original_message(embed=original_shown_embed, view=None, content=None)

    @slash_command(guild_ids=[SERVER_ID])
    @permissions.has_any_role(ROLE_SERVERLEADER, guild_id=SERVER_ID)
    async def unmute(self, ctx, user: discord.Member):
        view = Confirm(ctx)
        await ctx.respond(f"Are you sure you want to unmute `{user}`?", view=view)
        await view.wait()
        if view.value is False:
            return await ctx.interaction.edit_original_message('Unmute Canceled')
        else:
            role = discord.utils.get(user.guild.roles, name=ROLE_MUTED)
            await user.remove_roles(role)
            em5 = discord.Embed(title="",
                                description=f"Successfully unmuted {user.mention}.",
                                color=discord.Color.brand_green())
            em5.timestamp = discord.utils.utcnow()
            server = self.bot.get_guild(SERVER_ID)
            reports_channel = discord.utils.get(server.text_channels, id=CHANNEL_REPORTS)
            await reports_channel.send(embed=em5)
            await ctx.interaction.edit_original_message(embed=em5, view=None, content=None)
            for obj in CRON_LIST[:]:
                if obj['do'] == f'unmute {user.id}':
                    CRON_LIST.remove(obj)
        return view.value

    @slash_command(guild_ids=[SERVER_ID])
    @permissions.has_any_role(ROLE_SERVERLEADER, guild_id=SERVER_ID)
    async def nuke(self, ctx, count: Option(int, description="The amount of messages to delete")):
        """Nukes (deletes) a specified amount of messages."""
        global STOPNUKE
        MAX_DELETE = 100
        if int(count) > MAX_DELETE:
            return await ctx.respond("Chill. No more than deleting 100 messages at a time.")
        channel = ctx.channel
        if int(count) < 0:
            history = await channel.history(limit=105).flatten()
            message_count = len(history)
            if message_count > 100:
                count = 100
            else:
                count = message_count + int(count) - 1
            if count <= 0:
                return await ctx.respond(
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
        view = Nuke(ctx)
        await ctx.respond(embed=original_shown_embed, view=view)
        await asyncio.sleep(1)

        for i in range(9, 0, -1):
            if view.stopped:
                break
            original_shown_embed.description = f"""
            {count} messages will be deleted from {channel.mention} in `{i}` seconds...
            To stop this nuke, press the red button below!
            """
            await ctx.interaction.edit_original_message(embed=original_shown_embed, view=view)
            await asyncio.sleep(1)

        if not view.stopped:
            original_shown_embed.description = f"""
            Now nuking {count} messages from the channel...
            """
            await ctx.interaction.edit_original_message(embed=original_shown_embed, view=None)

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

    @slash_command(guild_ids=[SERVER_ID])
    @permissions.has_any_role(ROLE_SERVERLEADER, guild_id=SERVER_ID)
    async def lock(self,
                   ctx,
                   channel: Option(discord.TextChannel, description="The channel you want to lock")):
        """
        Locks a channel to Member access.
        """
        member = ctx.author
        if channel is None:
            member_role = discord.utils.get(member.guild.roles, name=ROLE_MR)
            await ctx.channel.set_permissions(member_role, add_reactions=False, send_messages=False, read_messages=True)
            SL = discord.utils.get(member.guild.roles, name=ROLE_SERVERLEADER)
            await ctx.channel.set_permissions(SL, add_reactions=True, send_messages=True, read_messages=True)
            await ctx.respond(f"Locked :lock: {ctx.channel.mention} to Member access.")
        else:
            member_role = discord.utils.get(member.guild.roles, name=ROLE_MR)
            await channel.set_permissions(member_role, add_reactions=False, send_messages=False, read_messages=True)
            SL = discord.utils.get(member.guild.roles, name=ROLE_SERVERLEADER)
            await channel.set_permissions(SL, add_reactions=True, send_messages=True, read_messages=True)
            await ctx.respond(f"Locked :lock: {channel.mention} to Member access.")

    @slash_command(guild_ids=[SERVER_ID])
    @permissions.has_any_role(ROLE_SERVERLEADER, guild_id=SERVER_ID)
    async def unlock(
            self,
            ctx,
            channel: Option(discord.TextChannel, description="The channel to unlock", required=False)
    ):
        """Unlocks a channel to Member access."""
        member = ctx.author
        if channel is None:
            member_role = discord.utils.get(member.guild.roles, name=ROLE_MR)
            await ctx.channel.set_permissions(member_role, add_reactions=True, send_messages=True, read_messages=True)
            SL = discord.utils.get(member.guild.roles, name=ROLE_SERVERLEADER)
            await ctx.channel.set_permissions(SL, add_reactions=True, send_messages=True, read_messages=True)
            await ctx.respond(
                f"Unlocked :unlock: {ctx.channel.mention} to Member access. Please check if permissions need to be synced.")
        else:
            member_role = discord.utils.get(member.guild.roles, name=ROLE_MR)
            await channel.set_permissions(member_role, add_reactions=True, send_messages=True, read_messages=True)
            SL = discord.utils.get(member.guild.roles, name=ROLE_SERVERLEADER)
            await channel.set_permissions(SL, add_reactions=True, send_messages=True, read_messages=True)
            await ctx.respond(
                f"Unlocked :unlock: {channel.mention} to Member access. Please check if permissions need to be synced.")

    @slash_command(guild_ids=[SERVER_ID])
    @permissions.has_any_role(ROLE_SERVERLEADER, guild_id=SERVER_ID)
    async def warn(self,
                   ctx,
                   member: Option(discord.Member, description="Which user to warn"),
                   reason: Option(str, description="Why you are warning this user")
                   ):
        '''Warns a user'''
        server = self.bot.get_guild(SERVER_ID)
        reports_channel = discord.utils.get(server.text_channels, id=CHANNEL_REPORTS)
        mod = ctx.author
        avatar = mod.avatar
        avatar1 = member.avatar.url

        if member is ctx.author:
            return await ctx.respond("You cannot warn yourself :rolling_eyes:")
        if member.id in TMS_BOT_IDS:
            return await ctx.respond(f"Hey {ctx.author.mention}! You can't warn {member.mention}")
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
        await ctx.respond(embed=embed1)
        await member.send(embed=embed2)

    @slash_command(guild_ids=[SERVER_ID])
    @permissions.has_any_role(ROLE_SERVERLEADER, guild_id=SERVER_ID)
    async def blacklist(self, ctx,
                        member: Option(discord.Member,
                                       description="The member you want to blacklist from using commands")):
        '''Blacklist a user from using commands'''
        if member.id == self.bot.owner_id:
            return await ctx.respond("You can't blacklist the owner of the bot :rolling_eyes:")
        try:
            with open("blacklist.json") as f:
                data = json.load(f)
            if member.id in data['blacklisted_ids']:
                return await ctx.respond(f'{member.mention} is already blacklisted from using commands!')
            else:
                data["blacklisted_ids"].append(member.id)
                with open("blacklist.json", 'w') as f:
                    json.dump(data, f)
                await ctx.respond(f'Blacklisted {member.mention} from using commands!')
        except Exception:
            await ctx.respond(f'Failed to blacklist {member.mention}!')

    @slash_command(guild_ids=[SERVER_ID])
    @permissions.has_any_role(ROLE_SERVERLEADER, guild_id=SERVER_ID)
    async def unblacklist(self, ctx, member: discord.Member):
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

                await ctx.respond(f"Successfully removed command blacklist from {member.mention}")
            #
            # except Exception:
            #     await ctx.respond(f"Couldn't remove command blacklist from {member.mention}", ephemeral=True)
        else:
            await ctx.respond(f"{member.mention} is not blacklisted from using commands")


def setup(bot):
    bot.add_cog(Moderation(bot))
