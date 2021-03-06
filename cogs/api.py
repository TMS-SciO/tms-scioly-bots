from __future__ import annotations

from typing import (
    Callable,
    Dict,
    Generator,
    Iterable,
    Literal,
    overload,
    TYPE_CHECKING,
    Optional,
)

from discord.app_commands import command, Group
from discord.ext import commands
import discord
import re
import zlib
import io
import os
import lxml.etree as etree

from utils import SERVER_ID

if TYPE_CHECKING:
    from bot import TMS

RTFM_PAGE_TYPES = {
    "stable": "https://discordpy.readthedocs.io/en/stable",
    "stable-jp": "https://discordpy.readthedocs.io/ja/stable",
    "latest": "https://discordpy.readthedocs.io/en/latest",
    "latest-jp": "https://discordpy.readthedocs.io/ja/latest",
    "python": "https://docs.python.org/3",
    "python-jp": "https://docs.python.org/ja/3",
}


@overload
def finder(
    text: str,
    collection: Iterable[str],
    *,
    key: Optional[Callable[[str], str]] = ...,
    lazy: Literal[False],
) -> list[str]:
    ...


@overload
def finder(
    text: str,
    collection: Iterable[str],
    *,
    key: Optional[Callable[[str], str]] = ...,
    lazy: bool = ...,
) -> Generator[str, None, None] | list[str]:
    ...


def finder(
    text: str,
    collection: Iterable[str],
    *,
    key: Optional[Callable[[str], str]] = ...,
    lazy: bool = True,
) -> Generator[str, None, None] | list[str]:
    suggestions: list[tuple[int, int, str]] = []
    text = str(text)
    pat = ".*?".join(map(re.escape, text))
    regex = re.compile(pat, flags=re.IGNORECASE)
    for item in collection:
        to_search = key(item) if key else item
        r = regex.search(to_search)
        if r:
            suggestions.append((len(r.group()), r.start(), item))

    def sort_key(tup: tuple[int, int, str]) -> tuple[int, int, str]:
        if key:
            return tup[0], tup[1], key(tup[2])
        return tup

    if lazy:
        return (z for _, _, z in sorted(suggestions, key=sort_key))
    else:
        return [z for _, _, z in sorted(suggestions, key=sort_key)]


class SphinxObjectFileReader:
    # Inspired by Sphinx's InventoryFileReader
    BUFSIZE = 16 * 1024

    def __init__(self, buffer):
        self.stream = io.BytesIO(buffer)

    def readline(self):
        return self.stream.readline().decode("utf-8")

    def skipline(self):
        self.stream.readline()

    def read_compressed_chunks(self):
        decompressor = zlib.decompressobj()
        while True:
            chunk = self.stream.read(self.BUFSIZE)
            if len(chunk) == 0:
                break
            yield decompressor.decompress(chunk)
        yield decompressor.flush()

    def read_compressed_lines(self):
        buf = b""
        for chunk in self.read_compressed_chunks():
            buf += chunk
            pos = buf.find(b"\n")
            while pos != -1:
                yield buf[:pos].decode("utf-8")
                buf = buf[pos + 1 :]
                pos = buf.find(b"\n")


class RtfmGroup(Group):
    def __init__(self, bot: TMS):
        self.bot = bot
        super().__init__(name="rtfm", guild_ids=[SERVER_ID])

    @property
    def cog(self) -> commands.Cog:
        return self.bot.get_cog("API")

    def parse_object_inv(self, stream, url):
        # key: URL
        # n.b.: key doesn't have `discord` or `discord.ext.commands` namespaces
        result = {}

        # first line is version info
        inv_version = stream.readline().rstrip()

        if inv_version != "# Sphinx inventory version 2":
            raise RuntimeError("Invalid objects.inv file version.")

        # next line is "# Project: <name>"
        # then after that is "# Version: <version>"
        projname = stream.readline().rstrip()[11:]
        version = stream.readline().rstrip()[11:]

        # next line says if it's a zlib header
        line = stream.readline()
        if "zlib" not in line:
            raise RuntimeError("Invalid objects.inv file, not z-lib compatible.")

        # This code mostly comes from the Sphinx repository.
        entry_regex = re.compile(r"(?x)(.+?)\s+(\S*:\S*)\s+(-?\d+)\s+(\S+)\s+(.*)")
        for line in stream.read_compressed_lines():
            match = entry_regex.match(line.rstrip())
            if not match:
                continue

            name, directive, prio, location, dispname = match.groups()
            domain, _, subdirective = directive.partition(":")
            if directive == "py:module" and name in result:
                # From the Sphinx Repository:
                # due to a bug in 1.1 and below,
                # two inventory entries are created
                # for Python modules, and the first
                # one is correct
                continue

            # Most documentation pages have a label
            if directive == "std:doc":
                subdirective = "label"

            if location.endswith("$"):
                location = location[:-1] + name

            key = name if dispname == "-" else dispname
            prefix = f"{subdirective}:" if domain == "std" else ""

            if projname == "discord.py":
                key = key.replace("discord.ext.commands.", "").replace("discord.", "")

            result[f"{prefix}{key}"] = os.path.join(url, location)

        return result

    async def build_rtfm_lookup_table(self):
        cache = {}
        for key, page in RTFM_PAGE_TYPES.items():
            cache[key] = {}
            async with self.bot.session.get(page + "/objects.inv") as resp:
                if resp.status != 200:
                    raise RuntimeError(
                        "Cannot build rtfm lookup table, try again later."
                    )

                stream = SphinxObjectFileReader(await resp.read())
                cache[key] = self.parse_object_inv(stream, page)

        self._rtfm_cache = cache

    async def do_rtfm(
        self, interaction: discord.Interaction, key: str, obj: Optional[str]
    ):
        await interaction.response.defer()

        if obj is None:
            return await interaction.followup.send(RTFM_PAGE_TYPES[key])

        if not hasattr(self, "_rtfm_cache"):
            await self.build_rtfm_lookup_table()

        obj = re.sub(r"^(?:discord\.(?:ext\.)?)?(?:commands\.)?(.+)", r"\1", obj)

        if key.startswith("latest"):
            # point the abc.Messageable types properly:
            q = obj.lower()
            for name in dir(discord.abc.Messageable):
                if name[0] == "_":
                    continue
                if q == name:
                    obj = f"abc.Messageable.{name}"
                    break

        cache = list(self._rtfm_cache[key].items())
        matches = finder(obj, cache, key=lambda t: t[0], lazy=False)[:8]

        e = discord.Embed(colour=discord.Colour.blurple())
        if len(matches) == 0:
            return await interaction.followup.send("Could not find anything. Sorry.")

        e.description = "\n".join(f"[`{key}`]({url})" for key, url in matches)
        return await interaction.followup.send(embed=e)

    @command(name="python")
    async def rtfm_python(self, interaction: discord.Interaction, *, obj: str = None):
        """Gives you a documentation link for a Python entity."""
        await self.do_rtfm(interaction, "python", obj)

    @command(name="master")
    async def rtfm_master(self, interaction: discord.Interaction, *, obj: str = None):
        """Gives you a documentation link for a discord.py entity (master branch)"""
        await self.do_rtfm(interaction, "latest", obj)

    @command(name="refresh")
    @commands.is_owner()
    async def rtfm_refresh(self, interaction: discord.Interaction):
        """Refreshes the RTFM and FAQ cache"""

        await interaction.response.defer()
        await self.build_rtfm_lookup_table()
        await self.refresh_faq_cache()

        await interaction.followup.send("\N{THUMBS UP SIGN}")

    async def refresh_faq_cache(self):
        self.faq_entries = {}
        base_url = "https://discordpy.readthedocs.io/en/latest/faq.html"
        async with self.bot.session.get(base_url) as resp:
            text = await resp.text(encoding="utf-8")

            root = etree.fromstring(text, etree.HTMLParser())
            nodes = root.findall(".//div[@id='questions']/ul[@class='simple']/li/ul//a")
            for node in nodes:
                self.faq_entries["".join(node.itertext()).strip()] = (
                    base_url + node.get("href").strip()
                )


class API(commands.Cog):
    """Discord API exclusive things."""

    faq_entries: Dict[str, str]

    def __init__(self, bot: TMS):
        self.bot: TMS = bot
        self.issue = re.compile(r"##(?P<number>\d+)")
        self.__cog_app_commands__.append(RtfmGroup(bot))

    @property
    def display_emoji(self) -> discord.PartialEmoji:
        return discord.PartialEmoji(name="\N{PERSONAL COMPUTER}")


async def setup(bot: TMS):
    await bot.add_cog(API(bot))
