from __future__ import annotations

import discord
from discord.app_commands import command, guilds
from discord.ext import commands
from utils.variables import *
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bot import TMS

class Medals(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @command()
    @guilds(SERVER_ID)
    async def medals(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="Medals \U0001f947",
            description=(
                "**Eric** \N{SPORTS MEDAL} \N{SPORTS MEDAL} \N{SPORTS MEDAL} \N{SPORTS MEDAL} \N{FIRST PLACE MEDAL} "
                "\N{SPORTS MEDAL} \N{SPORTS MEDAL} \N{SPORTS MEDAL} \N{SPORTS MEDAL} \N{SPORTS MEDAL} "
                "\N{FIRST PLACE MEDAL} \N{FIRST PLACE MEDAL} \N{SPORTS MEDAL} \N{SPORTS MEDAL}"
                "\n**Shyla** \N{SPORTS MEDAL} \N{SPORTS MEDAL} \N{FIRST PLACE MEDAL} \N{SPORTS MEDAL} \N{SPORTS MEDAL} "
                "\N{FIRST PLACE MEDAL} \N{SPORTS MEDAL}"
                "\n**Vivienne** \N{SPORTS MEDAL} \N{THIRD PLACE MEDAL} \N{SPORTS MEDAL} \N{SPORTS MEDAL} "
                "\N{SPORTS MEDAL}"
                "\n**Gio** \N{SPORTS MEDAL} \N{SPORTS MEDAL} \N{SPORTS MEDAL} \N{SPORTS MEDAL} \N{THIRD PLACE MEDAL}"
                "\n**Ryan S** \N{SPORTS MEDAL} \N{SPORTS MEDAL} \N{SECOND PLACE MEDAL} \N{FIRST PLACE MEDAL}"
                "\n**Eva** \N{SPORTS MEDAL} \N{SPORTS MEDAL} \N{THIRD PLACE MEDAL} \N{SECOND PLACE MEDAL}"
                "\n**Michelle** \N{THIRD PLACE MEDAL} \N{SPORTS MEDAL} \N{THIRD PLACE MEDAL}"
                "\n**Emilee** \N{SPORTS MEDAL} \N{SPORTS MEDAL} \N{SPORTS MEDAL} \N{SECOND PLACE MEDAL}"
                "\n**Vishnu** \N{FIRST PLACE MEDAL} \N{SPORTS MEDAL}"
                "\n**Nikhil** \N{SPORTS MEDAL} \N{SPORTS MEDAL}"
                "\n**Ryan M** \N{FIRST PLACE MEDAL} \N{SPORTS MEDAL}"
                "\n**Aayushi** \N{SPORTS MEDAL} \N{SPORTS MEDAL}"
                "\n**Brody** \N{SECOND PLACE MEDAL}"
                "\n**Anya** \N{SPORTS MEDAL}"
                "\n**Sam** \N{SPORTS MEDAL}"
                "\n**Christian** \N{SPORTS MEDAL}"
                "\n**Anlin** \N{FIRST PLACE MEDAL} \N{FIRST PLACE MEDAL} \N{FIRST PLACE MEDAL}"
                "\n**Nathan** \N{THIRD PLACE MEDAL} \N{SPORTS MEDAL} \N{FIRST PLACE MEDAL} \N{FIRST PLACE MEDAL}"
                "\n**Grace** \N{THIRD PLACE MEDAL} \N{SECOND PLACE MEDAL} \N{FIRST PLACE MEDAL}"
                "\n**Nayan** \N{FIRST PLACE MEDAL} \N{FIRST PLACE MEDAL} \N{SPORTS MEDAL}"
                "\n**Sydney**  \N{SPORTS MEDAL} \N{SPORTS MEDAL} \N{SECOND PLACE MEDAL}"
                "\n**Colton** \N{THIRD PLACE MEDAL} \N{SECOND PLACE MEDAL} \N{SECOND PLACE MEDAL}"
                "\n**Ahbi** \N{SPORTS MEDAL} \N{FIRST PLACE MEDAL}"
                "\n**Harini** \N{SPORTS MEDAL} \N{SPORTS MEDAL} \N{THIRD PLACE MEDAL}"
                "\n**Haritha** \N{SPORTS MEDAL} \N{SECOND PLACE MEDAL}"
                "\n**Krishiv** \N{FIRST PLACE MEDAL} \N{SECOND PLACE MEDAL}"
                "\n**Kedus** \N{FIRST PLACE MEDAL} \N{FIRST PLACE MEDAL}"
                "\n**Ahir** \N{FIRST PLACE MEDAL}"
                "\n**Varun** \N{SECOND PLACE MEDAL}"
                "\n**Prisha** \N{THIRD PLACE MEDAL}"
                "\n**Abhinav** \N{THIRD PLACE MEDAL}"
                "\n**Luka** \N{THIRD PLACE MEDAL}"
                "\n**Srikrishna** \N{SPORTS MEDAL}"
            ),
            color=discord.Color.blurple()
        )
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Medals(bot))
