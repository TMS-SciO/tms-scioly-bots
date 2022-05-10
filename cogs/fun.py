from __future__ import annotations

import asyncio
import datetime
import json
import random

import aiohttp
import unicodedata

import discord

import math
import io
from deep_translator import GoogleTranslator
from deep_translator.exceptions import LanguageNotSupportedException as UnsupportedLanguage
from discord import app_commands
from discord.app_commands import command, describe, guilds
from discord.ext import commands
from typing import List, TYPE_CHECKING

import mongo
from utils import (
    get_akita, get_cotondetulear, get_doggo,
    get_shiba, image_filters, GOOGLE_LANGUAGES,
    Counter, TicTacToe, is_not_blacklisted,
    SERVER_ID, STEALFISH_BAN
)

if TYPE_CHECKING:
    from bot import TMS


class Fun(commands.Cog):
    """Commands for Fun!"""

    print('Fun Cog Loaded')

    def __init__(self, bot: TMS):
        self.bot = bot
        self.fish_now = 0

    @property
    def display_emoji(self) -> discord.PartialEmoji:
        return discord.PartialEmoji(name='\U0001f973')

    async def cog_check(self, ctx) -> bool:
        return await is_not_blacklisted(ctx)

    @command()
    @guilds(SERVER_ID)
    async def roll(self, interaction: discord.Interaction):
        """Rolls a dice"""
        await interaction.response.defer(thinking=True)
        await asyncio.sleep(2)
        sayings = ['<:dice1:884113954383728730>',
                   '<:dice2:884113968493391932>',
                   '<:dice3:884113979033665556>',
                   '<:dice4:884113988596674631>',
                   '<:dice5:884114002156867635>',
                   '<:dice6:884114012281901056>'
                   ]
        response = sayings[math.floor(random.random() * len(sayings))]
        await interaction.followup.send(f"{response}")

    @command()
    @guilds(SERVER_ID)
    async def magic8ball(self, interaction: discord.Interaction, question: str):
        """Swishes a Magic8ball"""
        await asyncio.sleep(3)
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
        response = random.choice(sayings)
        await interaction.response.send_message(f"**{response}**")

    @command()
    @guilds(SERVER_ID)
    async def candy(self, interaction: discord.Interaction):
        """Feeds panda some candy!"""
        r = random.random()
        if r > 0.9:
            self.fish_now += 100
            return await interaction.response.send_message(
                f"Wow, you gave panda a super candy! Added 100 candy! Panda now has {self.fish_now} pieces of candy!")
        if r > 0.1:
            self.fish_now += 1
            return await interaction.response.send_message(
                f"You feed panda one candy. Panda now has {self.fish_now} pieces of candy!")
        if r > 0.02:
            self.fish_now += 0
            return await interaction.response.send_message(
                f"You can't find any candy... and thus can't feed panda. "
                f"Panda still has {self.fish_now} pieces of candy."
            )

    @command()
    @guilds(SERVER_ID)
    async def stealcandy(self, interaction: discord.Interaction):
        """Steals some candy from panda"""
        member = interaction.user
        r = random.random()
        if member.id in STEALFISH_BAN:
            return await interaction.response.send_message("Hey! You've been banned from stealing candy for now.")
        if r >= 0.75:
            ratio = r - 0.5
            self.fish_now = round(self.fish_now * (1 - ratio))
            per = round(ratio * 100)
            return await interaction.response.send_message(f"You stole {per}% of panda's candy!")
        if r >= 0.416:
            date = datetime.datetime.now() + datetime.timedelta(hours=1)
            STEALFISH_BAN.append(member.id)
            await mongo.insert(
                "bot", "cron",
                {
                    'type': "UNSTEALCANDYBAN",
                    'user': member.id,
                    'time': date,
                    'tag': str(member)
                }
            )
            return await interaction.response.send_message(
                f"Sorry {member.mention}, but it looks like you're going to be banned from using this command for 1 "
                f"hour!")
        if r >= 0.25:
            date = datetime.datetime.now() + datetime.timedelta(days=1)
            STEALFISH_BAN.append(member.id)
            await mongo.insert(
                "bot", "cron",
                {
                    'type': "UNSTEALCANDYBAN",
                    'user': member.id,
                    'time': date,
                    'tag': str(member)
                }
            )
            return await interaction.response.send_message(
                f"Sorry {member.mention}, but it looks like you're going to be banned from using this command for 1 day!")
        if r >= 0.01:
            return await interaction.response.send_message("Hmm, nothing happened. *crickets*")
        else:
            STEALFISH_BAN.append(member.id)
            return await interaction.response.send_message(
                "You are banned from using `/stealcandy` until the next version of TMS-Bot is released.")

    @command()
    @guilds(SERVER_ID)
    async def count(self, interaction: discord.Interaction):
        """Counts the number of members in the server"""
        guild = interaction.user.guild
        await interaction.response.send_message(f"Currently, there are `{len(guild.members)}` members in the server.")

    @command()
    @guilds(SERVER_ID)
    @describe(latex="LaTex Code")
    async def latex(self, interaction: discord.Interaction, latex: str):
        """Displays an image of an equation, uses LaTex as input"""
        print(latex)
        new_args = latex.replace(" ", r"&space;")
        print(new_args)
        await interaction.response.send_message(
            r"https://latex.codecogs.com/png.latex?\dpi{175}{\color{White}" + new_args + "}")

    @command()
    @guilds(SERVER_ID)
    async def image(self, interaction: discord.Interaction, member: discord.User, manipulate: str):
        await interaction.response.defer()
        params = {
            'image_url': member.avatar.url,
        }

        r = await self.bot.session.get(f'https://api.jeyy.xyz/image/{manipulate}', params=params)
        buf = io.BytesIO(await r.read())

        await interaction.followup.send(file=discord.File(buf, 'image.gif'))

    @image.autocomplete(name="manipulate")
    async def image_autocomplete(
            self,
            interaction: discord.Interaction,
            current: str
    ) -> List[app_commands.Choice[str]]:
        return [
            app_commands.Choice(name=filter, value=filter)
            for filter in image_filters if current.lower() in filter.lower()
        ][:25]

    @command()
    @guilds(SERVER_ID)
    async def profile(
            self, interaction: discord.Interaction, user: discord.User
    ):
        try:
            await interaction.response.send_message(f'{user.display_avatar}')
        except Exception as e:
            await interaction.response.send_message(f"Couldn't find profile: {e}")

    @command()
    @guilds(SERVER_ID)
    async def ping(self, interaction: discord.Interaction):
        """Get the bot's latency"""
        latency = round(self.bot.latency * 1000, 2)
        em = discord.Embed(
            title="Pong :ping_pong:",
            description=f":clock1: My ping is {latency} ms!",
            color=discord.Color.brand_green()
        )
        await interaction.response.send_message(embed=em)

    @command()
    @guilds(SERVER_ID)
    async def counter(self, interaction: discord.Interaction):
        """Starts a counter for pressing."""
        await interaction.response.send_message('Press!', view=Counter())

    @command()
    @guilds(SERVER_ID)
    async def tictactoe(self, interaction: discord.Interaction, to_invite: discord.Member):
        """Starts a tic-tac-toe game."""
        await interaction.response.send_message(
            f"Tic Tac Toe: {interaction.user.mention} goes first",
            view=TicTacToe(interaction.user, to_invite),
        )

    @command()
    @guilds(SERVER_ID)
    @describe(member="Who are you trying to shiba?")
    async def shiba(self, interaction: discord.Interaction, member: discord.Member):
        """Shiba-s another user"""
        async with self.bot.session as session:
            page: aiohttp.ClientResponse = await session.get("https://dog.ceo/api/breed/shiba/images/random")
        text = await page.content.read()
        text = text.decode("utf-8")
        jso = json.loads(text)
        await interaction.response.send_message(jso)
        await interaction.channel.send(f"{member.mention}, <@{interaction.user.id}> shiba-d you!!")

    @command()
    @guilds(SERVER_ID)
    @describe(member="Who are you trying to cottondetulear?")
    async def cottondetulear(self, interaction: discord.Interaction, member: discord.Member):
        """"Cottondetulear-s Another Member!\""""
        doggo = await get_cotondetulear()
        await interaction.response.send_message(doggo)
        await interaction.channel.send(f"{member.mention}, {interaction.user.mention} cottondetulear-d you!!")

    @command()
    @guilds(SERVER_ID)
    @describe(member="Who are you trying to akita?")
    async def akita(self, interaction: discord.Interaction, member: discord.Member):
        """Akita-s a user!"""
        doggo = await get_akita()
        await interaction.response.send_message(doggo)
        await interaction.channel.send(f"{member.mention}, <@{interaction.user.id}> akita-d you!!")

    @command()
    @guilds(SERVER_ID)
    @describe(member="Who are you trying to doge?")
    async def doge(self, interaction: discord.Interaction, member: discord.Member):
        """Dogeee-s someone!"""
        doggo = await get_doggo()
        await interaction.response.send_message(doggo)
        await interaction.channel.send(f"{member.mention}, <@{interaction.user.id}> dogeee-d you!!")

    @command()
    @guilds(SERVER_ID)
    async def charinfo(self, interaction: discord.Interaction, *, characters: str):
        """Shows you information about a number of characters.
        Only up to 25 characters at a time.
        """

        def to_string(c):
            digit = f'{ord(c):x}'
            name = unicodedata.name(c, 'Name not found.')
            return f'`\\U{digit:>08}`: {name} - {c} \N{EM DASH} <http://www.fileformat.info/info/unicode/char/{digit}>'

        msg = '\n'.join(map(to_string, characters))
        if len(msg) > 2000:
            return await interaction.response.send_message('Output too long to display.')
        await interaction.response.send_message(msg)

    @command()
    @guilds(SERVER_ID)
    async def translate(self, interaction: discord.Interaction, language: str, *, input: str):
        try:
            translator = GoogleTranslator(source='auto', target=language.lower())
            translated = translator.translate(input)
        except UnsupportedLanguage:
            return await interaction.response.send_message(
                embed=discord.Embed(title='Error Occurred', description='Please input valid language to translate to'))
        embed = discord.Embed()
        embed.add_field(name=f'Text in `{language}:`', value=translated)
        embed.set_footer(text='Please remember, that the translations can\'t be a 100% accurate')

        await interaction.response.send_message(embed=embed)

    @translate.autocomplete(name="language")
    async def translate_autocomplete(
            self, interaction: discord.Interaction, current: str
    ) -> List[app_commands.Choice[str]]:
        return [
            app_commands.Choice(name=lang, value=lang)
            for lang in GOOGLE_LANGUAGES if current.lower() in lang.lower()
        ][:25]


async def setup(bot: TMS):
    await bot.add_cog(Fun(bot))
