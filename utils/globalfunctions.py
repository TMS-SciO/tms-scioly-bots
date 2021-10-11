import discord
from utils.variables import *
from utils.embed import assemble_embed
from utils.censor import CENSORED_WORDS
import dateparser
import pytz
import re
import asyncio


async def auto_report(bot, reason, color, message):
    """Allows Pi-Bot to generate a report by himself."""
    server = bot.get_guild(SERVER_ID)
    reports_channel = discord.utils.get(server.text_channels, id=CHANNEL_REPORTS)
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


async def censor(message):
    """Constructs Pi-Bot's censor."""
    channel = message.channel
    ava = message.author.avatar
    wh = await channel.create_webhook(name="Censor (Automated)")
    content = message.content
    for word in CENSORED_WORDS:
        content = re.sub(fr'\b({word})\b', "<censored>", content, flags=re.IGNORECASE)
    author = message.author.nick
    if author is None:
        author = message.author.name
    # Make sure pinging through @everyone, @here, or any role can not happen
    mention_perms = discord.AllowedMentions(everyone=False, users=True, roles=False)
    await wh.send(content, username=(author + " (Auto-Censor)"), avatar_url=ava, allowed_mentions=mention_perms)
    await wh.delete()


async def send_to_dm_log(bot, message):
    server = bot.get_guild(SERVER_ID)
    dmChannel = discord.utils.get(server.text_channels, id=CHANNEL_DMLOG)
    embed = assemble_embed(
        title=":speech_balloon: New DM",
        fields=[
            {
                    "name": "Author",
                    "value": message.author,
                    "inline": "True"
                },
                {
                    "name": "Message ID",
                    "value": message.id,
                    "inline": "True"
                },
                {
                    "name": "Created At (UTC)",
                    "value": message.created_at,
                    "inline": "True"
                },
                {
                    "name": "Attachments",
                    "value": " | ".join([f"**{a.filename}**: [Link]({a.url})" for a in message.attachments]) if len(message.attachments) > 0 else "None",
                    "inline": "False"
                },
                {
                    "name": "Content",
                    "value": message.content if len(message.content) > 0 else "None",
                    "inline": "False"
                },
                {
                    "name": "Embed",
                    "value": "\n".join([str(e.to_dict()) for e in message.embeds]) if len(message.embeds) > 0 else "None",
                    "inline": "False"
                }
            ]
    )
    await dmChannel.send(embed=embed)

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


