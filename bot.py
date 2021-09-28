import discord
from discord.ext import commands, tasks
from embed import assemble_embed
from commanderr import CommandNotAllowedInChannel
from views import Counter, HelpButtons, paginationList, Ticket, TicTacToe, Close, Role1, Role2, Role3, Role4, Role5, Pronouns, Allevents, Google
from doggo import get_doggo, get_akita, get_shiba, get_cotondetulear
from censor import CENSORED_WORDS
from checks import is_staff
from globalfunctions import auto_report
from rules import RULES
from secret import TOKEN
from variables import *
import random
import os
import math
import datetime
import dateparser
import wikipedia as wikip
from aioify import aioify
import traceback
import re
import inspect
import asyncio
import unicodedata

intents = discord.Intents.all()

aiowikip = aioify(obj=wikip)


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
            await auto_report(bot ,"Error with a cron task", "red", f"Error: `{string}`")
    except Exception as e:
        await auto_report(bot, "Error with a cron task", "red", f"Error: `{e}`\nOriginal task: `{string}`")


@bot.command()
async def help(ctx: commands.Context):
    '''Sends a menu with all the commands'''
    current = 0
    view = HelpButtons(ctx, current)
    await ctx.send(embed=paginationList[current], view=view)


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
            await auto_report(bot, "Innapropriate Username Detected", "red", f"A member ({str(after)}) has updated their nickname to **{after.nick}**, which the censor caught as innapropriate.")


@bot.command()
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
async def count(ctx):
    '''Counts the number of members in the server'''
    guild = ctx.message.author.guild
    await ctx.send(f"Currently, there are `{len(guild.members)}` members in the server.")


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
async def ping(ctx):
    '''Get the bot's latency'''
    latency = round(bot.latency * 1000, 2)
    em = discord.Embed(title="Pong :ping_pong:",
                     description=f":clock1: My ping is {latency} ms!",
                     color=0x16F22C)
    await ctx.reply(embed=em, mention_author=False)


@bot.command()
async def counter(ctx: commands.Context):
    """Starts a counter for pressing."""
    await ctx.send('Press!', view=Counter())


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

    staff_member = await is_staff(bot, ctx)
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
async def google(ctx: commands.Context, *, query: str):
    """Returns a google link for a query"""
    await ctx.send(f'Google Result for: `{query}`', view=Google(query))


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
        await auto_report(bot, "User was auto-muted (spam)", "red", f"A user ({str(message.author)}) was auto muted in {message.channel.mention} because of repeated spamming.")
    elif RECENT_MESSAGES.count({"author": message.author.id, "content": message.content.lower()}) >= 3:
        await message.channel.send(f"{message.author.mention}, please watch the spam. You will be muted if you do not stop.")
    # Caps checker
    elif sum(1 for m in RECENT_MESSAGES if m['author'] == message.author.id and m['caps']) > 8 and caps:
        muted_role = discord.utils.get(message.author.guild.roles, name=ROLE_MUTED)
        parsed = dateparser.parse("1 hour", settings={"PREFER_DATES_FROM": "future"})
        CRON_LIST.append({"date": parsed, "do": f"unmute {message.author.id}"})
        await message.author.add_roles(muted_role)
        await message.channel.send(f"Successfully muted {message.author.mention} for 1 hour.")
        await auto_report(bot, "User was auto-muted (caps)", "red", f"A user ({str(message.author)}) was auto muted in {message.channel.mention} because of repeated caps.")
    elif sum(1 for m in RECENT_MESSAGES if m['author'] == message.author.id and m['caps']) > 3 and caps:
        await message.channel.send(f"{message.author.mention}, please watch the caps, or else I will lay down the mute hammer!")

    if message.content.count(BOT_PREFIX) != len(message.content):
        await bot.process_commands(message)

bot.load_extension('mod')
bot.run(TOKEN)
