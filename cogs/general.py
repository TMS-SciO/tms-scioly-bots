from discord.ext import commands
import discord
from utils.views import HelpButtons, paginationList
from utils.variables import *
from utils.rules import RULES
from utils.checks import is_staff
from utils.embed import assemble_embed
import datetime
import psutil
import pygit2
from typing import Literal
import os
import itertools
import pkg_resources
import inspect


class GeneralCommands(commands.Cog):
    """Fun related commands."""
    print('GeneralCommands Cog Loaded')

    def __init__(self, bot):
        self.bot = bot
        self.process = psutil.Process()

    def get_last_commits(self, count=5):
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


    @commands.command()
    async def help(self, ctx: commands.Context):
        '''Sends a menu with all the commands'''
        current = 0
        view = HelpButtons(ctx, current)
        await ctx.send(embed=paginationList[current], view=view)

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
        embed = discord.Embed(title="Report received using `!report`", description=" ", color=0xFF0000)
        embed.add_field(name="User:", value=f"{ctx.message.author.mention} \n id: `{ctx.message.author.id}`")
        embed.add_field(name="Report:", value=f"`{message}`")
        embed.set_author(name=f"{ctx.message.author}", icon_url=ava)
        message = await reports_channel.send(embed=embed)
        REPORT_IDS.append(message.id)
        await message.add_reaction("\U00002705")
        await message.add_reaction("\U0000274C")
        await ctx.reply("Thanks, report created.")

    @commands.command()
    async def info(self, ctx):
        """Gets information about the Discord server."""
        server = ctx.message.guild
        name = server.name
        owner = server.owner
        creation_date = server.created_at
        emoji_count = len(server.emojis)
        icon = server.icon.replace(format='gif', static_format='jpeg')
        animated_icon = server.icon.is_animated()
        iden = server.id
        banner = server.banner
        desc = server.description
        mfa_level = server.mfa_level
        verification_level = server.verification_level
        content_filter = server.explicit_content_filter
        default_notifs = server.default_notifications
        features = server.features
        splash = server.splash
        premium_level = server.premium_tier
        boosts = server.premium_subscription_count
        channel_count = len(server.channels)
        text_channel_count = len(server.text_channels)
        voice_channel_count = len(server.voice_channels)
        category_count = len(server.categories)
        system_channel = server.system_channel
        if type(system_channel) == discord.TextChannel: system_channel = system_channel.mention
        rules_channel = server.rules_channel
        if type(rules_channel) == discord.TextChannel: rules_channel = rules_channel.mention
        public_updates_channel = server.public_updates_channel
        if type(public_updates_channel) == discord.TextChannel: public_updates_channel = public_updates_channel.mention
        emoji_limit = server.emoji_limit
        bitrate_limit = server.bitrate_limit
        filesize_limit = round(server.filesize_limit / 1000000, 3)
        boosters = server.premium_subscribers
        for i, b in enumerate(boosters):
            # convert user objects to mentions
            boosters[i] = b.mention
        boosters = ", ".join(boosters)
        print(boosters)
        role_count = len(server.roles)
        member_count = len(server.members)
        max_members = server.max_members
        discovery_splash_url = server.discovery_splash
        member_percentage = round(member_count / max_members * 100, 3)
        emoji_percentage = round(emoji_count / emoji_limit * 100, 3)
        channel_percentage = round(channel_count / 500 * 100, 3)
        role_percenatege = round(role_count / 250 * 100, 3)

        staff_member = is_staff()
        fields = [
            {
                "name": "Basic Information",
                "value": (
                        f"**Creation Date:** {creation_date}\n" +
                        f"**ID:** {iden}\n" +
                        f"**Animated Icon:** {animated_icon}\n" +
                        f"**Banner URL:** {banner}\n" +
                        f"**Splash URL:** {splash}\n" +
                        f"**Discovery Splash URL:** {discovery_splash_url}"
                ),
                "inline": False
            },
            {
                "name": "Nitro Information",
                "value": (
                        f"**Nitro Level:** {premium_level} ({boosts} individual boosts)\n" +
                        f"**Boosters:** {boosters}"
                ),
                "inline": False
            }
        ]
        if staff_member:
            fields.extend(
                [{
                    "name": "Staff Information",
                    "value": (
                            f"**Owner:** {owner}\n" +
                            f"**MFA Level:** {mfa_level}\n" +
                            f"**Verification Level:** {verification_level}\n" +
                            f"**Content Filter:** {content_filter}\n" +
                            f"**Default Notifications:** {default_notifs}\n" +
                            f"**Features:** {features}\n" +
                            f"**Bitrate Limit:** {bitrate_limit}\n" +
                            f"**Filesize Limit:** {filesize_limit} MB"
                    ),
                    "inline": False
                },
                    {
                        "name": "Channels",
                        "value": (
                                f"**Public Updates Channel:** {public_updates_channel}\n" +
                                f"**System Channel:** {system_channel}\n" +
                                f"**Rules Channel:** {rules_channel}\n" +
                                f"**Text Channel Count:** {text_channel_count}\n" +
                                f"**Voice Channel Count:** {voice_channel_count}\n" +
                                f"**Category Count:** {category_count}\n"
                        ),
                        "inline": False
                    },
                    {
                        "name": "Limits",
                        "value": (
                                f"**Channels:** *{channel_percentage}%* ({channel_count}/500 channels)\n" +
                                f"**Members:** *{member_percentage}%* ({member_count}/{max_members} members)\n" +
                                f"**Emoji:** *{emoji_percentage}%* ({emoji_count}/{emoji_limit} emojis)\n" +
                                f"**Roles:** *{role_percenatege}%* ({role_count}/250 roles)"
                        ),
                        "inline": False
                    }
                ])
        embed = assemble_embed(
            title=f"Information for `{name}`",
            desc=f"**Description:** {desc}",
            thumbnailUrl=icon,
            fields=fields
        )
        await ctx.send(embed=embed)

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
            await ctx.reply("Sorry I couldn't find that tag", mention_author=False)

    @commands.command()
    async def invite(self, ctx):
        '''Gives you a 1 time use invite link'''
        x = await ctx.channel.create_invite(max_uses=1)
        await ctx.send(x)

    @commands.command()
    async def about(self, ctx):
        """Tells you information about the bot itself."""

        revision = self.get_last_commits()
        embed = discord.Embed(description='Latest Changes:\n' + revision)
        # embed = discord.Embed(description='Latest Changes:\n')
        embed.colour = discord.Colour.blurple()

        # To properly cache myself, I need to use the bot support server.
        support_guild = self.bot.get_guild(816806329925894217)
        owner = await support_guild.fetch_member(747126643587416174)
        embed.set_author(name=str(owner), icon_url=owner.display_avatar.url)

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

        version = pkg_resources.get_distribution('discord.py').version
        embed.add_field(name='Guilds', value=guilds)
        embed.add_field(name='Number of Commands', value=len(self.bot.commands))
        embed.set_footer(text=f'Made with discord.py v{version}', icon_url='https://i.imgur.com/RPrw70n.png')
        embed.timestamp = discord.utils.utcnow()
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(GeneralCommands(bot))
