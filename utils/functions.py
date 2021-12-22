import discord
from utils.variables import *
from utils.embed import assemble_embed
from cogs.censor import CENSORED
import dateparser
import pytz
import re


async def auto_report(bot, reason, color, message):
    """Allows Pi-Bot to generate a report by himself."""
    server = bot.get_guild(SERVER_ID)
    reports_channel = discord.utils.get(server.text_channels, id=CHANNEL_REPORTS)
    embed = assemble_embed(title=f"{reason} (message from TMS-Bot)", webcolor=color, fields=[{
        "name": "Message",
        "value": message,
        "inline": False
    }])
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
    if time is None:
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


async def send_to_dm_log(bot, message):
    guild = bot.get_guild(SERVER_ID)
    dm_channel = discord.utils.get(guild.text_channels, id=CHANNEL_DMLOG)

    if message.author.id == bot.user.id:
        title = ":speech_balloon: Outgoing Direct Message"
        color = discord.Color.fuchsia()
    else:
        title = ":speech_balloon: Incoming Direct Message to TMS-Bot"
        color = discord.Color.brand_green()

    # Create an embed containing the direct message info and send it to the log channel
    message_embed = discord.Embed(
        title=title,
        description=message.content if len(message.content) > 0 else "This message contained no content.",
        color=color
    )
    message_embed.add_field(name="Author", value=message.author.mention, inline=True)
    message_embed.add_field(name="Message ID", value=message.id, inline=True)
    message_embed.add_field(name="Sent", value=discord.utils.format_dt(message.created_at, 'R'), inline=True)
    message_embed.add_field(name="Attachments", value=" | ".join(
        [f"**{a.filename}**: [Link]({a.url})" for a in message.attachments]) if len(
        message.attachments) > 0 else "None", inline=True)
    await dm_channel.send(embed=message_embed)



