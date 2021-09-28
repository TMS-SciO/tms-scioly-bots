import discord
from discord.ext import commands
from variables import ROLE_COACH, ROLE_SERVERLEADER

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())


async def is_staff(ctx):
    """Checks to see if the user is a staff member."""
    member = ctx.message.author
    staffRole = discord.utils.get(member.guild.roles, name=ROLE_SERVERLEADER)
    coachRole = discord.utils.get(member.guild.roles, name=ROLE_COACH)
    return staffRole in member.roles or coachRole in member.roles
