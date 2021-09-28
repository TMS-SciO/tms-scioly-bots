import discord
from discord.ext import commands, tasks
from embed import assemble_embed
from commanderr import CommandNotAllowedInChannel
from views import Confirm, Counter, HelpButtons, paginationList, Ticket, TicTacToe, Close, Role1, Role2, Role3, Role4, Role5, Pronouns, Nitro, Allevents, Google
from doggo import get_doggo, get_akita, get_shiba, get_cotondetulear
from censor import CENSORED_WORDS
from checks import is_staff
from rules import RULES
from secret import TOKEN
from variables import *
import random
import os
import math
import datetime
import dateparser
import pytz
import wikipedia as wikip
from aioify import aioify
import traceback
import re
import inspect
import json
import asyncio
import unicodedata
import tabulate

intents = discord.Intents.all()

aiowikip = aioify(obj=wikip)

STEALFISH_BAN = []
CRON_LIST = []
fish_now = 0
REPORT_IDS = []
WARN_IDS = []
RECENT_MESSAGES = []

STOPNUKE = datetime.datetime.utcnow()


class PersistentViewBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned_or(BOT_PREFIX1, BOT_PREFIX),
                         case_insensitive=True,
                         help_command=None,
                         intents=intents,
                         slash_commands=True)
        self.persistent_views_added = False

    async def on_ready(self):
        if not self.persistent_views_added:
            self.add_view(Role1())
            self.add_view(Role2())
            self.add_view(Role3())
            self.add_view(Role4())
            self.add_view(Role5())
            self.add_view(Allevents())
            self.add_view(Pronouns())
            self.add_view(Ticket())
            self.add_view(Close())
            self.persistent_views_added = True
        print(f'{bot.user} has connected!')
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')
        print(discord.__version__)
        await bot.change_presence(status=discord.Status.dnd, activity=discord.Game('Minecraft'))
        cron.start()


bot = PersistentViewBot()


@tasks.loop(seconds=60)
async def cron():
    print(f"Executed cron.")

    global CRON_LIST
    for c in CRON_LIST:
        date = c['date']
        if datetime.datetime.now() > date:
            CRON_LIST.remove(c)
            await handle_cron(c['do'])


async def handle_cron(string):
    try:
        if string.find("unban") != -1:
            iden = int(string.split(" ")[1])
            server = bot.get_guild(SERVER_ID)
            member = await bot.fetch_user(int(iden))
            await server.unban(member)
            print(f"Unbanned user ID: {iden}")
        elif string.find("unmute") != -1:
            iden = int(string.split(" ")[1])
            server = bot.get_guild(SERVER_ID)
            member = server.get_member(int(iden))
            role = discord.utils.get(server.roles, name=ROLE_MUTED)
            self_role = discord.utils.get(server.roles, name=ROLE_SELFMUTE)
            await member.remove_roles(role, self_role)
            print(f"Unmuted user ID: {iden}")
        elif string.find("unstealfishban") != -1:
            iden = int(string.split(" ")[1])
            STEALFISH_BAN.remove(iden)
            print(f"Un-stealfished user ID: {iden}")
        else:
            print("ERROR:")
            await auto_report("Error with a cron task", "red", f"Error: `{string}`")
    except Exception as e:
        await auto_report("Error with a cron task", "red", f"Error: `{e}`\nOriginal task: `{string}`")
        
        
def not_blacklisted_channel(blacklist):
    """Given a string array blacklist, check if command was not invoked in specified blacklist channels."""
    async def predicate(ctx):
        channel = ctx.message.channel
        server = bot.get_guild(SERVER_ID)
        for c in blacklist:
            if channel == discord.utils.get(server.text_channels, name=c):
                raise CommandNotAllowedInChannel(channel, "Command was invoked in a blacklisted channel.")
        return True

    return commands.check(predicate)


@bot.command()
async def help(ctx: commands.Context):
    '''Sends a menu with all the commands'''
    current = 0
    view = HelpButtons(ctx, current)
    await ctx.send(embed=paginationList[current], view=view)


@bot.command()
@commands.check(is_staff)
async def ticket(ctx):
    '''Sends the ticket button embed'''
    view = Ticket()
    em1 = discord.Embed(title="TMS Tickets",
                       description="To create a ticket press the button below",color=0xff008c)
    em1.set_image(
        url='https://cdn.discordapp.com/attachments/685035292989718554/724301857157283910/ezgif-1-a2a2e7173d80.gif')
    em1.set_footer(text="TMS-Bot Tickets for reporting or questions")
    await ctx.send(embed=em1, view=view)
    
    
@bot.command()
async def source(ctx, command = None):
    """Displays my full source code or for a specific command.
    To display the source code of a subcommand you can separate it by
    periods, e.g. tag.create for the create subcommand of the tag command
    or by spaces.
    """
    source_url = 'https://github.com/pandabear189/tms-scioly-bots'
    branch = 'main'
    if command is None:
        await ctx.send(source_url)

    else:
        obj = bot.get_command(command.replace('.', ' '))
        if obj is None:
            return await ctx.send('Could not find command.')

        src = obj.callback.__code__
        module = obj.callback.__module__
        filename = src.co_filename

        lines, firstlineno = inspect.getsourcelines(src)
        if not module.startswith('discord'):
            location = os.path.relpath(filename).replace('\\', '/')
        else:
            location = module.replace('.', '/') + '.py'
            source_url = 'https://github.com/Rapptz/discord.py'
            branch = 'master'

        final_url = f'<{source_url}/blob/{branch}/{location}#L{firstlineno}-L{firstlineno + len(lines) - 1}>'
        await ctx.send(final_url)


@bot.command()
async def rule(ctx, number = commands.Option(description="Which rule to display")):
    """Gets a specified rule."""
    if not number.isdigit() or int(number) < 1 or int(number) > 6:

        return await ctx.reply("Please use a valid rule number, from 1 through 6. (Ex: `!rule 4`)")
    rule = RULES[int(number) - 1]
    embed=discord.Embed(title="",
                        description=f"**Rule {number}:**\n> {rule}",
                        color=0xff008c)
    return await ctx.send(embed=embed)


@bot.command()
@commands.check(is_staff)
async def embed(ctx, title=None, description=None):
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


@bot.command()
async def roll(ctx):
    '''Rolls a dice'''
    msg = await ctx.send("<a:typing:883864406537162793> Rolling a dice...")
    await ctx.channel.trigger_typing()
    await asyncio.sleep(5)
    sayings = ['<:dice1:884113954383728730>',
               '<:dice2:884113968493391932>',
               '<:dice3:884113979033665556>',
               '<:dice4:884113988596674631>',
               '<:dice5:884114002156867635>',
               '<:dice6:884114012281901056>'
                ]
    response = sayings[math.floor(random.random() * len(sayings))]
    await msg.edit(f"{response}")


@bot.command()
async def magic8ball(ctx, question):
    '''Swishes a Magic8ball'''
    msg = await ctx.send("<a:typing:883864406537162793> Swishing the magic 8 ball...")
    await ctx.channel.trigger_typing()
    await asyncio.sleep(4)
    sayings = [
        "Yes.",
        "Ask again later.",
        "Not looking good.",
        "Cannot predict now.",
        "It is certain.",
        "Try again.",
        "Without a doubt.",
        "Don't rely on it.",
        "Outlook good.",
        "My reply is no.",
        "Don't count on it.",
        "Yes - definitely.",
        "Signs point to yes.",
        "I believe so.",
        "Nope.",
        "Concentrate and ask later.",
        "Try asking again.",
        "For sure not.",
        "Definitely no."
    ]
    response = sayings[math.floor(random.random()*len(sayings))]
    await msg.edit(f"**{response}**")


@bot.command()
async def report(ctx, reason):
    """Creates a report that is sent to staff members."""
    server = bot.get_guild(SERVER_ID)
    reports_channel = discord.utils.get(server.text_channels, name=CHANNEL_REPORTS)
    ava = ctx.message.author.avatar

    message = reason
    embed = discord.Embed(title="Report received using `!report`", description=" ", color = 0xFF0000)
    embed.add_field(name="User:", value=f"{ctx.message.author.mention} \n id: `{ctx.message.author.id}`")
    embed.add_field(name="Report:", value=f"`{message}`")
    embed.set_author(name=f"{ctx.message.author}",icon_url=ava)
    message = await reports_channel.send(embed=embed)
    REPORT_IDS.append(message.id)
    await message.add_reaction("\U00002705")
    await message.add_reaction("\U0000274C")
    await ctx.reply("Thanks, report created.", mention_author=False)

# Meant for TMS-Bot only
async def auto_report(reason, color, message):
    """Allows Pi-Bot to generate a report by himself."""
    server = bot.get_guild(SERVER_ID)
    reports_channel = discord.utils.get(server.text_channels, name=CHANNEL_REPORTS)
    embed = assemble_embed(
        title=f"{reason} (message from TMS-Bot)",
        webcolor=color,
        fields = [{
            "name": "Message",
            "value": message,
            "inline": False
        }]
    )
    message = await reports_channel.send(embed=embed)
    REPORT_IDS.append(message.id)
    await message.add_reaction("\U00002705")
    await message.add_reaction("\U0000274C")


@bot.command()
async def warn(ctx,
               member:discord.Member = commands.Option(description="Which user to warn"),
               reason = commands.Option(description="Why you are warning this user")
               ):
    '''Warns a user'''
    server = bot.get_guild(SERVER_ID)
    reports_channel = discord.utils.get(server.text_channels, name=CHANNEL_REPORTS)
    mod = ctx.message.author
    avatar = mod.avatar
    avatar1 = member.avatar.url

    if member is None or member == ctx.message.author:
        return await ctx.reply("You cannot warn yourself :rolling_eyes:",
                                   mention_author=False)
    if reason is None:
        return await ctx.reply(f"{ctx.message.author.mention} You need to give a reason for why you are warning {member.mention}",
                                   mention_author=False)
    if member.id in TMS_BOT_IDS:
        return await ctx.reply(f"Hey {ctx.message.author.mention}! You can't warn {member.mention}",
                                   mention_author=False)
    embed = discord.Embed(title="Warning Given",
                          description=f"Warning issued to {member.mention} \n id: `{member.id}`",
                                color= 0xFF0000)
    embed.add_field(name="Reason:", value=f"`{reason}`")
    embed.add_field(name="Responsible Moderator:", value=f"{mod.mention}")
    embed.set_author(name=f"{member}",
                     icon_url=avatar1)


    embed1=discord.Embed(title=" ", description=f"{member} has been warned", color= 0x2E66B6)

    embed2=discord.Embed(title=f"Warning",
                         description=f"You have been given a warning by {mod.mention} for `{reason}`. \n Please follow the rules of the server",
                         color= 0xFF0000)
    embed2.set_author(name=f"{mod}",
                     icon_url=avatar)

    message = await reports_channel.send(embed=embed)
    WARN_IDS.append(message.id)
    await message.add_reaction("\U00002705")
    await message.add_reaction("\U0000274C")
    await ctx.reply(embed=embed1, mention_author=False)
    await member.send(embed=embed2)


@bot.event
async def on_raw_reaction_add(payload):
    if payload.user_id not in TMS_BOT_IDS:
        guild = bot.get_guild(payload.guild_id)
        reports_channel = discord.utils.get(guild.text_channels, name=CHANNEL_REPORTS)
        if payload.message_id in WARN_IDS:
            messageObj = await reports_channel.fetch_message(payload.message_id)
            if payload.emoji.name == "\U0000274C": # :x:
                print("Warning cleared with no action.")
                await messageObj.delete()
            if payload.emoji.name == "\U00002705": # :white_check_mark:
                print("Warning handled.")
                await messageObj.delete()

        elif payload.message_id in REPORT_IDS:
            messageObj = await reports_channel.fetch_message(payload.message_id)
            if payload.emoji.name == "\U0000274C": # :x:
                print("Report cleared with no action.")
                await messageObj.delete()
            if payload.emoji.name == "\U00002705": # :white_check_mark:
                print("Report handled.")
                await messageObj.delete()
            return


@bot.event
async def on_member_update(before, after):
    if after.nick is None:
        return
    for word in CENSORED_WORDS:
        if len(re.findall(fr"\b({word})\b", after.nick, re.I)):
            await auto_report("Innapropriate Username Detected", "red", f"A member ({str(after)}) has updated their nickname to **{after.nick}**, which the censor caught as innapropriate.")


@bot.command()
@not_blacklisted_channel(blacklist=[WELCOME_CHANNEL])
async def candy(ctx):
    '''Feeds panda some candy!'''
    global fish_now
    r = random.random()
    if len(str(fish_now)) > 1500:
        fish_now = round(pow(fish_now, 0.5))
        if fish_now == 69: fish_now = 70
        return await ctx.send("Woah! Panda's amount of candy is a little too much, so it unfortunately has to be square rooted.")
    if r > 0.9:
        fish_now += 100
        if fish_now == 69: fish_now = 70
        return await ctx.send(f"Wow, you gave panda a super candy! Added 100 candy! Panda now has {fish_now} pieces of candy!")
    if r > 0.1:
        fish_now += 1
        if fish_now == 69:
            fish_now = 70
            return await ctx.send(f"You feed panda two candy. Panda now has {fish_now} pieces of candy!")
        else:
            return await ctx.send(f"You feed panda one candy. Panda now has {fish_now} pieces of candy!")
    if r > 0.02:
        fish_now += 0
        return await ctx.send(f"You can't find any candy... and thus can't feed panda. Panda still has {fish_now} pieces of candy.")
    else:
        fish_now = round(pow(fish_now, 0.5))
        if fish_now == 69: fish_now = 70
        return await ctx.send(f":sob:\n:sob:\n:sob:\nAww, panda's candy was accidentally square root'ed. Panda now has {fish_now} pieces of candy. \n:sob:\n:sob:\n:sob:")


@bot.command()
@not_blacklisted_channel(blacklist=[WELCOME_CHANNEL])
async def stealcandy(ctx):
    '''Steals some candy from panda'''
    global fish_now
    member = ctx.message.author
    r = random.random()
    if member.id in STEALFISH_BAN:
        return await ctx.send("Hey! You've been banned from stealing candy for now.")
    if r >= 0.75:
        ratio = r - 0.5
        fish_now = round(fish_now * (1 - ratio))
        per = round(ratio * 100)
        return await ctx.send(f"You stole {per}% of panda's candy!")
    if r >= 0.416:
        parsed = dateparser.parse("1 hour", settings={"PREFER_DATES_FROM": "future"})
        STEALFISH_BAN.append(member.id)
        CRON_LIST.append({"date": parsed, "do": f"unstealfishban {member.id}"})
        return await ctx.send(f"Sorry {member.mention}, but it looks like you're going to be banned from using this command for 1 hour!")
    if r >= 0.25:
        parsed = dateparser.parse("1 day", settings={"PREFER_DATES_FROM": "future"})
        STEALFISH_BAN.append(member.id)
        CRON_LIST.append({"date": parsed, "do": f"unstealfishban {member.id}"})
        return await ctx.send(f"Sorry {member.mention}, but it looks like you're going to be banned from using this command for 1 day!")
    if r >= 0.01:
        return await ctx.send("Hmm, nothing happened. *crickets*")
    else:
        STEALFISH_BAN.append(member.id)
        return await ctx.send("You are banned from using `!stealcandy` until the next version of TMS-Bot is released.")


@bot.command()
@commands.check(is_staff)
async def slowmode(ctx,
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


@bot.command()
@commands.check(is_staff)
async def ban(ctx,
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
    server = bot.get_guild(SERVER_ID)
    reports_channel = discord.utils.get(server.text_channels, name=CHANNEL_REPORTS)
    embed1 = discord.Embed(title=f"New Banned Member",
                           description=f"{member.mention} has been banned from {server}",
                           color=0xFF0000)
    embed1.add_field(name="Reason:", value=f'`{reason}`')
    embed1.add_field(name="Responsible Moderator:", value=f"`{ctx.message.author}`")
    embed1.set_author(name=f'{member}', icon_url=f"{member.avatar}")

    await reports_channel.send(embed=embed1)
    await ctx.reply(embed=embed, mention_author=False)


@bot.command()
@commands.check(is_staff)
async def unban(ctx,
                member:discord.User= commands.Option(description="The user (id) to unban")
                ):
    """Unbans a user."""
    if member == None:
        await ctx.channel.send("Please give either a user ID or mention a user.")
        return
    await ctx.guild.unban(member)
    embed=discord.Embed(title="Unban Request",
                        description=f"Inverse ban hammer applied, {member.mention} unbanned. Please remember that I cannot force them to re-join the server, they must join themselves.",
                        color=0x00FF00)
    await ctx.channel.send(embed=embed)


@bot.event
async def on_member_unban(guild,member):
    server = bot.get_guild(SERVER_ID)
    reports_channel = discord.utils.get(server.text_channels, name=CHANNEL_REPORTS)
    embed = assemble_embed(
        title=f"New Unban (Message from TMS-Bot)",
        webcolor= "lime",
        fields=[{
            "name": "Message",
            "value": f"{member.mention} unbanned from {guild}",
            "inline": False
        }]
    )
    await reports_channel.send(embed=embed)


@bot.command()
async def charinfo(ctx,
                   characters: str = commands.Option(description="Characters you want")
                   ):
    """
    Shows you information about a number of characters.
    Only up to 25 characters at a time.
    """
    def to_string(c):
        digit = f'{ord(c):x}'
        name = unicodedata.name(c, 'Name not found.')
        return f'`\\U{digit:>08}`: {name} - {c} \N{EM DASH} <http://www.fileformat.info/info/unicode/char/{digit}>'

    msg = '\n'.join(map(to_string, characters))
    if len(msg) > 2000:
        return await ctx.send('Output too long to display.')
    await ctx.send(msg)


@bot.command()
@commands.check(is_staff)
async def dm(ctx, member: discord.Member,
             message=commands.Option(description="What to DM the member")
             ):
    '''DMs a user.'''
    em1=discord.Embed(title=f" ",
                      description=f"> {message}",
                      color=0x2F3136)
    em1.set_author(name=f"Message from {ctx.message.author}", icon_url=ctx.message.author.avatar)
    await ctx.reply(f"Message sent to `{member}`", mention_author=False)
    await member.send(embed=em1)


@bot.command()
async def emoji(ctx,
                custom_emojis: commands.Greedy[discord.PartialEmoji] = commands.Option(description="Up to 5 custom emojis")
                ):
    """
    Makes an emoji bigger and shows it's formatting
    """
    if not custom_emojis:
        await ctx.send('This command only works for custom emojis')

    if len(custom_emojis) > 5:
        raise commands.TooManyArguments()

    for emoji in custom_emojis:
        if emoji.animated:
            emoticon = f"*`<`*`a:{emoji.name}:{emoji.id}>`"
        else:
            emoticon = f"*`<`*`:{emoji.name}:{emoji.id}>`"
        embed = discord.Embed(description=f"{emoticon}", color=ctx.me.color)
        embed.set_image(url=emoji.url)
        await ctx.send(embed=embed)


@bot.command()
@not_blacklisted_channel(blacklist=[WELCOME_CHANNEL])
async def count(ctx):
    '''Counts the number of members in the server'''
    guild = ctx.message.author.guild
    await ctx.send(f"Currently, there are `{len(guild.members)}` members in the server.")


@bot.command()
@commands.check(is_staff)
async def sync(ctx,
               channel: discord.TextChannel= commands.Option(description="The channel to sync permissions with")
               ):
    '''Syncs permmissions to channel category'''

    if channel is None:
        await ctx.message.channel.edit(sync_permissions=True)
        await ctx.send(f'Permissions for {ctx.message.channel.mention} synced with {ctx.message.channel.category}')
    else:
        await channel.edit(sync_permissions=True)
        await ctx.send(f'Permissions for {channel.mention} synced with {channel.category}')


@bot.command()
async def latex(ctx,
                latex):
    '''Displays an image of an equation, uses LaTex as input'''

    print(latex)
    new_args = latex.replace(" ", r"&space;")
    print(new_args)
    await ctx.send(r"https://latex.codecogs.com/png.latex?\dpi{175}{\color{White}" + new_args + "}")


@bot.command()
async def profile(ctx,
                  user:discord.User = commands.Option (description="The user you want")
                  ):

    if user is None:
        avatar = ctx.author.avatar
        await ctx.send(f'{avatar}')
    else:
        try:
            await ctx.send(f'{user.avatar}')
        except Exception as e:
            await ctx.send(f"Couldn't find profile: {e}")


@bot.event
async def on_raw_message_edit(payload):
    channel = bot.get_channel(payload.channel_id)
    guild = bot.get_guild(SERVER_ID) if channel.type == discord.ChannelType.private else channel.guild
    edited_channel = discord.utils.get(guild.text_channels, name=CHANNEL_EDITEDM)
    if channel.type != discord.ChannelType.private or discord.DMChannel or channel.name in [CHANNEL_EDITEDM, CHANNEL_DELETEDM, CHANNEL_DMLOG]:
        return
    try:
        message = payload.cached_message
        if (datetime.datetime.now() - message.created_at).total_seconds() < 2:
            # no need to log events because message was created
            return
        message_now = await channel.fetch_message(message.id)
        channel_name = f"{message.author.mention}'s DM" if channel.type == discord.ChannelType.private else message.channel.mention
        embed = assemble_embed(
            title=":pencil: Edited Message",
            fields=[
                {
                    "name": "Author",
                    "value": message.author,
                    "inline": "False"
                },
                {
                    "name": "Channel",
                    "value": channel_name,
                    "inline": "False"
                },
                {
                    "name": "Message ID",
                    "value": message.id,
                    "inline": "False"
                },
                {
                    "name": "Before",
                    "value": message.content[:1024] if len(message.content) > 0 else "None",
                    "inline": "False"
                },
                {
                    "name": "After",
                    "value": message_now.content[:1024] if len(message_now.content) > 0 else "None",
                    "inline": "False"
                },
            ]
        )
        await edited_channel.send(embed=embed)
    except Exception as e:
        message_now = await channel.fetch_message(payload.message_id)
        embed = assemble_embed(
            title=":pencil: Edited Message",
            fields=[
                {
                    "name": "Channel",
                    "value": bot.get_channel(payload.channel_id).mention,
                    "inline": "False"
                },
                {
                    "name": "Message ID",
                    "value": payload.message_id,
                    "inline": "False"
                },
                {
                    "name": "Author",
                    "value": message_now.author,
                    "inline": "True"
                },
                {
                    "name": "Current Message",
                    "value": message_now.content[:1024] if len(message_now.content) > 0 else "None",
                    "inline": "False"
                },
            ]
        )
        await edited_channel.send(embed=embed)


@bot.command()
@commands.check(is_staff)
async def vip(ctx,
              user:discord.Member= commands.Option(description="The user you wish to VIP")):
    """Exalts/VIPs a user."""
    member = ctx.message.author
    role = discord.utils.get(member.guild.roles, name=ROLE_VIP)
    await user.add_roles(role)
    await ctx.send(f"Successfully added VIP. Congratulations {user.mention}! :partying_face: :partying_face: ")


@bot.command()
@commands.check(is_staff)
async def unvip(ctx,
                user:discord.Member=commands.Option(description="The user you wish to unVIP")):
    """Unexalts/unVIPs a user."""
    member = ctx.message.author
    role = discord.utils.get(member.guild.roles, name=ROLE_VIP)
    await user.remove_roles(role)
    await ctx.send(f"Successfully removed VIP from {user.mention}.")


@bot.command()
@commands.check(is_staff)
async def trial(ctx,
              user:discord.Member= commands.Option(description="The user you wish promote to trial leader")):
    """Promotes/Trials a user."""
    member = ctx.message.author
    role = discord.utils.get(member.guild.roles, name=ROLE_TRIAL)
    await user.add_roles(role)
    await ctx.send(f"Successfully added {role}. Congratulations {user.mention}! :partying_face: :partying_face: ")


@bot.command()
@commands.check(is_staff)
async def untrial(ctx,
                user:discord.Member=commands.Option(description="The user you wish to demote")):
    """Demotes/unTrials a user."""
    member = ctx.message.author
    role = discord.utils.get(member.guild.roles, name=ROLE_TRIAL)
    await user.remove_roles(role)
    await ctx.send(f"Successfully removed {role} from {user.mention}.")


@bot.command()
async def grade(ctx,
                a: float = commands.Option(description="Your points"),
                b: float = commands.Option(description="Total points")
                ):
    '''Returns a percentage/grade'''
    x = a / b
    z = x*100
    if z < 60:
        await ctx.send(f'{round(z, 2)}% F')
    elif 60 <= z < 70:
        await ctx.send(f'{round(z, 2)}% D')
    elif 70 <= z <80:
        await ctx.send(f'{round(z, 2)}% C')
    elif 80 <= z <90:
        await ctx.send(f'{round(z, 2)}% B')
    elif 90 <= z < 93:
        await ctx.send(f'{round(z, 2)}% A-')
    elif 93 <= z < 97:
        await ctx.send(f'{round(z, 2)}% A')
    elif 97 <= z <= 100:
        await ctx.send(f'{round(z, 2)}% A+')
    elif z > 100:
        await ctx.send(f"{round(z, 2)}% A++ must've gotten extra credit")


@bot.event
async def on_raw_message_delete(payload):
    channel = bot.get_channel(payload.channel_id)

    guild = bot.get_guild(SERVER_ID) if channel.type == discord.ChannelType.private else channel.guild
    if channel.type != discord.ChannelType.private and channel.name in [CHANNEL_REPORTS, CHANNEL_DELETEDM, CHANNEL_DMLOG]:
        print("Ignoring deletion event because of the channel it's from.")
        return

    deleted_channel = discord.utils.get(guild.text_channels, name=CHANNEL_DELETEDM)
    try:
        message = payload.cached_message
        channel_name = f"{message.author.mention}'s DM" if channel.type == discord.ChannelType.private else message.channel.mention
        embed = assemble_embed(
            title=":fire: Deleted Message",
            fields=[
                {
                    "name": "Author",
                    "value": message.author,
                    "inline": "False"
                },
                {
                    "name": "Channel",
                    "value": channel_name,
                    "inline": "False"
                },
                {
                    "name": "Message ID",
                    "value": message.id,
                    "inline": "False"
                },
                {
                    "name": "Created At (UTC)",
                    "value": message.created_at,
                    "inline": "False"
                },
                {
                    "name": "Edited At (UTC)",
                    "value": message.edited_at,
                    "inline": "False"
                },
                {
                    "name": "Attachments",
                    "value": " | ".join([f"**{a.filename}**: [Link]({a.url})" for a in message.attachments]) if len(message.attachments) > 0 else "None",
                    "inline": "False"
                },
                {
                    "name": "Content",
                    "value": str(message.content)[:1024] if len(message.content) > 0 else "None",
                    "inline": "True"
                },
                {
                    "name": "Embed",
                    "value": "\n".join([str(e.to_dict()) for e in message.embeds])[:1024] if len(message.embeds) > 0 else "None",
                    "inline": "False"
                }
            ]
        )
        await deleted_channel.send(embed=embed)
    except Exception as e:
        print(e)
        embed = assemble_embed(
            title=":fire: Deleted Message",
            fields=[
                {
                    "name": "Channel",
                    "value": bot.get_channel(payload.channel_id).mention,
                    "inline": "True"
                },
                {
                    "name": "Message ID",
                    "value": payload.message_id,
                    "inline": "True"
                }
            ]
        )
        await deleted_channel.send(embed=embed)


@bot.command()
@commands.check(is_staff)
async def kick(ctx,
               member:discord.Member = commands.Option(description="Which user to kick"),
               reason = commands.Option(description="Why you're kicking this user")
               ):
    view = Confirm(ctx)

    await ctx.reply(f"Are you sure you want to kick {member} for {reason}", view=view)
    await view.wait()
    if view.value is False:
        await ctx.send('Aborting...')
    if view.value is True:

        if reason == None:
            return await ctx.send("Please specify a reason why you want to kick this user!")
        if member.id in TMS_BOT_IDS:
            return await ctx.send("Hey! You can't kick me!!")
        await member.kick(reason=reason)

        em6 = discord.Embed(title="",
                            description=f"{member.mention} was kicked for {reason}.",
                            color=0xFF0000)

        await ctx.send(embed=em6)
    return view.value


@bot.command()
@not_blacklisted_channel(blacklist=[WELCOME_CHANNEL])
async def ping(ctx):
    '''Get the bot's latency'''
    latency = round(bot.latency * 1000, 2)
    em = discord.Embed(title="Pong :ping_pong:",
                     description=f":clock1: My ping is {latency} ms!",
                     color=0x16F22C)
    await ctx.reply(embed=em, mention_author=False)


@bot.command()
@commands.check(is_staff)
async def mute(ctx,
               user: discord.Member = commands.Option(description= "The user to mute"),
               time= commands.Option(description="The amount of time to mute the user")
               ):
    """
    Mutes a user.
    """
    view = Confirm(ctx)

    await ctx.reply(f"Are you sure you want to mute {user} for {time}", view=view)
    await view.wait()
    if view.value is False:
        await ctx.send('Aborting...')
    if view.value is True:
        await _mute(ctx, user, time, self=False)
    return view.value


async def _mute(ctx, user:discord.Member, time: str, self: bool):
    """
    Helper function for muting commands.
    :param user: User to be muted.
    :type user: discord.Member
    :param time: The time to mute the user for.
    :type time: str
    """
    if user.id in TMS_BOT_IDS:
        return await ctx.send("Hey! You can't mute me!!")
    if time == None:
        return await ctx.send("You need to specify a length that this used will be muted. Examples are: `1 day`, `2 months, 1 day`, or `indef` (aka, forever).")
    role = None
    if self:
        role = discord.utils.get(user.guild.roles, name=ROLE_SELFMUTE)
    else:
        role = discord.utils.get(user.guild.roles, name=ROLE_MUTED)
    parsed = "indef"
    if time != "indef":
        parsed = dateparser.parse(time, settings={"PREFER_DATES_FROM": "future"})
        if parsed == None:
            return await ctx.send("Sorry, but I don't understand that length of time.")
        CRON_LIST.append({"date": parsed, "do": f"unmute {user.id}"})
    await user.add_roles(role)
    central = pytz.timezone("US/Central")
    em4=discord.Embed(title="",
                      description=f"Successfully muted {user.mention} until `{str(central.localize(parsed))} CT`.",
                      color=0xFF0000)
    await ctx.send(embed=em4)


@bot.command()
@commands.check(is_staff)
async def getvariable(ctx,
                      var= commands.Option(description="The global variable to display")):
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
            # await ctx.send(f"`{var}`  Variable value: ```ini\n{variable}```")
            header = variable[0].keys()
            rows = [x.values() for x in variable]
            table = tabulate.tabulate(rows, header, "fancy_grid")
            await ctx.reply(f"```{table}```", mention_author=False)

        except Exception as e:
            await ctx.send(f"Can't find that variable! `{e}`")


@bot.command()
@commands.check(is_staff)
async def removevariable(ctx,
                         user: discord.User = commands.Option(description= "The user to remove from the CRON_LIST")
                         ):
    for obj in CRON_LIST[:]:
        if obj['do'] == f'unmute {user.id}':
            CRON_LIST.remove(obj)
            await ctx.send(f'Removed {user} unmute from CRON_LIST')
        elif obj['do'] == f'unban {user.id}':
            CRON_LIST.remove(obj)
            await ctx.send(f'Removed {user} unban from CRON_LIST')
        else:
            await ctx.send('Unknown object to remove')


@bot.command()
async def selfmute(ctx, time):
    """
    Self mutes the user that invokes the command.

    """
    view = Confirm(ctx)
    user = ctx.message.author

    if time is None:
        await ctx.send('You need to specify a length that this used will be muted. `exe:` `1 day`, `2 months, 1 day`')
    else:
        await ctx.reply(f"Are you sure you want to selfmute for {time}", view=view)
        await view.wait()
        if view.value is False:

            await ctx.send('Aborting...')
        if view.value is True:

            await _mute(ctx, user, time, self=True)
        return view.value


@bot.command()
async def counter(ctx: commands.Context):
    """Starts a counter for pressing."""
    await ctx.send('Press!', view=Counter())


@bot.command()
@commands.check(is_staff)
async def unmute(ctx, user: discord.Member):
    view = Confirm(ctx)
    await ctx.reply(f"Are you sure you want to unmute `{user}`?", view=view)
    await view.wait()
    if view.value is False:
        await ctx.send('Unmute Canceled')
    if view.value is True:
        role = discord.utils.get(user.guild.roles, name=ROLE_MUTED)
        await user.remove_roles(role)
        em5=discord.Embed(title="",
                      description=f"Successfully unmuted {user.mention}.",
                      color=0x16F22C)

        await ctx.send(embed=em5)
        for obj in CRON_LIST[:]:
            if obj['do'] == f'unmute {user.id}':
                CRON_LIST.remove(obj)
    return view.value


def is_nuke_allowed(ctx):
    import datetime
    global STOPNUKE
    time_delta = STOPNUKE - datetime.datetime.utcnow()
    if time_delta > datetime.timedelta():
        raise discord.ext.commands.CommandOnCooldown(None, time_delta.total_seconds())
    return True


async def _nuke_countdown(ctx, count=-1):
    import datetime
    global STOPNUKE
    await ctx.send("=====\nINCOMING TRANSMISSION.\n=====")
    await ctx.send("PREPARE FOR IMPACT.")
    for i in range(10, 0, -1):
        if count < 0:
            await ctx.send(f"NUKING MESSAGES IN {i}... TYPE `!stopnuke` AT ANY TIME TO STOP ALL TRANSMISSION.")
        else:
            await ctx.send(f"NUKING {count} MESSAGES IN {i}... TYPE `!stopnuke` AT ANY TIME TO STOP ALL TRANSMISSION.")
        await asyncio.sleep(1)
        if STOPNUKE > datetime.datetime.utcnow():
            return await ctx.send(
                "A COMMANDER HAS PAUSED ALL NUKES FOR 20 SECONDS. NUKE CANCELLED.")  # magic number MonkaS


@bot.command()
@commands.check(is_staff)
async def nuke(ctx, count:int):
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


@bot.command()
@commands.check(is_staff)
async def nukeuntil(ctx, message_id):  # prob can use converters to convert the msgid to a Message object

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
async def nuke_error(ctx, error):
    ctx.__slots__ = True
    print(f"{BOT_PREFIX}nuke error handler: {error}")
    if isinstance(error, discord.ext.commands.MissingAnyRole):
        return await ctx.send("APOLOGIES. INSUFFICIENT RANK FOR NUKE.")
    if isinstance(error, discord.ext.commands.CommandOnCooldown):
        return await ctx.send(
            f"TRANSMISSION FAILED. ALL NUKES ARE CURRENTLY PAUSED FOR ANOTHER {'%.3f' % error.retry_after} SECONDS. TRY AGAIN LATER.")
    ctx.__slots__ = False


@bot.command()
@commands.check(is_staff)
async def stopnuke(ctx):
    global STOPNUKE
    NUKE_COOLDOWN = 20
    STOPNUKE = datetime.datetime.utcnow() + datetime.timedelta(seconds=NUKE_COOLDOWN)  # True
    await ctx.send(f"TRANSMISSION RECEIVED. STOPPED ALL CURRENT NUKES FOR {NUKE_COOLDOWN} SECONDS.")


@stopnuke.error
async def stopnuke_error(ctx, error):
    ctx.__slots__ = True
    print(f"{BOT_PREFIX}nuke error handler: {error}")
    if isinstance(error, discord.ext.commands.MissingAnyRole):
        return await ctx.send("APOLOGIES. INSUFFICIENT RANK FOR STOPPING NUKE.")


@bot.command()
async def wikipedia(ctx,
                    request = commands.Option(default=None, description= "Action, like summary or search"),
                    page = commands.Option(description="What page you want!")
                    ):
    '''Get a wikipedia page or summary!'''
    term = page
    if request is None:
        return await ctx.send("You must specifiy a command and keyword, such as `/wikipedia search \"Science Olympiad\"`")
    if request == "search":
        return await ctx.send("\n".join([f"`{result}`" for result in aiowikip.search(term, results=5)]))
    elif request == "summary":
        try:
            term = term.title()
            page = await aiowikip.page(term)
            return await ctx.send(aiowikip.summary(term, sentences=3) + f"\n\nRead more on Wikipedia here: <{page.url}>!")
        except wikip.exceptions.DisambiguationError as e:
            return await ctx.send(f"Sorry, the `{term}` term could refer to multiple pages, try again using one of these terms:" + "\n".join([f"`{o}`" for o in e.options]))
        except wikip.exceptions.PageError as e:
            return await ctx.send(f"Sorry, but the `{term}` page doesn't exist! Try another term!")
    else:
        try:
            term = f"{request} {term}".strip()
            term = term.title()
            page = await aiowikip.page(term)
            return await ctx.send(f"Sure, here's the link: <{page.url}>")
        except wikip.exceptions.PageError as e:
            return await ctx.send(f"Sorry, but the `{term}` page doesn't exist! Try another term!")
        except wikip.exceptions.DisambiguationError as e:
            return await ctx.send(f"Sorry, but the `{term}` page is a disambiguation page. Please try again!")


@bot.command()
async def tictactoe(ctx: commands.Context):
    """Starts a tic-tac-toe game."""
    await ctx.send('Tic Tac Toe: X goes first', view=TicTacToe())


@bot.command()
async def info(ctx):
    """Gets information about the Discord server."""
    server = ctx.message.guild
    name = server.name
    owner = server.owner
    creation_date = server.created_at
    emoji_count = len(server.emojis)
    icon = server.icon.replace(format='gif', static_format='jpeg')
    animated_icon = server.icon.is_animated()
    iden = server.id
    banner = server.banner
    desc = server.description
    mfa_level = server.mfa_level
    verification_level = server.verification_level
    content_filter = server.explicit_content_filter
    default_notifs = server.default_notifications
    features = server.features
    splash = server.splash
    premium_level = server.premium_tier
    boosts = server.premium_subscription_count
    channel_count = len(server.channels)
    text_channel_count = len(server.text_channels)
    voice_channel_count = len(server.voice_channels)
    category_count = len(server.categories)
    system_channel = server.system_channel
    if type(system_channel) == discord.TextChannel: system_channel = system_channel.mention
    rules_channel = server.rules_channel
    if type(rules_channel) == discord.TextChannel: rules_channel = rules_channel.mention
    public_updates_channel = server.public_updates_channel
    if type(public_updates_channel) == discord.TextChannel: public_updates_channel = public_updates_channel.mention
    emoji_limit = server.emoji_limit
    bitrate_limit = server.bitrate_limit
    filesize_limit = round(server.filesize_limit/1000000, 3)
    boosters = server.premium_subscribers
    for i, b in enumerate(boosters):
        # convert user objects to mentions
        boosters[i] = b.mention
    boosters = ", ".join(boosters)
    print(boosters)
    role_count = len(server.roles)
    member_count = len(server.members)
    max_members = server.max_members
    discovery_splash_url = server.discovery_splash
    member_percentage = round(member_count/max_members * 100, 3)
    emoji_percentage = round(emoji_count/emoji_limit * 100, 3)
    channel_percentage = round(channel_count/500 * 100, 3)
    role_percenatege = round(role_count/250 * 100, 3)

    staff_member = await is_staff(ctx)
    fields = [
            {
                "name": "Basic Information",
                "value": (
                    f"**Creation Date:** {creation_date}\n" +
                    f"**ID:** {iden}\n" +
                    f"**Animated Icon:** {animated_icon}\n" +
                    f"**Banner URL:** {banner}\n" +
                    f"**Splash URL:** {splash}\n" +
                    f"**Discovery Splash URL:** {discovery_splash_url}"
                ),
                "inline": False
            },
            {
                "name": "Nitro Information",
                "value": (
                    f"**Nitro Level:** {premium_level} ({boosts} individual boosts)\n" +
                    f"**Boosters:** {boosters}"
                ),
                "inline": False
            }
        ]
    if staff_member:
        fields.extend(
            [{
                "name": "Staff Information",
                "value": (
                    f"**Owner:** {owner}\n" +
                    f"**MFA Level:** {mfa_level}\n" +
                    f"**Verification Level:** {verification_level}\n" +
                    f"**Content Filter:** {content_filter}\n" +
                    f"**Default Notifications:** {default_notifs}\n" +
                    f"**Features:** {features}\n" +
                    f"**Bitrate Limit:** {bitrate_limit}\n" +
                    f"**Filesize Limit:** {filesize_limit} MB"
                ),
                "inline": False
            },
            {
                "name": "Channels",
                "value": (
                    f"**Public Updates Channel:** {public_updates_channel}\n" +
                    f"**System Channel:** {system_channel}\n" +
                    f"**Rules Channel:** {rules_channel}\n" +
                    f"**Text Channel Count:** {text_channel_count}\n" +
                    f"**Voice Channel Count:** {voice_channel_count}\n" +
                    f"**Category Count:** {category_count}\n"
                ),
                "inline": False
            },
            {
                "name": "Limits",
                "value": (
                    f"**Channels:** *{channel_percentage}%* ({channel_count}/500 channels)\n" +
                    f"**Members:** *{member_percentage}%* ({member_count}/{max_members} members)\n" +
                    f"**Emoji:** *{emoji_percentage}%* ({emoji_count}/{emoji_limit} emojis)\n" +
                    f"**Roles:** *{role_percenatege}%* ({role_count}/250 roles)"
                ),
                "inline": False
            }
        ])
    embed = assemble_embed(
        title=f"Information for `{name}`",
        desc=f"**Description:** {desc}",
        thumbnailUrl=icon,
        fields=fields
    )
    await ctx.send(embed=embed)


@bot.command()
async def shiba(ctx,
                member:discord.Member = commands.Option(description="Who are you trying to shiba?")
                ):
    """Shiba bombs a user!"""
    if member is None:
        return await ctx.send("Tell me who you want to shiba!! :dog:")
    else:
        doggo = await get_shiba()
        await ctx.send(doggo)
        await ctx.send(f"{member.mention}, <@{ctx.message.author.id}> shiba-d you!!")


@bot.command()
async def cottondetulear(ctx,
                         member:discord.Member = commands.Option(description="Who are you trying to cottondetulear?")
                         ):
    """Cottondetulear-s Another Member!"""
    if member is None:
        return await ctx.send("Tell me who you want to cottondetulear!! :dog:")
    else:
        doggo = await get_cotondetulear()
        await ctx.send(doggo)
        await ctx.send(f"{member.mention}, {ctx.message.author.mention} cottondetulear-d you!!")


@bot.command()
async def akita(ctx,
                member:discord.User = commands.Option(description="Who are you trying to akita?")
                ):
    """Akita-s a user!"""
    if member is None:
        return await ctx.send("Tell me who you want to akita!! :dog:")
    else:
        doggo = await get_akita()
        await ctx.send(doggo)
        await ctx.send(f"{member.mention}, <@{ctx.message.author.id}> akita-d you!!")


@bot.command()
@not_blacklisted_channel(blacklist=[WELCOME_CHANNEL])
async def doge(ctx,
               member:discord.Member = commands.Option(description="Who are you trying to doge?")
               ):
    """Dogeee-s someone!"""
    if member is None:
        return await ctx.send("Tell me who you want to dogeeee!! :dog:")
    else:
        doggo = await get_doggo()
        await ctx.send(doggo)
        await ctx.send(f"{member.mention}, <@{ctx.message.author.id}> dogeee-d you!!")


async def send_to_dm_log(message):
    server = bot.get_guild(SERVER_ID)
    dmChannel = discord.utils.get(server.text_channels, name=CHANNEL_DMLOG)
    embed = assemble_embed(
        title=":speech_balloon: New DM",
        fields=[
            {
                    "name": "Author",
                    "value": message.author,
                    "inline": "True"
                },
                {
                    "name": "Message ID",
                    "value": message.id,
                    "inline": "True"
                },
                {
                    "name": "Created At (UTC)",
                    "value": message.created_at,
                    "inline": "True"
                },
                {
                    "name": "Attachments",
                    "value": " | ".join([f"**{a.filename}**: [Link]({a.url})" for a in message.attachments]) if len(message.attachments) > 0 else "None",
                    "inline": "False"
                },
                {
                    "name": "Content",
                    "value": message.content if len(message.content) > 0 else "None",
                    "inline": "False"
                },
                {
                    "name": "Embed",
                    "value": "\n".join([str(e.to_dict()) for e in message.embeds]) if len(message.embeds) > 0 else "None",
                    "inline": "False"
                }
            ]
    )
    await dmChannel.send(embed=embed)


@bot.command()
@commands.check(is_staff)
async def lock(ctx,
               channel: discord.TextChannel = commands.Option(default=None, description="The channel you want to lock")
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


@bot.command()
@commands.check(is_staff)
async def unlock(ctx,
                 channel:discord.TextChannel = commands.Option(default=None, description="The channel to unlock")
                 ):
    """Unlocks a channel to Member access."""
    member = ctx.message.author
    if channel is None:
        member_role = discord.utils.get(member.guild.roles, name=ROLE_MR)
        await ctx.channel.set_permissions(member_role, add_reactions=True, send_messages=True, read_messages=True)
        SL = discord.utils.get(member.guild.roles, name=ROLE_SERVERLEADER)
        await ctx.channel.set_permissions(SL, add_reactions=True, send_messages=True, read_messages=True)
        await ctx.send(f"Unlocked :unlock: {ctx.channel.mention} to Member access. Please check if permissions need to be synced.")
    else:
        member_role = discord.utils.get(member.guild.roles, name=ROLE_MR)
        await channel.set_permissions(member_role, add_reactions=True, send_messages=True, read_messages=True)
        SL = discord.utils.get(member.guild.roles, name=ROLE_SERVERLEADER)
        await channel.set_permissions(SL, add_reactions=True, send_messages=True, read_messages=True)
        await ctx.send(f"Unlocked :unlock: {channel.mention} to Member access. Please check if permissions need to be synced.")


@bot.command()
async def tag(ctx,
              name=commands.Option(description="Name of the tag")
              ):
    '''Retrieves a tag'''
    tag = name.lower()
    if tag == 'rules':
        em1=discord.Embed(title="Rules", description="Here are the rules for the 2021-22 season", color = 0xff008c)
        em1.add_field(name='Division B Rules',
                      value="[Click Here](https://www.soinc.org/sites/default/files/2021-09/Science_Olympiad_Div_B_2022_Rules_Manual_Web_0.pdf/ \"Division B\")")
        em1.add_field(name='Division C Rules',
                      value="[Click Here](https://www.soinc.org/sites/default/files/2021-09/Science_Olympiad_Div_C_2022_Rules_Manual_Web_1.pdf/ \"Division C\")")
        await ctx.send(embed=em1)

    elif tag == 'anatomy':
        em2 = discord.Embed(title="Anatomy & Physiology Rules",
                            description="Participants will be assessed on their understanding of the anatomy and physiology for the human Nervous, Sense Organs, and Endocrine systems.  \n This Event may be administered as a written test or as series of lab-practical stations which can include but are not limited to experiments, scientific apparatus, models, illustrations, specimens, data collection and analysis, and problems for students to solve.",
                            color=0xff008c)
        em2.add_field(name='Full Anatomy Rules',
                      value="[Click Here](https://www.soinc.org/sites/default/files/2021-09/Science_Olympiad_Div_B_2022_Rules_Manual_Web_0.pdf#page=7/ \"Anatomy\")")
        await ctx.send(embed=em2)

    elif tag == 'bpl':
        em3 = discord.Embed(title="Bio Process Lab Rules",
                            description="This event is a lab-oriented competition involving the  fundamental  science  processes of a middle school life science/biology lab program. \n This event will consist of a series of lab stations. Each station will require the use of process skills to answer questions and/or perform a required task such as formulating and/or evaluating hypotheses and procedures, using scientific instruments to collect data, making observations, presenting and/or interpreting data, or making inferences and conclusions",
                    color=0xff008c)
        em3.add_field(name='Full Bio Process Lab',
                      value="[Click Here](https://www.soinc.org/sites/default/files/2021-09/Science_Olympiad_Div_B_2022_Rules_Manual_Web_0.pdf#page=9/ \"Bio Process Lab\")")
        await ctx.send(embed=em3)

    else:
        await ctx.reply("Sorry I couldn't find that tag", mention_author=False)


@bot.command()
@commands.check(is_staff)
async def rules(ctx):
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


@bot.command()
@commands.check(is_staff)
async def gift(ctx):
    em1=discord.Embed(title="You've been gifted a subscription!", description=" ", color=0x2F3136)
    em1.set_image(
        url='https://cdn.discordapp.com/attachments/882408068242092062/883882671028179014/Screenshot_2021-09-04_201357.jpg')
    view=Nitro()
    await ctx.send(embed=em1, view=view)


@bot.command()
@commands.check(is_staff)
async def events1(ctx: commands.Context):
    '''Buttons for Life Science Events'''
    em1 = discord.Embed(title="What events do you want to do?",
                        description="To choose your event roles press the buttons below",
                        color=0xff008c)
    em1.set_image(url='https://cdn.discordapp.com/attachments/685035292989718554/724301857157283910/ezgif-1-a2a2e7173d80.gif')
    em1.set_footer(text="Life Science Events - Page 1 of 5")
    await ctx.send(embed=em1, view=Role1())


@bot.command()
@commands.check(is_staff)
async def events2(ctx: commands.Context):
    '''Buttons for Earth and Space Science Events'''
    em1 = discord.Embed(title="What events do you want to do?",
                        description="To choose your event roles press the buttons below",
                        color=0xff008c)
    em1.set_image(
        url='https://cdn.discordapp.com/attachments/685035292989718554/724301857157283910/ezgif-1-a2a2e7173d80.gif')
    em1.set_footer(text="Earth and Space Science Events - Page 2 of 5")
    await ctx.send(embed=em1, view=Role2())


@bot.command()
@commands.check(is_staff)
async def events3(ctx: commands.Context):
    '''Buttons for Physical Science & Chemistry Events'''
    em1 = discord.Embed(title="What events do you want to do?",
                        description="To choose your event roles press the buttons below",
                        color=0xff008c)
    em1.set_image(
        url='https://cdn.discordapp.com/attachments/685035292989718554/724301857157283910/ezgif-1-a2a2e7173d80.gif')
    em1.set_footer(text="Physical Science & Chemistry Events - Page 3 of 5")
    await ctx.send(embed=em1, view=Role3())


@bot.command()
@commands.check(is_staff)
async def events4(ctx: commands.Context):
    '''Buttons for Technology & Engineering Design Events'''
    em1 = discord.Embed(title="What events do you want to do?",
                        description="To choose your event roles press the buttons below",
                        color=0xff008c)
    em1.set_image(
        url='https://cdn.discordapp.com/attachments/685035292989718554/724301857157283910/ezgif-1-a2a2e7173d80.gif')
    em1.set_footer(text="Technology & Engineering Design Events - Page 4 of 5")
    await ctx.send(embed=em1, view=Role4())


@bot.command()
@commands.check(is_staff)
async def events5(ctx: commands.Context):
    '''Buttons for Inquiry & Nature'''
    em1 = discord.Embed(title="What events do you want to do?",
                        description="To choose your event roles press the buttons below",
                        color=0xff008c)
    em1.set_image(url='https://cdn.discordapp.com/attachments/685035292989718554/724301857157283910/ezgif-1-a2a2e7173d80.gif')
    em1.set_footer(text="Inquiry & Nature of Science Events")
    await ctx.send(embed=em1, view=Role5())


@bot.command()
@commands.check(is_staff)
async def events6(ctx: commands.Context):
    '''Buttons for All Events Role'''
    em1 = discord.Embed(title="What events do you want to do?",
                        description="Press the button below to gain access to all the event channels",
                        color=0xff008c)
    em1.set_image(url='https://cdn.discordapp.com/attachments/685035292989718554/724301857157283910/ezgif-1-a2a2e7173d80.gif')
    await ctx.send(embed=em1, view=Allevents())


@bot.command()
@commands.check(is_staff)
async def pronouns(ctx: commands.Context):
    '''Buttons for Pronoun Roles'''
    em1 = discord.Embed(title="What pronouns do you use?",
                        description="Press the buttons below to choose your pronoun role(s)",
                        color=0xff008c)
    em1.set_image(
        url='https://cdn.discordapp.com/attachments/685035292989718554/724301857157283910/ezgif-1-a2a2e7173d80.gif')
    em1.set_footer(text="Pronoun Roles")
    await ctx.send(embed=em1, view=Pronouns())


@bot.command()
@commands.check(is_staff)
async def eventroles(ctx: commands.Context):
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


@bot.command()
@commands.check(is_staff)
async def close(ctx):
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
            await bot.wait_for('message', check=check, timeout=60)
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



@bot.command()
async def google(ctx: commands.Context, *, query: str):
    """Returns a google link for a query"""
    await ctx.send(f'Google Result for: `{query}`', view=Google(query))


@bot.command()
@commands.check(is_staff)
async def addaccess(ctx,
                    role_id= commands.Option(description="Role id: allow see tickets")
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


@bot.command()
@commands.check(is_staff)
async def delaccess(ctx,
                    role_id= commands.Option(description="Role id: delete access to see tickets")
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


@bot.command()
@commands.check(is_staff)
async def addpingedrole(ctx,
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
                               description="That role already receives pings when tickets are created.", color=0x00a8ff)
            await ctx.send(embed=em)

    else:
        em = discord.Embed(title="TMS Tickets", description="Sorry, you don't have permission to run that command.",
                           color=0x00a8ff)
        await ctx.send(embed=em)


@bot.command()
@commands.check(is_staff)
async def delpingedrole(ctx,
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


@bot.command()
@commands.check(is_staff)
async def addadminrole(ctx,
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


@bot.command()
@commands.check(is_staff)
async def deladminrole(ctx,
                       role_id =commands.Option(description="Role id, delete access to admin ticket commands")):
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


@bot.command()
@commands.check(is_staff)
async def update(ctx):
    '''Sends the message containing all bot updates'''
    em5=discord.Embed(title="TMS Bot `v2.1.0` Update for 9/5/21",
                      description="", color=0xff008c)
    em5.add_field(name="Temporarily removed webhook commands",
                  value="The webhook commands have been removed as the discord.py library beta does not use the old converter",
                  inline=False)
    em5.add_field(name="Removed `/` Prefix",
                  value="The slash prefix was interacting with the discord API thinking it was a slash command",
                  inline=False)
    em5.add_field(name="New commands",
                  value="`emoji`, `charinfo`, `tictactoe`, `roll`",
                  inline=False)
    em5.add_field(name="New confirmation screen",
                  value=f"The new confirmaton screen when invoking certain commands like `selfmute` has been added",
                  inline=False)
    em5.set_thumbnail(
        url="https://cdn.discordapp.com/avatars/870741665294467082/0da0cbe08327c1081e6a055d957b3229.png?size=1024")
    em5.set_footer(text="TMS SciOly Bot Development Updates")
    await ctx.send(embed=em5)


@bot.command()
async def invite(ctx):
    '''Gives you a 1 time use invite link'''
    x = await ctx.channel.create_invite(max_uses=1)
    await ctx.send(x)


@bot.event
async def on_command_error(ctx, error):
    server = bot.get_guild(SERVER_ID)
    reports_channel = discord.utils.get(server.text_channels, name=CHANNEL_DEV)
    print("Command Error:")
    print(error)
    # Argument parsing errors
    if isinstance(error, discord.ext.commands.UnexpectedQuoteError) or isinstance(error, discord.ext.commands.InvalidEndOfQuotedStringError):
        return await ctx.send("Sorry, it appears that your quotation marks are misaligned, and I can't read your query.")
    if isinstance(error, discord.ext.commands.ExpectedClosingQuoteError):
        return await ctx.send("Oh. I was expecting you were going to close out your command with a quote somewhere, but never found it!")

    # User input errors
    if isinstance(error, discord.ext.commands.MissingRequiredArgument):
        return await ctx.send("Oops, you are missing a required argument in the command.")
    if isinstance(error, discord.ext.commands.ArgumentParsingError):
        return await ctx.send("Sorry, I had trouble parsing one of your arguments.")
    if isinstance(error, discord.ext.commands.TooManyArguments):
        return await ctx.send("Woahhh!! Too many arguments for this command!")
    if isinstance(error, discord.ext.commands.BadArgument) or isinstance(error, discord.ext.commands.BadUnionArgument):
        return await ctx.send("Sorry, I'm having trouble reading one of the arguments you just used. Try again!")

    # Check failure errors
    if isinstance(error, discord.ext.commands.CheckAnyFailure):
        return await ctx.send("It looks like you aren't able to run this command, sorry.")
    if isinstance(error, discord.ext.commands.PrivateMessageOnly):
        return await ctx.send("Pssttt. You're going to have to DM me to run this command!")
    if isinstance(error, discord.ext.commands.NoPrivateMessage):
        return await ctx.send("Ope. You can't run this command in the DM's!")
    if isinstance(error, discord.ext.commands.NotOwner):
        return await ctx.send("Oof. You have to be the bot's master to run that command!")
    if isinstance(error, discord.ext.commands.MissingPermissions) or isinstance(error, discord.ext.commands.BotMissingPermissions):
        return await ctx.send("Er, you don't have the permissions to run this command.")
    if isinstance(error, discord.ext.commands.MissingRole) or isinstance(error, discord.ext.commands.BotMissingRole):
        return await ctx.send("Oh no... you don't have the required role to run this command.")
    if isinstance(error, discord.ext.commands.MissingAnyRole) or isinstance(error, discord.ext.commands.BotMissingAnyRole):
        return await ctx.send("Oh no... you don't have the required role to run this command.")
    # Command errors
    if isinstance(error, CommandNotAllowedInChannel):
        return await ctx.send(f"You are not allowed to use this command in {error.channel.mention}.")

    if isinstance(error, discord.ext.commands.ConversionError):
        return await ctx.send('Oops, there was a bot error here, sorry about that.')

    if isinstance(error, discord.ext.commands.UserInputError):
        return await ctx.send("Hmmm... I'm having trouble reading what you're trying to tell me.")
    if isinstance(error, discord.ext.commands.CommandNotFound):
        return await ctx.send("Sorry, I couldn't find that command.")
    if isinstance(error, discord.ext.commands.CheckFailure):
        return await ctx.send("Sorry, but I don't think you can run that command.")
    if isinstance(error, discord.ext.commands.DisabledCommand):
        return await ctx.send("Sorry, but this command is disabled.")
    if isinstance(error, discord.ext.commands.CommandInvokeError):
        return await ctx.send(f'Sorry, but an error incurred when the command was invoked. \n error: {error}')
    if isinstance(error, discord.ext.commands.CommandOnCooldown):
        return await ctx.send("Slow down buster! This command's on cooldown.")
    if isinstance(error, discord.ext.commands.MaxConcurrencyReached):
        return await ctx.send("Uh oh. This command has reached MAXIMUM CONCURRENCY. *lightning flash*. Try again later.")

    # Extension errors (not doing specifics)
    if isinstance(error, discord.ext.commands.ExtensionError):
        return await ctx.send("Oh no. There's an extension error. Please ping Eric about this one.")



    # Client exception errors (not doing specifics)
    if isinstance(error, discord.ext.commands.CommandRegistrationError):
        return await ctx.send("Oh boy. Command registration error. Please ping Eric about this.")

    # Overall errors
    if isinstance(error, discord.ext.commands.CommandError):
        return await ctx.send('Oops, there was a command error. Try again.')

    if isinstance(error, discord.errors.NotFound):
        return await ctx.send('Oops, there was a channel error')

    if isinstance(error, RuntimeError):
        return await reports_channel.send('Oops, there was a runtime error')

    return


@bot.event
async def on_error(event, *args, **kwargs):
    print("Code Error:")
    print(traceback.format_exc())


@bot.event
async def on_member_join(member):
    role = discord.utils.get(member.guild.roles, name=ROLE_MR)
    join_channel = discord.utils.get(member.guild.text_channels, name=WELCOME_CHANNEL)
    await member.add_roles(role)
    await join_channel.send(f"Everyone Welcome {member.mention} to the TMS SciOly Discord, If you need any help please open a ticket or type !`help`")


async def censor(message):
    """Constructs Pi-Bot's censor."""
    channel = message.channel
    ava = message.author.avatar
    wh = await channel.create_webhook(name="Censor (Automated)")
    content = message.content
    for word in CENSORED_WORDS:
        content = re.sub(fr'\b({word})\b', "<censored>", content, flags=re.IGNORECASE)
    author = message.author.nick
    if author == None:
        author = message.author.name
    mention_perms = discord.AllowedMentions(everyone=False, users=True, roles=False)
    await wh.send(content, username=(author + " (Auto-Censor)"), avatar_url=ava, allowed_mentions=mention_perms)
    await wh.delete()


@bot.event
async def on_message(message):
    # Log DMs
    if type(message.channel) == discord.DMChannel:
        await send_to_dm_log(message)
    else:
        # Print to output
        if not (message.author.id in TMS_BOT_IDS and message.channel.name in [CHANNEL_EDITEDM,
                                                                              CHANNEL_DELETEDM,
                                                                              CHANNEL_DMLOG,
                                                                              CHANNEL_BOTSPAM,
                                                                              WELCOME_CHANNEL]):
            # avoid sending logs for messages in log channels
            print(f'Message from {message.author} in #{message.channel}: {message.content}')

    # Prevent command usage in channels outside of #bot-spam
    author = message.author
    if type(message.channel) != discord.DMChannel and message.content.startswith(BOT_PREFIX) and author.roles[-1] == discord.utils.get(author.guild.roles, name=ROLE_MR):
        if message.channel.name != CHANNEL_BOTSPAM:
            allowedCommands = ["latex", "report", "rule", "wiki", "rules", "help", "magic8ball"]
            allowed = False
            for c in allowedCommands:
                if message.content.find(BOT_PREFIX + c) != -1: allowed = True
            if not allowed:
                botspam_channel = discord.utils.get(message.guild.text_channels, name=CHANNEL_BOTSPAM)
                clarify_message = await message.channel.send(f"{author.mention}, please use bot commands only in {botspam_channel.mention}. If you have more questions, you can ping a Server Leader.")
                await asyncio.sleep(10)
                await clarify_message.delete()
                return await message.delete()

    if message.author.id in TMS_BOT_IDS:
        return
    content = message.content

    for word in CENSORED_WORDS:
        if len(re.findall(fr"\b({word})\b", content, re.I)):
            print(f"Censoring message by {message.author} because of the word: `{word}`")
            await message.delete()
            await censor(message)
    # SPAM TESTING
    global RECENT_MESSAGES
    caps = False
    u = sum(1 for c in message.content if c.isupper())
    l = sum(1 for c in message.content if c.islower())
    if u > (l + 3): caps = True
    RECENT_MESSAGES = [{"author": message.author.id,"content": message.content.lower(), "caps": caps}] + RECENT_MESSAGES[:20]
    if RECENT_MESSAGES.count({"author": message.author.id, "content": message.content.lower()}) >= 6:
        muted_role = discord.utils.get(message.author.guild.roles, name=ROLE_MUTED)
        parsed = dateparser.parse("1 hour", settings={"PREFER_DATES_FROM": "future"})
        CRON_LIST.append({"date": parsed, "do": f"unmute {message.author.id}"})
        await message.author.add_roles(muted_role)
        await message.channel.send(f"Successfully muted {message.author.mention} for 1 hour.")
        await auto_report("User was auto-muted (spam)", "red", f"A user ({str(message.author)}) was auto muted in {message.channel.mention} because of repeated spamming.")
    elif RECENT_MESSAGES.count({"author": message.author.id, "content": message.content.lower()}) >= 3:
        await message.channel.send(f"{message.author.mention}, please watch the spam. You will be muted if you do not stop.")
    # Caps checker
    elif sum(1 for m in RECENT_MESSAGES if m['author'] == message.author.id and m['caps']) > 8 and caps:
        muted_role = discord.utils.get(message.author.guild.roles, name=ROLE_MUTED)
        parsed = dateparser.parse("1 hour", settings={"PREFER_DATES_FROM": "future"})
        CRON_LIST.append({"date": parsed, "do": f"unmute {message.author.id}"})
        await message.author.add_roles(muted_role)
        await message.channel.send(f"Successfully muted {message.author.mention} for 1 hour.")
        await auto_report("User was auto-muted (caps)", "red", f"A user ({str(message.author)}) was auto muted in {message.channel.mention} because of repeated caps.")
    elif sum(1 for m in RECENT_MESSAGES if m['author'] == message.author.id and m['caps']) > 3 and caps:
        await message.channel.send(f"{message.author.mention}, please watch the caps, or else I will lay down the mute hammer!")

    if message.content.count(BOT_PREFIX) != len(message.content):
        await bot.process_commands(message)


bot.run(TOKEN)
