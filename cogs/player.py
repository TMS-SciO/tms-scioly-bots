from __future__ import annotations

from typing import Literal, TYPE_CHECKING

import discord
import slate
from discord.ext import commands

from custom import Context, embed, enums
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
        bot_voice_channel = ctx.player and ctx.player.voice_channel

        if (author_voice_channel and bot_voice_channel) and (
            author_voice_channel == bot_voice_channel
        ):
            return

        if (not author_voice_channel and bot_voice_channel) or (
            author_voice_channel and bot_voice_channel
        ):
            await ctx.reply(
                f"You must be connected to {bot_voice_channel.mention} to use this command."
            )
            return
        if not author_voice_channel:
            await ctx.reply(
                "You must be connected to a voice channel to use this command."
            )
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

        await ctx.player.searcher.queue(query, source=slate.Source.YOUTUBE, ctx=ctx)

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

        await ctx.player.searcher.queue(
            query, source=slate.Source.YOUTUBE, ctx=ctx, play_next=True
        )

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

        await ctx.player.searcher.queue(
            query, source=slate.Source.YOUTUBE, ctx=ctx, play_now=True
        )

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

        await ctx.player.searcher.select(query, source=slate.Source.YOUTUBE, ctx=ctx)

    @commands.hybrid_command(
        name="search-next", aliases=["search_next", "searchnext", "sne"]
    )
    async def search_next(self, ctx: Context, *, query: str) -> None:
        """
        Allows you to select which tracks to add to the start of the queue.
        **Arguments:**
        ● `query`: The track to search for. Can be a URL or search query.
        **Note:**
        This command supports all sources providing you use a direct URL. When using a search query with this command you will always get a YouTube track.
        """

        await self._ensure_connected(ctx)
        await ctx.player.searcher.select(
            query, source=slate.Source.YOUTUBE, ctx=ctx, play_next=True
        )

    @commands.hybrid_command(
        name="search-now", aliases=["search_now", "searchnow", "sno"]
    )
    async def search_now(self, ctx: Context, *, query: str) -> None:
        """
        Allows you to select which tracks to play immediately.
        **Arguments:**
        ● `query`: The track to search for. Can be a URL or search query.
        **Note:**
        This command supports all sources providing you use a direct URL. When using a search query with this command you will always get a YouTube track.
        """

        await self._ensure_connected(ctx)

        await ctx.player.searcher.select(
            query, source=slate.Source.YOUTUBE, ctx=ctx, play_now=True
        )

    # Youtube

    @commands.hybrid_command(name="youtube", aliases=["yt"])
    async def youtube(self, ctx: Context, *, query: str) -> None:
        """
        Searches for tracks from YouTube to add to the queue.
        **Arguments:**
        ● `query`: The track to search for. Can be a URL or search query.
        """
        await self.play(ctx, query=query)

    @commands.command(
        name="youtube-next",
        aliases=["youtube_next", "youtubenext", "ytne"],
        hidden=True,
    )
    async def youtube_next(self, ctx: Context, *, query: str) -> None:
        await self.play_next(ctx, query=query)

    @commands.command(
        name="youtube-now", aliases=["youtube_now", "youtubenow", "ytno"], hidden=True
    )
    async def youtube_now(self, ctx: Context, *, query: str) -> None:
        await self.play_now(ctx, query=query)

    # YouTube search

    @commands.hybrid_command(
        name="youtube-search", aliases=["youtube_search", "youtubesearch", "yts"]
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
        hidden=True,
    )
    async def youtube_search_next(self, ctx: Context, *, query: str) -> None:
        await self.search_next(ctx, query=query)

    @commands.command(
        name="youtube-search-now",
        aliases=["youtube_search_now", "youtubesearchnow", "ytsno"],
        hidden=True,
    )
    async def youtube_search_now(self, ctx: Context, *, query: str) -> None:
        await self.search_now(ctx, query=query)

    # YouTube Music

    @commands.hybrid_command(
        name="youtube-music", aliases=["youtube_music", "youtubemusic", "ytm"]
    )
    async def youtube_music(self, ctx: Context, *, query: str) -> None:
        """
        Searches for tracks from YouTube Music to add to the queue.
        **Arguments:**
        ● `query`: The track to search for. Can be a URL or search query.
        """

        await self._ensure_connected(ctx)

        await ctx.player.searcher.queue(
            query, source=slate.Source.YOUTUBE_MUSIC, ctx=ctx
        )

    @commands.command(
        name="youtube-music-next",
        aliases=["youtube_music_next", "youtubemusicnext", "ytmne"],
        hidden=True,
    )
    async def youtube_music_next(self, ctx: Context, *, query: str) -> None:

        await self._ensure_connected(ctx)

        await ctx.player.searcher.queue(
            query, source=slate.Source.YOUTUBE_MUSIC, ctx=ctx, play_next=True
        )

    @commands.command(
        name="youtube-music-now",
        aliases=["youtube_music_now", "youtubemusicnow", "ytmno"],
        hidden=True,
    )
    async def youtube_music_now(self, ctx: Context, *, query: str) -> None:

        await self._ensure_connected(ctx)

        await ctx.player.searcher.queue(
            query, source=slate.Source.YOUTUBE_MUSIC, ctx=ctx, play_now=True
        )

    # YouTube Music search

    @commands.hybrid_command(
        name="youtube-music-search",
        aliases=["youtube_music_search", "youtubemusicsearch", "ytms"],
    )
    async def youtube_music_search(self, ctx: Context, *, query: str) -> None:
        """
        Allows you to select which tracks from YouTube Music to add to the queue.
        **Arguments:**
        ● `query`: The track to search for. Can be a URL or search query.
        """

        await self._ensure_connected(ctx)

        await ctx.player.searcher.select(
            query, source=slate.Source.YOUTUBE_MUSIC, ctx=ctx
        )

    @commands.command(
        name="youtube-music-search-next",
        aliases=["youtube_music_search_next", "youtubemusicsearchnext", "ytmsne"],
        hidden=True,
    )
    async def youtube_music_search_next(self, ctx: Context, *, query: str) -> None:

        await self._ensure_connected(ctx)

        await ctx.player.searcher.select(
            query, source=slate.Source.YOUTUBE_MUSIC, ctx=ctx, play_next=True
        )

    @commands.command(
        name="youtube-music-search-now",
        aliases=["youtube_music_search_now", "youtubemusicsearchnow", "ytmsno"],
        hidden=True,
    )
    async def youtube_music_search_now(self, ctx: Context, *, query: str) -> None:

        await self._ensure_connected(ctx)

        await ctx.player.searcher.select(
            query, source=slate.Source.YOUTUBE_MUSIC, ctx=ctx, play_now=True
        )

    # Soundcloud

    @commands.hybrid_command(name="soundcloud", aliases=["sc"])
    async def soundcloud(self, ctx: Context, *, query: str) -> None:
        """
        Searches for tracks from Soundcloud to add to the queue.
        **Arguments:**
        ● `query`: The track to search for. Can be a URL or search query.
        """

        await self._ensure_connected(ctx)

        await ctx.player.searcher.queue(query, source=slate.Source.SOUNDCLOUD, ctx=ctx)

    @commands.command(
        name="soundcloud-next",
        aliases=["soundcloud_next", "soundcloudnext", "scne"],
        hidden=True,
    )
    async def soundcloud_next(self, ctx: Context, *, query: str) -> None:

        await self._ensure_connected(ctx)

        await ctx.player.searcher.queue(
            query, source=slate.Source.SOUNDCLOUD, ctx=ctx, play_next=True
        )

    @commands.command(
        name="soundcloud-now",
        aliases=["soundcloud_now", "soundcloudnow", "scno"],
        hidden=True,
    )
    async def soundcloud_now(self, ctx: Context, *, query: str) -> None:

        await self._ensure_connected(ctx)

        await ctx.player.searcher.queue(
            query, source=slate.Source.SOUNDCLOUD, ctx=ctx, play_now=True
        )

    # Soundcloud search

    @commands.hybrid_command(
        name="soundcloud-search",
        aliases=["soundcloud_search", "soundcloudsearch", "scs"],
    )
    async def soundcloud_search(self, ctx: Context, *, query: str) -> None:
        """
        Allows you to select which tracks from Soundcloud to add to the queue.
        **Arguments:**
        ● `query`: The track to search for. Can be a URL or search query.
        """

        await self._ensure_connected(ctx)

        await ctx.player.searcher.select(query, source=slate.Source.SOUNDCLOUD, ctx=ctx)

    @commands.command(
        name="soundcloud-search-next",
        aliases=["soundcloud_search_next", "soundcloudsearchnext", "scsne"],
        hidden=True,
    )
    async def soundcloud_search_next(self, ctx: Context, *, query: str) -> None:

        await self._ensure_connected(ctx)

        await ctx.player.searcher.select(
            query, source=slate.Source.SOUNDCLOUD, ctx=ctx, play_next=True
        )

    @commands.command(
        name="soundcloud-search-now",
        aliases=["soundcloud_search_now", "soundcloudsearchnow", "scsno"],
        hidden=True,
    )
    async def soundcloud_search_now(self, ctx: Context, *, query: str) -> None:

        await self._ensure_connected(ctx)

        await ctx.player.searcher.select(
            query, source=slate.Source.SOUNDCLOUD, ctx=ctx, play_now=True
        )

    # Local

    @commands.command(name="local", aliases=["l"], hidden=True)
    @checks.is_bot_owner()
    async def local(self, ctx: Context, *, query: str) -> None:

        await self._ensure_connected(ctx)

        await ctx.player.searcher.queue(query, source=slate.Source.LOCAL, ctx=ctx)

    @commands.command(
        name="local-next", aliases=["local_next", "localnext", "lne"], hidden=True
    )
    @checks.is_bot_owner()
    async def local_next(self, ctx: Context, *, query: str) -> None:

        await self._ensure_connected(ctx)

        await ctx.player.searcher.queue(
            query, source=slate.Source.LOCAL, ctx=ctx, play_next=True
        )

    @commands.command(
        name="local-now", aliases=["local_now", "localnow", "lno"], hidden=True
    )
    @checks.is_bot_owner()
    async def local_now(self, ctx: Context, *, query: str) -> None:

        await self._ensure_connected(ctx)

        await ctx.player.searcher.queue(
            query, source=slate.Source.LOCAL, ctx=ctx, play_now=True
        )

    @commands.command(name="http", aliases=["h"], hidden=True)
    @checks.is_bot_owner()
    async def http(self, ctx: Context, *, query: str) -> None:

        await self._ensure_connected(ctx)

        await ctx.player.searcher.queue(query, source=slate.Source.NONE, ctx=ctx)

    @commands.command(
        name="http-next", aliases=["http_next", "httpnext", "hne"], hidden=True
    )
    @checks.is_bot_owner()
    async def http_next(self, ctx: Context, *, query: str) -> None:

        await self._ensure_connected(ctx)

        await ctx.player.searcher.queue(
            query, source=slate.Source.NONE, ctx=ctx, play_next=True
        )

    @commands.command(
        name="http-now", aliases=["http_now", "httpnow", "hno"], hidden=True
    )
    @checks.is_bot_owner()
    async def http_now(self, ctx: Context, *, query: str) -> None:

        await self._ensure_connected(ctx)

        await ctx.player.searcher.queue(
            query, source=slate.Source.NONE, ctx=ctx, play_now=True
        )

    # Controls

    EFFECT_MAP: dict[enums.Effect, dict[str, slate.Filter]] = {
        enums.Effect.ROTATION: {"rotation": slate.Rotation(speed=0.5)},
        enums.Effect.NIGHTCORE: {"timescale": slate.Timescale(speed=1.12, pitch=1.12)},
        enums.Effect.MONO: {
            "channel_mix": slate.ChannelMix(left_to_right=1, right_to_left=1)
        },
        enums.Effect.LEFT_EAR: {
            "channel_mix": slate.ChannelMix(right_to_right=0, right_to_left=1)
        },
        enums.Effect.RIGHT_EAR: {
            "channel_mix": slate.ChannelMix(left_to_left=0, left_to_right=1)
        },
    }

    INVERSE_EFFECT_MAP: dict[enums.Effect, dict[str, slate.Filter]] = {
        enums.Effect.ROTATION: {"rotation": slate.Rotation()},
        enums.Effect.NIGHTCORE: {"timescale": slate.Timescale()},
        enums.Effect.MONO: {"channel_mix": slate.ChannelMix()},
        enums.Effect.LEFT_EAR: {"channel_mix": slate.ChannelMix()},
        enums.Effect.RIGHT_EAR: {"channel_mix": slate.ChannelMix()},
    }

    INCOMPATIBLE_EFFECTS: dict[enums.Effect, list[enums.Effect]] = {
        enums.Effect.MONO: [enums.Effect.LEFT_EAR, enums.Effect.RIGHT_EAR],
        enums.Effect.LEFT_EAR: [enums.Effect.MONO, enums.Effect.RIGHT_EAR],
        enums.Effect.RIGHT_EAR: [enums.Effect.MONO, enums.Effect.LEFT_EAR],
    }

    async def _toggle_effect(self, ctx: Context, effect: enums.Effect) -> None:

        assert ctx.player

        if effect in ctx.player.effects:
            description = f"Disabled the **{effect.value}** audio effect."
            ctx.player.effects.remove(effect)
            await ctx.player.set_filter(
                slate.Filter(ctx.player.filter, **self.INVERSE_EFFECT_MAP[effect])
            )

        else:
            description = f"Enabled the **{effect.value}** audio effect."
            ctx.player.effects.add(effect)
            await ctx.player.set_filter(
                slate.Filter(ctx.player.filter, **self.EFFECT_MAP[effect])
            )

            if effect in self.INCOMPATIBLE_EFFECTS:
                for incompatible_effect in self.INCOMPATIBLE_EFFECTS[effect]:
                    try:
                        ctx.player.effects.remove(incompatible_effect)
                    except KeyError:
                        pass

        await ctx.reply(
            embed=embed(colour=discord.Colour.brand_green(), description=description)
        )

    # Commands

    @commands.hybrid_command(name="8d")
    @checks.is_author_connected()
    @checks.is_player_connected()
    async def _8d(self, ctx: Context) -> None:
        """
        Toggles an 8D audio effect.
        This effect makes the audio sound like its rotating around your head.
        """

        await self._toggle_effect(ctx, enums.Effect.ROTATION)

    @commands.hybrid_command(
        name="nightcore", aliases=["night-core", "night_core", "nc"]
    )
    @checks.is_author_connected()
    @checks.is_player_connected()
    async def night_core(self, ctx: Context) -> None:
        """
        Toggles a nightcore audio effect.
        This effect slightly increases the speed and pitch of the audio.
        """

        await self._toggle_effect(ctx, enums.Effect.NIGHTCORE)

    @commands.hybrid_command(name="mono")
    @checks.is_author_connected()
    @checks.is_player_connected()
    async def mono(self, ctx: Context) -> None:
        """
        Toggles a mono audio effect.
        This effect makes the left and right audio channels play the same thing.
        **Note:** Enabling this effect will disable the `left-ear` and `right-ear` effects.
        """

        await self._toggle_effect(ctx, enums.Effect.MONO)

    @commands.hybrid_command(name="left-ear", aliases=["left_ear", "leftear", "left"])
    @checks.is_author_connected()
    @checks.is_player_connected()
    async def left_ear(self, ctx: Context) -> None:
        """
        Toggles a left ear audio effect.
        This effect makes the audio only come out of your left headphone/speaker/earbud.
        **Note:** Enabling this effect will disable the `mono` and `right-ear` effects.
        """

        await self._toggle_effect(ctx, enums.Effect.LEFT_EAR)

    @commands.hybrid_command(
        name="right-ear", aliases=["right_ear", "rightear", "right"]
    )
    @checks.is_author_connected()
    @checks.is_player_connected()
    async def right_ear(self, ctx: Context) -> None:
        """
        Toggles a right ear audio effect.
        This effect makes the audio only come out of your right headphone/speaker/earbud.
        **Note:** Enabling this effect will disable the `mono` and `left-ear` effects.
        """

        await self._toggle_effect(ctx, enums.Effect.RIGHT_EAR)

    @commands.hybrid_command(
        name="reset-effects", aliases=["reset_effects", "reseteffects"]
    )
    @checks.is_author_connected()
    @checks.is_player_connected()
    async def reset_effects(self, ctx: Context) -> None:
        """
        Resets all audio effects.
        """

        assert ctx.player is not None

        ctx.player.effects.clear()
        await ctx.player.set_filter(slate.Filter())
        await ctx.reply(
            embed=embed(
                colour=discord.Colour.brand_green(),
                description="**Disabled** all audio effects.",
            )
        )


async def setup(bot: TMS):
    await bot.add_cog(Play(bot))
