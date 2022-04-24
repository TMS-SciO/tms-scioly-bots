from __future__ import annotations

from typing import Literal, TYPE_CHECKING

import discord
import slate
from discord.ext import commands

from custom import Context
import voice
from voice import checks

if TYPE_CHECKING:
    from bot import TMS


class Play(commands.Cog):
    """
    Various platform-specific play commands.
    """

    def __init__(self, bot: TMS) -> None:
        self.bot: TMS = bot

    def cog_check(self, ctx: Context) -> Literal[True]:

        if not ctx.guild:
            raise commands.NoPrivateMessage()

        return True

    @staticmethod
    async def _ensure_connected(ctx: Context) -> None:

        assert isinstance(ctx.author, discord.Member)

        author_voice_channel = ctx.author.voice and ctx.author.voice.channel
        bot_voice_channel = ctx.voice_client and ctx.voice_client.voice_channel

        if (author_voice_channel and bot_voice_channel) and (author_voice_channel == bot_voice_channel):
            return

        if (not author_voice_channel and bot_voice_channel) or (author_voice_channel and bot_voice_channel):
            await ctx.reply(f"You must be connected to {bot_voice_channel.mention} to use this command.")
            return
        if not author_voice_channel:
            await ctx.reply("You must be connected to a voice channel to use this command.")
            return

        # slate doesn't like this for some reason, investigate later.
        await author_voice_channel.connect(cls=voice.Player(text_channel=ctx.channel))  # type: ignore

    # Play

    @commands.hybrid_command(name="play", aliases=["p"])
    async def play(self, ctx: Context, *, query: str) -> None:
        """
        Searches for and adds a track to the queue.
        **Arguments:**
        ● `query`: The track to search for. Can be a URL or search query.
        **Note:**
        This command supports all sources providing you use a direct URL. When using a search query with this command you will always get a YouTube track.
        """

        await self._ensure_connected(ctx)

        await ctx.voice_client.searcher.queue(query, source=slate.Source.YOUTUBE, ctx=ctx)

    @commands.hybrid_command(name="play-next", aliases=["play_next", "playnext", "pne"])
    async def play_next(self, ctx: Context, *, query: str) -> None:
        """
        Searches for and adds a track to the start of the queue.
        **Arguments:**
        ● `query`: The track to search for. Can be a URL or search query.
        **Note:**
        This command supports all sources providing you use a direct URL. When using a search query with this command you will always get a YouTube track.
        """

        await self._ensure_connected(ctx)

        await ctx.voice_client.searcher.queue(query, source=slate.Source.YOUTUBE, ctx=ctx, play_next=True)

    @commands.hybrid_command(name="play-now", aliases=["play_now", "playnow", "pno"])
    async def play_now(self, ctx: Context, *, query: str) -> None:
        """
        Searches for and plays a track immediately.
        **Arguments:**
        ● `query`: The track to search for. Can be a URL or search query.
        **Note:**
        This command supports all sources providing you use a direct URL. When using a search query with this command you will always get a YouTube track.
        """

        await self._ensure_connected(ctx)

        await ctx.voice_client.searcher.queue(query, source=slate.Source.YOUTUBE, ctx=ctx, play_now=True)

    # Search

    @commands.hybrid_command(name="search", aliases=["s"])
    async def search(self, ctx: Context, *, query: str) -> None:
        """
        Allows you to select which tracks to add to the queue.
        **Arguments:**
        ● `query`: The track to search for. Can be a URL or search query.
        **Note:**
        This command supports all sources providing you use a direct URL. When using a search query with this command you will always get a YouTube track.
        """

        await self._ensure_connected(ctx)

        await ctx.voice_client.searcher.select(query, source=slate.Source.YOUTUBE, ctx=ctx)

    @commands.hybrid_command(name="search-next", aliases=["search_next", "searchnext", "sne"])
    async def search_next(self, ctx: Context, *, query: str) -> None:
        """
        Allows you to select which tracks to add to the start of the queue.
        **Arguments:**
        ● `query`: The track to search for. Can be a URL or search query.
        **Note:**
        This command supports all sources providing you use a direct URL. When using a search query with this command you will always get a YouTube track.
        """

        await self._ensure_connected(ctx)
        await ctx.voice_client.searcher.select(query, source=slate.Source.YOUTUBE, ctx=ctx, play_next=True)

    @commands.hybrid_command(name="search-now", aliases=["search_now", "searchnow", "sno"])
    async def search_now(self, ctx: Context, *, query: str) -> None:
        """
        Allows you to select which tracks to play immediately.
        **Arguments:**
        ● `query`: The track to search for. Can be a URL or search query.
        **Note:**
        This command supports all sources providing you use a direct URL. When using a search query with this command you will always get a YouTube track.
        """

        await self._ensure_connected(ctx)

        await ctx.voice_client.searcher.select(query, source=slate.Source.YOUTUBE, ctx=ctx, play_now=True)

    # Youtube

    @commands.hybrid_command(name="youtube", aliases=["yt"])
    async def youtube(self, ctx: Context, *, query: str) -> None:
        """
        Searches for tracks from YouTube to add to the queue.
        **Arguments:**
        ● `query`: The track to search for. Can be a URL or search query.
        """
        await self.play(ctx, query=query)

    @commands.command(name="youtube-next", aliases=["youtube_next", "youtubenext", "ytne"], hidden=True)
    async def youtube_next(self, ctx: Context, *, query: str) -> None:
        await self.play_next(ctx, query=query)

    @commands.command(name="youtube-now", aliases=["youtube_now", "youtubenow", "ytno"], hidden=True)
    async def youtube_now(self, ctx: Context, *, query: str) -> None:
        await self.play_now(ctx, query=query)

    # YouTube search

    @commands.hybrid_command(
        name="youtube-search",
        aliases=["youtube_search", "youtubesearch", "yts"]
    )
    async def youtube_search(self, ctx: Context, *, query: str) -> None:
        """
        Allows you to select which tracks from YouTube to add to the queue.
        **Arguments:**
        ● `query`: The track to search for. Can be a URL or search query.
        """
        await self.search(ctx, query=query)

    @commands.command(
        name="youtube-search-next",
        aliases=["youtube_search_next", "youtubesearchnext", "ytsne"],
        hidden=True
    )
    async def youtube_search_next(self, ctx: Context, *, query: str) -> None:
        await self.search_next(ctx, query=query)

    @commands.command(
        name="youtube-search-now",
        aliases=["youtube_search_now", "youtubesearchnow", "ytsno"],
        hidden=True
    )
    async def youtube_search_now(self, ctx: Context, *, query: str) -> None:
        await self.search_now(ctx, query=query)

    # YouTube Music

    @commands.hybrid_command(
        name="youtube-music",
        aliases=["youtube_music", "youtubemusic", "ytm"]
    )
    async def youtube_music(self, ctx: Context, *, query: str) -> None:
        """
        Searches for tracks from YouTube Music to add to the queue.
        **Arguments:**
        ● `query`: The track to search for. Can be a URL or search query.
        """

        await self._ensure_connected(ctx)

        await ctx.voice_client.searcher.queue(query, source=slate.Source.YOUTUBE_MUSIC, ctx=ctx)

    @commands.command(
        name="youtube-music-next",
        aliases=["youtube_music_next", "youtubemusicnext", "ytmne"],
        hidden=True
    )
    async def youtube_music_next(self, ctx: Context, *, query: str) -> None:

        await self._ensure_connected(ctx)

        await ctx.voice_client.searcher.queue(query, source=slate.Source.YOUTUBE_MUSIC, ctx=ctx, play_next=True)

    @commands.command(
        name="youtube-music-now",
        aliases=["youtube_music_now", "youtubemusicnow", "ytmno"],
        hidden=True
    )
    async def youtube_music_now(self, ctx: Context, *, query: str) -> None:

        await self._ensure_connected(ctx)

        await ctx.voice_client.searcher.queue(query, source=slate.Source.YOUTUBE_MUSIC, ctx=ctx, play_now=True)

    # YouTube Music search

    @commands.hybrid_command(
        name="youtube-music-search",
        aliases=["youtube_music_search", "youtubemusicsearch", "ytms"]
    )
    async def youtube_music_search(self, ctx: Context, *, query: str) -> None:
        """
        Allows you to select which tracks from YouTube Music to add to the queue.
        **Arguments:**
        ● `query`: The track to search for. Can be a URL or search query.
        """

        await self._ensure_connected(ctx)

        await ctx.voice_client.searcher.select(query, source=slate.Source.YOUTUBE_MUSIC, ctx=ctx)

    @commands.command(
        name="youtube-music-search-next",
        aliases=["youtube_music_search_next", "youtubemusicsearchnext", "ytmsne"],
        hidden=True
    )
    async def youtube_music_search_next(self, ctx: Context, *, query: str) -> None:

        await self._ensure_connected(ctx)

        await ctx.voice_client.searcher.select(query, source=slate.Source.YOUTUBE_MUSIC, ctx=ctx, play_next=True)

    @commands.command(
        name="youtube-music-search-now",
        aliases=["youtube_music_search_now", "youtubemusicsearchnow", "ytmsno"],
        hidden=True
    )
    async def youtube_music_search_now(self, ctx: Context, *, query: str) -> None:

        await self._ensure_connected(ctx)

        await ctx.voice_client.searcher.select(query, source=slate.Source.YOUTUBE_MUSIC, ctx=ctx, play_now=True)

    # Soundcloud

    @commands.hybrid_command(
        name="soundcloud",
        aliases=["sc"]
    )
    async def soundcloud(self, ctx: Context, *, query: str) -> None:
        """
        Searches for tracks from Soundcloud to add to the queue.
        **Arguments:**
        ● `query`: The track to search for. Can be a URL or search query.
        """

        await self._ensure_connected(ctx)

        await ctx.voice_client.searcher.queue(query, source=slate.Source.SOUNDCLOUD, ctx=ctx)

    @commands.command(
        name="soundcloud-next",
        aliases=["soundcloud_next", "soundcloudnext", "scne"],
        hidden=True
    )
    async def soundcloud_next(self, ctx: Context, *, query: str) -> None:

        await self._ensure_connected(ctx)

        await ctx.voice_client.searcher.queue(query, source=slate.Source.SOUNDCLOUD, ctx=ctx, play_next=True)

    @commands.command(
        name="soundcloud-now",
        aliases=["soundcloud_now", "soundcloudnow", "scno"],
        hidden=True
    )
    async def soundcloud_now(self, ctx: Context, *, query: str) -> None:

        await self._ensure_connected(ctx)

        await ctx.voice_client.searcher.queue(query, source=slate.Source.SOUNDCLOUD, ctx=ctx, play_now=True)

    # Soundcloud search

    @commands.hybrid_command(
        name="soundcloud-search",
        aliases=["soundcloud_search", "soundcloudsearch", "scs"]
    )
    async def soundcloud_search(self, ctx: Context, *, query: str) -> None:
        """
        Allows you to select which tracks from Soundcloud to add to the queue.
        **Arguments:**
        ● `query`: The track to search for. Can be a URL or search query.
        """

        await self._ensure_connected(ctx)

        await ctx.voice_client.searcher.select(query, source=slate.Source.SOUNDCLOUD, ctx=ctx)

    @commands.command(
        name="soundcloud-search-next",
        aliases=["soundcloud_search_next", "soundcloudsearchnext", "scsne"],
        hidden=True
    )
    async def soundcloud_search_next(self, ctx: Context, *, query: str) -> None:

        await self._ensure_connected(ctx)

        await ctx.voice_client.searcher.select(query, source=slate.Source.SOUNDCLOUD, ctx=ctx, play_next=True)

    @commands.command(
        name="soundcloud-search-now",
        aliases=["soundcloud_search_now", "soundcloudsearchnow", "scsno"],
        hidden=True
    )
    async def soundcloud_search_now(self, ctx: Context, *, query: str) -> None:

        await self._ensure_connected(ctx)

        await ctx.voice_client.searcher.select(query, source=slate.Source.SOUNDCLOUD, ctx=ctx, play_now=True)

    # Local

    @commands.command(name="local", aliases=["l"], hidden=True)
    @checks.is_bot_owner()
    async def local(self, ctx: Context, *, query: str) -> None:

        await self._ensure_connected(ctx)

        await ctx.voice_client.searcher.queue(query, source=slate.Source.LOCAL, ctx=ctx)

    @commands.command(name="local-next", aliases=["local_next", "localnext", "lne"], hidden=True)
    @checks.is_bot_owner()
    async def local_next(self, ctx: Context, *, query: str) -> None:

        await self._ensure_connected(ctx)

        await ctx.voice_client.searcher.queue(query, source=slate.Source.LOCAL, ctx=ctx, play_next=True)

    @commands.command(name="local-now", aliases=["local_now", "localnow", "lno"], hidden=True)
    @checks.is_bot_owner()
    async def local_now(self, ctx: Context, *, query: str) -> None:

        await self._ensure_connected(ctx)

        await ctx.voice_client.searcher.queue(query, source=slate.Source.LOCAL, ctx=ctx, play_now=True)

    @commands.command(name="http", aliases=["h"], hidden=True)
    @checks.is_bot_owner()
    async def http(self, ctx: Context, *, query: str) -> None:

        await self._ensure_connected(ctx)

        await ctx.voice_client.searcher.queue(query, source=slate.Source.NONE, ctx=ctx)

    @commands.command(name="http-next", aliases=["http_next", "httpnext", "hne"], hidden=True)
    @checks.is_bot_owner()
    async def http_next(self, ctx: Context, *, query: str) -> None:

        await self._ensure_connected(ctx)

        await ctx.voice_client.searcher.queue(query, source=slate.Source.NONE, ctx=ctx, play_next=True)

    @commands.command(name="http-now", aliases=["http_now", "httpnow", "hno"], hidden=True)
    @checks.is_bot_owner()
    async def http_now(self, ctx: Context, *, query: str) -> None:

        await self._ensure_connected(ctx)

        await ctx.voice_client.searcher.queue(query, source=slate.Source.NONE, ctx=ctx, play_now=True)


async def setup(bot: TMS):
    await bot.add_cog(Play(bot))
