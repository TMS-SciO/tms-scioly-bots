import discord.ext.commands as commands


class CommandNotAllowedInChannel(commands.CommandError):
    def __init__(self, channel, *args, **kwargs):
        self.channel = channel
        super().__init__(*args, **kwargs)


class CommandBlacklistedUserInvoke(commands.CommandError):
    def __init__(self, member, *args, **kwargs):
        self.member = member
        super().__init__(*args, **kwargs)
