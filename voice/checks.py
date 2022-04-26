from __future__ import annotations

__all__ = (
    "is_track_seekable",
)

from collections.abc import Callable
from typing import Literal, TypeVar, TYPE_CHECKING

import discord
from discord.ext import commands
from custom import exceptions

T = TypeVar("T")

if TYPE_CHECKING:
    from custom import Context


def is_track_seekable() -> Callable[[T], T]:
    async def predicate(ctx: Context) -> bool:
        if not ctx.voice_client or not ctx.voice_client.current or not ctx.voice_client.current.is_seekable():
            raise exceptions.EmbedError(description="The current track is not seekable.")
        return True

    return commands.check(predicate)


def is_queue_not_empty() -> Callable[[T], T]:
    async def predicate(ctx: Context) -> Literal[True]:
        if not ctx.voice_client or not ctx.voice_client.queue.items:
            raise exceptions.EmbedError(description="The queue is empty.")

        return True

    return commands.check(predicate)


def is_queue_history_not_empty() -> Callable[[T], T]:
    async def predicate(ctx: Context) -> Literal[True]:
        if not ctx.voice_client or not ctx.voice_client.queue.history:
            raise exceptions.EmbedError(description="The queue history is empty.")

        return True

    return commands.check(predicate)


def is_player_playing() -> Callable[[T], T]:
    async def predicate(ctx: Context) -> Literal[True]:
        if not ctx.voice_client or not ctx.voice_client.is_playing():
            raise exceptions.EmbedError(description="There are no tracks playing.")

        return True

    return commands.check(predicate)


def is_player_connected() -> Callable[[T], T]:
    async def predicate(ctx: Context) -> Literal[True]:
        if not ctx.voice_client or not ctx.voice_client.is_connected():
            raise exceptions.EmbedError(description="I'm not connected to any voice channels.")

        return True

    return commands.check(predicate)


def is_guild_owner() -> Callable[[T], T]:
    def predicate(ctx: Context) -> bool:
        return ctx.guild is not None and ctx.guild.owner_id == ctx.author.id

    return commands.check(predicate)


def is_bot_owner() -> Callable[[T], T]:
    async def predicate(ctx: Context) -> bool:
        if not await ctx.bot.is_owner(ctx.author):
            raise commands.NotOwner("You do not own this bot.")

        return True

    return commands.check(predicate)


def is_author_connected() -> Callable[[T], T]:
    async def predicate(ctx: Context) -> Literal[True]:
        assert isinstance(ctx.author, discord.Member)

        author_channel = ctx.author.voice and ctx.author.voice.channel
        voice_client_channel = ctx.voice_client and ctx.voice_client.voice_channel

        if voice_client_channel != author_channel:
            raise exceptions.EmbedError(
                description=f"You must be connected to {getattr(voice_client_channel, 'mention', None)} to use this "
                            f"command."
            )

        return True

    return commands.check(predicate)


def has_any_permission(**permissions: bool) -> Callable[[T], T]:
    if invalid := set(permissions) - set(discord.Permissions.VALID_FLAGS):
        raise TypeError(f"Invalid permission(s): {', '.join(invalid)}")

    def predicate(ctx: Context) -> bool:

        # permissions_for doesn't exist for certain channel types, but trust me, it's fine.
        current = dict(ctx.channel.permissions_for(ctx.author))  # type: ignore

        for permission in permissions.keys():
            if current[permission] is True:
                return True

        raise commands.CheckFailure()

    return commands.check(predicate)


async def global_check(ctx: Context) -> bool:
    if not ctx.guild:
        return True

    assert not isinstance(ctx.channel, discord.PartialMessageable)

    current = dict(ctx.channel.permissions_for(ctx.guild.me))
    permissions_ = discord.Permissions(
        read_messages=True,
        send_messages=True,
        embed_links=True,
        attach_files=True,
        read_message_history=True,
        add_reactions=True,
        external_emojis=True,
    )
    needed = {
        permission: value for permission, value in permissions_ if value is True
    }

    if missing := [permission for permission, value in needed.items() if current[permission] != value]:
        raise commands.BotMissingPermissions(missing)

    return True
