from discord.ext import commands
import discord
from utils.variables import *
from utils.rules import RULES
from utils.checks import is_not_blacklisted
from collections import Counter
from utils.times import plural
import datetime
import psutil
import asyncio
import pygit2
from typing import Literal, Union
import os
import googletrans
import itertools
import pkg_resources
import inspect


class GeneralCommands(commands.Cog):
    """Fun related commands."""
    print('GeneralCommands Cog Loaded')

    def __init__(self, bot):
        self.bot = bot
        self.process = psutil.Process()
        self.bot.launch_time = datetime.datetime.utcnow()
        self.trans = googletrans.Translator()

    async def cog_check(self, ctx):
        return await is_not_blacklisted(ctx)

    def cog_unload(self):
        print("general cog unloaded")

    def get_bot_uptime(self):
        delta_uptime = datetime.datetime.utcnow() - self.bot.launch_time
        hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)
        uptime = f"{days} Days, {hours} Hours, {minutes} Minutes, {seconds} Seconds"
        return uptime

    def get_last_commits(self, count:int):
        repo = pygit2.Repository("tms-scioly-bots")
        commits = list(itertools.islice(repo.walk(repo.head.target, pygit2.GIT_SORT_TOPOLOGICAL), count))
        return '\n'.join(self.format_commit(c) for c in commits)

    def format_relative(self, dt):
        return self.format_dt(dt, 'R')

    def format_commit(self, commit):
        short, _, _ = commit.message.partition('\n')
        short_sha2 = commit.hex[0:6]
        commit_tz = datetime.timezone(datetime.timedelta(minutes=commit.commit_time_offset))
        commit_time = datetime.datetime.fromtimestamp(commit.commit_time).astimezone(commit_tz)

        # [`hash`](url) message (offset)
        offset = self.format_relative(commit_time.astimezone(datetime.timezone.utc))
        return f'[`{short_sha2}`](https://github.com/pandabear189/tms-scioly-bots/commit/{commit.hex}) {short} ({offset})'

    def format_dt(self, dt, style=None):
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=datetime.timezone.utc)

        if style is None:
            return f'<t:{int(dt.timestamp())}>'
        return f'<t:{int(dt.timestamp())}:{style}>'

    # @commands.command()
    # async def help(self, ctx: commands.Context):
    #     '''Sends a menu with all the commands'''
    #     current = 0
    #     view = HelpButtons(ctx, current)
    #     await ctx.send(embed=paginationList[current], view=view)

    @commands.command()
    async def source(self, ctx, command=None):
        """Displays my full source code or for a specific command.
        To display the source code of a subcommand you can separate it by
        periods, e.g. tag.create for the create subcommand of the tag command
        or by spaces.
        """
        source_url = 'https://github.com/pandabear189/tms-scioly-bots'
        branch = 'main'
        if command is None:
            await ctx.send(source_url)

        else:
            obj = self.bot.get_command(command.replace('.', ' '))
            if obj is None:
                return await ctx.send('Could not find command.')

            src = obj.callback.__code__
            module = obj.callback.__module__
            filename = src.co_filename

            lines, firstlineno = inspect.getsourcelines(src)
            if not module.startswith('discord'):
                location = os.path.relpath(filename).replace('\\', '/')
            else:
                location = module.replace('.', '/') + '.py'
                source_url = 'https://github.com/Rapptz/discord.py'
                branch = 'master'

            final_url = f'<{source_url}/blob/{branch}/{location}#L{firstlineno}-L{firstlineno + len(lines) - 1}>'
            await ctx.send(final_url)

    @commands.command()
    async def rule(self, ctx, number:Literal["1", "2", "3", "4", "5", "6"] = commands.Option(description="Which rule to display")):
        """Gets a specified rule."""
        rule = RULES[int(number) - 1]
        embed = discord.Embed(title="",
                              description=f"**Rule {number}:**\n> {rule}",
                              color=0xff008c)
        return await ctx.send(embed=embed)

    @commands.command()
    async def report(self, ctx, reason):
        """Creates a report that is sent to staff members."""
        server = self.bot.get_guild(SERVER_ID)
        reports_channel = discord.utils.get(server.text_channels, id=CHANNEL_REPORTS)
        ava = ctx.message.author.avatar

        message = reason
        embed = discord.Embed(title="Report received", description=" ", color=0xFF0000)
        embed.add_field(name="User:", value=f"{ctx.message.author.mention} \n id: `{ctx.message.author.id}`")
        embed.add_field(name="Report:", value=f"`{message}`")
        embed.set_author(name=f"{ctx.message.author}", icon_url=ava)
        message = await reports_channel.send(embed=embed)
        REPORT_IDS.append(message.id)
        await message.add_reaction("\U00002705")
        await message.add_reaction("\U0000274C")
        await ctx.send("Thanks, report created.")

    def tick(self, opt, label=None):
        lookup = {
            True: '<:greenTick:899466945672392704>',
            False: '<:redTick:899466976748003398>',
            None: '<:greyTick:899466890102075393>',
        }
        emoji = lookup.get(opt, '<:redTick:330090723011592193>')
        if label is not None:
            return f'{emoji}: {label}'
        return emoji

    @commands.command()
    @commands.guild_only()
    async def serverinfo(self, ctx, guild_id: int = None):
        """Shows info about the current server."""

        if guild_id is not None and await self.bot.is_owner(ctx.author):
            guild = self.bot.get_guild(guild_id)
            if guild is None:
                return await ctx.send(f'Invalid Guild ID given.')
        else:
            guild = ctx.guild

        roles = [role.name.replace('@', '@\u200b') for role in guild.roles]

        if not guild.chunked:
            async with ctx.typing():
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
            elif isinstance(channel, discord.VoiceChannel) and (not perms.connect or not perms.speak):
                secret[channel_type] += 1

        e = discord.Embed()
        e.title = guild.name
        e.description = f'**ID**: {guild.id}\n**Owner**: {guild.owner}'
        if guild.icon:
            e.set_thumbnail(url=guild.icon.url)

        channel_info = []
        key_to_emoji = {
            discord.TextChannel: '<:text_channel:899326950785576970>',
            discord.VoiceChannel: '<:voice_channel:899326987255021619>',
        }
        for key, total in totals.items():
            secrets = secret[key]
            try:
                emoji = key_to_emoji[key]
            except KeyError:
                continue

            if secrets:
                channel_info.append(f'{emoji} {total} ({secrets} locked)')
            else:
                channel_info.append(f'{emoji} {total}')

        info = []
        features = set(guild.features)
        all_features = {
            'PARTNERED': 'Partnered',
            'VERIFIED': 'Verified',
            'DISCOVERABLE': 'Server Discovery',
            'COMMUNITY': 'Community Server',
            'FEATURABLE': 'Featured',
            'WELCOME_SCREEN_ENABLED': 'Welcome Screen',
            'INVITE_SPLASH': 'Invite Splash',
            'VIP_REGIONS': 'VIP Voice Servers',
            'VANITY_URL': 'Vanity Invite',
            'COMMERCE': 'Commerce',
            'LURKABLE': 'Lurkable',
            'NEWS': 'News Channels',
            'ANIMATED_ICON': 'Animated Icon',
            'BANNER': 'Banner',
        }

        for feature, label in all_features.items():
            if feature in features:
                info.append(f'{self.tick(True)}: {label}')

        if info:
            e.add_field(name='Features', value='\n'.join(info))

        e.add_field(name='Channels', value='\n'.join(channel_info))

        if guild.premium_tier != 0:
            boosts = f'Level {guild.premium_tier}\n{guild.premium_subscription_count} boosts'
            last_boost = max(guild.members, key=lambda m: m.premium_since or guild.created_at)
            if last_boost.premium_since is not None:
                boosts = f'{boosts}\nLast Boost: {last_boost} ({self.format_relative(last_boost.premium_since)})'
            e.add_field(name='Boosts', value=boosts, inline=False)

        bots = sum(m.bot for m in guild.members)
        fmt = f'Total: {guild.member_count} ({plural(bots):bot})'

        e.add_field(name='Members', value=fmt, inline=False)
        e.add_field(name='Roles', value=', '.join(roles) if len(roles) < 10 else f'{len(roles)} roles')

        emoji_stats = Counter()
        for emoji in guild.emojis:
            if emoji.animated:
                emoji_stats['animated'] += 1
                emoji_stats['animated_disabled'] += not emoji.available
            else:
                emoji_stats['regular'] += 1
                emoji_stats['disabled'] += not emoji.available

        fmt = (
            f'Regular: {emoji_stats["regular"]}/{guild.emoji_limit}\n'
            f'Animated: {emoji_stats["animated"]}/{guild.emoji_limit}\n'
        )
        if emoji_stats['disabled'] or emoji_stats['animated_disabled']:
            fmt = f'{fmt}Disabled: {emoji_stats["disabled"]} regular, {emoji_stats["animated_disabled"]} animated\n'

        fmt = f'{fmt}Total Emoji: {len(guild.emojis)}/{guild.emoji_limit * 2}'
        e.add_field(name='Emoji', value=fmt, inline=False)
        e.set_footer(text='Created').timestamp = guild.created_at
        await ctx.send(embed=e)

    async def say_permissions(self, ctx, member, channel):
        permissions = channel.permissions_for(member)
        e = discord.Embed(colour=member.colour)
        avatar = member.display_avatar.with_static_format('png')
        e.set_author(name=str(member), url=avatar)
        allowed, denied = [], []
        for name, value in permissions:
            name = name.replace('_', ' ').replace('guild', 'server').title()
            if value:
                allowed.append(name)
            else:
                denied.append(name)

        e.add_field(name='Allowed', value='\n'.join(allowed))
        e.add_field(name='Denied', value='\n'.join(denied))
        await ctx.send(embed=e)

    @commands.command()
    @commands.guild_only()
    async def permissions(self, ctx, member: discord.Member = None, channel: discord.TextChannel = None):
        """Shows a member's permissions in a specific channel.
        If no channel is given then it uses the current one.
        You cannot use this in private messages. If no member is given then
        the info returned will be yours.
        """
        channel = channel or ctx.channel
        if member is None:
            member = ctx.author

        await self.say_permissions(ctx, member, channel)

    @commands.command()
    @commands.guild_only()
    async def botpermissions(self, ctx, channel: discord.TextChannel = None):
        """Shows the bot's permissions in a specific channel.
        If no channel is given then it uses the current one.
        This is a good way of checking if the bot has the permissions needed
        to execute the commands it wants to execute.
        To execute this command you must have Manage Roles permission.
        You cannot use this in private messages.
        """
        channel = channel or ctx.channel
        member = ctx.guild.me
        await self.say_permissions(ctx, member, channel)

    @commands.command()
    @commands.is_owner()
    async def debugpermissions(self, ctx, guild_id: int, channel_id: int, author_id: int = None):
        """Shows permission resolution for a channel and an optional author."""

        guild = self.bot.get_guild(guild_id)
        if guild is None:
            return await ctx.send('Guild not found?')

        channel = guild.get_channel(channel_id)
        if channel is None:
            return await ctx.send('Channel not found?')

        if author_id is None:
            member = guild.me
        else:
            member = await self.bot.get_or_fetch_member(guild, author_id)

        if member is None:
            return await ctx.send('Member not found?')

        await self.say_permissions(ctx, member, channel)

    @commands.command()
    async def info(self, ctx, user: Union[discord.Member, discord.User] = None):
        """Shows info about a user."""

        user = user or ctx.author
        e = discord.Embed()
        roles = [role.name.replace('@', '@\u200b') for role in getattr(user, 'roles', [])]
        e.set_author(name=str(user))

        def format_date(dt):
            if dt is None:
                return 'N/A'
            return f'{self.format_dt(dt, "F")} ({self.format_relative(dt)})'

        e.add_field(name='ID', value=user.id, inline=False)
        e.add_field(name='Joined', value=format_date(getattr(user, 'joined_at', None)), inline=False)
        e.add_field(name='Created', value=format_date(user.created_at), inline=False)

        voice = getattr(user, 'voice', None)
        if voice is not None:
            vc = voice.channel
            other_people = len(vc.members) - 1
            voice = f'{vc.name} with {other_people} others' if other_people else f'{vc.name} by themselves'
            e.add_field(name='Voice', value=voice, inline=False)

        if roles:
            e.add_field(name='Roles', value=', '.join(roles) if len(roles) < 15 else f'{len(roles)} roles',
                        inline=False)

        colour = user.colour
        if colour.value:
            e.colour = colour

        e.set_thumbnail(url=user.display_avatar.url)

        if isinstance(user, discord.User):
            e.set_footer(text='This member is not in this server.')

        await ctx.send(embed=e)

    @commands.command()
    async def tag(self,
                  ctx,
                  name=commands.Option(description="Name of the tag")
                  ):
        '''Retrieves a tag'''
        tag = name.lower()
        if tag == 'rules':
            em1 = discord.Embed(title="Rules", description="Here are the rules for the 2021-22 season", color=0xff008c)
            em1.add_field(name='Division B Rules',
                          value="[Click Here](https://www.soinc.org/sites/default/files/2021-09/Science_Olympiad_Div_B_2022_Rules_Manual_Web_0.pdf/ \"Division B\")")
            em1.add_field(name='Division C Rules',
                          value="[Click Here](https://www.soinc.org/sites/default/files/2021-09/Science_Olympiad_Div_C_2022_Rules_Manual_Web_1.pdf/ \"Division C\")")
            await ctx.send(embed=em1)

        elif tag == 'anatomy':
            em2 = discord.Embed(title="Anatomy & Physiology Rules",
                                description="Participants will be assessed on their understanding of the anatomy and physiology for the human Nervous, Sense Organs, and Endocrine systems.  \n This Event may be administered as a written test or as series of lab-practical stations which can include but are not limited to experiments, scientific apparatus, models, illustrations, specimens, data collection and analysis, and problems for students to solve.",
                                color=0xff008c)
            em2.add_field(name='Full Anatomy Rules',
                          value="[Click Here](https://www.soinc.org/sites/default/files/2021-09/Science_Olympiad_Div_B_2022_Rules_Manual_Web_0.pdf#page=7/ \"Anatomy\")")
            await ctx.send(embed=em2)

        elif tag == 'bpl':
            em3 = discord.Embed(title="Bio Process Lab Rules",
                                description="This event is a lab-oriented competition involving the  fundamental  science  processes of a middle school life science/biology lab program. \n This event will consist of a series of lab stations. Each station will require the use of process skills to answer questions and/or perform a required task such as formulating and/or evaluating hypotheses and procedures, using scientific instruments to collect data, making observations, presenting and/or interpreting data, or making inferences and conclusions",
                                color=0xff008c)
            em3.add_field(name='Full Bio Process Lab',
                          value="[Click Here](https://www.soinc.org/sites/default/files/2021-09/Science_Olympiad_Div_B_2022_Rules_Manual_Web_0.pdf#page=9/ \"Bio Process Lab\")")
            await ctx.send(embed=em3)

        else:
            await ctx.send("Sorry I couldn't find that tag", mention_author=False)

    @commands.command()
    async def invite(self, ctx):
        '''Gives you a 1 time use invite link'''
        x = await ctx.channel.create_invite(max_uses=1)
        await ctx.send(x)

    @commands.command()
    async def uptime(self, ctx):
        '''Sends how long the bot has been online'''
        uptime = self.get_bot_uptime()
        await ctx.send(f"**{uptime}**")

    @commands.command()
    async def about(self, ctx):
        """Tells you information about the bot itself."""

        revision = self.get_last_commits(count=5)
        embed = discord.Embed(description='Latest Changes:\n' + revision)
        # embed = discord.Embed(description='Latest Changes:\n')
        embed.colour = discord.Colour.blurple()

        # To properly cache myself, I need to use the bot support server.
        support_guild = self.bot.get_guild(816806329925894217)
        owner = await support_guild.fetch_member(747126643587416174)
        name = str(owner)
        embed.set_author(name=name, icon_url=owner.display_avatar.url, url = 'https://github.com/pandabear189')

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

        embed.add_field(name='Members', value=f'{total_members} total\n{total_unique} unique')
        embed.add_field(name='Channels', value=f'{text + voice} total\n{text} text\n{voice} voice')

        memory_usage = self.process.memory_full_info().uss / 1024 ** 2
        cpu_usage = self.process.cpu_percent() / psutil.cpu_count()
        embed.add_field(name='Process', value=f'{memory_usage:.2f} MiB\n{cpu_usage:.2f}% CPU')

        dpyversion = pkg_resources.get_distribution('discord.py').version
        embed.add_field(name='Guilds', value=guilds)
        embed.add_field(name='Number of Commands', value=len(self.bot.commands))
        uptime = self.get_bot_uptime()
        embed.add_field(name="Uptime", value= uptime)
        embed.set_footer(text=f'Made with discord.py v{dpyversion}', icon_url='https://i.imgur.com/RPrw70n.png')
        embed.timestamp = discord.utils.utcnow()
        await ctx.send(embed=embed)

    @commands.command()
    async def bothealth(self, ctx):
        """Various bot health monitoring tools."""

        # This uses a lot of private methods because there is no
        # clean way of doing this otherwise.

        HEALTHY = discord.Colour(value=0x43B581)
        UNHEALTHY = discord.Colour(value=0xF04947)

        total_warnings = 0

        embed = discord.Embed(title='Bot Health Report', colour=HEALTHY)

        description = [
        ]

        task_retriever = asyncio.all_tasks
        all_tasks = task_retriever(loop=self.bot.loop)

        event_tasks = [
            t for t in all_tasks
            if 'Client._run_event' in repr(t) and not t.done()
        ]

        cogs_directory = os.path.dirname(__file__)
        tasks_directory = os.path.join('discord', 'ext', 'tasks', '__init__.py')
        inner_tasks = [
            t for t in all_tasks
            if cogs_directory in repr(t) or tasks_directory in repr(t)
        ]

        bad_inner_tasks = ", ".join(hex(id(t)) for t in inner_tasks if t.done() and t._exception is not None)
        total_warnings += bool(bad_inner_tasks)
        embed.add_field(name='Inner Tasks', value=f'Total: {len(inner_tasks)}\nFailed: {bad_inner_tasks or "None"}')
        embed.add_field(name='Events Waiting', value=f'Total: {len(event_tasks)}', inline=False)

        memory_usage = self.process.memory_full_info().uss / 1024 ** 2
        cpu_usage = self.process.cpu_percent() / psutil.cpu_count()
        embed.add_field(name='Process', value=f'{memory_usage:.2f} MiB\n{cpu_usage:.2f}% CPU', inline=False)

        global_rate_limit = not self.bot.http._global_over.is_set()
        description.append(f'Global Rate Limit: {global_rate_limit}')

        if global_rate_limit or total_warnings >= 9:
            embed.colour = UNHEALTHY

        embed.set_footer(text=f'{total_warnings} warning(s)')
        embed.description = '\n'.join(description)
        await ctx.send(embed=embed)

    @commands.command()
    async def update(self, ctx):
        '''Shows all the recent bot updates'''
        count = 20
        revisions = self.get_last_commits(count)
        embed = discord.Embed(title="Recent Changes", description = f"Displaying {count} changes \n" + revisions)
        await ctx.send(embed=embed)

    @commands.command()
    async def suggest(self, ctx, suggestion):
        '''Make a suggestion for the server, team or bot'''
        server = self.bot.get_guild(SERVER_ID)
        suggest_channel = discord.utils.get(server.text_channels, id=CHANNEL_SUGGESTIONS)
        reports_channel = discord.utils.get(server.text_channels, id=CHANNEL_REPORTS)
        embed = discord.Embed(title = "New Suggestion" , description = f"{suggestion}", color = 0x967DCB)
        embed.timestamp = discord.utils.utcnow()
        embed.set_author(name = ctx.author.nick, icon_url=ctx.author.avatar)
        suggest_message = await suggest_channel.send(embed=embed)
        await suggest_message.add_reaction("\U0001f44d")
        await suggest_message.add_reaction("\U0001f44e")
        await reports_channel.send(embed=embed)
        suggest_url = suggest_message.jump_url
        embed2 = discord.Embed(title = " ", description= f"Posted! [Your Suggestion!]({suggest_url})")
        await ctx.send(embed= embed2)


def setup(bot):
    bot.add_cog(GeneralCommands(bot))
