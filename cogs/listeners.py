from discord.ext import commands
import discord
from utils.variables import *
from utils.censor import CENSORED_WORDS
from utils.globalfunctions import auto_report, send_to_dm_log, censor
from utils.embed import assemble_embed
from utils.commanderr import CommandNotAllowedInChannel
import re
import traceback
import dateparser
import asyncio


class discordEvents(commands.Cog):
    """Discord Events."""
    print('Events Cog Loaded')

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        if payload.user_id not in TMS_BOT_IDS:
            guild = self.bot.get_guild(payload.guild_id)
            reports_channel = discord.utils.get(guild.text_channels, id=CHANNEL_REPORTS)
            if payload.message_id in WARN_IDS:
                messageObj = await reports_channel.fetch_message(payload.message_id)
                if payload.emoji.name == "\U0000274C":  # :x:
                    print("Warning cleared with no action.")
                    await messageObj.delete()
                if payload.emoji.name == "\U00002705":  # :white_check_mark:
                    print("Warning handled.")
                    await messageObj.delete()

            elif payload.message_id in REPORT_IDS:
                messageObj = await reports_channel.fetch_message(payload.message_id)
                if payload.emoji.name == "\U0000274C":  # :x:
                    print("Report cleared with no action.")
                    await messageObj.delete()
                if payload.emoji.name == "\U00002705":  # :white_check_mark:
                    print("Report handled.")
                    await messageObj.delete()





    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        if after.nick is None:
            return
        for word in CENSORED_WORDS:
            if len(re.findall(fr"\b({word})\b", after.nick, re.I)):
                await auto_report(self.bot, "Innapropriate Username Detected", "red",
                                  f"A member ({str(after)}) has updated their nickname to **{after.nick}**, which the censor caught as innapropriate.")

    @commands.Cog.listener()
    async def on_raw_message_delete(self, payload):
        channel = self.bot.get_channel(payload.channel_id)
        guild = self.bot.get_guild(SERVER_ID) if channel.type == discord.ChannelType.private else channel.guild
        if channel.type != discord.ChannelType.private and channel.id in [CHANNEL_REPORTS, CHANNEL_DELETEDM,
                                                                            CHANNEL_DMLOG]:
            print("Ignoring deletion event because of the channel it's from.")
            return

        deleted_channel = discord.utils.get(guild.text_channels, id=CHANNEL_DELETEDM)
        try:
            message = payload.cached_message
            channel_name = f"{message.author.mention}'s DM" if channel.type == discord.ChannelType.private else message.channel.mention
            embed = assemble_embed(
                title=":fire: Deleted Message",
                fields=[
                    {
                        "name": "Author",
                        "value": message.author,
                        "inline": "False"
                    },
                    {
                        "name": "Channel",
                        "value": channel_name,
                        "inline": "False"
                    },
                    {
                        "name": "Message ID",
                        "value": message.id,
                        "inline": "False"
                    },
                    {
                        "name": "Created At (UTC)",
                        "value": message.created_at,
                        "inline": "False"
                    },
                    {
                        "name": "Edited At (UTC)",
                        "value": message.edited_at,
                        "inline": "False"
                    },
                    {
                        "name": "Attachments",
                        "value": " | ".join([f"**{a.filename}**: [Link]({a.url})" for a in message.attachments]) if len(
                            message.attachments) > 0 else "None",
                        "inline": "False"
                    },
                    {
                        "name": "Content",
                        "value": str(message.content)[:1024] if len(message.content) > 0 else "None",
                        "inline": "True"
                    },
                    {
                        "name": "Embed",
                        "value": "\n".join([str(e.to_dict()) for e in message.embeds])[:1024] if len(
                            message.embeds) > 0 else "None",
                        "inline": "False"
                    }
                ]
            )
            await deleted_channel.send(embed=embed)
        except Exception as e:
            print(e)
            embed = assemble_embed(
                title=":fire: Deleted Message",
                fields=[
                    {
                        "name": "Channel",
                        "value": self.bot.get_channel(payload.channel_id).mention,
                        "inline": "True"
                    },
                    {
                        "name": "Message ID",
                        "value": payload.message_id,
                        "inline": "True"
                    }
                ]
            )
            await deleted_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        server = self.bot.get_guild(SERVER_ID)
        reports_channel = discord.utils.get(server.text_channels, id=CHANNEL_DEV)
        print("Command Error:")
        print(error)
        # Argument parsing errors
        if isinstance(error, discord.ext.commands.UnexpectedQuoteError) or isinstance(error,
                                                                                      discord.ext.commands.InvalidEndOfQuotedStringError):
            return await ctx.send(
                "Sorry, it appears that your quotation marks are misaligned, and I can't read your query.")
        if isinstance(error, discord.ext.commands.ExpectedClosingQuoteError):
            return await ctx.send(
                "Oh. I was expecting you were going to close out your command with a quote somewhere, but never found it!")

            # User input errors
        if isinstance(error, discord.ext.commands.MissingRequiredArgument):
            return await ctx.send("Oops, you are missing a required argument in the command.")
        if isinstance(error, discord.ext.commands.ArgumentParsingError):
            return await ctx.send("Sorry, I had trouble parsing one of your arguments.")
        if isinstance(error, discord.ext.commands.TooManyArguments):
            return await ctx.send("Woahhh!! Too many arguments for this command!")
        if isinstance(error, discord.ext.commands.BadArgument) or isinstance(error,
                                                                             discord.ext.commands.BadUnionArgument):
            return await ctx.send("Sorry, I'm having trouble reading one of the arguments you just used. Try again!")

            # Check failure errors
        if isinstance(error, discord.ext.commands.CheckAnyFailure):
            return await ctx.send("It looks like you aren't able to run this command, sorry.")
        if isinstance(error, discord.ext.commands.PrivateMessageOnly):
            return await ctx.send("Pssttt. You're going to have to DM me to run this command!")
        if isinstance(error, discord.ext.commands.NoPrivateMessage):
            return await ctx.send("Ope. You can't run this command in the DM's!")
        if isinstance(error, discord.ext.commands.NotOwner):
            return await ctx.send("Oof. You have to be the bot's master to run that command!")
        if isinstance(error, discord.ext.commands.MissingPermissions) or isinstance(error,
                                                                                    discord.ext.commands.BotMissingPermissions):
            return await ctx.send("Er, you don't have the permissions to run this command.")
        if isinstance(error, discord.ext.commands.MissingRole) or isinstance(error,
                                                                             discord.ext.commands.BotMissingRole):
            return await ctx.send("Oh no... you don't have the required role to run this command.")
        if isinstance(error, discord.ext.commands.MissingAnyRole) or isinstance(error,
                                                                                discord.ext.commands.BotMissingAnyRole):
            return await ctx.send("Oh no... you don't have the required role to run this command.")
            # Command errors
        if isinstance(error, CommandNotAllowedInChannel):
            return await ctx.send(f"You are not allowed to use this command in {error.channel.mention}.")

        if isinstance(error, discord.ext.commands.ConversionError):
            return await ctx.send('Oops, there was a bot error here, sorry about that.')

        if isinstance(error, discord.ext.commands.UserInputError):
            return await ctx.send("Hmmm... I'm having trouble reading what you're trying to tell me.")
        if isinstance(error, discord.ext.commands.CommandNotFound):
            return await ctx.send("Sorry, I couldn't find that command.")
        if isinstance(error, discord.ext.commands.CheckFailure):
            return await ctx.send("Sorry, but I don't think you can run that command.")
        if isinstance(error, discord.ext.commands.DisabledCommand):
            return await ctx.send("Sorry, but this command is disabled.")
        if isinstance(error, discord.ext.commands.CommandInvokeError):
            return await ctx.send(f'Sorry, but an error incurred when the command was invoked. \n error: {error}')
        if isinstance(error, discord.ext.commands.CommandOnCooldown):
            return await ctx.send("Slow down buster! This command's on cooldown.")
        if isinstance(error, discord.ext.commands.MaxConcurrencyReached):
            return await ctx.send(
                "Uh oh. This command has reached MAXIMUM CONCURRENCY. *lightning flash*. Try again later.")

            # Extension errors (not doing specifics)
        if isinstance(error, discord.ext.commands.ExtensionError):
            return await ctx.send("Oh no. There's an extension error. Please ping Eric about this one.")

            # Client exception errors (not doing specifics)
        if isinstance(error, discord.ext.commands.CommandRegistrationError):
            return await ctx.send("Oh boy. Command registration error. Please ping Eric about this.")

            # Overall errors
        if isinstance(error, discord.ext.commands.CommandError):
            return await ctx.send('Oops, there was a command error. Try again.')

        if isinstance(error, discord.errors.NotFound):
            return await ctx.send('Oops, there was a channel error')

        if isinstance(error, RuntimeError):
            return await reports_channel.send('Oops, there was a runtime error')

    @commands.Cog.listener()
    async def on_error(self, event, *args, **kwargs):
        print("Code Error:")
        print(traceback.format_exc())

    @commands.Cog.listener()
    async def on_member_join(self, member):
        role = discord.utils.get(member.guild.roles, name=ROLE_MR)
        join_channel = discord.utils.get(member.guild.text_channels, id=WELCOME_CHANNEL)
        await member.add_roles(role)
        await join_channel.send(
            f"Everyone Welcome {member.mention} to the TMS SciOly Discord, If you need any help please open a ticket or type !`help`")

    @commands.Cog.listener()
    async def on_message(self, message):
        # Log DMs
        if type(message.channel) == discord.DMChannel:
            await send_to_dm_log(self.bot, message)
        else:
            # Print to output
            if not (message.author.id in TMS_BOT_IDS and message.channel.name in [CHANNEL_EDITEDM, CHANNEL_DELETEDM,
                                                                                  CHANNEL_DMLOG]):
                # avoid sending logs for messages in log channels
                print(f'Message from {message.author} in #{message.channel}: {message.content}')

        # Prevent command usage in channels outside of #self.bot-spam
        author = message.author
        if type(message.channel) != discord.DMChannel and message.content.startswith(BOT_PREFIX) and author.roles[
            -1] == discord.utils.get(author.guild.roles, name=ROLE_MR):
            if message.channel.name != CHANNEL_BOTSPAM:
                allowedCommands = ["about", "dogbomb", "exchange", "gallery", "invite", "me", "magic8ball", "latex",
                                   "obb", "profile", "r", "report", "rule", "shibabomb", "tag", "wiki", "wikipedia",
                                   "wp"]
                allowed = False
                for c in allowedCommands:
                    if message.content.find(BOT_PREFIX + c) != -1: allowed = True
                if not allowed:
                    botspam_channel = discord.utils.get(message.guild.text_channels, id=CHANNEL_BOTSPAM)
                    clarify_message = await message.channel.send(
                        f"{author.mention}, please use bot commands only in {botspam_channel.mention}. If you have more questions, you can ping a moderator.")
                    await asyncio.sleep(10)
                    await clarify_message.delete()
                    return await message.delete()

        if message.author.id in TMS_BOT_IDS: return
        content = message.content
        for word in CENSORED_WORDS:
            if len(re.findall(fr"\b({word})\b", content, re.I)):
                print(f"Censoring message by {message.author} because of the word: `{word}`")
                await message.delete()
                await censor(message)

        if message.author.id == 588924782221983764 and message.content.lower() == "i win":
            await message.channel.send("Gum wins again!")

        # SPAM TESTING
        global RECENT_MESSAGES
        caps = False
        u = sum(1 for c in message.content if c.isupper())
        l = sum(1 for c in message.content if c.islower())
        if u > (l + 3): caps = True
        RECENT_MESSAGES = [{"author": message.author.id, "content": message.content.lower(),
                            "caps": caps}] + RECENT_MESSAGES[:20]
        # Spam checker
        if RECENT_MESSAGES.count({"author": message.author.id, "content": message.content.lower()}) >= 6:
            muted_role = discord.utils.get(message.author.guild.roles, name=ROLE_MUTED)
            parsed = dateparser.parse("1 hour", settings={"PREFER_DATES_FROM": "future"})
            CRON_LIST.append({"date": parsed, "do": f"unmute {message.author.id}"})
            await message.author.add_roles(muted_role)
            await message.channel.send(f"Successfully muted {message.author.mention} for 1 hour.")
            await auto_report(self.bot, "User was auto-muted (spam)", "red",
                              f"A user ({str(message.author)}) was auto muted in {message.channel.mention} because of repeated spamming.")
        elif RECENT_MESSAGES.count({"author": message.author.id, "content": message.content.lower()}) >= 3:
            await message.channel.send(
                f"{message.author.mention}, please watch the spam. You will be muted if you do not stop.")
        # Caps checker
        elif sum(1 for m in RECENT_MESSAGES if m['author'] == message.author.id and m['caps']) > 8 and caps:
            muted_role = discord.utils.get(message.author.guild.roles, name=ROLE_MUTED)
            parsed = dateparser.parse("1 hour", settings={"PREFER_DATES_FROM": "future"})
            CRON_LIST.append({"date": parsed, "do": f"unmute {message.author.id}"})
            await message.author.add_roles(muted_role)
            await message.channel.send(f"Successfully muted {message.author.mention} for 1 hour.")
            await auto_report(self.bot, "User was auto-muted (caps)", "red",
                              f"A user ({str(message.author)}) was auto muted in {message.channel.mention} because of repeated caps.")
        elif sum(1 for m in RECENT_MESSAGES if m['author'] == message.author.id and m['caps']) > 3 and caps:
            await message.channel.send(
                f"{message.author.mention}, please watch the caps, or else I will lay down the mute hammer!")

        # # Do not treat messages with only exclamations as command
        # if message.content.count(BOT_PREFIX, BOT_PREFIX1) > 1:
        #     return

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        print('Message from {0.author} edited to: {0.content}, from: {1.content}'.format(after, before))
        for word in CENSORED_WORDS:
            if len(re.findall(fr"\b({word})\b", after.content, re.I)):
                print(f"Censoring message by {after.author} because of the word: `{word}`")
                await after.delete()
                await censor(after)
        if after.content.startswith(BOT_PREFIX):
            await self.bot.process_commands(after)


def setup(bot):
    bot.add_cog(discordEvents(bot))
