import asyncio
import os

import discord
import functools
import re
import textwrap
from collections import namedtuple
from textwrap import shorten
from urllib.parse import quote_plus

from bs4 import BeautifulSoup
from discord.commands import slash_command
from discord.ext import commands
from html2text import html2text as h2t

from utils.variables import SERVER_ID
from utils.paginate import Pages, Source

s = namedtuple("searchres", "url title desc")


class Google(commands.Cog):
    '''
    Google Related Commands
    '''

    def __init__(self, bot):
        self.nsfwcheck = lambda ctx: (not ctx.guild) or ctx.channel.is_nsfw()
        self.bot = bot
        self.options = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36",
            "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
        }

    print("Google Cog Loaded")

    @property
    def display_emoji(self) -> discord.PartialEmoji:
        return discord.PartialEmoji(name="google", id=922144879046438942)

    def parser_text(self, text, soup=None, cards: bool = True):
        """My bad logic for scraping"""
        if not soup:
            soup = BeautifulSoup(text, features="html.parser")

        final = []
        kwargs = {"stats": h2t(str(soup.find("div", id="result-stats")))}

        if cards:
            self.get_card(soup, final, kwargs)

        for res in soup.findAll("div", class_="g"):
            if name := res.find("div", class_="yuRUbf"):
                url = name.a["href"]
                if title := name.find("h3", class_=re.compile("LC20lb")):
                    title = title.text
                else:
                    title = url
            else:
                url = None
                title = None
            if desc := res.find("div", class_="IsZvec"):
                if remove := desc.find("span", class_="f"):
                    remove.decompose()
                if final_desc := desc.find_all("div", class_="VwiC3b"):
                    desc = h2t(str(final_desc[-1]))[:500]
                else:
                    desc = "Nothing found"
            else:
                desc = "Not found"
            if title:
                final.append(s(url, title, desc.replace("\n", " ")))
        return final, kwargs

    async def get_result(self, query, images=False, nsfw=False):
        """Fetch the data"""
        encoded = quote_plus(query, encoding="utf-8", errors="replace")

        async def get_html(url, encoded):
            async with self.bot.session.get(url + encoded, headers=self.options) as resp:
                self.cookies = resp.cookies
                return await resp.text(), resp.url

        if not nsfw:
            encoded += "&safe=active"

        # TYSM fixator, for the non-js query url
        url = (
            "https://www.google.com/search?tbm=isch&q="
            if images
            else "https://www.google.com/search?q="
        )
        text, redir = await get_html(url, encoded)
        prep = functools.partial(self.parser_image if images else self.parser_text, text)

        fin, kwargs = await self.bot.loop.run_in_executor(None, prep)
        kwargs["redir"] = redir
        return fin, kwargs

    @slash_command(guild_ids=[SERVER_ID])
    async def google(self, ctx: discord.ApplicationContext, *, query: str):
        """Google search your query from Discord channel."""
        if not query:
            return await ctx.send("Please enter something to search")

        isnsfw = self.nsfwcheck(ctx)
        await ctx.defer()
        response, kwargs = await self.get_result(query, nsfw=isnsfw)
        pages = []
        groups = [response[n: n + 3] for n in range(0, len(response), 3)]
        for num, group in enumerate(groups, 1):
            emb = discord.Embed(
                title="Google Search: {}".format(
                    query[:44] + "\N{HORIZONTAL ELLIPSIS}" if len(query) > 45 else query
                ),
                color=0x4285F4,
                url=kwargs["redir"],
            )
            emb.set_author(
                name="Google",
                icon_url="https://i.imgur.com/N3oHABo.png",
            )
            for result in group:
                desc = (
                           f"[{result.url[:60]}]({result.url})\n" if result.url else ""
                       ) + f"{result.desc}"[:800]
                emb.add_field(
                    name=f"{result.title}",
                    value=desc or "Nothing",
                    inline=False,
                )
            emb.description = f"Page {num} of {len(groups)}"
            emb.set_footer(
                text=f"Safe Search: {not isnsfw} | " + kwargs["stats"].replace("\n", " ")
            )
            if "thumbnail" in kwargs:
                emb.set_thumbnail(url=kwargs["thumbnail"])

            if "image" in kwargs and num == 1:
                emb.set_image(url=kwargs["image"])
            pages.append(emb)
        if pages:
            menu = Pages(ctx=ctx, source=Source(pages, per_page=1), compact=True)
            await menu.start()
        else:
            await ctx.respond("No results.")

    def get_card(self, soup, final, kwargs):
        """Getting cards if present, here started the pain"""
        # common card
        if card := soup.find("div", class_="g mnr-c g-blk"):
            if desc := card.find("span", class_="hgKElc"):
                final.append(s(None, "Google Info Card:", h2t(str(desc))))
                return
        # another webpull card: what is the language JetBrains made?
        if card := soup.find("div", class_="kp-blk c2xzTb"):
            if head := card.find("div", class_="Z0LcW XcVN5d AZCkJd"):
                if desc := card.find("div", class_="iKJnec"):
                    final.append(s(None, f"Answer: {head.text}", h2t(str(desc))))
                    return

        # calculator card
        if card := soup.find("div", class_="tyYmIf"):
            if question := card.find("span", class_="vUGUtc"):
                if answer := card.find("span", class_="qv3Wpe"):
                    tmp = h2t(str(question)).strip("\n")
                    final.append(s(None, "Google Calculator:", f"**{tmp}** {h2t(str(answer))}"))
                    return

        # sidepage card
        if card := soup.find("div", class_="osrp-blk"):
            if thumbnail := card.find("g-img", attrs={"data-lpage": True}):
                kwargs["thumbnail"] = thumbnail["data-lpage"]
            if title := card.find("div", class_=re.compile("ZxoDOe")):
                if desc := soup.find("div", class_=re.compile("qDOt0b|kno-rdesc")):
                    if remove := desc.find(class_=re.compile("Uo8X3b")):
                        remove.decompose()

                    desc = textwrap.shorten(h2t(str(desc.span)), 1024, placeholder="...") + "\n"

                    if more_info := soup.findAll("div", class_="Z1hOCe"):
                        for thing in more_info:
                            tmp = thing.findAll("span")
                            if len(tmp) >= 2:
                                desc2 = f"\n **{tmp[0].text}**`{tmp[1].text.lstrip(':')}`"
                                # More jack advises :D
                                MAX = 1024
                                MAX_LEN = MAX - len(desc2)
                                if len(desc) > MAX_LEN:
                                    desc = (
                                            next(
                                                self.pagify(
                                                    desc,
                                                    deliminators=[" ", "\n"],
                                                    page_length=MAX_LEN - 1,
                                                    shorten_by=0,
                                                )
                                            )
                                            + "\N{HORIZONTAL ELLIPSIS}"
                                    )
                                desc = desc + desc2
                    final.append(
                        s(
                            None,
                            "Google Featured Card: "
                            + h2t(str(title)).replace("\n\n", "\n").replace("#", ""),
                            desc,
                        )
                    )
                return

        # time cards and unit conversions and moar-_- WORK ON THIS, THIS IS BAD STUFF 100
        if card := soup.find("div", class_="vk_c"):
            if conversion := card.findAll("div", class_="rpnBye"):
                if len(conversion) != 2:
                    return
                tmp = tuple(
                    map(
                        lambda thing: (
                            thing.input["value"],
                            thing.findAll("option", selected=True)[0].text,
                        ),
                        conversion,
                    )
                )
                final.append(
                    s(
                        None,
                        "Unit Conversion v1:",
                        "`" + " ".join(tmp[0]) + " is equal to " + " ".join(tmp[1]) + "`",
                    )
                )
                return
            elif card.find("div", "lu_map_section"):
                if img := re.search(r"\((.*)\)", h2t(str(card)).replace("\n", "")):
                    kwargs["image"] = "https://www.google.com" + img[1]
                    return
            else:
                # time card
                if tail := card.find("table", class_="d8WIHd"):
                    tail.decompose()
                tmp = h2t(str(card)).replace("\n\n", "\n").split("\n")
                final.append(s(None, tmp[0], "\n".join(tmp[1:])))
                return

        # translator cards
        if card := soup.find("div", class_="tw-src-ltr"):
            langs = soup.find("div", class_="pcCUmf")
            src_lang = "**" + langs.find("span", class_="source-language").text + "**"
            dest_lang = "**" + langs.find("span", class_="target-language").text + "**"
            final_text = ""
            if source := card.find("div", id="KnM9nf"):
                final_text += (src_lang + "\n`" + source.find("pre").text) + "`\n"
            if dest := card.find("div", id="kAz1tf"):
                final_text += dest_lang + "\n`" + dest.find("pre").text.strip("\n") + "`"
            final.append(s(None, "Google Translator", final_text))
            return

        # Unit conversions
        if card := soup.find("div", class_="nRbRnb"):
            final_text = "\N{ZWSP}\n**"
            if source := card.find("div", class_="vk_sh c8Zgcf"):
                final_text += "`" + h2t(str(source)).strip("\n")
            if dest := card.find("div", class_="dDoNo ikb4Bb gsrt gzfeS"):
                final_text += " " + h2t(str(dest)).strip("\n") + "`**"
            if time := card.find("div", class_="hqAUc"):
                if remove := time.find("select"):
                    remove.decompose()
                tmp = h2t(str(time)).replace("\n", " ").split("·")
                final_text += (
                        "\n"
                        + (f"`{tmp[0].strip()}` ·{tmp[1]}" if len(tmp) == 2 else "·".join(tmp))
                        + "\n\N{ZWSP}"
                )
            final.append(s(None, "Unit Conversion", final_text))
            return

        # Definition cards -
        if card := soup.find("div", class_="KIy09e"):
            final_text = ""
            if word := card.find("div", class_="ya2TWb"):
                if sup := word.find("sup"):
                    sup.decompose()
                final_text += "`" + word.text + "`"

            if pronounciate := card.find("div", class_="S23sjd"):
                final_text += "   |   " + pronounciate.text

            if type_ := card.find("span", class_="YrbPuc"):
                final_text += "   |   " + type_.text + "\n\n"

            if definition := card.find("div", class_="LTKOO sY7ric"):
                if remove_flex_row := definition.find(class_="bqVbBf jfFgAc CqMNyc"):
                    remove_flex_row.decompose()

                for text in definition.findAll("span"):
                    tmp = h2t(str(text))
                    if tmp.count("\n") < 5:
                        final_text += "`" + tmp.strip("\n").replace("\n", " ") + "`" + "\n"

            final.append(s(None, "Definition", final_text))
            return

        # single answer card
        if card := soup.find("div", class_="ayRjaf"):
            final.append(
                s(
                    None,
                    h2t(str(card.find("div", class_="zCubwf"))).replace("\n", ""),
                    h2t(str(card.find("span").find("span"))).strip("\n") + "\n\N{ZWSP}",
                )
            )
            return
        # another single card?
        if card := soup.find("div", class_="sXLaOe"):
            final.append(s(None, "Single Answer Card:", card.text))
            return

    @slash_command(guild_ids=[SERVER_ID])
    async def book(self, ctx: discord.ApplicationContext, *, query: str):
        """Search for a book or magazine on Google Books.
        This command requires an API key. If you are the bot owner,
        you can follow instructions on below link for how to get one:
        https://gist.github.com/ow0x/53d2dbf0f753a01b7579cd8c68edbf90
        There are special keywords you can specify in the query to search in particular fields.
        You can read more on that in detail over at:
        https://developers.google.com/books/docs/v1/using#PerformingSearch
        """
        api_key = os.getenv("GOOGLE_API_KEY")

        await ctx.defer()
        base_url = "https://www.googleapis.com/books/v1/volumes"
        params = {
            "apiKey": api_key,
            "q": query,
            "printType": "all",
            "maxResults": 20,
            "orderBy": "relevance",
        }
        try:
            async with self.bot.session.get(base_url, params=params) as response:
                if response.status != 200:
                    return await ctx.send(f"https://http.cat/{response.status}")
                data = await response.json()
        except asyncio.TimeoutError:
            return await ctx.send("Operation timed out.")

        if len(data.get("items")) == 0:
            return await ctx.send("No results.")

        pages = []
        for i, info in enumerate(data.get("items")):
            embed = discord.Embed(colour=0x4285F4)
            embed.title = info.get("volumeInfo").get("title")
            embed.url = info.get("volumeInfo").get("canonicalVolumeLink")
            summary = info.get("volumeInfo").get("description", "No summary.")
            embed.description = shorten(summary, 500, placeholder="...")
            embed.set_author(
                name="Google Books",
                url="https://books.google.com/",
                icon_url="https://i.imgur.com/N3oHABo.png",
            )
            if info.get("volumeInfo").get("imageLinks"):
                embed.set_thumbnail(
                    url=info.get("volumeInfo").get("imageLinks").get("thumbnail")
                )
            embed.add_field(
                name="Published Date",
                value=info.get("volumeInfo").get("publishedDate", "Unknown"),
            )
            if info.get("volumeInfo").get("authors"):
                embed.add_field(
                    name="Authors",
                    value=", ".join(info.get("volumeInfo").get("authors")),
                )
            embed.add_field(
                name="Publisher",
                value=info.get("volumeInfo").get("publisher", "Unknown"),
            )
            if info.get("volumeInfo").get("pageCount"):
                embed.add_field(
                    name="Page Count",
                    value=(info.get("volumeInfo").get("pageCount")),
                )
            embed.add_field(
                name="Web Reader Link",
                value=f"[Click here!]({info.get('accessInfo').get('webReaderLink')})",
            )
            if info.get("volumeInfo").get("categories"):
                embed.add_field(
                    name="Category",
                    value=", ".join(info.get("volumeInfo").get("categories")),
                )
            if info.get("saleInfo").get("retailPrice"):
                currency_format = (
                    f"[{info.get('saleInfo').get('retailPrice').get('amount')} "
                    f"{info.get('saleInfo').get('retailPrice').get('currencyCode')}]"
                    f"({info.get('saleInfo').get('buyLink')} 'Click to buy on Google Books!')"
                )
                embed.add_field(
                    name="Retail Price",
                    value=currency_format,
                )
            epub_available = (
                "✅" if info.get("accessInfo").get("epub").get("isAvailable") else "❌"
            )
            pdf_available = (
                "✅" if info.get("accessInfo").get("pdf").get("isAvailable") else "❌"
            )
            if info.get("accessInfo").get("epub").get("downloadLink"):
                epub_available += (
                    " [`Download Link`]"
                    f"({info.get('accessInfo').get('epub').get('downloadLink')})"
                )
            if info.get("accessInfo").get("pdf").get("downloadLink"):
                pdf_available += (
                    " [`Download Link`]"
                    f"({info.get('accessInfo').get('pdf').get('downloadLink')})"
                )
            embed.add_field(name="EPUB available?", value=epub_available)
            embed.add_field(name="PDF available?", value=pdf_available)
            viewablility = (
                f"{info.get('accessInfo').get('viewability').replace('_', ' ').title()}"
            )
            embed.add_field(name="Viewablility", value=viewablility)
            embed.set_footer(text=f"Page {i + 1} of {len(data.get('items'))}")
            pages.append(embed)

        if len(pages) == 1:
            await ctx.respond(embed=pages[0])
        else:
            menu = Pages(ctx=ctx, source=Source(pages, per_page=1), compact=True)
            await menu.start()


def setup(bot):
    bot.add_cog(Google(bot))
