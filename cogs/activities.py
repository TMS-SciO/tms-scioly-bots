from __future__ import annotations

from typing import TYPE_CHECKING

import discord
from discord.ext import commands
from discord.http import Route
from utils import SERVER_ID
from discord.app_commands import command, guilds, describe

if TYPE_CHECKING:
    from bot import TMS


class Activities(commands.Cog):
    """
    Open an activity in a voice channel!
    """

    def __init__(self, bot: TMS):
        self.bot = bot

    @property
    def display_emoji(self) -> discord.PartialEmoji:
        return discord.PartialEmoji(name="\U0001f3ae")

    async def _create_invite(self, interaction: discord.Interaction, app_id: int, max_age: int, app_name: str):
        voice = interaction.user.voice
        if not voice:
            return await interaction.response.send_message("You have to be in a voice channel to use this command.")
        if not voice.channel.permissions_for(interaction.guild.me).create_instant_invite is True:
            return await interaction.response.send_message(
                "I need the `Create Invite` permission for your channel before you can use this command."
            )

        r = Route("POST", "/channels/{channel_id}/invites", channel_id=voice.channel.id)
        payload = {"max_age": max_age, "target_type": 2, "target_application_id": app_id}
        code = (await self.bot.http.request(r, json=payload))["code"]

        await interaction.response.send_message(
            embed=discord.Embed(
                description=f"[Click here to join {app_name} in {voice.channel.name}!](https://discord.gg/{code})",
                color=0x2F3136,
            ),
        )

    @command()
    @guilds(SERVER_ID)
    async def ytparty(self, ctx, invite_max_age_in_seconds=86400):
        """
        Create a YouTube Together voice channel invite.
        Use `0` for `invite_max_age_in_seconds` if you want the invite to be permanent.
        """
        app_name = "YouTube Together"
        await self._create_invite(ctx, 880218394199220334, invite_max_age_in_seconds, app_name)

    @command()
    @guilds(SERVER_ID)
    async def betrayal(self, ctx, invite_max_age_in_seconds=86400):
        """
        Create a Betrayal.io voice channel invite.
        Use `0` for `invite_max_age_in_seconds` if you want the invite to be permanent.
        """
        app_name = "the Betrayal game"
        await self._create_invite(ctx, 773336526917861400, invite_max_age_in_seconds, app_name)

    @command()
    @guilds(SERVER_ID)
    async def fishington(self, ctx, invite_max_age_in_seconds=86400):
        """
        Create a Fishington.io voice channel invite.
        Use `0` for `invite_max_age_in_seconds` if you want the invite to be permanent.
        """
        app_name = "the Fishington game"
        await self._create_invite(ctx, 814288819477020702, invite_max_age_in_seconds, app_name)

    @command()
    @guilds(SERVER_ID)
    async def chess(self, ctx, invite_max_age_in_seconds=86400):
        """
        Create a Chess in the Park voice channel invite.
        Use `0` for `invite_max_age_in_seconds` if you want the invite to be permanent.
        """
        app_name = "Chess in the Park"
        await self._create_invite(ctx, 832012774040141894, invite_max_age_in_seconds, app_name)

    @command()
    @guilds(SERVER_ID)
    async def chessdev(self, ctx, invite_max_age_in_seconds=86400):
        """
        Create a Chess in the Park voice channel invite, the dev version.
        Use `0` for `invite_max_age_in_seconds` if you want the invite to be permanent.
        """
        app_name = "Chess in the Park (Dev Version)"
        await self._create_invite(ctx, 832012586023256104, invite_max_age_in_seconds, app_name)

    @command()
    @guilds(SERVER_ID)
    async def doodlecrew(self, ctx, invite_max_age_in_seconds=86400):
        """
        Create a Doodle Crew voice channel invite.
        Use `0` for `invite_max_age_in_seconds` if you want the invite to be permanent.
        """
        app_name = "the Doodle Crew game"
        await self._create_invite(ctx, 878067389634314250, invite_max_age_in_seconds, app_name)

    @command()
    @guilds(SERVER_ID)
    async def doodlecrewdev(self, ctx, invite_max_age_in_seconds=86400):
        """
        Create a Doodle Crew voice channel invite, the dev version.
        Use `0` for `invite_max_age_in_seconds` if you want the invite to be permanent.
        """
        app_name = "the Doodle Crew game (Dev Version)"
        await self._create_invite(ctx, 878067427668275241, invite_max_age_in_seconds, app_name)

    @command()
    @guilds(SERVER_ID)
    async def lettertile(self, ctx, invite_max_age_in_seconds=86400):
        """
        Create a Letter Tile voice channel invite.
        Use `0` for `invite_max_age_in_seconds` if you want the invite to be permanent.
        """
        app_name = "the Letter Tile game"
        await self._create_invite(ctx, 879863686565621790, invite_max_age_in_seconds, app_name)

    @command()
    @guilds(SERVER_ID)
    async def wordsnacks(self, ctx, invite_max_age_in_seconds=86400):
        """
        Create a Word Snacks voice channel invite.
        Use `0` for `invite_max_age_in_seconds` if you want the invite to be permanent.
        """
        app_name = "the Word Snacks game"
        await self._create_invite(ctx, 879863976006127627, invite_max_age_in_seconds, app_name)

    @command()
    @guilds(SERVER_ID)
    async def wordsnacksdev(self, ctx, invite_max_age_in_seconds=86400):
        """
        Create a Word Snacks voice channel invite, the dev version.
        Use `0` for `invite_max_age_in_seconds` if you want the invite to be permanent.
        """
        app_name = "the Word Snacks game (Dev Version)"
        await self._create_invite(ctx, 879864010126786570, invite_max_age_in_seconds, app_name)

    @command()
    @guilds(SERVER_ID)
    async def spellcast(self, ctx, invite_max_age_in_seconds=86400):
        """
        Create a SpellCast voice channel invite.
        Use `0` for `invite_max_age_in_seconds` if you want the invite to be permanent.
        """
        app_name = "the SpellCast game"
        await self._create_invite(ctx, 852509694341283871, invite_max_age_in_seconds, app_name)

    @command()
    @guilds(SERVER_ID)
    async def checkers(self, ctx, invite_max_age_in_seconds=86400):
        """
        Create a Checkers in the Park voice channel invite.
        Use `0` for `invite_max_age_in_seconds` if you want the invite to be permanent.
        """
        app_name = "Checkers in the Park"
        await self._create_invite(ctx, 832013003968348200, invite_max_age_in_seconds, app_name)

    @command()
    @guilds(SERVER_ID)
    async def sketchy(self, ctx, invite_max_age_in_seconds=86400):
        """
        Create a Sketchy Artist voice channel invite.
        Use `0` for `invite_max_age_in_seconds` if you want the invite to be permanent.
        """
        app_name = "the Sketchy Artist game"
        await self._create_invite(ctx, 879864070101172255, invite_max_age_in_seconds, app_name)

    @command()
    @guilds(SERVER_ID)
    async def sketchydev(self, ctx, invite_max_age_in_seconds=86400):
        """
        Create a Sketchy Artist voice channel invite, the dev version.
        Use `0` for `invite_max_age_in_seconds` if you want the invite to be permanent.
        """
        app_name = "the Sketchy Artist game (Dev Version)"
        await self._create_invite(ctx, 879864104980979792, invite_max_age_in_seconds, app_name)

    @command()
    @guilds(SERVER_ID)
    async def awkword(self, ctx, invite_max_age_in_seconds=86400):
        """
        Create a Awkword voice channel invite.
        Use `0` for `invite_max_age_in_seconds` if you want the invite to be permanent.
        """
        app_name = "the Awkword game"
        await self._create_invite(ctx, 879863881349087252, invite_max_age_in_seconds, app_name)

    @command()
    @guilds(SERVER_ID)
    async def decodersdev(self, ctx, invite_max_age_in_seconds=86400):
        """
        Create a Decoders voice channel invite, the dev version.
        Use `0` for `invite_max_age_in_seconds` if you want the invite to be permanent.
        """
        app_name = "the Decoders game (Dev Version)"
        await self._create_invite(ctx, 891001866073296967, invite_max_age_in_seconds, app_name)


async def setup(bot: TMS):
    await bot.add_cog(Activities(bot))
