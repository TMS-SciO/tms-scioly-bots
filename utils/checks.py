import discord
from utils.variables import *
import asyncio
import datetime
from discord.ext import commands

STOPNUKE = datetime.datetime.utcnow()


def is_staff():
    """Checks to see if the author of ctx message is a staff member."""
    #TODO make all variables id based
    def predicate(ctx):
        guild = ctx.bot.get_guild(SERVER_ID)
        member = guild.get_member(ctx.message.author.id)
        staffRole = discord.utils.get(guild.roles, name=ROLE_SERVERLEADER)
        coachRole = discord.utils.get(guild.roles, name=ROLE_COACH)
        if any(r in [staffRole, coachRole] for r in member.roles):
            return True
        raise discord.ext.commands.MissingAnyRole([staffRole, coachRole])
    return commands.check(predicate)


# async def is_staff(bot):
#     """Checks to see if the user is a staff member."""
#     member = ctx.message.author
#     staffRole = discord.utils.get(member.guild.roles, name=ROLE_SERVERLEADER)
#     coachRole = discord.utils.get(member.guild.roles, name=ROLE_COACH)
#     return staffRole in member.roles or coachRole in member.roles


# def not_blacklisted_channel(blacklist):
#     """Given a string array blacklist, check if command was not invoked in specified blacklist channels."""
#     async def predicate(ctx):
#         channel = ctx.message.channel
#         server = bot.get_guild(SERVER_ID)
#         for c in blacklist:
#             if channel == discord.utils.get(server.text_channels, name=c):
#                 raise CommandNotAllowedInChannel(channel, "Command was invoked in a blacklisted channel.")
#         return True
#
#     return commands.check(predicate)
