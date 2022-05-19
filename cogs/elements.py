from __future__ import annotations

from typing import Any, TYPE_CHECKING

import discord
from discord.ext import commands
from discord.app_commands import command, guilds
from mendeleev import element as ELEMENTS
from utils import SERVER_ID, Pages, Source, LATTICES, IMAGES

if TYPE_CHECKING:
    from bot import TMS


async def convert(argument: str) -> ELEMENTS:
    if argument.isdigit():
        if int(argument) > 118 or int(argument) < 1:
            raise commands.BadArgument("`{}` is not a valid element!".format(argument))
        result = ELEMENTS(int(argument))
    else:
        try:
            result = ELEMENTS(argument.title())
        except Exception:
            raise commands.BadArgument("`{}` is not a valid element!".format(argument))
    if not result:
        raise commands.BadArgument("`{}` is not a valid element!".format(argument))
    return result


class Elements(commands.Cog):
    """Display information from the periodic table of elements"""

    def __init__(self, bot: TMS):
        self.bot = bot

    @property
    def display_emoji(self) -> discord.PartialEmoji:
        return discord.PartialEmoji(name="\U0000269b")

    @staticmethod
    def get_lattice_string(element: ELEMENTS) -> str:
        if element.lattice_structure:
            name, link = LATTICES[element.lattice_structure]
            return "[{}]({})".format(name, link)
        else:
            return ""

    @staticmethod
    def get_xray_wavelength(element: ELEMENTS) -> str:
        try:
            ka = 1239.84 / (
                13.6057
                * ((element.atomic_number - 1) ** 2)
                * ((1 / 1**2) - (1 / 2**2))
            )
        except Exception:
            ka = ""
        try:
            kb = 1239.84 / (
                13.6057
                * ((element.atomic_number - 1) ** 2)
                * ((1 / 1**2) - (1 / 3**2))
            )
        except Exception:
            kb = ""
        try:
            la = 1239.84 / (
                13.6057
                * ((element.atomic_number - 7.4) ** 2)
                * ((1 / 1**2) - (1 / 2**3))
            )
        except Exception:
            la = ""
        try:
            lb = 1239.84 / (
                13.6057
                * ((element.atomic_number - 7.4) ** 2)
                * ((1 / 1**2) - (1 / 2**4))
            )
        except Exception:
            lb = ""

        data = "Kα {:.2}".format(ka) if ka else ""
        extra_1 = "Kβ {:.2}".format(kb) if kb else ""
        extra_2 = "Lα {:.2}".format(la) if la else ""
        extra_3 = "Lβ {:.2}".format(lb) if lb else ""
        return ", ".join(x for x in [data, extra_1, extra_2, extra_3] if x)

    @command()
    @guilds(SERVER_ID)
    async def element(
        self,
        interaction: discord.Interaction,
        element: str,
    ) -> None:
        """
        Display information about an element
        `element` can be the name, symbol or atomic number of the element
        """
        element = await convert(argument=element)
        await interaction.response.send_message(embed=await self.element_embed(element))

    @command(name="periodic-table")
    @guilds(SERVER_ID)
    async def periodictable(self, interaction: discord.Interaction) -> None:
        """Display a menu of all elements"""
        await interaction.response.defer(thinking=True)
        embeds = [await self.element_embed(ELEMENTS(e)) for e in range(1, 119)]
        menu = Pages(
            bot=self.bot,
            interaction=interaction,
            source=Source(embeds, per_page=1),
            compact=False,
        )
        await menu.start()

    async def element_embed(self, element: ELEMENTS) -> discord.Embed:
        embed = discord.Embed()
        embed_title = (
            f"[{element.name} ({element.symbol})"
            f" - {element.atomic_number}](https://en.wikipedia.org/wiki/{element.name})"
        )
        embed.description = "{embed_title}\n\n{desc}\n\n{sources}\n\n{uses}".format(
            embed_title=embed_title,
            desc=element.description,
            sources=element.sources,
            uses=element.uses,
        )
        if element.name in IMAGES:
            embed.set_thumbnail(url=IMAGES[element.name]["image"])
        if element.cpk_color:
            embed.colour = int(element.cpk_color.replace("#", ""), 16)
        attributes = {
            "atomic_weight": ("Atomic Weight", ""),
            "melting_point": ("Melting Point", "K"),
            "boiling_point": ("Boiling Point", "K"),
            "density": ("Density", "g/cm³"),
            "abundance_crust": ("Abundance in the Crust", "mg/kg"),
            "abundance_sea": ("Abundance in the Sea", "mg/L"),
            "name_origin": ("Name Origin", ""),
            "lattice_structure": ("Crystal Lattice", self.get_lattice_string(element)),
        }
        for attr, name in attributes.items():
            x = getattr(element, attr, "")
            if x:
                embed.add_field(name=name[0], value=f"{x} {name[1]}")
        embed.add_field(
            name="X-ray Fluorescence", value=self.get_xray_wavelength(element)
        )
        discovery = f"{element.discoverers} ({element.discovery_year}) in {element.discovery_location}"
        embed.add_field(name="Discovery", value=discovery)

        return embed


async def setup(bot: TMS):
    await bot.add_cog(Elements(bot))
