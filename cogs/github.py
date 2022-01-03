import datetime
import inspect
import itertools
import os
import pygit2

import discord
from discord.ext import commands

from utils.checks import is_not_blacklisted
from utils.variables import *
from utils import times


class Github(commands.Cog):
    """Github related commands."""
    print('Github Cog Loaded')

    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        return await is_not_blacklisted(ctx)

    @property
    def display_emoji(self) -> discord.PartialEmoji:
        return discord.PartialEmoji(name='github', id=902367446986543116)

    def get_last_commits(self, count: int):
        repo = pygit2.Repository("tms-scioly-bots")
        commits = list(itertools.islice(repo.walk(repo.head.target, pygit2.GIT_SORT_TOPOLOGICAL), count))
        return '\n'.join(self.format_commit(c) for c in commits)

    @staticmethod
    def format_commit(commit):
        short, _, _ = commit.message.partition('\n')
        short_sha2 = commit.hex[0:6]
        commit_tz = datetime.timezone(datetime.timedelta(minutes=commit.commit_time_offset))
        commit_time = datetime.datetime.fromtimestamp(commit.commit_time).astimezone(commit_tz)

        # [`hash`](url) message (offset)
        offset = times.format_relative(commit_time.astimezone(datetime.timezone.utc))
        return f'[`{short_sha2}`](https://github.com/pandabear189/tms-scioly-bots/commit/{commit.hex}) {short} ({offset})'

    github = discord.SlashCommandGroup(
        "github",
        "Shows information about my repository",
        [SERVER_ID]
    )

    @github.command()
    async def commits(self, ctx):
        '''Shows all the recent bot commits'''
        count = 20
        revisions = self.get_last_commits(count)
        embed = discord.Embed(title="Recent Changes", description=f"Displaying {count} changes \n" + revisions)
        await ctx.respond(embed=embed)

    @github.command()
    async def source(self, ctx, *, command: str = None):
        """Displays my full source code or for a specific command.
        To display the source code of a subcommand you can separate it by
        periods, e.g. tag.create for the create subcommand of the tag command
        or by spaces.
        """
        source_url = 'https://github.com/pandabear189/tms-scioly-bots'
        branch = 'master'
        if command is None:
            return await ctx.respond(source_url)

        if command == 'help':
            src = type(self.bot.help_command)
            module = src.__module__
            filename = inspect.getsourcefile(src)
        else:
            obj = self.bot.get_application_command(command.replace('.', ' '))
            if obj is None:
                return await ctx.respond('Could not find command.')

            # since we found the command we're looking for, presumably anyway, let's
            # try to access the code itself
            src = obj.callback.__code__
            module = obj.callback.__module__
            filename = src.co_filename

        lines, firstlineno = inspect.getsourcelines(src)
        if not module.startswith('discord'):
            # not a built-in command
            location = os.path.relpath(filename).replace('\\', '/')
        else:
            location = module.replace('.', '/') + '.py'
            source_url = 'https://github.com/Rapptz/discord.py'
            branch = 'master'

        final_url = f'<{source_url}/blob/{branch}/{location}#L{firstlineno}-L{firstlineno + len(lines) - 1}>'
        await ctx.respond(final_url)


def setup(bot):
    bot.add_cog(Github(bot))
