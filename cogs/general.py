from __future__ import annotations

import asyncio
import datetime
import os
from collections import Counter
from typing import Literal, Optional, TYPE_CHECKING

import discord
import pkg_resources
import psutil
from discord.app_commands import command, Group, guilds
from discord.ext import commands

from utils import times
from utils.checks import is_not_blacklisted
from utils.rules import RULES
from utils.variables import *

if TYPE_CHECKING:
    from bot import TMS


class BotGroup(Group):
    def __init__(self, bot: TMS):
        self.bot = bot
        self.process = psutil.Process()
        self.launch_time = datetime.datetime.utcnow()
        super().__init__(name="bot", guild_ids=[SERVER_ID])

    @property
    def cog(self) -> commands.Cog:
        return self.bot.get_cog("General")

    @staticmethod
    async def say_permissions(interaction: discord.Interaction, member, channel):
        permissions = channel.permissions_for(member)
        e = discord.Embed(colour=member.colour)
        avatar = member.display_avatar.with_static_format("png")
        e.set_author(name=str(member), url=avatar)
        allowed, denied = [], []
        for name, value in permissions:
            name = name.replace("_", " ").replace("guild", "server").title()
            if value:
                allowed.append(name)
            else:
                denied.append(name)

        e.add_field(name="Allowed", value="\n".join(allowed))
        e.add_field(name="Denied", value="\n".join(denied))
        await interaction.response.send_message(embed=e)

    def get_bot_uptime(self) -> str:
        delta_uptime = datetime.datetime.utcnow() - self.launch_time
        hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)
        uptime = f"{days} Days, {hours} Hours, {minutes} Minutes, {seconds} Seconds"
        return uptime

    @command(name="permissions")
    async def _permissions(
        self, interaction: discord.Interaction, channel: Optional[discord.TextChannel]
    ):
        """Shows the bot's permissions in a specific channel.
        If no channel is given then it uses the current one.
        This is a good way of checking if the bot has the permissions needed
        to execute the commands it wants to execute.
        To execute this command you must have Manage Roles permission.
        You cannot use this in private messages.
        """
        channel = channel or interaction.channel
        member = interaction.guild.me
        await self.say_permissions(interaction, member, channel)

    @command()
    async def uptime(self, interaction: discord.Interaction):
        """Sends how long the bot has been online"""
        uptime = self.get_bot_uptime()
        await interaction.response.send_message(f"**{uptime}**")

    #
    # @_bot.command()
    # async def socketstats(self, interaction):
    #     delta = discord.utils.utcnow() - self.bot.uptime
    #     minutes = delta.total_seconds() / 60
    #     total = sum(self.bot.socket_stats.values())
    #     cpm = total / minutes

    #     await interaction.response.send_message(f'{total} socket events observed ({cpm:.2f}/minute):\n{self.bot.socket_stats}')
    @command()
    async def about(self, interaction: discord.Interaction):
        """Tells you information about the bot itself."""

        # revision = Github.get_last_commits(self, count=5)
        embed = discord.Embed()  # description='Latest Changes:\n' + revision)
        # embed = discord.Embed(description='Latest Changes:\n')
        embed.colour = discord.Colour.blurple()

        # To properly cache myself, I need to use the bot support server.
        support_guild = self.bot.get_guild(816806329925894217)
        owner = await support_guild.get_member(747126643587416174)
        name = str(owner)
        embed.set_author(
            name=name,
            icon_url=owner.display_avatar.url,
            url="https://github.com/pandabear189",
        )

        # statistics
        total_members = 0
        total_unique = len(self.bot.users)

        text = 0
        voice = 0
        guilds = 0
        for guild in self.bot.guilds:
            guilds += 1
            if guild.unavailable:
                continue

            total_members += guild.member_count
            for channel in guild.channels:
                if isinstance(channel, discord.TextChannel):
                    text += 1
                elif isinstance(channel, discord.VoiceChannel):
                    voice += 1

        embed.add_field(
            name="Members", value=f"{total_members} total\n{total_unique} unique"
        )
        embed.add_field(
            name="Channels", value=f"{text + voice} total\n{text} text\n{voice} voice"
        )

        memory_usage = self.process.memory_full_info().uss / 1024**2
        cpu_usage = self.process.cpu_percent() / psutil.cpu_count()
        embed.add_field(
            name="Process", value=f"{memory_usage:.2f} MiB\n{cpu_usage:.2f}% CPU"
        )

        dpyversion = pkg_resources.get_distribution("py-cord").version
        embed.add_field(name="Guilds", value=guilds)
        embed.add_field(
            name="Number of Commands",
            value=(len(self.bot.commands) + len(self.bot.tree.get_commands())),
        )
        uptime = self.get_bot_uptime()
        embed.add_field(name="Uptime", value=uptime)
        embed.set_footer(
            text=f"Made with discord.py v{dpyversion}",
            icon_url="https://i.imgur.com/RPrw70n.png",
        )
        embed.timestamp = discord.utils.utcnow()
        await interaction.response.send_message(embed=embed)

    @command(name="health")
    async def _health(self, interaction: discord.Interaction):
        """Various bot health monitoring tools."""

        # This uses a lot of private methods because there is no
        # clean way of doing this otherwise.

        HEALTHY = discord.Colour.brand_green()
        UNHEALTHY = discord.Colour.brand_red()

        total_warnings = 0

        embed = discord.Embed(title="Bot Health Report", colour=HEALTHY)

        description = []

        task_retriever = asyncio.all_tasks
        all_tasks = task_retriever(loop=self.bot.loop)

        event_tasks = [
            t for t in all_tasks if "Client._run_event" in repr(t) and not t.done()
        ]

        cogs_directory = os.path.dirname(__file__)
        tasks_directory = os.path.join("discord", "ext", "tasks", "__init__.py")
        inner_tasks = [
            t
            for t in all_tasks
            if cogs_directory in repr(t) or tasks_directory in repr(t)
        ]

        bad_inner_tasks = ", ".join(
            hex(id(t)) for t in inner_tasks if t.done() and t._exception is not None
        )
        total_warnings += bool(bad_inner_tasks)
        embed.add_field(
            name="Inner Tasks",
            value=f'Total: {len(inner_tasks)}\nFailed: {bad_inner_tasks or "None"}',
        )
        embed.add_field(
            name="Events Waiting", value=f"Total: {len(event_tasks)}", inline=False
        )

        memory_usage = self.process.memory_full_info().uss / 1024**2
        cpu_usage = self.process.cpu_percent() / psutil.cpu_count()
        embed.add_field(
            name="Process",
            value=f"{memory_usage:.2f} MiB\n{cpu_usage:.2f}% CPU",
            inline=False,
        )

        ws_rate_limit = self.bot.is_ws_ratelimited()
        description.append(f"Websocket Rate Limit: {ws_rate_limit}")

        global_rate_limit = self.bot.http._global_over.set()
        description.append(f"Global Rate Limit: {global_rate_limit}")

        if ws_rate_limit or total_warnings >= 3 or len(event_tasks) >= 4:
            embed.colour = UNHEALTHY

        embed.set_footer(text=f"{total_warnings} warning(s)")
        embed.description = "\n".join(description)
        await interaction.response.send_message(embed=embed)


class General(commands.Cog):
    """General commands."""

    print("GeneralCommands Cog Loaded")

    def __init__(self, bot: TMS):
        self.bot = bot
        self.__cog_app_commands__.append(BotGroup(bot))

    @property
    def display_emoji(self) -> discord.PartialEmoji:
        return discord.PartialEmoji(name="\U0001f62f")

    async def cog_check(self, interaction) -> bool:
        return await is_not_blacklisted(interaction)

    def cog_unload(self) -> None:
        pass

    @staticmethod
    async def _basic_cleanup_strategy(interaction: discord.Interaction, search):
        count = 0
        async for msg in interaction.channel.history(
            limit=search, before=interaction.message
        ):
            if msg.author == interaction.guild.me and not (
                msg.mentions or msg.role_mentions
            ):
                await msg.delete()
                count += 1
        return {"Bot": count}

    @staticmethod
    async def _complex_cleanup_strategy(interaction: discord.Interaction, search):
        def check(m):
            return m.author == interaction.guild.me or m.content.startswith("!" or "?")

        deleted = await interaction.channel.purge(
            limit=search, check=check, before=interaction.message
        )
        return Counter(m.author.display_name for m in deleted)

    @staticmethod
    async def _regular_user_cleanup_strategy(interaction: discord.Interaction, search):
        def check(m):
            return (
                m.author == interaction.guild.me or m.content.startswith("!" or "?")
            ) and not (m.mentions or m.role_mentions)

        deleted = await interaction.channel.purge(
            limit=search, check=check, before=interaction.message
        )
        return Counter(m.author.display_name for m in deleted)

    @staticmethod
    def format_commit(commit):
        short, _, _ = commit.message.partition("\n")
        short_sha2 = commit.hex[0:6]
        commit_tz = datetime.timezone(
            datetime.timedelta(minutes=commit.commit_time_offset)
        )
        commit_time = datetime.datetime.fromtimestamp(commit.commit_time).astimezone(
            commit_tz
        )

        # [`hash`](url) message (offset)
        offset = times.format_relative(commit_time.astimezone(datetime.timezone.utc))
        return f"[`{short_sha2}`](https://github.com/pandabear189/tms-scioly-bots/commit/{commit.hex}) {short} ({offset})"

    @command()
    @guilds(SERVER_ID)
    async def rule(
        self,
        interaction: discord.Interaction,
        number: Literal["1", "2", "3", "4", "5", "6"],
    ):
        """Gets a specified rule."""
        rule = RULES[int(number) - 1]
        embed = discord.Embed(
            title="", description=f"**Rule {number}:**\n> {rule}", color=0xFF008C
        )
        await interaction.response.send_message(embed=embed)

    @staticmethod
    def tick(opt, label=None):
        lookup = {
            True: "<:greenTick:899466945672392704>",
            False: "<:redTick:899466976748003398>",
            None: "<:greyTick:899466890102075393>",
        }
        emoji = lookup.get(opt, "<:redTick:330090723011592193>")
        if label is not None:
            return f"{emoji}: {label}"
        return emoji

    @command()
    @guilds(SERVER_ID)
    async def serverinfo(
        self, interaction: discord.Interaction, *, guild_id: int = None
    ):
        """Shows info about the current server."""
        if guild_id is not None and await self.bot.is_owner(interaction.user):
            guild = self.bot.get_guild(guild_id)
            if guild is None:
                return await interaction.response.send_message(
                    f"Invalid Guild ID given."
                )
        else:
            guild = interaction.guild

        roles = [role.name.replace("@", "@\u200b") for role in guild.roles]

        if not guild.chunked:
            await guild.chunk(cache=True)

        # figure out what channels are 'secret'
        everyone = guild.default_role
        everyone_perms = everyone.permissions.value
        secret = Counter()
        totals = Counter()
        for channel in guild.channels:
            allow, deny = channel.overwrites_for(everyone).pair()
            perms = discord.Permissions((everyone_perms & ~deny.value) | allow.value)
            channel_type = type(channel)
            totals[channel_type] += 1
            if not perms.read_messages:
                secret[channel_type] += 1
            elif isinstance(channel, discord.VoiceChannel) and (
                not perms.connect or not perms.speak
            ):
                secret[channel_type] += 1

        e = discord.Embed()
        e.title = guild.name
        e.description = f"**ID**: {guild.id}\n**Owner**: {guild.owner}"
        if guild.icon:
            e.set_thumbnail(url=guild.icon.url)

        channel_info = []
        key_to_emoji = {
            discord.TextChannel: "<:text_channel:899326950785576970>",
            discord.VoiceChannel: "<:voice_channel:899326987255021619>",
        }
        for key, total in totals.items():
            secrets = secret[key]
            try:
                emoji = key_to_emoji[key]
            except KeyError:
                continue

            if secrets:
                channel_info.append(f"{emoji} {total} ({secrets} locked)")
            else:
                channel_info.append(f"{emoji} {total}")

        info = []
        features = set(guild.features)
        all_features = {
            "PARTNERED": "Partnered",
            "VERIFIED": "Verified",
            "DISCOVERABLE": "Server Discovery",
            "COMMUNITY": "Community Server",
            "FEATURABLE": "Featured",
            "WELCOME_SCREEN_ENABLED": "Welcome Screen",
            "INVITE_SPLASH": "Invite Splash",
            "VIP_REGIONS": "VIP Voice Servers",
            "VANITY_URL": "Vanity Invite",
            "COMMERCE": "Commerce",
            "LURKABLE": "Lurkable",
            "NEWS": "News Channels",
            "ANIMATED_ICON": "Animated Icon",
            "BANNER": "Banner",
        }

        for feature, label in all_features.items():
            if feature in features:
                info.append(f"{self.tick(True)}: {label}")

        if info:
            e.add_field(name="Features", value="\n".join(info))

        e.add_field(name="Channels", value="\n".join(channel_info))

        if guild.premium_tier != 0:
            boosts = (
                f"Level {guild.premium_tier}\n{guild.premium_subscription_count} boosts"
            )
            last_boost = max(
                guild.members, key=lambda m: m.premium_since or guild.created_at
            )
            if last_boost.premium_since is not None:
                boosts = f"{boosts}\nLast Boost: {last_boost} ({times.format_relative(last_boost.premium_since)})"
            e.add_field(name="Boosts", value=boosts, inline=False)

        bots = sum(m.bot for m in guild.members)
        fmt = f"Total: {guild.member_count} ({bots} bots)"

        e.add_field(name="Members", value=fmt, inline=False)
        e.add_field(
            name="Roles",
            value=", ".join(roles) if len(roles) < 10 else f"{len(roles)} roles",
        )

        emoji_stats = Counter()
        for emoji in guild.emojis:
            if emoji.animated:
                emoji_stats["animated"] += 1
                emoji_stats["animated_disabled"] += not emoji.available
            else:
                emoji_stats["regular"] += 1
                emoji_stats["disabled"] += not emoji.available

        fmt = (
            f'Regular: {emoji_stats["regular"]}/{guild.emoji_limit}\n'
            f'Animated: {emoji_stats["animated"]}/{guild.emoji_limit}\n'
        )
        if emoji_stats["disabled"] or emoji_stats["animated_disabled"]:
            fmt = f'{fmt}Disabled: {emoji_stats["disabled"]} regular, {emoji_stats["animated_disabled"]} animated\n'

        fmt = f"{fmt}Total Emoji: {len(guild.emojis)}/{guild.emoji_limit * 2}"
        e.add_field(name="Emoji", value=fmt, inline=False)
        e.set_footer(text="Created").timestamp = guild.created_at
        await interaction.response.send_message(embed=e)

    @staticmethod
    async def say_permissions(
        interaction: discord.Interaction, member: discord.Member, channel
    ):
        permissions = channel.permissions_for(member)
        e = discord.Embed(colour=member.colour)
        avatar = member.display_avatar.with_static_format("png")
        e.set_author(name=str(member), url=avatar)
        allowed, denied = [], []
        for name, value in permissions:
            name = name.replace("_", " ").replace("guild", "server").title()
            if value:
                allowed.append(name)
            else:
                denied.append(name)

        e.add_field(name="Allowed", value="\n".join(allowed))
        e.add_field(name="Denied", value="\n".join(denied))
        await interaction.response.send_message(embed=e)

    @command()
    @guilds(SERVER_ID)
    async def permissions(
        self,
        interaction: discord.Interaction,
        member: Optional[discord.Member],
        channel: Optional[discord.TextChannel],
    ):
        """Shows a member's permissions in a specific channel.
        If no channel is given then it uses the current one.
        You cannot use this in private messages. If no member is given then
        the info returned will be yours.
        """
        channel = channel or interaction.channel
        if member is None:
            member = interaction.user

        await self.say_permissions(interaction, member, channel)

    @command()
    @guilds(SERVER_ID)
    async def debugpermissions(
        self,
        interaction: discord.Interaction,
        guild_id: int,
        channel_id: int,
        author_id: int = None,
    ):
        """Shows permission resolution for a channel and an optional author."""

        guild = self.bot.get_guild(guild_id)
        if guild is None:
            return await interaction.response.send_message("Guild not found?")

        channel = guild.get_channel(channel_id)
        if channel is None:
            return await interaction.response.send_message("Channel not found?")

        if author_id is None:
            member = guild.me
        else:
            member = await interaction.guild.get_member(author_id)

        if member is None:
            return await interaction.response.send_message("Member not found?")

        await self.say_permissions(interaction, member, channel)

    @command()
    @guilds(SERVER_ID)
    async def info(self, interaction: discord.Interaction, user: discord.User):
        """Shows info about a user."""

        user = user or interaction.user
        e = discord.Embed()
        roles = [
            role.name.replace("@", "@\u200b") for role in getattr(user, "roles", [])
        ]
        e.set_author(name=str(user))

        def format_date(dt):
            if dt is None:
                return "N/A"
            return f'{times.format_dt(dt, "F")} ({times.format_relative(dt)})'

        e.add_field(name="ID", value=user.id, inline=False)
        e.add_field(
            name="Joined",
            value=format_date(getattr(user, "joined_at", None)),
            inline=False,
        )
        e.add_field(name="Created", value=format_date(user.created_at), inline=False)

        voice = getattr(user, "voice", None)
        if voice is not None:
            vc = voice.channel
            other_people = len(vc.members) - 1
            voice = (
                f"{vc.name} with {other_people} others"
                if other_people
                else f"{vc.name} by themselves"
            )
            e.add_field(name="Voice", value=voice, inline=False)

        if roles:
            e.add_field(
                name="Roles",
                value=", ".join(roles) if len(roles) < 15 else f"{len(roles)} roles",
                inline=False,
            )

        colour = user.colour
        if colour.value:
            e.colour = colour

        e.set_thumbnail(url=user.display_avatar.url)

        if isinstance(user, discord.User):
            e.set_footer(text="This member is not in this server.")

        await interaction.response.send_message(embed=e)

    @command()
    @guilds(SERVER_ID)
    async def invite(self, interaction: discord.Interaction):
        """Gives you a 1 time use invite link"""
        x = await interaction.channel.create_invite(max_uses=1)
        await interaction.response.send_message(x)

    @command()
    @guilds(SERVER_ID)
    async def suggest(self, interaction: discord.Interaction, suggestion: str):
        """Make a suggestion for the server, team or bot"""
        server = self.bot.get_guild(SERVER_ID)
        suggest_channel = interaction.guild.get_channel(Channel.SUGGESTIONS)
        reports_channel = interaction.guild.get_channel(Channel.REPORTS)
        embed = discord.Embed(
            title="New Suggestion",
            description=f"{suggestion}",
            color=discord.Color.blurple(),
        )
        embed.timestamp = discord.utils.utcnow()
        name = interaction.user.nick or interaction.user
        embed.set_author(name=name, icon_url=interaction.user.avatar)
        suggest_message = await suggest_channel.send(embed=embed)
        await suggest_message.add_reaction("\U0001f44d")
        await suggest_message.add_reaction("\U0001f44e")
        await reports_channel.send(embed=embed)
        suggest_url = suggest_message.jump_url
        embed2 = discord.Embed(
            title=" ", description=f"Posted! [Your Suggestion!]({suggest_url})"
        )
        await interaction.response.send_message(embed=embed2)
        suggest_id = suggest_message.id
        suggest_embed = suggest_message.embeds[0]
        copy_of_embed = suggest_embed.copy()
        copy_of_embed.add_field(name="Suggestion ID", value=f"`{suggest_id}`")
        await suggest_message.edit(embed=copy_of_embed)

    @command()
    @guilds(SERVER_ID)
    async def cleanup(self, interaction: discord.Interaction, search: int = 100):
        """Cleans up the bot's messages from the channel.
        If a search number is specified, it searches that many messages to delete.
        If the bot has Manage Messages permissions then it will try to delete
        messages that look like they invoked the bot as well.
        After the cleanup is completed, the bot will send you a message with
        which people got their messages deleted and their count. This is useful
        to see which users are spammers.
        Members with Manage Messages can search up to 1000 messages.
        Members without can search up to 25 messages.
        """

        strategy = self._basic_cleanup_strategy
        is_mod = interaction.channel.permissions_for(interaction.user).manage_messages
        if interaction.channel.permissions_for(interaction.guild.me).manage_messages:
            if is_mod:
                strategy = self._complex_cleanup_strategy
            else:
                strategy = self._regular_user_cleanup_strategy

        if is_mod:
            search = min(max(2, search), 1000)
        else:
            search = min(max(2, search), 10)

        spammers = await strategy(interaction, search)
        deleted = sum(spammers.values())
        messages = [f'{deleted} message{" was" if deleted == 1 else "s were"} removed.']
        if deleted:
            messages.append("")
            spammers = sorted(spammers.items(), key=lambda t: t[1], reverse=True)
            messages.extend(f"- **{author}**: {count}" for author, count in spammers)

        await interaction.response.send_message("\n".join(messages))

    #
    # @command()
    # @guilds(SERVER_ID)
    # async def selfmute(self,
    #                    interaction,
    #                    mute_length: Option(str, "How long to mute yourself for.", choices=[
    #                        "10 minutes",
    #                        "30 minutes",
    #                        "1 hour",
    #                        "2 hours",
    #                        "4 hours",
    #                        "8 hours",
    #                        "1 day",
    #                        "4 days",
    #                        "7 days",
    #                        "1 month",
    #                        "1 year"
    #                    ], required=True)
    #                    ):
    #     """
    #     Self mutes the user that invokes the command.
    #     """
    #     member = interaction.author
    #
    #     times = {
    #         "10 minutes": discord.utils.utcnow() + datetime.timedelta(minutes=10),
    #         "30 minutes": discord.utils.utcnow() + datetime.timedelta(minutes=30),
    #         "1 hour": discord.utils.utcnow() + datetime.timedelta(hours=1),
    #         "2 hours": discord.utils.utcnow() + datetime.timedelta(hours=2),
    #         "4 hours": discord.utils.utcnow() + datetime.timedelta(hours=4),
    #         "8 hours": discord.utils.utcnow() + datetime.timedelta(hours=8),
    #         "1 day": discord.utils.utcnow() + datetime.timedelta(days=1),
    #         "4 days": discord.utils.utcnow() + datetime.timedelta(days=4),
    #         "7 days": discord.utils.utcnow() + datetime.timedelta(days=7),
    #         "1 month": discord.utils.utcnow() + datetime.timedelta(days=30),
    #         "1 year": discord.utils.utcnow() + datetime.timedelta(days=365),
    #     }
    #     selected_time = times[mute_length]
    #     original_shown_embed = discord.Embed(
    #         title="Mute Confirmation",
    #         color=discord.Color.brand_red(),
    #         description=f""" You will be muted across the entire server. You will no longer be able to communicate in
    #         any channels you can read until {discord.utils.format_dt(selected_time)}.
    #                                """
    #     )
    #     view = Confirm(interaction)
    #     await interaction.interaction.response.send_message(
    #         content="Please confirm that you would like to mute yourself.",
    #         view=view,
    #         embed=original_shown_embed,
    #         ephemeral=True
    #     )
    #     await view.wait()
    #     if view.value:
    #         try:
    #             role = discord.utils.get(member.guild.roles, name=ROLE_SELFMUTE)
    #             unselfmute_channel = discord.utils.get(member.guild.text_channels, id=CHANNEL_UNSELFMUTE)
    #             await member.add_roles(role)
    #             await mongo.insert(
    #                 "bot", "cron",
    #                 {
    #                     "type": "UNSELFMUTE",
    #                     "user": member.id,
    #                     "time": times[mute_length],
    #                     "tag": str(member)
    #                 })
    #             return await interaction.interaction.edit_original_message(
    #                 content=f"You have been muted. You may use the button in the {unselfmute_channel} channel to unmute.",
    #                 embed=None, view=None)
    #         except:
    #             pass
    #
    #     await interaction.interaction.edit_original_message(
    #         content=f"The operation was cancelled, and you can still speak throughout the server.", embed=None,
    #         view=None)

    @command()
    @guilds(SERVER_ID)
    async def newusers(self, interaction: discord.Interaction, count: int = None):
        """Tells you the newest members of the server.
        This is useful to check if any suspicious members have
        joined.
        The count parameter can only be up to 25.
        """

        if not interaction.guild.chunked:
            members = await interaction.guild.chunk(cache=True)
        else:
            members = sorted(
                interaction.guild.members, key=lambda m: m.joined_at, reverse=True
            )[:count]

        e = discord.Embed(title="New Members", colour=discord.Colour.green())

        for member in members:
            body = f"Joined {times.format_relative(member.joined_at)}\nCreated {times.format_relative(member.created_at)}"
            e.add_field(name=f"{member} (ID: {member.id})", value=body, inline=False)

        await interaction.response.send_message(embed=e)


async def setup(bot: TMS):
    await bot.add_cog(General(bot))
