from __future__ import annotations

from discord.ext import commands
import re
import discord
from typing import Dict, List, TYPE_CHECKING
import mongo

if TYPE_CHECKING:
    from bot import TMS


CENSORED: Dict[str, List[str]] = {}


class Censor(commands.Cog):
    def __init__(self, bot: TMS):
        self.bot = bot

    print("Censor Cog Loaded")

    @commands.Cog.listener("on_ready")
    async def on_ready(self) -> None:

        global CENSORED
        CENSORED = await mongo.get_censor()

    @staticmethod
    def censor_needed(content: str) -> bool:
        """
        Determines whether the message has content that needs to be censored.
        """

        global CENSORED

        for word in CENSORED["words"]:
            if len(re.findall(rf"\b({word})\b", content, re.I)):
                return True
        return False

    @staticmethod
    async def censor(message: discord.Message):
        """Constructs TMS Bot's censor."""

        global CENSORED

        channel = message.channel
        ava = message.author.avatar
        wh = await channel.create_webhook(name="Censor (Automated)")
        content = message.content
        for word in CENSORED["words"]:
            content = re.sub(
                rf"\b({word})\b", "<censored>", content, flags=re.IGNORECASE
            )
        author_nickname = message.author.nick
        if author_nickname is None:
            author_nickname = message.author.name
        # Make sure pinging through @everyone, @here, or any role can not happen
        mention_perms = discord.AllowedMentions(everyone=False, users=True, roles=False)
        await wh.send(
            content,
            username=(author_nickname + " (Auto-Censor)"),
            avatar_url=ava,
            allowed_mentions=mention_perms,
        )
        await wh.delete()

    async def on_message(self, message: discord.Message):
        """
        Will censor the message. Will replace any flags in content with "<censored>".
        :param message: The message being checked. message.context will be modified
        if censor gets triggered if and only if the author is not a staff member.
        :type message: discord.Message
        """
        # if message.author.id == 817169150983012412:
        #     await message.delete()
        #     await message.channel.send(message.content[::-1])

        global CENSORED

        print(f"Message in {message.channel} from {message.author}: {message.content}")
        if message.author.bot:
            return
        if message.author.discriminator == "0000":
            return
        content = message.content
        for word in CENSORED["words"]:
            if len(re.findall(rf"\b({word})\b", content, re.I)):
                print(
                    f"Censoring message by {message.author} because of the word: `{word}`"
                )
                await message.delete()
                return await self.censor(message)


async def setup(bot: TMS):
    await bot.add_cog(Censor(bot))
