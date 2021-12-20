import discord
from discord.ext import commands
from discord.ext.commands.errors import BadArgument
from discord import slash_command
from utils.element_info import LATTICES, IMAGES
from mendeleev import element as ELEMENTS
from utils.paginate import Pages, Source
from utils.variables import SERVER_ID

# CREDIT -> https://github.com/TrustyJAID/Trusty-cogs/tree/master/elements


async def convert(argument: str) -> ELEMENTS:
    if argument.isdigit():
        if int(argument) > 118 or int(argument) < 1:
            raise BadArgument("`{}` is not a valid element!".format(argument))
        result = ELEMENTS(int(argument))
    else:
        try:
            result = ELEMENTS(argument.title())
        except Exception:
            raise BadArgument("`{}` is not a valid element!".format(argument))
    if not result:
        raise BadArgument("`{}` is not a valid element!".format(argument))
    return result


class Elements(commands.Cog):
    """Display information from the periodic table of elements"""

    def __init__(self, bot):
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
                    13.6057 * ((element.atomic_number - 1) ** 2) * ((1 / 1 ** 2) - (1 / 2 ** 2))
            )
        except Exception:
            ka = ""
        try:
            kb = 1239.84 / (
                    13.6057 * ((element.atomic_number - 1) ** 2) * ((1 / 1 ** 2) - (1 / 3 ** 2))
            )
        except Exception:
            kb = ""
        try:
            la = 1239.84 / (
                    13.6057 * ((element.atomic_number - 7.4) ** 2) * ((1 / 1 ** 2) - (1 / 2 ** 3))
            )
        except Exception:
            la = ""
        try:
            lb = 1239.84 / (
                    13.6057 * ((element.atomic_number - 7.4) ** 2) * ((1 / 1 ** 2) - (1 / 2 ** 4))
            )
        except Exception:
            lb = ""

        data = "Kα {:.2}".format(ka) if ka else ""
        extra_1 = "Kβ {:.2}".format(kb) if kb else ""
        extra_2 = "Lα {:.2}".format(la) if la else ""
        extra_3 = "Lβ {:.2}".format(lb) if lb else ""
        return ", ".join(x for x in [data, extra_1, extra_2, extra_3] if x)

    @slash_command(guild_ids=[SERVER_ID])
    async def element(
            self,
            ctx: discord.ApplicationContext,
            element: str,
    ) -> discord.InteractionResponse:
        """
        Display information about an element
        `element` can be the name, symbol or atomic number of the element
        """
        await ctx.defer()
        element = await convert(argument=element)
        return await ctx.respond(embed=await self.element_embed(element))

    @slash_command(guild_ids=[SERVER_ID])
    async def periodictable(
            self,
            ctx: discord.ApplicationContext
    ) -> None:
        """Display a menu of all elements"""
        await ctx.defer()
        embeds = [await self.element_embed(ELEMENTS(e)) for e in range(1, 119)]
        menu = Pages(ctx=ctx, source=Source(embeds, per_page=1), compact=True)
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
        embed.add_field(name="X-ray Fluorescence", value=self.get_xray_wavelength(element))
        discovery = (
            f"{element.discoverers} ({element.discovery_year}) in {element.discovery_location}"
        )
        embed.add_field(name="Discovery", value=discovery)

        return embed


def setup(bot):
    bot.add_cog(Elements(bot))
