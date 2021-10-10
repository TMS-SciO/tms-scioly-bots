from discord.ext import commands
import discord
from utils.variables import *
from utils.views import TicTacToe, Counter, Google
from utils.doggo import get_doggo, get_shiba, get_akita, get_cotondetulear
import asyncio
import random
import math
import dateparser
import wikipedia as wikip
from aioify import aioify
import unicodedata

aiowikip = aioify(obj=wikip)


class FunCommands(commands.Cog):
    """Fun related commands."""
    print('FunCommands Cog Loaded')

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def roll(self, ctx):
        '''Rolls a dice'''
        await ctx.channel.trigger_typing()
        msg = await ctx.send("<a:typing:883864406537162793> Rolling a dice...")
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

    @commands.command()
    async def magic8ball(self, ctx, question):
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
        response = sayings[math.floor(random.random() * len(sayings))]
        await msg.edit(f"**{response}**")

    @commands.command()
    async def candy(self, ctx):
        '''Feeds panda some candy!'''
        global fish_now
        r = random.random()

        if len(str(fish_now)) > 1500:
            fish_now = round(pow(fish_now, 0.5))
            if fish_now == 69: fish_now = 70
            return await ctx.send(
                "Woah! Panda's amount of candy is a little too much, so it unfortunately has to be square rooted.")
        if r > 0.9:
            fish_now += 100

            if fish_now == 69: fish_now = 70
            return await ctx.send(
                f"Wow, you gave panda a super candy! Added 100 candy! Panda now has {fish_now} pieces of candy!")
        if r > 0.1:
            fish_now += 1
            if fish_now == 69:
                fish_now = 70
                return await ctx.send(f"You feed panda two candy. Panda now has {fish_now} pieces of candy!")
            else:
                return await ctx.send(f"You feed panda one candy. Panda now has {fish_now} pieces of candy!")
        if r > 0.02:
            fish_now += 0
            return await ctx.send(
                f"You can't find any candy... and thus can't feed panda. Panda still has {fish_now} pieces of candy.")
        else:
            fish_now = round(pow(fish_now, 0.5))
            if fish_now == 69: fish_now = 70
            return await ctx.send(
                f":sob:\n:sob:\n:sob:\nAww, panda's candy was accidentally square root'ed. Panda now has {fish_now} pieces of candy. \n:sob:\n:sob:\n:sob:")

    @commands.command()
    async def stealcandy(self, ctx):
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
            return await ctx.send(
                f"Sorry {member.mention}, but it looks like you're going to be banned from using this command for 1 hour!")
        if r >= 0.25:
            parsed = dateparser.parse("1 day", settings={"PREFER_DATES_FROM": "future"})
            STEALFISH_BAN.append(member.id)
            CRON_LIST.append({"date": parsed, "do": f"unstealfishban {member.id}"})
            return await ctx.send(
                f"Sorry {member.mention}, but it looks like you're going to be banned from using this command for 1 day!")
        if r >= 0.01:
            return await ctx.send("Hmm, nothing happened. *crickets*")
        else:
            STEALFISH_BAN.append(member.id)
            return await ctx.send(
                "You are banned from using `!stealcandy` until the next version of TMS-Bot is released.")

    @commands.command()
    async def count(self, ctx):
        '''Counts the number of members in the server'''
        guild = ctx.message.author.guild
        await ctx.send(f"Currently, there are `{len(guild.members)}` members in the server.")

    @commands.command()
    async def latex(self,
                    ctx,
                    latex):
        '''Displays an image of an equation, uses LaTex as input'''

        print(latex)
        new_args = latex.replace(" ", r"&space;")
        print(new_args)
        await ctx.send(r"https://latex.codecogs.com/png.latex?\dpi{175}{\color{White}" + new_args + "}")

    @commands.command()
    async def profile(self,
                      ctx,
                      user: discord.User = commands.Option(description="The user you want")
                      ):

        if user is None:
            avatar = ctx.author.avatar
            await ctx.send(f'{avatar}')
        else:
            try:
                await ctx.send(f'{user.avatar}')
            except Exception as e:
                await ctx.send(f"Couldn't find profile: {e}")

    @commands.command()
    async def grade(self,
                    ctx,
                    a: float = commands.Option(description="Your points"),
                    b: float = commands.Option(description="Total points")
                    ):
        '''Returns a percentage/grade'''
        x = a / b
        z = x * 100
        if z < 60:
            await ctx.send(f'{round(z, 2)}% F')
        elif 60 <= z < 70:
            await ctx.send(f'{round(z, 2)}% D')
        elif 70 <= z < 80:
            await ctx.send(f'{round(z, 2)}% C')
        elif 80 <= z < 90:
            await ctx.send(f'{round(z, 2)}% B')
        elif 90 <= z < 93:
            await ctx.send(f'{round(z, 2)}% A-')
        elif 93 <= z < 97:
            await ctx.send(f'{round(z, 2)}% A')
        elif 97 <= z <= 100:
            await ctx.send(f'{round(z, 2)}% A+')
        elif z > 100:
            await ctx.send(f"{round(z, 2)}% A++ must've gotten extra credit")

    @commands.command()
    async def ping(self, ctx):
        '''Get the bot's latency'''
        latency = round(self.bot.latency * 1000, 2)
        em = discord.Embed(title="Pong :ping_pong:",
                           description=f":clock1: My ping is {latency} ms!",
                           color=0x16F22C)
        await ctx.reply(embed=em, mention_author=False)

    @commands.command()
    async def counter(self, ctx: commands.Context):
        """Starts a counter for pressing."""
        await ctx.send('Press!', view=Counter())

    @commands.command()
    async def wikipedia(self, ctx,
                        request=commands.Option(default=None, description="Action, like summary or search"),
                        page=commands.Option(description="What page you want!")
                        ):
        '''Get a wikipedia page or summary!'''
        term = page
        if request is None:
            return await ctx.send(
                "You must specifiy a command and keyword, such as `/wikipedia search \"Science Olympiad\"`")
        if request == "search":
            return await ctx.send("\n".join([f"`{result}`" for result in aiowikip.search(term, results=5)]))
        elif request == "summary":
            try:
                term = term.title()
                page = await aiowikip.page(term)
                return await ctx.send(
                    aiowikip.summary(term, sentences=3) + f"\n\nRead more on Wikipedia here: <{page.url}>!")
            except wikip.exceptions.DisambiguationError as e:
                return await ctx.send(
                    f"Sorry, the `{term}` term could refer to multiple pages, try again using one of these terms:" + "\n".join(
                        [f"`{o}`" for o in e.options]))
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

    @commands.command()
    async def tictactoe(self, ctx: commands.Context):
        """Starts a tic-tac-toe game."""
        await ctx.send('Tic Tac Toe: X goes first', view=TicTacToe())

    @commands.command()
    async def shiba(self, ctx,
                    member: discord.Member = commands.Option(description="Who are you trying to shiba?")
                    ):
        """Shiba bombs a user!"""
        if member is None:
            return await ctx.send("Tell me who you want to shiba!! :dog:")
        else:
            doggo = await get_shiba()
            await ctx.send(doggo)
            await ctx.send(f"{member.mention}, <@{ctx.message.author.id}> shiba-d you!!")

    @commands.command()
    async def cottondetulear(self, ctx,
                             member: discord.Member = commands.Option(
                                 description="Who are you trying to cottondetulear?")
                             ):
        """Cottondetulear-s Another Member!"""
        if member is None:
            return await ctx.send("Tell me who you want to cottondetulear!! :dog:")
        else:
            doggo = await get_cotondetulear()
            await ctx.send(doggo)
            await ctx.send(f"{member.mention}, {ctx.message.author.mention} cottondetulear-d you!!")

    @commands.command()
    async def akita(self, ctx,
                    member: discord.User = commands.Option(description="Who are you trying to akita?")
                    ):
        """Akita-s a user!"""
        if member is None:
            return await ctx.send("Tell me who you want to akita!! :dog:")
        else:
            doggo = await get_akita()
            await ctx.send(doggo)
            await ctx.send(f"{member.mention}, <@{ctx.message.author.id}> akita-d you!!")

    @commands.command()
    async def doge(self, ctx,
                   member: discord.Member = commands.Option(description="Who are you trying to doge?")
                   ):
        """Dogeee-s someone!"""
        if member is None:
            return await ctx.send("Tell me who you want to dogeeee!! :dog:")
        else:
            doggo = await get_doggo()
            await ctx.send(doggo)
            await ctx.send(f"{member.mention}, <@{ctx.message.author.id}> dogeee-d you!!")

    @commands.command()
    async def charinfo(self, ctx,
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

    @commands.command()
    async def emoji(self, ctx,
                    custom_emojis: commands.Greedy[discord.PartialEmoji] = commands.Option(
                        description="Your Custom Emoji")
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

    @commands.command()
    async def google(self, ctx: commands.Context, *, query: str):
        """Returns a google link for a query"""
        await ctx.send(f'Google Result for: `{query}`', view=Google(query))


def setup(bot):
    bot.add_cog(FunCommands(bot))
