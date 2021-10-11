import discord
from discord.ext import commands
from utils.variables import *
from utils.views import Confirm, Role1, Role2, Role3, Role4, Role5, Allevents, Nitro, Pronouns, Ticket
from utils.checks import is_staff
from utils.globalfunctions import _mute, _nuke_countdown
import dateparser
import pytz
import asyncio
import json
import tabulate
import datetime


STOPNUKE = datetime.datetime.utcnow()


class Mod(commands.Cog):
    """Moderation related commands."""
    print('Moderation Cog Loaded')

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.check(is_staff())
    async def rules(self, ctx):
        '''Displays all of the servers rules'''
        em4 = discord.Embed(title="TMS SciOly Discord Rules",
                            description="",
                            color=0xff008c)
        em4.add_field(name="Rule 1",
                      value="⌬ Respect ALL individuals in this server",
                      inline=False)
        em4.add_field(name="Rule 2",
                      value="⌬ No profanity or inappropriate language, content, or links.",
                      inline=False)
        em4.add_field(name="Rule 3",
                      value="⌬ Do not spam or flood the chat with an excessive amount of repetitive messages",
                      inline=False)
        em4.add_field(name="Rule 4",
                      value="⌬ Do not self-promote",
                      inline=False)
        em4.add_field(name="Rule 5",
                      value="⌬ Do not harass other members",
                      inline=False)
        em4.add_field(name="Rule 6",
                      value="⌬ Use good judgment when deciding what content to leave in and take out. As a general rule of thumb: **When in doubt, leave it out**.",
                      inline=False)
        em4.add_field(name="Punishments",
                      value="◈ Violations of these rules may result in warnings, mutes, kicks and bans which will be decided by <@&823929718717677568>",
                      inline=False)
        em4.add_field(name="Support",
                      value="◈ If you need help with anything TMS SciOly or anything related to this Discord Server, or are reporting violations of these rules, feel free to open a ticket below or tag <@&823929718717677568> and <@!747126643587416174>",
                      inline=False)

        em4.set_footer(text="TMS SciOly Website https://sites.google.com/student.sd25.org/tmsscioly/home ")
        await ctx.send(embed=em4)

    @commands.command()
    @commands.check(is_staff())
    async def gift(self, ctx):
        em1 = discord.Embed(title="You've been gifted a subscription!", description=" ", color=0x2F3136)
        em1.set_thumbnail(
            url='https://i.imgur.com/w9aiD6F.png')
        view = Nitro()
        await ctx.send(embed=em1, view=view)

    @commands.command()
    @commands.check(is_staff())
    async def events1(self, ctx: commands.Context):
        '''Buttons for Life Science Events'''
        em1 = discord.Embed(title="What events do you want to do?",
                            description="To choose your event roles press the buttons below",
                            color=0xff008c)
        em1.set_image(
            url='https://cdn.discordapp.com/attachments/685035292989718554/724301857157283910/ezgif-1-a2a2e7173d80.gif')
        em1.set_footer(text="Life Science Events - Page 1 of 5")
        await ctx.send(embed=em1, view=Role1())

    @commands.command()
    @commands.check(is_staff())
    async def events2(self, ctx: commands.Context):
        '''Buttons for Earth and Space Science Events'''
        em1 = discord.Embed(title="What events do you want to do?",
                            description="To choose your event roles press the buttons below",
                            color=0xff008c)
        em1.set_image(
            url='https://cdn.discordapp.com/attachments/685035292989718554/724301857157283910/ezgif-1-a2a2e7173d80.gif')
        em1.set_footer(text="Earth and Space Science Events - Page 2 of 5")
        await ctx.send(embed=em1, view=Role2())

    @commands.command()
    @commands.check(is_staff())
    async def events3(self, ctx: commands.Context):
        '''Buttons for Physical Science & Chemistry Events'''
        em1 = discord.Embed(title="What events do you want to do?",
                            description="To choose your event roles press the buttons below",
                            color=0xff008c)
        em1.set_image(
            url='https://cdn.discordapp.com/attachments/685035292989718554/724301857157283910/ezgif-1-a2a2e7173d80.gif')
        em1.set_footer(text="Physical Science & Chemistry Events - Page 3 of 5")
        await ctx.send(embed=em1, view=Role3())

    @commands.command()
    @commands.check(is_staff())
    async def events4(self, ctx: commands.Context):
        '''Buttons for Technology & Engineering Design Events'''
        em1 = discord.Embed(title="What events do you want to do?",
                            description="To choose your event roles press the buttons below",
                            color=0xff008c)
        em1.set_image(
            url='https://cdn.discordapp.com/attachments/685035292989718554/724301857157283910/ezgif-1-a2a2e7173d80.gif')
        em1.set_footer(text="Technology & Engineering Design Events - Page 4 of 5")
        await ctx.send(embed=em1, view=Role4())

    @commands.command()
    @commands.check(is_staff())
    async def events5(self, ctx: commands.Context):
        '''Buttons for Inquiry & Nature'''
        em1 = discord.Embed(title="What events do you want to do?",
                            description="To choose your event roles press the buttons below",
                            color=0xff008c)
        em1.set_image(
            url='https://cdn.discordapp.com/attachments/685035292989718554/724301857157283910/ezgif-1-a2a2e7173d80.gif')
        em1.set_footer(text="Inquiry & Nature of Science Events")
        await ctx.send(embed=em1, view=Role5())

    @commands.command()
    @commands.check(is_staff())
    async def events6(self, ctx: commands.Context):
        '''Buttons for All Events Role'''
        em1 = discord.Embed(title="What events do you want to do?",
                            description="Press the button below to gain access to all the event channels",
                            color=0xff008c)
        em1.set_image(
            url='https://cdn.discordapp.com/attachments/685035292989718554/724301857157283910/ezgif-1-a2a2e7173d80.gif')
        await ctx.send(embed=em1, view=Allevents())

    @commands.command()
    @commands.check(is_staff())
    async def pronouns(self, ctx: commands.Context):
        '''Buttons for Pronoun Roles'''
        em1 = discord.Embed(title="What pronouns do you use?",
                            description="Press the buttons below to choose your pronoun role(s)",
                            color=0xff008c)
        em1.set_image(
            url='https://cdn.discordapp.com/attachments/685035292989718554/724301857157283910/ezgif-1-a2a2e7173d80.gif')
        em1.set_footer(text="Pronoun Roles")
        await ctx.send(embed=em1, view=Pronouns())

    @commands.command()
    @commands.check(is_staff())
    async def eventroles(self, ctx: commands.Context):
        '''Creates all the event role buttons'''
        em1 = discord.Embed(title="What events do you want to do?",
                            description="To choose your event roles press the buttons below",
                            color=0xff008c)
        em1.set_footer(text="Life Science Events - Page 1 of 5")

        em2 = discord.Embed(title="What events do you want to do?",
                            description="To choose your event roles press the buttons below",
                            color=0xff008c)

        em2.set_footer(text="Earth and Space Science Events - Page 2 of 5")

        em3 = discord.Embed(title="What events do you want to do?",
                            description="To choose your event roles press the buttons below",
                            color=0xff008c)

        em3.set_footer(text="Physical Science & Chemistry Events - Page 3 of 5")

        em4 = discord.Embed(title="What events do you want to do?",
                            description="To choose your event roles press the buttons below",
                            color=0xff008c)

        em4.set_footer(text="Technology & Engineering Design Events - Page 4 of 5")

        em5 = discord.Embed(title="What events do you want to do?",
                            description="To choose your event roles press the buttons below",
                            color=0xff008c)
        em5.set_footer(text="Inquiry & Nature of Science Events")

        em6 = discord.Embed(title="What pronouns do you use?",
                            description="Press the buttons below to choose your pronoun role(s)",
                            color=0xff008c)
        em6.set_footer(text="Pronoun Roles")

        await ctx.send(embed=em1, view=Role1())
        await ctx.send(embed=em2, view=Role2())
        await ctx.send(embed=em3, view=Role3())
        await ctx.send(embed=em4, view=Role4())
        await ctx.send(embed=em5, view=Role5())
        await ctx.send(embed=em6, view=Pronouns())

    @commands.command()
    @commands.check(is_staff())
    async def ticket(self, ctx):
        '''Sends the ticket button embed'''
        view = Ticket(self.bot)
        em1 = discord.Embed(title="TMS Tickets",
                           description="To create a ticket press the button below",color=0xff008c)
        em1.set_image(
            url='https://cdn.discordapp.com/attachments/685035292989718554/724301857157283910/ezgif-1-a2a2e7173d80.gif')
        em1.set_footer(text="TMS-Bot Tickets for reporting or questions")
        await ctx.send(embed=em1, view=view)

    @commands.command()
    @commands.check(is_staff())
    async def embed(self, ctx, title=None, description=None):
        '''Sends an embed'''
        ava = ctx.author.avatar
        if title is None:
            embed=discord.Embed(title=" ",
                                description=description,
                                color=0xff008c,
                                )
            embed.set_author(name=ctx.author,
                             icon_url=ava)
            await ctx.send(embed=embed)
        elif description is None:
            embed = discord.Embed(title=title,
                                  description=' ',
                                  color=0xff008c,
                                  )
            embed.set_author(name=ctx.author,
                             icon_url=ava)
            await ctx.send(embed=embed)
        else:
            embed = discord.Embed(title=title,
                                  description=description,
                                  color=0xff008c,
                                  )
            embed.set_author(name=ctx.author,
                             icon_url=ava)
            await ctx.send(embed=embed)

    @commands.command()
    @commands.check(is_staff())
    async def slowmode(self,
                       ctx,
                       time: int = commands.Option(description="The amount of seconds")
                       ):
        '''Sets slowmode for the channel.'''
        arg = time
        if arg is None:
            if ctx.channel.slowmode_delay == 0:
                await ctx.channel.edit(slowmode_delay=10)
                await ctx.send("Enabled a 10 second slowmode.")
            else:
                await ctx.channel.edit(slowmode_delay=0)
                await ctx.send("Removed slowmode.")
        else:
            await ctx.channel.edit(slowmode_delay=arg)
            if arg != 0:
                await ctx.send(f"Enabled a {arg} second slowmode.")
            else:
                await ctx.send(f"Removed slowmode.")

    @commands.command()
    @commands.check(is_staff())
    async def ban(self,
                  ctx,
                  member : discord.User= commands.Option(description='the member to ban'),
                  reason = commands.Option(description='the reason to ban this member'),
                  duration = commands.Option(description='the amount of time banned')):
        """Bans a user."""
        time = duration
        if member is None or member == ctx.message.author:
            return await ctx.reply("You cannot ban yourself! >:(", mention_author=False)
        elif reason is None:
            return await ctx.reply("You need to give a reason for you banning this user.", mention_author=False)
        elif time is None:
            return await ctx.reply("You need to specify a length that this used will be banned. Examples are: `1 day`, `2 months or 1 day`",
                                   mention_author=False)
        elif member.id in TMS_BOT_IDS:
            return await ctx.reply("Hey! You can't ban me!!", mention_author=False)
        message = f"You have been banned from the TMS SciOly Discord server for {reason}."
        parsed = "indef"
        if time != "indef":
            parsed = dateparser.parse(time, settings={"PREFER_DATES_FROM": "future"})
            if parsed is None:
                return await ctx.send(f"Sorry, but I don't understand the length of time: `{time}`.")
            CRON_LIST.append({"date": parsed, "do": f"unban {member.id}"})
        await member.send(message)
        await ctx.guild.ban(member, reason=reason)
        central = pytz.timezone("US/Central")
        embed = discord.Embed(title="Member Banned",
                              description=f"`{member}` is banned until `{str(central.localize(parsed))} CT` for `{reason}`.",
                              color=0xFF0000)
        server = self.bot.get_guild(SERVER_ID)
        reports_channel = discord.utils.get(server.text_channels, id=CHANNEL_REPORTS)
        embed1 = discord.Embed(title=f"New Banned Member",
                               description=f"{member.mention} has been banned from {server}",
                               color=0xFF0000)
        embed1.add_field(name="Reason:", value=f'`{reason}`')
        embed1.add_field(name="Responsible Moderator:", value=f"`{ctx.message.author}`")
        embed1.set_author(name=f'{member}', icon_url=f"{member.avatar}")

        await reports_channel.send(embed=embed1)
        await ctx.reply(embed=embed, mention_author=False)

    @commands.command()
    @commands.check(is_staff())
    async def unban(self,
                    ctx,
                    member:discord.User= commands.Option(description="The user (id) to unban")
                    ):
        """Unbans a user."""
        if member is None:
            await ctx.channel.send("Please give either a user ID or mention a user.")
            return
        await ctx.guild.unban(member)
        embed=discord.Embed(title="Unban Request",
                            description=f"Inverse ban hammer applied, {member.mention} unbanned. Please remember that I cannot force them to re-join the server, they must join themselves.",
                            color=0x00FF00)
        await ctx.channel.send(embed=embed)

    @commands.command()
    @commands.check(is_staff())
    async def dm(self, ctx, member: discord.Member,
                 message=commands.Option(description="What to DM the member")
                 ):
        '''DMs a user.'''
        em1 = discord.Embed(title=f" ",
                            description=f"> {message}",
                            color=0x2F3136)
        em1.set_author(name=f"Message from {ctx.message.author}", icon_url=ctx.message.author.avatar)
        await ctx.reply(f"Message sent to `{member}`", mention_author=False)
        await member.send(embed=em1)

    @commands.command()
    @commands.check(is_staff())
    async def sync(self,
                   ctx,
                   channel: discord.TextChannel = commands.Option(description="The channel to sync permissions with")
                   ):
        '''Syncs permmissions to channel category'''

        if channel is None:
            await ctx.message.channel.edit(sync_permissions=True)
            await ctx.send(f'Permissions for {ctx.message.channel.mention} synced with {ctx.message.channel.category}')
        else:
            await channel.edit(sync_permissions=True)
            await ctx.send(f'Permissions for {channel.mention} synced with {channel.category}')

    @commands.command()
    @commands.check(is_staff())
    async def vip(self,
                  ctx,
                  user: discord.Member = commands.Option(description="The user you wish to VIP")):
        """Exalts/VIPs a user."""
        member = ctx.message.author
        role = discord.utils.get(member.guild.roles, name=ROLE_VIP)
        await user.add_roles(role)
        await ctx.send(f"Successfully added VIP. Congratulations {user.mention}! :partying_face: :partying_face: ")

    @commands.command()
    @commands.check(is_staff())
    async def unvip(self,
                    ctx,
                    user: discord.Member = commands.Option(description="The user you wish to unVIP")):
        """Unexalts/unVIPs a user."""
        member = ctx.message.author
        role = discord.utils.get(member.guild.roles, name=ROLE_VIP)
        await user.remove_roles(role)
        await ctx.send(f"Successfully removed VIP from {user.mention}.")

    @commands.command()
    @commands.check(is_staff())
    async def trial(self,
                    ctx,
                    user: discord.Member = commands.Option(description="The user you wish promote to trial leader")):
        """Promotes/Trials a user."""
        member = ctx.message.author
        role = discord.utils.get(member.guild.roles, name=ROLE_TRIAL)
        await user.add_roles(role)
        await ctx.send(f"Successfully added {role}. Congratulations {user.mention}! :partying_face: :partying_face: ")

    @commands.command()
    @commands.check(is_staff())
    async def untrial(self,
                      ctx,
                      user: discord.Member = commands.Option(description="The user you wish to demote")):
        """Demotes/unTrials a user."""
        member = ctx.message.author
        role = discord.utils.get(member.guild.roles, name=ROLE_TRIAL)
        await user.remove_roles(role)
        await ctx.send(f"Successfully removed {role} from {user.mention}.")

    @commands.command()
    @commands.check(is_staff())
    async def kick(self,
                   ctx,
                   member: discord.Member = commands.Option(description="Which user to kick"),
                   reason=commands.Option(description="Why you're kicking this user")
                   ):
        view = Confirm(ctx)

        await ctx.reply(f"Are you sure you want to kick `{member}` for `{reason}`", view=view)
        await view.wait()
        if view.value is False:
            await ctx.send('Aborting...')
        if view.value is True:

            if reason is None:
                await ctx.send("Please specify a reason why you want to kick this user!")
            if member.id in TMS_BOT_IDS:
                return await ctx.send("Hey! You can't kick me!!")
            await member.kick(reason=reason)

            em6 = discord.Embed(title="",
                                description=f"{member.mention} was kicked for {reason}.",
                                color=0xFF0000)

            await ctx.send(embed=em6)
        return view.value

    @commands.command()
    @commands.check(is_staff())
    async def mute(self,
                   ctx,
                   user: discord.Member = commands.Option(description="The user to mute"),
                   time=commands.Option(description="The amount of time to mute the user")
                   ):
        """
        Mutes a user.
        """
        view = Confirm(ctx)

        await ctx.reply(f"Are you sure you want to mute `{user}` for `{time}`", view=view)
        await view.wait()
        if view.value is False:
            await ctx.send('Aborting...')
        if view.value is True:
            await _mute(ctx, user, time, self=False)
        return view.value

    @commands.command()
    @commands.check(is_staff())
    async def getvariable(self, ctx,
                          var=commands.Option(description="The global variable to display")):
        """Fetches a local variable."""
        await ctx.send("Attempting to find variable.")
        if var == "CRON_LIST":
            try:
                header = CRON_LIST[0].keys()
                rows = [x.values() for x in CRON_LIST]
                table = tabulate.tabulate(rows, header, "fancy_grid")
                await ctx.reply(f"```{table}```", mention_author=False)
            except IndexError as e:
                await ctx.send(f'Nothing in the cron list, {e}')
        else:
            try:
                variable = globals()[var]
                await ctx.reply(f"`{variable}`")
            except Exception as e:
                await ctx.send(f"Can't find that variable! `{e}`")

    @commands.command()
    @commands.check(is_staff())
    async def removevariable(self, ctx,
                             user: discord.User = commands.Option(description="The user to remove from the CRON_LIST")):
        '''Removes a variable in the CRON_LIST'''
        for obj in CRON_LIST[:]:
            if obj['do'] == f'unmute {user.id}':
                CRON_LIST.remove(obj)
                await ctx.send(f'Removed {user} unmute from CRON_LIST')
            elif obj['do'] == f'unban {user.id}':
                CRON_LIST.remove(obj)
                await ctx.send(f'Removed {user} unban from CRON_LIST')
            else:
                await ctx.send('Unknown object to remove')

    @commands.command()
    async def selfmute(self, ctx, time):
        """
        Self mutes the user that invokes the command.

        """
        view = Confirm(ctx)
        user = ctx.message.author

        if time is None:
            await ctx.send(
                'You need to specify a length that this used will be muted. `exe:` `1 day`, `2 months, 1 day`')
        else:
            await ctx.reply(f"Are you sure you want to selfmute for `{time}`", view=view)
            await view.wait()
            if view.value is False:
                await ctx.send('Aborting...')
            if view.value is True:
                await _mute(ctx, user, time, self=True)
            return view.value

    @commands.command()
    @commands.check(is_staff())
    async def unmute(self, ctx, user: discord.Member):
        view = Confirm(ctx)
        await ctx.reply(f"Are you sure you want to unmute `{user}`?", view=view)
        await view.wait()
        if view.value is False:
            await ctx.send('Unmute Canceled')
        if view.value is True:
            role = discord.utils.get(user.guild.roles, name=ROLE_MUTED)
            await user.remove_roles(role)
            em5 = discord.Embed(title="",
                                description=f"Successfully unmuted {user.mention}.",
                                color=0x16F22C)

            await ctx.send(embed=em5)
            for obj in CRON_LIST[:]:
                if obj['do'] == f'unmute {user.id}':
                    CRON_LIST.remove(obj)
        return view.value

    @commands.command()
    @commands.check(is_staff())
    async def nuke(self, ctx, count: int):
        """Nukes (deletes) a specified amount of messages."""
        import datetime
        global STOPNUKE
        MAX_DELETE = 100
        if int(count) > MAX_DELETE:
            return await ctx.send("Chill. No more than deleting 100 messages at a time.")
        channel = ctx.message.channel
        if int(count) < 0: count = MAX_DELETE
        await _nuke_countdown(ctx, count)
        if STOPNUKE <= datetime.datetime.utcnow():
            await channel.purge(limit=int(count) + 13, check=lambda m: not m.pinned)

            msg = await ctx.send("https://media.giphy.com/media/XUFPGrX5Zis6Y/giphy.gif")
            await msg.delete(delay=5)

    @commands.command()
    @commands.check(is_staff())
    async def nukeuntil(self, ctx, message_id):  # prob can use converters to convert the msgid to a Message object

        import datetime
        global STOPNUKE
        channel = ctx.message.channel
        message = await ctx.fetch_message(message_id)
        if channel == message.channel:
            await _nuke_countdown(ctx)
            if STOPNUKE <= datetime.datetime.utcnow():
                await channel.purge(limit=1000, after=message)
                msg = await ctx.send("https://media.giphy.com/media/XUFPGrX5Zis6Y/giphy.gif")
                await msg.delete(delay=5)
        else:
            return await ctx.send("MESSAGE ID DOES NOT COME FROM THIS TEXT CHANNEL. ABORTING NUKE.")

    @nuke.error
    @nukeuntil.error
    async def nuke_error(self, ctx, error):
        ctx.__slots__ = True
        print(f"{BOT_PREFIX}nuke error handler: {error}")
        if isinstance(error, discord.ext.commands.MissingAnyRole):
            return await ctx.send("APOLOGIES. INSUFFICIENT RANK FOR NUKE.")
        if isinstance(error, discord.ext.commands.CommandOnCooldown):
            return await ctx.send(
                f"TRANSMISSION FAILED. ALL NUKES ARE CURRENTLY PAUSED FOR ANOTHER {'%.3f' % error.retry_after} SECONDS. TRY AGAIN LATER.")
        ctx.__slots__ = False

    @commands.command()
    @commands.check(is_staff())
    async def stopnuke(self, ctx):
        global STOPNUKE
        NUKE_COOLDOWN = 20
        STOPNUKE = datetime.datetime.utcnow() + datetime.timedelta(seconds=NUKE_COOLDOWN)  # True
        await ctx.send(f"TRANSMISSION RECEIVED. STOPPED ALL CURRENT NUKES FOR {NUKE_COOLDOWN} SECONDS.")

    @stopnuke.error
    async def stopnuke_error(self, ctx, error):
        ctx.__slots__ = True
        print(f"{BOT_PREFIX}nuke error handler: {error}")
        if isinstance(error, discord.ext.commands.MissingAnyRole):
            return await ctx.send("APOLOGIES. INSUFFICIENT RANK FOR STOPPING NUKE.")

    @commands.command()
    @commands.check(is_staff())
    async def lock(self,
                   ctx,
                   channel: discord.TextChannel = commands.Option(default=None,
                                                                  description="The channel you want to lock")
                   ):
        """Locks a channel to Member access."""
        member = ctx.message.author
        if channel is None:
            member_role = discord.utils.get(member.guild.roles, name=ROLE_MR)
            await ctx.channel.set_permissions(member_role, add_reactions=False, send_messages=False, read_messages=True)
            SL = discord.utils.get(member.guild.roles, name=ROLE_SERVERLEADER)
            await ctx.channel.set_permissions(SL, add_reactions=True, send_messages=True, read_messages=True)
            await ctx.send(f"Locked :lock: {ctx.channel.mention} to Member access.")
        else:
            member_role = discord.utils.get(member.guild.roles, name=ROLE_MR)
            await channel.set_permissions(member_role, add_reactions=False, send_messages=False, read_messages=True)
            SL = discord.utils.get(member.guild.roles, name=ROLE_SERVERLEADER)
            await channel.set_permissions(SL, add_reactions=True, send_messages=True, read_messages=True)
            await ctx.send(f"Locked :lock: {channel.mention} to Member access.")

    @commands.command()
    @commands.check(is_staff())
    async def unlock(self,
                     ctx,
                     channel: discord.TextChannel = commands.Option(default=None, description="The channel to unlock")
                     ):
        """Unlocks a channel to Member access."""
        member = ctx.message.author
        if channel is None:
            member_role = discord.utils.get(member.guild.roles, name=ROLE_MR)
            await ctx.channel.set_permissions(member_role, add_reactions=True, send_messages=True, read_messages=True)
            SL = discord.utils.get(member.guild.roles, name=ROLE_SERVERLEADER)
            await ctx.channel.set_permissions(SL, add_reactions=True, send_messages=True, read_messages=True)
            await ctx.send(
                f"Unlocked :unlock: {ctx.channel.mention} to Member access. Please check if permissions need to be synced.")
        else:
            member_role = discord.utils.get(member.guild.roles, name=ROLE_MR)
            await channel.set_permissions(member_role, add_reactions=True, send_messages=True, read_messages=True)
            SL = discord.utils.get(member.guild.roles, name=ROLE_SERVERLEADER)
            await channel.set_permissions(SL, add_reactions=True, send_messages=True, read_messages=True)
            await ctx.send(
                f"Unlocked :unlock: {channel.mention} to Member access. Please check if permissions need to be synced.")

    @commands.command()
    @commands.check(is_staff())
    async def close(self, ctx):
        '''Manually closes a ticket channel'''
        with open('data.json') as f:
            data = json.load(f)

        if ctx.channel.id in data["ticket-channel-ids"]:

            channel_id = ctx.channel.id

            def check(message):
                return message.author == ctx.author and message.channel == ctx.channel and message.content.lower() == "close"

            try:

                em = discord.Embed(title="TMS Tickets",
                                   description="Are you sure you want to close this ticket? Reply with `close` if you are sure.",
                                   color=0x00a8ff)
                ticket_chnl = ctx.channel
                await ctx.send(embed=em)
                await self.bot.wait_for('message', check=check, timeout=60)
                await ticket_chnl.delete()

                index = data["ticket-channel-ids"].index(channel_id)
                del data["ticket-channel-ids"][index]

                with open('data.json', 'w') as f:
                    json.dump(data, f)

            except asyncio.TimeoutError:
                em = discord.Embed(title="TMS Tickets",
                                   description="You have run out of time to close this ticket. Please run the command again.",
                                   color=0x00a8ff)
                await ctx.send(embed=em)

    @commands.command()
    @commands.check(is_staff())
    async def addaccess(self,
                        ctx,
                        role_id=commands.Option(description="Role id: allow see tickets")
                        ):
        with open('data.json') as f:
            data = json.load(f)

        valid_user = False

        for role_id in data["verified-roles"]:
            try:
                if ctx.guild.get_role(role_id) in ctx.author.roles:
                    valid_user = True
            except:
                pass

        if valid_user or ctx.author.guild_permissions.administrator:
            role_id = int(role_id)

            if role_id not in data["valid-roles"]:

                try:
                    role = ctx.guild.get_role(role_id)

                    with open("data.json") as f:
                        data = json.load(f)

                    data["valid-roles"].append(role_id)

                    with open('data.json', 'w') as f:
                        json.dump(data, f)

                    em = discord.Embed(title="TMS Tickets",
                                       description="You have successfully added `{}` to the list of roles with access to tickets.".format(
                                           role.name), color=0x00a8ff)

                    await ctx.send(embed=em)

                except:
                    em = discord.Embed(title="TMS Tickets",
                                       description="That isn't a valid role ID. Please try again with a valid role ID.")
                    await ctx.send(embed=em)

            else:
                em = discord.Embed(title="TMS Tickets", description="That role already has access to tickets!",
                                   color=0x00a8ff)
                await ctx.send(embed=em)

        else:
            em = discord.Embed(title="TMS Tickets", description="Sorry, you don't have permission to run that command.",
                               color=0x00a8ff)
            await ctx.send(embed=em)

    @commands.command()
    @commands.check(is_staff())
    async def delaccess(self,
                        ctx,
                        role_id=commands.Option(description="Role id: delete access to see tickets")
                        ):
        with open('data.json') as f:
            data = json.load(f)

        valid_user = False

        for role_id in data["verified-roles"]:
            try:
                if ctx.guild.get_role(role_id) in ctx.author.roles:
                    valid_user = True
            except:
                pass

        if valid_user or ctx.author.guild_permissions.administrator:

            try:
                role_id = int(role_id)
                role = ctx.guild.get_role(role_id)

                with open("data.json") as f:
                    data = json.load(f)

                valid_roles = data["valid-roles"]

                if role_id in valid_roles:
                    index = valid_roles.index(role_id)

                    del valid_roles[index]

                    data["valid-roles"] = valid_roles

                    with open('data.json', 'w') as f:
                        json.dump(data, f)

                    em = discord.Embed(title="TMS Tickets",
                                       description="You have successfully removed `{}` from the list of roles with access to tickets.".format(
                                           role.name), color=0x00a8ff)

                    await ctx.send(embed=em)

                else:

                    em = discord.Embed(title="TMS Tickets",
                                       description="That role already doesn't have access to tickets!", color=0x00a8ff)
                    await ctx.send(embed=em)

            except:
                em = discord.Embed(title="TMS Tickets",
                                   description="That isn't a valid role ID. Please try again with a valid role ID.")
                await ctx.send(embed=em)

        else:
            em = discord.Embed(title="TMS Tickets", description="Sorry, you don't have permission to run that command.",
                               color=0x00a8ff)
            await ctx.send(embed=em)

    @commands.command()
    @commands.check(is_staff())
    async def addpingedrole(self,
                            ctx,
                            role_id=commands.Option(description="Role id to be pinged when tickets are opened")
                            ):
        with open('data.json') as f:
            data = json.load(f)

        valid_user = False

        for role_id in data["verified-roles"]:
            try:
                if ctx.guild.get_role(role_id) in ctx.author.roles:
                    valid_user = True
            except:
                pass

        if valid_user or ctx.author.guild_permissions.administrator:

            role_id = int(role_id)

            if role_id not in data["pinged-roles"]:

                try:
                    role = ctx.guild.get_role(role_id)

                    with open("data.json") as f:
                        data = json.load(f)

                    data["pinged-roles"].append(role_id)

                    with open('data.json', 'w') as f:
                        json.dump(data, f)

                    em = discord.Embed(title="TMS Tickets",
                                       description="You have successfully added `{}` to the list of roles that get pinged when new tickets are created!".format(
                                           role.name), color=0x00a8ff)

                    await ctx.send(embed=em)

                except:
                    em = discord.Embed(title="TMS Tickets",
                                       description="That isn't a valid role ID. Please try again with a valid role ID.")
                    await ctx.send(embed=em)

            else:
                em = discord.Embed(title="TMS Tickets",
                                   description="That role already receives pings when tickets are created.",
                                   color=0x00a8ff)
                await ctx.send(embed=em)

        else:
            em = discord.Embed(title="TMS Tickets", description="Sorry, you don't have permission to run that command.",
                               color=0x00a8ff)
            await ctx.send(embed=em)

    @commands.command()
    @commands.check(is_staff())
    async def delpingedrole(self,
                            ctx,
                            role_id=commands.Option(description="Role id: to delete, pinged when tickets are opened")
                            ):
        with open('data.json') as f:
            data = json.load(f)

        valid_user = False

        for role_id in data["verified-roles"]:
            try:
                if ctx.guild.get_role(role_id) in ctx.author.roles:
                    valid_user = True
            except:
                pass

        if valid_user or ctx.author.guild_permissions.administrator:

            try:
                role_id = int(role_id)
                role = ctx.guild.get_role(role_id)

                with open("data.json") as f:
                    data = json.load(f)

                pinged_roles = data["pinged-roles"]

                if role_id in pinged_roles:
                    index = pinged_roles.index(role_id)

                    del pinged_roles[index]

                    data["pinged-roles"] = pinged_roles

                    with open('data.json', 'w') as f:
                        json.dump(data, f)

                    em = discord.Embed(title="TMS Tickets",
                                       description="You have successfully removed `{}` from the list of roles that get pinged when new tickets are created.".format(
                                           role.name), color=0x00a8ff)
                    await ctx.send(embed=em)

                else:
                    em = discord.Embed(title="TMS Tickets",
                                       description="That role already isn't getting pinged when new tickets are created!",
                                       color=0xff008c)
                    await ctx.send(embed=em)

            except:
                em = discord.Embed(title="TMS Tickets",
                                   description="That isn't a valid role ID. Please try again with a valid role ID.")
                await ctx.send(embed=em)

        else:
            em = discord.Embed(title="TMS Tickets", description="Sorry, you don't have permission to run that command.",
                               color=0xff008c)
            await ctx.send(embed=em)

    @commands.command()
    @commands.check(is_staff())
    async def addadminrole(self,
                           ctx,
                           role_id=commands.Option(description="Role id, to have admin ticket commands")
                           ):
        try:
            role_id = int(role_id)
            role = ctx.guild.get_role(role_id)

            with open("data.json") as f:
                data = json.load(f)

            data["verified-roles"].append(role_id)

            with open('data.json', 'w') as f:
                json.dump(data, f)

            em = discord.Embed(title="TMS Tickets",
                               description="You have successfully added `{}` to the list of roles that can run admin-level commands!".format(
                                   role.name), color=0xff008c)
            await ctx.send(embed=em)

        except:
            em = discord.Embed(title="TMS Tickets",
                               description="That isn't a valid role ID. Please try again with a valid role ID.")
            await ctx.send(embed=em)

    @commands.command()
    @commands.check(is_staff())
    async def deladminrole(self,
                           ctx,
                           role_id=commands.Option(description="Role id, delete access to admin ticket commands")):
        try:
            role_id = int(role_id)
            role = ctx.guild.get_role(role_id)

            with open("data.json") as f:
                data = json.load(f)

            admin_roles = data["verified-roles"]

            if role_id in admin_roles:
                index = admin_roles.index(role_id)

                del admin_roles[index]

                data["verified-roles"] = admin_roles

                with open('data.json', 'w') as f:
                    json.dump(data, f)

                em = discord.Embed(title="TMS Tickets",
                                   description="You have successfully removed `{}` from the list of roles that get pinged when new tickets are created.".format(
                                       role.name), color=0x00a8ff)

                await ctx.send(embed=em)

            else:
                em = discord.Embed(title="TMS Tickets",
                                   description="That role isn't getting pinged when new tickets are created!",
                                   color=0x00a8ff)
                await ctx.send(embed=em)

        except:
            em = discord.Embed(title="TMS Tickets",
                               description="That isn't a valid role ID. Please try again with a valid role ID.")
            await ctx.send(embed=em)

    @commands.command()
    @commands.check(is_staff())
    async def warn(self,
                   ctx,
                   member: discord.Member = commands.Option(description="Which user to warn"),
                   reason=commands.Option(description="Why you are warning this user")
                   ):
        '''Warns a user'''
        server = self.bot.get_guild(SERVER_ID)
        reports_channel = discord.utils.get(server.text_channels, id=CHANNEL_REPORTS)
        mod = ctx.message.author
        avatar = mod.avatar
        avatar1 = member.avatar.url

        if member is None or member == ctx.message.author:
            return await ctx.reply("You cannot warn yourself :rolling_eyes:",
                                   mention_author=False)
        if reason is None:
            return await ctx.reply(
                f"{ctx.message.author.mention} You need to give a reason for why you are warning {member.mention}",
                mention_author=False)
        if member.id in TMS_BOT_IDS:
            return await ctx.reply(f"Hey {ctx.message.author.mention}! You can't warn {member.mention}",
                                   mention_author=False)
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

        message = await reports_channel.send(embed=embed)
        WARN_IDS.append(message.id)
        await message.add_reaction("\U00002705")
        await message.add_reaction("\U0000274C")
        await ctx.reply(embed=embed1, mention_author=False)
        await member.send(embed=embed2)


def setup(bot):
    bot.add_cog(Mod(bot))
