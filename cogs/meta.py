from discord.ext import commands, menus
from typing import Union, List, Any, Dict, Optional
import discord
from discord import slash_command
import utils.times as time
from utils.paginate import RoboPages
import inspect
import itertools

from utils.variables import SERVER_ID


class GroupHelpPageSource(menus.ListPageSource):
    def __init__(self,
                 group: Union[commands.Group, commands.Cog, discord.SlashCommandGroup],
                 commands: List[Union[commands.Command, discord.SlashCommand]], *, prefix: str):
        super().__init__(entries=commands, per_page=6)
        self.group = group
        self.prefix = prefix
        self.title = f'{self.group.qualified_name} Commands'
        self.description = self.group.description

    def signature(self, command: discord.SlashCommand) -> str:
        """:class:`str`: Returns a POSIX-like signature useful for help command output."""

        params = command.options
        if not params:
            return ''

        result = []
        for param in iter(params):
            if param.autocomplete:
                signature = f"{param.name} = **Autocomplete**"
                if param.required:
                    result.append(f'<{signature}>')
                elif not param.required:
                    result.append(f'[{signature}]')
            if param.choices:
                signature = f"{param.name} = [provided choices]"
                if param.required:
                    result.append(f'<{signature}>')
                elif not param.required:
                    result.append(f'[{signature}]')
            if param.default:
                # We don't want None or '' to trigger the [name=value] case and instead it should
                # do [name] since [name=None] or [name=] are not exactly useful for the user.
                should_print = param.default if isinstance(param.default, str) else param.default is not None
                if should_print:
                    result.append(f'[{param.name}={param.default}]')
                if not should_print:
                    result.append(f'[{param.name}]')
            elif not param.default or param.choices or param.autocomplete:
                if param.required:
                    result.append(f'<{param.name}>')
                elif not param.required:
                    result.append(f'[{param.name}]')

        return ' '.join(result)

    async def format_page(self, menu, commands: List[discord.SlashCommand]):
        embed = discord.Embed(title=self.title, description=self.description, colour=discord.Color.blurple())

        for command in commands:
            signature = f'{command.name} {self.signature(command)}'
            embed.add_field(name=signature, value=command.description or 'No help given...', inline=False)

        maximum = self.get_max_pages()
        if maximum > 1:
            embed.set_author(name=f'Page {menu.current_page + 1}/{maximum} ({len(self.entries)} commands)')

        embed.set_footer(text=f'Use "{self.prefix}help command" for more info on a command.')
        return embed


class HelpSelectMenu(discord.ui.Select['HelpMenu']):
    def __init__(self,
                 commands: Dict[commands.Cog, List[Union[commands.Command, discord.commands.SlashCommand]]],
                 bot: Union[commands.AutoShardedBot, commands.Bot]):
        super().__init__(
            placeholder='Select a category...',
            min_values=1,
            max_values=1,
            row=0,
        )
        self.commands = commands
        self.bot = bot
        self.__fill_options()

    def __fill_options(self) -> None:
        self.add_option(
            label='Index',
            emoji='\N{WAVING HAND SIGN}',
            value='__index',
            description='The help page showing how to use the bot.',
        )
        for cog, commands in self.commands.items():
            if not commands:
                continue
            description = cog.description.split('\n', 1)[0] or None
            emoji = getattr(cog, 'display_emoji', None)
            self.add_option(label=cog.qualified_name, value=cog.qualified_name, description=description, emoji=emoji)

    async def callback(self, interaction: discord.Interaction):
        assert self.view is not None
        value = self.values[0]
        if value == '__index':
            await self.view.rebind(FrontPageSource(), interaction)
        else:
            cog = self.bot.get_cog(value)
            if cog is None:
                await interaction.response.send_message('Somehow this category does not exist?', ephemeral=True)
                return

            commands = self.commands[cog]
            if not commands:
                await interaction.response.send_message('This category has no commands for you', ephemeral=True)
                return

            source = GroupHelpPageSource(cog, commands, prefix=self.view.ctx.clean_prefix)
            await self.view.rebind(source, interaction)


class HelpMenu(RoboPages):
    def __init__(self, source: menus.PageSource, ctx: commands.Context):
        super().__init__(source, ctx=ctx, compact=True)

    def add_categories(self,
                       commands: Dict[
                           commands.Cog, List[Union[commands.Command, discord.commands.SlashCommand]]]) -> None:
        self.clear_items()
        self.add_item(HelpSelectMenu(commands, self.ctx.bot))
        self.fill_items()

    async def rebind(self, source: menus.PageSource, interaction: discord.Interaction) -> None:
        self.source = source
        self.current_page = 0

        await self.source._prepare_once()
        page = await self.source.get_page(0)
        kwargs = await self._get_kwargs_from_page(page)
        self._update_labels(0)
        await interaction.response.edit_message(**kwargs, view=self)


class FrontPageSource(menus.PageSource):
    def is_paginating(self) -> bool:
        # This forces the buttons to appear even in the front page
        return True

    def get_max_pages(self) -> Optional[int]:
        # There's only one actual page in the front page
        # However we need at least 2 to show all the buttons
        return 2

    async def get_page(self, page_number: int) -> Any:
        # The front page is a dummy
        self.index = page_number
        return self

    def format_page(self, menu: HelpMenu, page):
        embed = discord.Embed(title='Bot Help', colour=discord.Color.blurple())
        embed.description = inspect.cleandoc(
            f"""
            Hello! Welcome to the help page.
            Use "{menu.ctx.clean_prefix}help command" for more info on a command.
            Use "{menu.ctx.clean_prefix}help category" for more info on a category.
            Use the dropdown menu below to select a category.
        """
        )

        created_at = time.format_dt(menu.ctx.bot.user.created_at, 'F')
        if self.index == 0:
            embed.add_field(
                name='Who are you?',
                value=(
                    "I'm a bot made by pandabear#0001. I've been running since "
                    f'{created_at}. I have features such as moderation, fun commands, and more. You can get more '
                    'information on my commands by using the dropdown below.\n\n'
                    "I'm also open source. You can see my code on [GitHub](https://github.com/pandabear189/tms-scioly-bots)!"
                ),
                inline=False,
            )
        elif self.index == 1:
            entries = (
                ('<argument>', 'This means the argument is __**required**__.'),
                ('[argument]', 'This means the argument is __**optional**__.'),
                ('[A|B]', 'This means that it can be __**either A or B**__.'),
                (
                    '[argument...]',
                    'This means you can have multiple arguments.\n'
                    'Now that you know the basics, it should be noted that...\n'
                    '__**You do not type in the brackets!**__',
                ),
            )

            embed.add_field(name='How do I use this bot?', value='Reading the bot signature is pretty simple.')

            for name, value in entries:
                embed.add_field(name=name, value=value, inline=False)

        return embed


class PaginatedHelpCommand(commands.HelpCommand):
    def __init__(self):
        super().__init__(
            command_attrs={
                'cooldown': commands.CooldownMapping.from_cooldown(1, 3.0, commands.BucketType.member),
                'help': 'Shows help about the bot, a command, or a category',
                'guild_ids': [SERVER_ID],
                'name': "help"
            }
        )

    async def filter_commands(self,
                              commands: List[discord.SlashCommand],
                              *,
                              sort=False,
                              key=None
                              ) -> List[discord.SlashCommand]:
        """|coro|
        Returns a filtered list of commands and optionally sorts them.
        This takes into account the :attr:`verify_checks` and :attr:`show_hidden`
        attributes.
        Parameters
        ------------
        commands: Iterable[:class:`Command`]
            An iterable of commands that are getting filtered.
        sort: :class:`bool`
            Whether to sort the result.
        key: Optional[Callable[:class:`Command`, Any]]
            An optional key function to pass to :func:`py:sorted` that
            takes a :class:`Command` as its sole parameter. If ``sort`` is
            passed as ``True`` then this will default as the command name.
        Returns
        ---------
        List[:class:`Command`]
            A list of commands that passed the filter.
        """

        if sort and key is None:
            key = lambda c: c.name

        # Ignore Application Commands cause they dont have hidden/docs
        iterator = commands

        if self.verify_checks is False:
            # if we do not need to verify the checks then we can just
            # run it straight through normally without using await.
            return sorted(iterator, key=key) if sort else list(iterator)

        if self.verify_checks is None and not self.context.guild:
            # if verify_checks is None and we're in a DM, don't verify
            return sorted(iterator, key=key) if sort else list(iterator)

        # if we're here then we need to check every command if it can run

        ret = []
        for cmd in iterator:
            ret.append(cmd)

        if sort:
            ret.sort(key=key)
        return ret

    def signature(self, command: discord.SlashCommand) -> str:
        """:class:`str`: Returns a POSIX-like signature useful for help command output."""

        params = command.options
        if not params:
            return ''

        result = []
        for param in iter(params):
            if param.autocomplete:
                signature = f"{param.name} = **Autocomplete**"
                if param.required:
                    result.append(f'<{signature}>')
                elif not param.required:
                    result.append(f'[{signature}]')
            if param.choices:
                signature = '|'.join(f'"{v}"' if isinstance(v, str) else str(v) for v in param.choices)
                if param.required:
                    result.append(f'<{signature}>')
                elif not param.required:
                    result.append(f'[{signature}]')
            if param.default:
                # We don't want None or '' to trigger the [name=value] case and instead it should
                # do [name] since [name=None] or [name=] are not exactly useful for the user.
                should_print = param.default if isinstance(param.default, str) else param.default is not None
                if should_print:
                    result.append(f'[{param.name}={param.default}]')
                if not should_print:
                    result.append(f'[{param.name}]')
            else:
                if param.required:
                    result.append(f'<{param.name}>')
                elif not param.required:
                    result.append(f'[{param.name}]')

        return ' '.join(result)

    async def on_help_command_error(self, ctx, error):
        if isinstance(error, commands.CommandInvokeError):
            # Ignore missing permission errors
            if isinstance(error.original, discord.HTTPException) and error.original.code == 50013:
                return

            await ctx.send(str(error.original))

    def get_command_signature(self, command: discord.SlashCommand):
        parent = command.full_parent_name
        alias = command.name if not parent else f'{parent} {command.name}'
        return f'{alias} {self.signature(command)}'

    async def send_bot_help(self, mapping):
        bot = self.context.bot

        def key(command: discord.SlashCommand) -> str:
            cog = command.cog
            return '\U0010ffff' if not cog else cog.qualified_name

        entries = await self.filter_commands(
            [x for x in bot.application_commands if isinstance(x, discord.SlashCommand)],
            sort=True,
            key=key)

        all_commands: Dict[commands.Cog, List[discord.SlashCommand]] = {}
        for name, children in itertools.groupby(entries, key=key):
            if name == '\U0010ffff':
                continue

            cog = bot.get_cog(name)
            all_commands[cog] = sorted(children, key=lambda c: c.name)

        menu = HelpMenu(FrontPageSource(), ctx=self.context)
        menu.add_categories(all_commands)
        await menu.start()

    async def send_cog_help(self, cog: commands.Cog):
        cmd_list = [x for x in cog.get_commands() if isinstance(x, discord.SlashCommand)]
        entries = await self.filter_commands(cmd_list, sort=True)
        menu = HelpMenu(GroupHelpPageSource(cog, entries, prefix=self.context.clean_prefix), ctx=self.context)
        await menu.start()

    def common_command_formatting(self, embed_like, command: discord.SlashCommand):
        embed_like.title = self.get_command_signature(command)
        if command.description:
            embed_like.description = f'{command.description}'
        else:
            embed_like.description = 'No help found...'

    async def send_command_help(self, command: Union[discord.SlashCommand, commands.Command]):
        # No pagination necessary for a single command.
        embed = discord.Embed(colour=self.context.bot.color)
        self.common_command_formatting(embed, command)
        await self.context.send(embed=embed)

    async def send_group_help(self, group: Union[discord.SlashCommandGroup, discord.SlashCommand, commands.Cog]):
        subcommands = group.subcommands
        if len(subcommands) == 0:
            return await self.send_command_help(group)

        entries = await self.filter_commands(subcommands, sort=True)
        if len(entries) == 0:
            return await self.send_command_help(group)

        source = GroupHelpPageSource(group, entries, prefix=self.context.clean_prefix)
        self.common_command_formatting(source, group)
        menu = HelpMenu(source, ctx=self.context)
        await menu.start()


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.old_help_command = bot.help_command
        bot.help_command = PaginatedHelpCommand()
        bot.help_command.cog = self

    @property
    def display_emoji(self) -> discord.PartialEmoji:
        return discord.PartialEmoji(name='\N{WHITE QUESTION MARK ORNAMENT}')

    def cog_unload(self):
        self.bot.help_command = self.old_help_command

    def cog_load(self):
        self.bot.add_application_command(self.bot.help_command)


def setup(bot):
    bot.add_cog(Help(bot))
