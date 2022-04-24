from __future__ import annotations

import datetime

from typing import Optional

import discord
from discord.ext import commands
from .embed_ import embed

__all__ = (
    "TMSError",
    "EmbedError",
)


class TMSError(commands.CommandError):
    pass


class EmbedError(TMSError):
    def __init__(
            self,
            *,
            colour: discord.Colour | None = discord.Colour.brand_red(),
            title: Optional[str] = None,
            url: Optional[str] = None,
            description: Optional[str] = None,
            timestamp: datetime.datetime | None = None,
            footer: Optional[str] = None,
            footer_icon_url: Optional[str] = None,
            image: Optional[str] = None,
            thumbnail: Optional[str] = None,
            author: Optional[str] = None,
            author_url: Optional[str] = None,
            author_icon_url: Optional[str] = None,
            emoji: Optional[str] = None,
            view: discord.ui.View | None = None,
    ) -> None:
        self.embed: discord.Embed = embed(
            colour=colour,
            title=title,
            url=url,
            description=description,
            timestamp=timestamp,
            footer=footer,
            footer_icon_url=footer_icon_url,
            image=image,
            thumbnail=thumbnail,
            author=author,
            author_url=author_url,
            author_icon_url=author_icon_url,
            emoji=emoji,
        )
        self.view: discord.ui.View | None = view
