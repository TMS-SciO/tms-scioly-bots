import discord
from variables import ROLE_COACH, ROLE_SERVERLEADER
import asyncio
import datetime


STOPNUKE = datetime.datetime.utcnow()


async def is_staff(bot, ctx):
    """Checks to see if the user is a staff member."""
    member = ctx.message.author
    staffRole = discord.utils.get(member.guild.roles, name=ROLE_SERVERLEADER)
    coachRole = discord.utils.get(member.guild.roles, name=ROLE_COACH)
    return staffRole in member.roles or coachRole in member.roles


async def _nuke_countdown(ctx, count=-1):
    import datetime
    global STOPNUKE
    await ctx.send("=====\nINCOMING TRANSMISSION.\n=====")
    await ctx.send("PREPARE FOR IMPACT.")
    for i in range(10, 0, -1):
        if count < 0:
            await ctx.send(f"NUKING MESSAGES IN {i}... TYPE `!stopnuke` AT ANY TIME TO STOP ALL TRANSMISSION.")
        else:
            await ctx.send(
                f"NUKING {count} MESSAGES IN {i}... TYPE `!stopnuke` AT ANY TIME TO STOP ALL TRANSMISSION.")
        await asyncio.sleep(1)
        if STOPNUKE > datetime.datetime.utcnow():
            return await ctx.send("A COMMANDER HAS PAUSED ALL NUKES FOR 20 SECONDS. NUKE CANCELLED.")


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
