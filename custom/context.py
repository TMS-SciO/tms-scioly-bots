from __future__ import annotations

from typing import Any, TYPE_CHECKING

import discord
from discord.ext import commands

if TYPE_CHECKING:
    from voice import Player


class Context(commands.Context[commands.Bot]):

    @property
    def player(self) -> Player | None:
        return getattr(self.guild, "voice_client", None)

    async def try_dm(self, *args: Any, **kwargs: Any) -> discord.Message | None:

        try:
            return await self.author.send(*args, **kwargs)
        except (discord.HTTPException, discord.Forbidden):
            try:
                return await self.reply(*args, **kwargs)
            except (discord.HTTPException, discord.Forbidden):
                return None
