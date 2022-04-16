from __future__ import annotations

import discord
from discord.ext import commands
from utils.paginate import Pages, Source
import aiohttp
import re
from typing import List, TYPE_CHECKING
from discord.app_commands import command, guilds
from utils.variables import *
from dateutil.parser import isoparse

if TYPE_CHECKING:
    from bot import TMS


class Wikipedia(commands.Cog):
    """Look up stuff on Wikipedia."""

    def __init__(self, bot: TMS):
        self.bot = bot

    @property
    def display_emoji(self) -> discord.PartialEmoji:
        return discord.PartialEmoji(name="wikipedia", id=922148836871385119)

    DISAMBIGUATION_CAT = "Category:All disambiguation pages"
    WHITESPACE = re.compile(r"[\n\s]{4,}")
    NEWLINES = re.compile(r"\n+")

    @command()
    @guilds(SERVER_ID)
    async def wikipedia(self, interaction: discord.Interaction, query: str):
        """Get information from Wikipedia."""
        embeds, url = await self.perform_search(query)

        if not embeds:
            return await interaction.response.send_message(
                f"I'm sorry, I couldn't find \"{query}\" on Wikipedia",
                embed=embeds[0]
            )
        elif len(embeds) == 1:
            embeds[0].set_author(name="Result 1 of 1")
            return await interaction.response.send_message(embed=embeds[0])
        else:
            count = 0
            for embed in embeds:
                count += 1
                embed.set_author(name=f"Result {count} of {len(embeds)}")
            menu = Pages(interaction=interaction, source=Source(embeds, per_page=1), compact=True, bot=self.bot)
            await menu.start()

    #
    # Public methods
    #

    def generate_payload(self, query: str):
        """Generate the payload for Wikipedia based on a query string."""
        query_tokens = query.split()
        payload = {
            # Main module
            "action": "query",  # Fetch data from and about MediaWiki
            "format": "json",  # Output data in JSON format
            # format:json options
            "formatversion": "2",  # Modern format
            # action:query options
            "generator": "search",  # Get list of pages by executing a query module
            "redirects": "1",  # Automatically resolve redirects
            "prop": "extracts|info|pageimages|revisions|categories",  # Which properties to get
            # action:query/generator:search options
            "gsrsearch": f"intitle:{' intitle:'.join(query_tokens)}",  # Search for page titles
            # action:query/prop:extracts options
            "exintro": "1",  # Return only content before the first section
            "explaintext": "1",  # Return extracts as plain text
            # action:query/prop:info options
            "inprop": "url",  # Gives a full URL for each page
            # action:query/prop:pageimages options
            "piprop": "original",  # Return URL of page image, if any
            # action:query/prop:revisions options
            "rvprop": "timestamp",  # Return timestamp of last revision
            # action:query/prop:revisions options
            "clcategories": self.DISAMBIGUATION_CAT,  # Only list this category
        }
        return payload

    async def perform_search(self, query, only_first_result: bool = False):
        """Query Wikipedia."""
        payload = self.generate_payload(query)
        async with aiohttp.ClientSession() as session:
            async with session.get(
                    "https://en.wikipedia.org/w/api.php",
                    params=payload,
            ) as res:
                result = await res.json()

        embeds: List[discord.Embed] = []
        if "query" in result and "pages" in result["query"]:
            result["query"]["pages"].sort(
                key=lambda unsorted_page: unsorted_page["index"]
            )
            for page in result["query"]["pages"]:
                try:
                    if (
                            "categories" in page
                            and page["categories"]
                            and "title" in page["categories"][0]
                            and page["categories"][0]["title"] == self.DISAMBIGUATION_CAT
                    ):
                        continue  # Skip disambiguation pages
                    embeds.append(self.generate_embed(page))
                    if only_first_result:
                        return embeds, page["fullurl"]
                except KeyError:
                    pass
        return embeds, None

    def generate_embed(self, page_json):
        """Generate the embed for the json page."""
        title = page_json["title"]
        description: str = page_json["extract"].strip()
        image = (
            page_json["original"]["source"]
            if "original" in page_json and "source" in page_json["original"]
            else None
        )
        url = page_json["fullurl"]
        timestamp = (
            isoparse(page_json["revisions"][0]["timestamp"])
            if "revisions" in page_json
               and page_json["revisions"]
               and "timestamp" in page_json["revisions"][0]
            else None
        )

        whitespace_location = None
        whitespace_check_result = self.WHITESPACE.search(description)
        if whitespace_check_result:
            whitespace_location = whitespace_check_result.start()
        if whitespace_location:
            description = description[:whitespace_location].strip()
        description = self.NEWLINES.sub("\n\n", description)
        if len(description) > 1000 or whitespace_location:
            description = description[:1000].strip()
            description += f"... [(read more)]({url})"

        embed = discord.Embed(
            title=f"Wikipedia: {title}",
            description=description,
            color=discord.Color.blue(),
            url=url,
            timestamp=timestamp,
        )
        if image:
            embed.set_image(url=image)
        text = "Information provided by Wikimedia"
        if timestamp:
            text += "\nArticle last updated"
        embed.set_footer(
            text=text,
            icon_url=(
                "https://upload.wikimedia.org/wikipedia/commons/thumb/5/53/Wikimedia-logo.png"
                "/600px-Wikimedia-logo.png"
            ),
        )
        return embed


async def setup(bot: TMS):
    await bot.add_cog(Wikipedia(bot))
