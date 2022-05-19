from __future__ import annotations

import discord
import webcolors
from typing import Literal, Optional, Union, List, Dict, TypeVar

F = TypeVar(
    "F",
    bound=Optional[List[Dict[str, Union[Literal["name", "value", "inline"], bool]]]],
)


def assemble_embed(
    title: Optional[str] = "",
    description: Optional[str] = "",
    title_url: Optional[str] = "",
    webcolor: Optional[str] = "",
    hexcolor: Optional[str] = "#2E66B6",
    thumbnail_url: Optional[str] = "",
    author_name: Optional[str] = "",
    author_url: Optional[str] = "",
    author_icon: Optional[str] = "",
    footer_text: Optional[str] = "",
    footer_url: Optional[str] = "",
    image_url: Optional[str] = "",
    fields: "F" = None,
) -> discord.Embed:
    """Assembles an embed with the specified parameters."""

    if len(webcolor) > 1:
        hexcolor = webcolors.name_to_hex(webcolor)
    hexcolor = hexcolor[1:]
    embed = discord.Embed(
        title=title, description=description, url=title_url, color=int(hexcolor, 16)
    )
    embed.set_author(name=author_name, url=author_url, icon_url=author_icon)
    embed.set_thumbnail(url=thumbnail_url)
    embed.set_footer(text=footer_text, icon_url=footer_url)
    if fields is None:
        fields = {}
    for field in fields:
        embed.add_field(
            name=field["name"], value=field["value"], inline=(field["inline"] == "True")
        )
    embed.set_image(url=image_url)
    return embed
