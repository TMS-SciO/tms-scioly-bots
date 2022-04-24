from __future__ import annotations

from typing import Optional
import datetime
import discord


def embed(
        *,
        colour: Optional[discord.Colour] = None,
        title: Optional[str] = None,
        url: Optional[str] = None,
        description: Optional[str] = None,
        timestamp: Optional[datetime.datetime] = None,
        footer: Optional[str] = None,
        footer_icon_url: Optional[str] = None,
        image: Optional[str] = None,
        thumbnail: Optional[str] = None,
        author: Optional[str] = None,
        author_url: Optional[str] = None,
        author_icon_url: Optional[str] = None,
        emoji: Optional[str] = None,
) -> discord.Embed:
    _embed = discord.Embed(
        colour=colour,
        title=title,
        url=url,
        description=description,
        timestamp=timestamp,
    )
    if emoji is not None:
        _embed.description = f"{emoji} \u200b {_embed.description}"
    if footer is not None:
        _embed.set_footer(text=footer, icon_url=footer_icon_url)
    if image is not None:
        _embed.set_image(url=image)
    if thumbnail is not None:
        _embed.set_thumbnail(url=thumbnail)
    if author:
        _embed.set_author(name=author, url=author_url, icon_url=author_icon_url)

    return _embed
