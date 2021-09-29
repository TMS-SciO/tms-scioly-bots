import discord
from variables import *
from embed import assemble_embed
import dateparser
import pytz


async def auto_report(bot, reason, color, message):
    """Allows Pi-Bot to generate a report by himself."""
    server = bot.get_guild(SERVER_ID)
    reports_channel = discord.utils.get(server.text_channels, name=CHANNEL_REPORTS)
    embed = assemble_embed(
        title=f"{reason} (message from TMS-Bot)",
        webcolor=color,
        fields = [{
            "name": "Message",
            "value": message,
            "inline": False
        }]
    )
    message = await reports_channel.send(embed=embed)
    REPORT_IDS.append(message.id)
    await message.add_reaction("\U00002705")
    await message.add_reaction("\U0000274C")


async def _mute(ctx, user: discord.Member, time: str, self: bool):
    """
    Helper function for muting commands.
    :param user: User to be muted.
    :type user: discord.Member
    :param time: The time to mute the user for.
    :type time: str
    """
    if user.id in TMS_BOT_IDS:
        return await ctx.send("Hey! You can't mute me!!")
    if time == None:
        return await ctx.send(
            "You need to specify a length that this used will be muted. Examples are: `1 day`, `2 months, 1 day`, or `indef` (aka, forever).")
    role = None
    if self:
        role = discord.utils.get(user.guild.roles, name=ROLE_SELFMUTE)
    else:
        role = discord.utils.get(user.guild.roles, name=ROLE_MUTED)
    parsed = "indef"
    if time != "indef":
        parsed = dateparser.parse(time, settings={"PREFER_DATES_FROM": "future"})
        if parsed is None:
            return await ctx.send("Sorry, but I don't understand that length of time.")
        CRON_LIST.append({"date": parsed, "do": f"unmute {user.id}"})
    await user.add_roles(role)
    central = pytz.timezone("US/Central")
    em4 = discord.Embed(title="",
                        description=f"Successfully muted {user.mention} until `{str(central.localize(parsed))} CT`.",
                        color=0xFF0000)
    await ctx.send(embed=em4)
