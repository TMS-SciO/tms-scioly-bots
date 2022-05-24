from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Optional, TYPE_CHECKING

import discord
import slate

from custom import enums, embed
from .queue import QueueItem
from voice import utilities, values

if TYPE_CHECKING:
    from .player import Player

__all__ = ("Controller",)

_MessageBuilder = Callable[
    ..., Awaitable[tuple[Optional[str], Optional[discord.Embed]]]
]

_SHUFFLE_STATE_EMOJIS: dict[bool, str] = {
    False: values.PLAYER_SHUFFLE_DISABLED,
    True: values.PLAYER_SHUFFLE_ENABLED,
}
_PAUSE_STATE_EMOJIS: dict[bool, str] = {
    False: values.PLAYER_IS_PLAYING,
    True: values.PLAYER_IS_PAUSED,
}
_LOOP_MODE_EMOJIS: dict[slate.QueueLoopMode, str] = {
    slate.QueueLoopMode.DISABLED: values.PLAYER_LOOP_DISABLED,
    slate.QueueLoopMode.ALL: values.PLAYER_LOOP_ALL,
    slate.QueueLoopMode.CURRENT: values.PLAYER_LOOP_CURRENT,
}


class ShuffleButton(discord.ui.Button["ControllerView"]):
    def __init__(self) -> None:
        super().__init__(
            emoji=values.PLAYER_SHUFFLE_DISABLED,
        )

    async def callback(self, interaction: discord.Interaction) -> None:

        assert self.view is not None
        await interaction.response.defer()

        voice_client = self.view.player

        match voice_client.queue.shuffle_state:
            case True:
                voice_client.queue.set_shuffle_state(False)
            case False:
                voice_client.queue.set_shuffle_state(True)

        await voice_client.controller.update_current_message()


class PreviousButton(discord.ui.Button["ControllerView"]):
    def __init__(self) -> None:
        super().__init__(
            emoji=values.PLAYER_PREVIOUS,
        )

    async def callback(self, interaction: discord.Interaction) -> None:
        assert self.view is not None
        await interaction.response.defer()

        voice_client = self.view.player

        # Pop the previous track from the queue history and
        # then add it to front of the queue.
        previous = voice_client.queue.history.pop(0)
        voice_client.queue.items.insert(0, QueueItem(previous))

        # Add the current track to the queue right after the
        # previous track so that it will play again if the
        # 'next' button is pressed after the 'previous' button.
        assert voice_client.current is not None
        voice_client.queue.items.insert(1, QueueItem(voice_client.current))

        # Trigger the next track in the queue to play.
        await voice_client.handle_track_end(enums.TrackEndReason.REPLACED)


class PauseStateButton(discord.ui.Button["ControllerView"]):
    def __init__(self) -> None:
        super().__init__(
            emoji=values.PLAYER_IS_PLAYING,
        )

    async def callback(self, interaction: discord.Interaction) -> None:

        assert self.view is not None
        await interaction.response.defer()

        voice_client = self.view.player

        if voice_client.is_paused():
            await voice_client.set_pause(False)
        else:
            await voice_client.set_pause(True)

        await voice_client.controller.update_current_message()


class NextButton(discord.ui.Button["ControllerView"]):
    def __init__(self) -> None:
        super().__init__(
            emoji=values.PLAYER_NEXT,
        )

    async def callback(self, interaction: discord.Interaction) -> None:
        assert self.view is not None
        await interaction.response.defer()

        await self.view.player.stop()


class LoopButton(discord.ui.Button["ControllerView"]):
    def __init__(self) -> None:
        super().__init__(
            emoji=values.PLAYER_LOOP_DISABLED,
        )

    async def callback(self, interaction: discord.Interaction) -> None:

        assert self.view is not None
        await interaction.response.defer()

        voice_client = self.view.player

        match voice_client.queue.loop_mode:
            case slate.QueueLoopMode.DISABLED:
                voice_client.queue.set_loop_mode(slate.QueueLoopMode.ALL)
            case slate.QueueLoopMode.ALL:
                voice_client.queue.set_loop_mode(slate.QueueLoopMode.CURRENT)
            case slate.QueueLoopMode.CURRENT:
                voice_client.queue.set_loop_mode(slate.QueueLoopMode.DISABLED)

        await voice_client.controller.update_current_message()


class ControllerView(discord.ui.View):
    def __init__(self, *, player: "Player") -> None:
        super().__init__(timeout=None)

        self.player: "Player" = player

        self._shuffle_button: ShuffleButton = ShuffleButton()
        self._previous_button: PreviousButton = PreviousButton()
        self._pause_state_button: PauseStateButton = PauseStateButton()
        self._next_button: NextButton = NextButton()
        self._loop_button: LoopButton = LoopButton()

        self.add_item(self._shuffle_button)
        self.add_item(self._previous_button)
        self.add_item(self._pause_state_button)
        self.add_item(self._next_button)
        self.add_item(self._loop_button)

    def update_state(self) -> None:
        self._shuffle_button.emoji = _SHUFFLE_STATE_EMOJIS[
            self.player.queue.shuffle_state
        ]
        self._previous_button.disabled = not self.player.queue.history
        self._pause_state_button.emoji = _PAUSE_STATE_EMOJIS[self.player.paused]
        self._loop_button.emoji = _LOOP_MODE_EMOJIS[self.player.queue.loop_mode]


class Controller:
    def __init__(self, *, player: Player) -> None:

        self.player: Player = player

        self.message: Optional[discord.Message] = None
        self.view: ControllerView = ControllerView(player=self.player)

        self._MESSAGE_BUILDERS: dict[enums.EmbedSize, _MessageBuilder] = {
            enums.EmbedSize.SMALL: self._build_small,
            enums.EmbedSize.MEDIUM: self._build_medium,
            enums.EmbedSize.LARGE: self._build_large,
        }

    async def _build_small(self) -> tuple[None, discord.Embed]:

        current = self.player.current
        assert current is not None

        return (
            None,
            embed(
                colour=discord.Colour.blurple(),
                title="Now Playing:",
                description=f"**[{discord.utils.escape_markdown(current.title)}]({current.uri})**\n"
                f"by **{discord.utils.escape_markdown(current.author or 'Unknown')}**",
                thumbnail=current.artwork_url
                or "https://dummyimage.com/1280x720/000/ffffff.png&text=no+thumbnail",
            ),
        )

    async def _build_medium(self) -> tuple[None, discord.Embed]:

        current = self.player.current
        assert current is not None

        _, embed = await self._build_small()

        assert embed.description is not None
        embed.description += (
            "\n\n"
            f"● **Requested by:** {getattr(current.extras['ctx'].author, 'mention', None)}\n"
            f"● **Source:** {current.source.value.title()}\n"
            f"● **Paused:** {utilities.readable_bool(self.player.paused).title()}\n"
            f"● **Effects:** {', '.join([effect.value for effect in self.player.effects] or ['N/A'])}\n"
            f"● **Position:** {utilities.format_seconds(self.player.position // 1000)} / {utilities.format_seconds(current.length // 1000)}\n"
        )

        return None, embed

    async def _build_large(self) -> tuple[None, discord.Embed]:

        _, embed_ = await self._build_medium()

        if self.player.queue.is_empty():
            return _, embed_

        entries = [
            f"**{index}. [{discord.utils.escape_markdown(item.track.title)}]({item.track.uri})**\n"
            f"**⤷** by **{discord.utils.escape_markdown(item.track.author)}** | {utilities.format_seconds(item.track.length // 1000, friendly=True)}\n"
            for index, item in enumerate(self.player.queue.items[:3], start=1)
        ]

        assert embed_.description is not None
        embed_.description += (
            f"\n● **Up next ({len(self.player.queue)}):**\n{''.join(entries)}"
        )

        return None, embed_

    async def build_message(self) -> dict[str, str | discord.Embed | None]:
        message = await self._build_medium()

        return {"content": message[0], "embed": message[1]}

    async def send_new_message(self) -> None:

        if not self.player.current:
            return

        kwargs = await self.build_message()
        self.view.update_state()

        self.message = await self.player.text_channel.send(**kwargs, view=self.view)

    async def update_current_message(self) -> None:

        if not self.message or not self.player.current:
            return

        kwargs = await self.build_message()
        self.view.update_state()

        try:
            await self.message.edit(**kwargs, view=self.view)
        except (discord.NotFound, discord.HTTPException):
            pass

    async def handle_track_start(self) -> None:
        await self.send_new_message()

    # Track End

    async def _edit_old_message(self, reason: enums.TrackEndReason) -> None:

        if not self.message:
            return

        assert self.player._current is not None
        track = self.player._current

        if reason in [enums.TrackEndReason.NORMAL, enums.TrackEndReason.REPLACED]:
            colour = discord.Colour.blurple()
            title = "Track ended:"
        else:
            colour = discord.Colour.brand_red()
            title = "Something went wrong!"

        try:
            await self.message.edit(
                embed=embed(
                    colour=colour,
                    title=title,
                    description=f"**[{discord.utils.escape_markdown(track.title)}]({track.uri})**\n"
                    f"by **{discord.utils.escape_markdown(track.author or 'Unknown')}**",
                    thumbnail=track.artwork_url
                    or "https://dummyimage.com/500x500/000/ffffff.png&text=thumbnail+not+found",
                ),
            )
        except (discord.NotFound, discord.HTTPException):
            pass

        self.message = None

    async def handle_track_end(self, reason: enums.TrackEndReason) -> None:
        await self._edit_old_message(reason)
