from __future__ import annotations

import asyncio
from typing import Optional, Set, TYPE_CHECKING, TypeVar

import async_timeout
import discord
import slate
from discord.ext import commands

from custom import Context, embed, EmbedError, enums
from .queue import Queue
from .controller import Controller
from .searcher import Searcher

__all__ = ("Player",)

BotT = TypeVar("BotT", bound=commands.Bot)


class Player(slate.Player):
    def __init__(self, *, text_channel: discord.TextChannel) -> None:
        super().__init__()

        self.text_channel: discord.TextChannel = text_channel
        self.controller: Controller = Controller(player=self)
        self.searcher: Searcher = Searcher(player=self)
        self.queue: Queue = Queue()
        self.skip_request_ids: Set[int] = set()
        self.effects: Set[enums.Effect] = set()
        self.waiting: bool = False

    async def stop(self, *, force: bool = False) -> None:

        current = self._current
        await super().stop(force=force)
        self._current = current

    # Miscellaneous

    async def _disconnect_on_timeout(self) -> None:
        await self.text_channel.send(
            embed=embed(
                colour=discord.Colour.blurple(),
                description=f"Left {self.voice_channel.mention}, nothing was added to the queue for two minutes.",
            )
        )
        await self.disconnect()

    async def _convert_spotify_track(self, track: slate.Track) -> slate.Track | None:

        ctx: Context = track.extras["ctx"]
        search = None

        if track.isrc:
            try:
                search = await self.searcher.search(
                    track.isrc, source=slate.Source.YOUTUBE_MUSIC, ctx=ctx
                )
            except EmbedError:
                try:
                    search = await self.searcher.search(
                        track.isrc, source=slate.Source.YOUTUBE, ctx=ctx
                    )
                except EmbedError:
                    pass

        if search is None:
            try:
                search = await self.searcher.search(
                    f"{track.author} - {track.title}",
                    source=slate.Source.YOUTUBE,
                    ctx=ctx,
                )
            except EmbedError:
                pass

        return search.tracks[0] if search else None

    async def _play_next(self) -> None:

        if self.is_playing() or self.waiting:
            return
        self.waiting = True

        if self.queue.is_empty() is False:
            item = self.queue.get()
            assert item is not None

        else:
            try:
                with async_timeout.timeout(180):
                    item = await self.queue.get_wait()
            except asyncio.TimeoutError:
                await self._disconnect_on_timeout()
                return

        track = item.track

        if track.source is slate.Source.SPOTIFY:

            if not (_track := await self._convert_spotify_track(track)):
                await self.text_channel.send(
                    embed=embed(
                        colour=discord.Colour.brand_red(),
                        description=f"No YouTube tracks were found for the Spotify track "
                        f"**[{discord.utils.escape_markdown(track.title)}]({track.uri})** "
                        f"by **{discord.utils.escape_markdown(track.author or 'Unknown')}**.",
                    )
                )
                self.waiting = False
                await self._play_next()
                return

            track = _track

        await self.play(track, start_time=item.start_time)
        self.waiting = False

    # Events

    async def handle_track_start(self) -> None:

        self.bot.dispatch("dashboard_track_start", voice_client=self)

        # Update controller message.
        await self.controller.handle_track_start()

    async def handle_track_end(self, reason: enums.TrackEndReason) -> None:

        self.bot.dispatch("dashboard_track_end", voice_client=self)

        if reason is not enums.TrackEndReason.REPLACED:
            # Add current track to the queue history.
            self.queue.history.insert(0, self._current)

        # Update controller message.
        await self.controller.handle_track_end(reason)

        # Set current track to None so that is_playing()
        # returns False.
        self._current = None

        # Play the next track.
        await self._play_next()

    async def connect(
        self,
        *,
        timeout: float | None = None,
        reconnect: bool | None = None,
        self_mute: bool = False,
        self_deaf: bool = True,
    ) -> None:

        await super().connect(
            timeout=timeout,
            reconnect=reconnect,
            self_mute=self_mute,
            self_deaf=self_deaf,
        )

        self.bot.dispatch("dashboard_player_connect", voice_client=self)

    async def disconnect(self, *, force: bool = False) -> None:

        await super().disconnect(force=force)

        self.bot.dispatch("dashboard_player_disconnect", voice_client=self)
