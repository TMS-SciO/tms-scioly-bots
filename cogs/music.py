from __future__ import annotations

import datetime
import math
from typing import Literal, Optional, TYPE_CHECKING

import discord
import slate
from discord.ext import commands
from voice import checks, utilities, Player as Player_
from custom import exceptions, Context, embed, converter

if TYPE_CHECKING:
    from bot import TMS


class Player(commands.Cog):
    """
    Player control commands.
    """

    def __init__(self, bot: TMS) -> None:
        self.bot: TMS = bot

    def cog_check(self, ctx: Context) -> bool:

        if not ctx.guild:
            return False
        return True

    @staticmethod
    async def _ensure_connected(ctx: Context) -> None:

        assert isinstance(ctx.author, discord.Member)

        author_voice_channel = ctx.author.voice and ctx.author.voice.channel
        bot_voice_channel = ctx.player and ctx.player.voice_channel

        if (author_voice_channel and bot_voice_channel) and (
            author_voice_channel == bot_voice_channel
        ):
            return

        if (not author_voice_channel and bot_voice_channel) or (
            author_voice_channel and bot_voice_channel
        ):
            raise exceptions.EmbedError(
                description=f"You must be connected to {bot_voice_channel.mention} to use this command."
            )
        if not author_voice_channel:
            raise exceptions.EmbedError(
                description="You must be connected to a voice channel to use this command."
            )

        # slate doesn't like this for some reason, investigate later.
        await author_voice_channel.connect(cls=Player_(text_channel=ctx.channel))

    @commands.hybrid_command(name="connect", aliases=["join", "summon"])
    async def _connect(self, ctx: Context) -> None:
        """
        Connects the bot to your voice channel.
        """

        assert isinstance(ctx.author, discord.Member)

        if not ctx.author.voice or not ctx.author.voice.channel:
            raise exceptions.EmbedError(
                description="You must be connected to a voice channel to use this command."
            )

        if ctx.player and ctx.player.voice_channel:
            raise exceptions.EmbedError(
                description=f"I'm already connected to {ctx.player.voice_channel.mention}."
            )

        # slate doesn't like this for some reason, investigate later.
        await ctx.author.voice.channel.connect(cls=Player_(text_channel=ctx.channel))  # type: ignore
        await ctx.send(
            embed=embed(
                colour=discord.Color.brand_green(),
                description=f"Connected to {ctx.author.voice.channel}.",
            )
        )

    @commands.hybrid_command(name="disconnect", aliases=["dc", "leave", "destroy"])
    @checks.is_author_connected()
    @checks.is_player_connected()
    async def _disconnect(self, ctx: Context) -> None:
        """
        Disconnects the bot from its voice channel.
        """

        assert ctx.player is not None

        await ctx.send(
            embed=embed(
                colour=discord.Color.brand_green(),
                description=f"Disconnected from {ctx.player.voice_channel.mention}.",
            )
        )
        await ctx.player.disconnect()

    # Pausing

    @commands.hybrid_command(name="pause", aliases=["stop"])
    @checks.is_author_connected()
    @checks.is_player_connected()
    async def _pause(self, ctx: Context) -> None:
        """
        Pauses the player.
        """

        assert ctx.player is not None

        if ctx.player.paused is True:
            raise exceptions.EmbedError(description="The player is already paused.")

        await ctx.player.set_pause(True)
        await ctx.reply(
            embed=embed(
                colour=discord.Color.brand_green(), description="Paused the player."
            )
        )

    @commands.hybrid_command(name="resume", aliases=["continue", "unpause"])
    @checks.is_author_connected()
    @checks.is_player_connected()
    async def _resume(self, ctx: Context) -> None:
        """
        Resumes the player.
        """

        assert ctx.player is not None

        if ctx.player.paused is False:
            await ctx.reply("The player is already playing.")
            return

        await ctx.player.set_pause(False)
        await ctx.reply(
            embed=embed(
                colour=discord.Color.brand_green(), description="Resumed the player."
            )
        )

    # Seeking

    _TIME_CONVERTER = commands.parameter(converter=converter.TimeConverter)

    @commands.hybrid_command(name="seek", aliases=["scrub"])
    @checks.is_track_seekable()
    @checks.is_player_playing()
    @checks.is_author_connected()
    @checks.is_player_connected()
    async def _seek(self, ctx: Context, *, position: int = _TIME_CONVERTER) -> None:
        """
        Seeks to a position in the current track.
        **Arguments:**
        ● `position`: The position to seek to. Can be in any of the following formats:
        - `ss`
        - `mm:ss`
        - `hh:mm:ss`
        - `30s`
        - `1m30s`
        - `1h30m`
        - `1h30m30s`
        - `1 hour 30 minutes 30 seconds`
        - `1 hour, 30 minutes, 30 seconds`
        - `1 hour and 30 minutes and 30 seconds`
        - etc, most permutations of these will work.
        """

        assert ctx.player is not None
        assert ctx.player.current is not None

        milliseconds = position * 1000

        if 0 < milliseconds > ctx.player.current.length:
            raise exceptions.EmbedError(
                description=f"**{utilities.format_seconds(position, friendly=True)}** is not a valid position, the "
                f"current track is only "
                f"**{utilities.format_seconds(ctx.player.current.length // 1000, friendly=True)}** "
                f"long.",
            )

        await ctx.player.set_position(milliseconds)
        await ctx.reply(
            embed=embed(
                colour=discord.Color.brand_green(),
                description=f"Set the players position to "
                f"**{utilities.format_seconds(milliseconds // 1000, friendly=True)}**.",
            )
        )

    @commands.hybrid_command(
        name="fast-forward",
        aliases=["fast_forward", "fastforward", "ff", "forward", "fwd"],
    )
    @checks.is_track_seekable()
    @checks.is_player_playing()
    @checks.is_author_connected()
    @checks.is_player_connected()
    async def _fast_forward(self, ctx: Context, *, time: int = _TIME_CONVERTER) -> None:
        """
        Fast-forwards the current track by an amount of time.
        **Arguments:**
        ● `time`: The amount of time to fast-forward by. Can be in any of the following formats:
        - `ss`
        - `mm:ss`
        - `hh:mm:ss`
        - `30s`
        - `1m30s`
        - `1h30m`
        - `1h30m30s`
        - `1 hour 30 minutes 30 seconds`
        - `1 hour, 30 minutes, 30 seconds`
        - `1 hour and 30 minutes and 30 seconds`
        - etc, most permutations of these will work.
        """

        assert ctx.player is not None
        assert ctx.player.current is not None

        milliseconds = time * 1000
        position = ctx.player.position
        remaining = ctx.player.current.length - position

        formatted = utilities.format_seconds(time, friendly=True)

        if milliseconds >= remaining:
            raise exceptions.EmbedError(
                description=f"**{formatted}** is too much time to fast forward, the current track only has "
                f"**{utilities.format_seconds(remaining // 1000, friendly=True)}** remaining."
            )

        await ctx.player.set_position(position + milliseconds)
        await ctx.reply(
            embed=embed(
                colour=discord.Color.brand_green(),
                description=f"Fast-forwarding by **{formatted}**, the players position is now "
                f"**{utilities.format_seconds((position + milliseconds) // 1000, friendly=True)}**.",
            )
        )

    @commands.hybrid_command(name="rewind", aliases=["rwd", "backward", "bwd"])
    @checks.is_track_seekable()
    @checks.is_player_playing()
    @checks.is_author_connected()
    @checks.is_player_connected()
    async def _rewind(self, ctx: Context, *, time: int = _TIME_CONVERTER) -> None:
        """
        Rewinds the current track by an amount of time.
        **Arguments:**
        ● `time`: The amount of time to rewind by. Can be in any of the following formats:
        - `ss`
        - `mm:ss`
        - `hh:mm:ss`
        - `30s`
        - `1m30s`
        - `1h30m`
        - `1h30m30s`
        - `1 hour 30 minutes 30 seconds`
        - `1 hour, 30 minutes, 30 seconds`
        - `1 hour and 30 minutes and 30 seconds`
        - etc, most permutations of these will work.
        """

        assert ctx.player is not None
        assert ctx.player.current is not None

        milliseconds = time * 1000
        position = ctx.player.position

        formatted = utilities.format_seconds(time, friendly=True)

        if milliseconds >= position:
            raise exceptions.EmbedError(
                description=f"**{formatted}** is too much time to rewind, only "
                f"**{utilities.format_seconds(position // 1000, friendly=True)}** of the current track "
                f"has passed."
            )

        await ctx.player.set_position(position - milliseconds)
        await ctx.reply(
            embed=embed(
                colour=discord.Color.brand_green(),
                description=f"Rewinding by **{formatted}**, the players position is now "
                f"**{utilities.format_seconds((position - milliseconds) // 1000, friendly=True)}**.",
            )
        )

    @commands.hybrid_command(name="replay", aliases=["restart"])
    @checks.is_track_seekable()
    @checks.is_player_playing()
    @checks.is_author_connected()
    @checks.is_player_connected()
    async def _replay(self, ctx: Context) -> None:
        """
        Replays the current track.
        """

        assert ctx.player is not None
        assert ctx.player.current is not None

        await ctx.player.set_position(0)
        await ctx.reply(
            embed=embed(
                colour=discord.Color.brand_green(),
                description="Replaying the current track.",
            )
        )

    # Now playing

    @commands.hybrid_command(
        name="now-playing", aliases=["now_playing", "nowplaying", "np"]
    )
    @checks.is_player_playing()
    @checks.is_player_connected()
    async def _now_playing(self, ctx: Context) -> None:
        """
        Shows the current track.
        """

        assert ctx.player is not None

        kwargs = await ctx.player.controller.build_message()
        await ctx.send(**kwargs)

    # Skipping

    @staticmethod
    async def _check_force_skip_permissions(ctx: Context) -> None:

        _checks = [
            checks.is_bot_owner(),
            checks.is_guild_owner(),
            checks.has_any_permission(
                manage_channels=True,
                manage_roles=True,
                manage_guild=True,
                kick_members=True,
                ban_members=True,
                administrator=True,
            ),
        ]

        assert ctx.guild is not None
        try:
            await commands.check_any(*_checks).predicate(ctx=ctx)
        except (commands.CheckAnyFailure, commands.MissingRole):
            raise exceptions.EmbedError(
                description="You don't have permission to force skip."
            )

    @commands.hybrid_command(
        name="force-skip", aliases=["force_skip", "forceskip", "fs", "skipto"]
    )
    @checks.is_player_playing()
    @checks.is_author_connected()
    @checks.is_player_connected()
    async def _force_skip(self, ctx: Context, amount: int = 0) -> None:
        """
        Force skips tracks in the queue.
        **Arguments:**
        ● `amount`: An optional amount of tracks to skip, defaults to 1.
        **Note:**
        You can only use this command if you meet one (or more) of the following requirements:
        - You are the owner of the bot.
        - You are the owner of this server.
        - You have the `Manage Channels`, `Manage Roles`, `Manage Guild`, `Kick Members`, `Ban Members`, or `Administrator` permissions.
        - You have the servers DJ role.
        """

        await self._check_force_skip_permissions(ctx)

        assert ctx.player is not None

        if amount:
            if 0 <= amount > len(ctx.player.queue) + 1:
                raise exceptions.EmbedError(
                    description=f"**{amount}** is not a valid amount of tracks to skip, there are only"
                    f"**{len(ctx.player.queue) + 1}** tracks in the queue."
                )
            del ctx.player.queue.items[: amount - 1]

        await ctx.player.stop()
        await ctx.reply(
            embed=embed(
                colour=discord.Color.brand_green(),
                description=f"Skipped **{amount or 1}** {utilities.pluralize('track', amount)}.",
            )
        )

        ctx.player.skip_request_ids.clear()

    @commands.hybrid_command(
        name="skip", aliases=["vote-skip", "vote_skip", "voteskip", "vs"]
    )
    @checks.is_player_playing()
    @checks.is_author_connected()
    @checks.is_player_connected()
    async def _skip(self, ctx: Context) -> None:
        """
        Starts a vote-skip for the current track.
        **Note:**
        If you meet one or more of the following conditions, the track will be force skipped:
        - You are the owner of the bot.
        - You are the owner of this server.
        - You have the `Manage Channels`, `Manage Roles`, `Manage Guild`, `Kick Members`, `Ban Members`, or `Administrator` permissions.
        - You have the servers DJ role.
        - You are the requester of the current track.
        """

        assert ctx.player is not None
        assert ctx.player.current is not None

        try:
            await self._check_force_skip_permissions(ctx)
            await self._force_skip(ctx, amount=0)
            return
        except exceptions.EmbedError:
            pass

        if ctx.author not in ctx.player.listeners:
            raise exceptions.EmbedError(
                description="You can't vote to skip because you are currently deafened."
            )

        async def skip() -> None:

            assert ctx.player is not None

            await ctx.player.stop()
            await ctx.reply(
                embed=embed(
                    colour=discord.Color.brand_green(),
                    description="Skipped the current track.",
                )
            )
            ctx.player.skip_request_ids.clear()

        if ctx.author.id == ctx.player.current.extras["ctx"].author.id:
            await skip()
            return

        if ctx.author.id in ctx.player.skip_request_ids:

            ctx.player.skip_request_ids.remove(ctx.author.id)
            await ctx.reply(
                embed=embed(
                    colour=discord.Color.brand_green(),
                    description="Removed your vote to skip.",
                )
            )
            return

        skips_needed = math.floor(75 * len(ctx.player.listeners) / 100)

        if (
            len(ctx.player.listeners) < 3
            or (len(ctx.player.skip_request_ids) + 1) >= skips_needed
        ):
            await skip()
            return

        ctx.player.skip_request_ids.add(ctx.author.id)
        await ctx.reply(
            embed=embed(
                colour=discord.Color.brand_green(),
                description=f"Added your vote to skip, now at "
                f"**{len(ctx.player.skip_request_ids)}** out of **{skips_needed}** votes.",
            )
        )

    @commands.command(name="lyrics")
    async def lyrics(self, ctx: Context, *, query: Optional[str]) -> None:
        """
        Searches for lyrics.
        **Arguments:**
        `query`: The query to search for lyrics with.
        If `query` matches `spotify`, the lyric search will be performed with your current spotify track, if you are currently listening to one.
        If `query` matches `player`, the lyric search will be performed with the players current track, if there is one.
        """

        def get_spotify_query() -> str | None:
            assert isinstance(ctx.author, discord.Member)

            if not (
                activity := discord.utils.find(
                    lambda x: isinstance(x, discord.Spotify), ctx.author.activities
                )
            ):
                return None

            assert isinstance(activity, discord.Spotify)
            return f"{activity.artists[0]} - {activity.title}"

    @commands.command(name="sync")
    async def sync(self, ctx: Context) -> None:

        assert isinstance(ctx.author, discord.Member)

        if not (
            activity := discord.utils.find(
                lambda x: isinstance(x, discord.Spotify), ctx.author.activities
            )
        ):
            raise exceptions.EmbedError(
                description="You dont have an active spotify status."
            )

        assert isinstance(activity, discord.Spotify)

        await self._ensure_connected(ctx)

        assert ctx.player is not None
        await ctx.player.searcher.queue(
            activity.track_url,
            source=slate.Source.YOUTUBE,
            ctx=ctx,
            play_now=True,
            start_time=(
                datetime.datetime.now(tz=datetime.timezone.utc) - activity.start
            ).seconds
            * 1000,
        )


async def setup(bot: TMS):
    await bot.add_cog(Player(bot))
