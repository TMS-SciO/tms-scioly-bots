import discord
from discord.ext import commands
from discord.ext.commands import Option
from utils.variables import *
from utils.times import times
from utils.views import Confirm, Role1, Role2, Role3, Role4, Role5, Allevents, Pronouns, Ticket, Nuke
from utils.checks import is_staff
from utils.globalfunctions import assemble_embed
from typing import Literal, Union, Optional
import asyncio
import json
import datetime
import math
import random


STOPNUKE = datetime.datetime.utcnow()


class Moderation(commands.Cog):
    """Moderation related commands."""
    print('Moderation Cog Loaded')

    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        return await is_staff(ctx)

    @property
    def display_emoji(self) -> discord.PartialEmoji:
        return discord.PartialEmoji(name='mod_badge', id=900488706748731472)

    @commands.command()
    async def slowmode(self,
                       ctx,
                       mode: Literal["set", "remove"] = Option(description="How to change the slowmode in the channel."),
                       delay = Option(description="Optional. How long the slowmode delay should be, in seconds. If none, assumed to be 20 seconds.", default=20),
                       channel: discord.TextChannel = Option(description="The channel to edit slowmode", default=None)
                       ):
        true_channel = channel or ctx.channel
        if mode == "remove":
            await true_channel.edit(slowmode_delay=0)
            await ctx.send("The slowmode was removed.")
        elif mode == "set":
            await true_channel.edit(slowmode_delay=delay)
            await ctx.send(f"Enabled a slowmode delay of {delay} seconds.")

    @commands.command()
    async def ban(self,
                  ctx,
                  member:discord.User = Option(description='the member to ban'),
                  reason = Option(description='the reason to ban this member'),
                  ban_length:Literal["10 minutes",
                                     "30 minutes",
                                     "1 hour",
                                     "2 hours",
                                     "8 hours",
                                     "1 day",
                                     "4 days",
                                     "7 days",
                                     "1 month",
                                     "1 year",
                                     "Indefinitely"
                                     ] = Option(
                      description='the amount of time banned')
                  ):

        """Bans a user."""
        if ban_length == "Indefinitely":
            time_statement = f"They will never be automatically unbanned."
        else:
            time_statement = f"They will be banned until {discord.utils.format_dt(times[ban_length], 'F')}."

        original_shown_embed = discord.Embed(
            title="Ban Confirmation",
            color=discord.Color.brand_red(),
            description=f"""
                    {member.mention} will be banned from the entire server. 
                    \n They will not be able to re-enter the server until the ban is lifted or the time expires.
                    \n {time_statement}
                    """
        )

        view = Confirm(ctx)
        confirm_msg = await ctx.send("Please confirm that you would like to ban this user.", view=view,
                                        embed=original_shown_embed,
                                        ephemeral=False)

        message = f"""
        You have been banned from the TMS Scioly Discord server for {reason}. \n
        If you would like to appeal please DM `pandabear#0001`
        """

        guild = ctx.author.guild
        server = self.bot.get_guild(SERVER_ID)
        reports_channel = discord.utils.get(server.text_channels, id=CHANNEL_REPORTS)

        await view.wait()
        if view.value is True:
            if member in guild.members:
                original_shown_embed.colour = discord.Color.brand_green()
                original_shown_embed.title = "Successfully Banned"
                original_shown_embed.description = f"member: `{member}` \n id: `{member.id}`\n\n was successfully banned"
                original_shown_embed.timestamp = discord.utils.utcnow()
                embed = discord.Embed(title=" ", description = message)
                embed.colour = discord.Color.brand_red()

                await member.send(embed=embed)
                await ctx.guild.ban(member, reason=reason)
                await confirm_msg.edit(embed=original_shown_embed, content= None)
                await reports_channel.send(embed=original_shown_embed)
                if ban_length != "Indefinitely":
                    CRON_LIST.append({"date": times[ban_length], "do": f"unban {member.id}"})

            elif member not in guild.members:
                original_shown_embed.colour = discord.Color.brand_green()
                original_shown_embed.title = "Successfully Banned"
                original_shown_embed.description = f"member: `{member}` \n id: `{member.id}`\n\n was successfully banned"
                original_shown_embed.timestamp = discord.utils.utcnow()
                await confirm_msg.edit(embed=original_shown_embed, content = None)
                await reports_channel.send(embed=original_shown_embed)
                if ban_length != "Indefinitely":
                    CRON_LIST.append({"date": times[ban_length], "do": f"unban {member.id}"})
            else:
                await confirm_msg.edit(
                    content="The user was not successfully banned because of an error. They remain in the server.",
                    embed=None, view=None)
        else:
            original_shown_embed.colour = discord.Colour.brand_green()
            original_shown_embed.description = "f`{member.name}` was not banned"
            original_shown_embed.title = "Ban Cancelled"
            await ctx.send(embed=original_shown_embed, view = None, content=None)

    @commands.command()
    async def unban(self, ctx, member:discord.User = Option(description="The user (id) to unban")):
        """Unbans a user."""
        if member is None:
            await ctx.channel.send("Please give either a user ID or mention a user.")
        else:
            await ctx.guild.unban(member)
            embed=discord.Embed(title="Unban Request",
                                description=f"Inverse ban hammer applied, {member.mention} unbanned. Please remember that I cannot force them to re-join the server, they must join themselves.",
                                color=0x00FF00)
            await ctx.send(embed=embed)

    @commands.command()
    async def dm(self, ctx,
                 member:discord.Member = Option(description="The member you want to send the message to"),
                 message:str = Option(description="The message you wish to send to the member")):
        em1 = discord.Embed(title=f" ",
                            description=f"> {message}",
                            color=0x2F3136)
        em1.set_author(name=f"Message from {ctx.message.author}", icon_url=ctx.message.author.avatar)
        await ctx.send(f"Message sent to `{member}`", mention_author=False)
        await member.send(embed=em1)

    @commands.command()
    async def sync(self, ctx,
                   channel: discord.TextChannel = Option(description="The channel to sync permissions with",
                                                         default=None)):
        '''Syncs permmissions to channel category'''

        if channel is None:
            await ctx.message.channel.edit(sync_permissions=True)
            await ctx.send(f'Permissions for {ctx.message.channel.mention} synced with {ctx.message.channel.category}')
        else:
            await channel.edit(sync_permissions=True)
            await ctx.send(f'Permissions for {channel.mention} synced with {channel.category}')

    @commands.command()
    async def kick(self,
                   ctx,
                   member:discord.Member= Option(description="Which user to kick"),
                   reason:str = Option(description="Why you're kicking this user")
                   ):
        view = Confirm(ctx.author)

        await ctx.send(f"Are you sure you want to kick `{member}` for `{reason}`", view=view)
        await view.wait()
        if view.value is False:
            await ctx.send('Aborting...')
        if view.value is True:

            if reason is None:
                await ctx.send("Please specify a reason why you want to kick this user!")
            if member.id in TMS_BOT_IDS:
                return await ctx.send("Hey! You can't kick me!!")
            await member.kick(reason=reason)

            em6 = discord.Embed(title="",
                                description=f"{member.mention} was kicked for {reason}.",
                                color=0xFF0000)

            await ctx.send(embed=em6)
        return view.value

    @commands.command()
    async def mute(self,
                   ctx,
                   user: discord.Member = Option(description= "The user to mute."),
                   reason: str = Option(description= "The reason to mute the user."),
                   mute_length: Literal[
                        "10 minutes",
                        "30 minutes",
                        "1 hour",
                        "2 hours",
                        "8 hours",
                        "1 day",
                        "4 days",
                        "7 days",
                        "1 month",
                        "1 year",
                        "Indefinitely"
                    ] = Option(description="How long to mute the user for.")
                   ):

        if mute_length == "Indefinitely":
            time_statement = "The user will never be automatically unmuted."
        else:
            time_statement = f"The user will be muted until {discord.utils.format_dt(times[mute_length], 'F')}."

        original_shown_embed = discord.Embed(
            title = "Mute Confirmation",
            color = discord.Color.brand_red(),
            description = f"""
            {user.mention} will be muted across the entire server. 
            The user will no longer be able to communicate in any channels they can read.
            {time_statement}
            """
        )

        view = Confirm(ctx)
        msg = await ctx.send("Please confirm that you would like to mute this user.", view = view, embed = original_shown_embed)

        message = f"You have been muted from the TMS Scioly Discord server for {reason}."

        await view.wait()
        role = discord.utils.get(user.guild.roles, name=ROLE_MUTED)
        if view.value is True:
            await user.add_roles(role)
            await user.send(message)
            if mute_length != "Indefinitely":
                CRON_LIST.append({"date": times[mute_length], "do": f"unmute {user.id}"})
            original_shown_embed.colour = discord.Colour.brand_green()
            original_shown_embed.title = "Successfully Muted"
            original_shown_embed.description = f"{user.name} was successfully muted"
            original_shown_embed.timestamp = discord.utils.utcnow()
            await msg.edit(embed=original_shown_embed, view=None, content=None)

        else:
            original_shown_embed.colour = discord.Colour.brand_green()
            original_shown_embed.title = "Mute Canceled"
            original_shown_embed.description = f"Mute of {user.name} was canceled"
            original_shown_embed.timestamp = discord.utils.utcnow()
            await msg.edit(embed=original_shown_embed, view=None, content=None)

    @commands.command()
    async def unmute(self, ctx, user: discord.Member):
        view = Confirm(ctx)
        msg = await ctx.send(f"Are you sure you want to unmute `{user}`?", view=view)
        await view.wait()
        if view.value is False:
            await ctx.send('Unmute Canceled')
        else:
            role = discord.utils.get(user.guild.roles, name=ROLE_MUTED)
            await user.remove_roles(role)
            em5 = discord.Embed(title="",
                                description=f"Successfully unmuted {user.mention}.",
                                color=0x16F22C)
            em5.timestamp = discord.utils.utcnow()
            server = self.bot.get_guild(SERVER_ID)
            reports_channel = discord.utils.get(server.text_channels, id=CHANNEL_REPORTS)
            await reports_channel.send(embed=em5)
            await msg.edit(embed=em5, view=None, content=None)
            for obj in CRON_LIST[:]:
                if obj['do'] == f'unmute {user.id}':
                    CRON_LIST.remove(obj)
        return view.value

    @commands.command()
    async def nuke(self, ctx, count: int):
        """Nukes (deletes) a specified amount of messages."""
        global STOPNUKE
        MAX_DELETE = 100
        if int(count) > MAX_DELETE:
            return await ctx.send("Chill. No more than deleting 100 messages at a time.")
        channel = ctx.channel
        if int(count) < 0:
            history = await channel.history(limit=105).flatten()
            message_count = len(history)
            if message_count > 100:
                count = 100
            else:
                count = message_count + int(count) - 1
            if count <= 0:
                return await ctx.send("Sorry, you can not delete a negative amount of messages. This is likely because you are asking to save more messages than there are in the channel.")

        original_shown_embed = discord.Embed(
            title = "NUKE COMMAND PANEL",
            color = discord.Color.brand_red(),
            description = f"""
            {count} messages will be deleted from {channel.mention} in `10` seconds...
            To stop this nuke, press the red button below!
            """
        )
        view = Nuke()
        msg = await ctx.send(embed = original_shown_embed, view = view)
        await asyncio.sleep(1)

        for i in range(9, 0, -1):
            original_shown_embed.description = f"""
            {count} messages will be deleted from {channel.mention} in `{i}` seconds...
            To stop this nuke, press the red button below!
            """
            await msg.edit(embed = original_shown_embed, view = view)
            if view.stopped:
                return
            await asyncio.sleep(1)

        original_shown_embed.description = f"""
        Now nuking {count} messages from the channel...
        """
        await msg.edit(embed = original_shown_embed, view = None)

        # Nuke has not been stopped, proceed with deleting messages
        def nuke_check(msgs: discord.Message):
            return not len(msgs.components) and not msgs.pinned

        new_embed = discord.Embed(
            title="NUKE COMMAND PANEL",
            color=discord.Color.brand_green(),
            description=f"""
                    {count} messages have been deleted from {channel.mention} 
                    """
        )

        await channel.purge(limit=count + 1, check=nuke_check)
        await ctx.send(embed=new_embed)

    @commands.command()
    async def lock(self,
                   ctx,
                   channel: discord.TextChannel= Option(default=None, description= "The channel you want to lock")
                   ):
        """
        Locks a channel to Member access.
        """
        member = ctx.message.author
        if channel is None:
            member_role = discord.utils.get(member.guild.roles, name=ROLE_MR)
            await ctx.channel.set_permissions(member_role, add_reactions=False, send_messages=False, read_messages=True)
            SL = discord.utils.get(member.guild.roles, name=ROLE_SERVERLEADER)
            await ctx.channel.set_permissions(SL, add_reactions=True, send_messages=True, read_messages=True)
            await ctx.send(f"Locked :lock: {ctx.channel.mention} to Member access.")
        else:
            member_role = discord.utils.get(member.guild.roles, name=ROLE_MR)
            await channel.set_permissions(member_role, add_reactions=False, send_messages=False, read_messages=True)
            SL = discord.utils.get(member.guild.roles, name=ROLE_SERVERLEADER)
            await channel.set_permissions(SL, add_reactions=True, send_messages=True, read_messages=True)
            await ctx.send(f"Locked :lock: {channel.mention} to Member access.")

    @commands.command()
    async def unlock(self,
                     ctx,
                     channel: discord.TextChannel= Option(default=None, description="The channel to unlock")
                     ):
        """Unlocks a channel to Member access."""
        member = ctx.message.author
        if channel is None:
            member_role = discord.utils.get(member.guild.roles, name=ROLE_MR)
            await ctx.channel.set_permissions(member_role, add_reactions=True, send_messages=True, read_messages=True)
            SL = discord.utils.get(member.guild.roles, name=ROLE_SERVERLEADER)
            await ctx.channel.set_permissions(SL, add_reactions=True, send_messages=True, read_messages=True)
            await ctx.send(
                f"Unlocked :unlock: {ctx.channel.mention} to Member access. Please check if permissions need to be synced.")
        else:
            member_role = discord.utils.get(member.guild.roles, name=ROLE_MR)
            await channel.set_permissions(member_role, add_reactions=True, send_messages=True, read_messages=True)
            SL = discord.utils.get(member.guild.roles, name=ROLE_SERVERLEADER)
            await channel.set_permissions(SL, add_reactions=True, send_messages=True, read_messages=True)
            await ctx.send(
                f"Unlocked :unlock: {channel.mention} to Member access. Please check if permissions need to be synced.")

    @commands.command()
    async def warn(self,
                   ctx,
                   member:discord.Member = Option(description="Which user to warn"),
                   reason:str = Option(description="Why you are warning this user")
                   ):
        '''Warns a user'''
        server = self.bot.get_guild(SERVER_ID)
        reports_channel = discord.utils.get(server.text_channels, id=CHANNEL_REPORTS)
        mod = ctx.message.author
        avatar = mod.avatar
        avatar1 = member.avatar.url

        if member is ctx.message.author:
            return await ctx.send("You cannot warn yourself :rolling_eyes:")
        if member.id in TMS_BOT_IDS:
            return await ctx.send(f"Hey {ctx.message.author.mention}! You can't warn {member.mention}")
        embed = discord.Embed(title="Warning Given",
                              description=f"Warning issued to {member.mention} \n id: `{member.id}`",
                              color=0xFF0000)
        embed.add_field(name="Reason:", value=f"`{reason}`")
        embed.add_field(name="Responsible Moderator:", value=f"{mod.mention}")
        embed.set_author(name=f"{member}",
                         icon_url=avatar1)

        embed1 = discord.Embed(title=" ", description=f"{member} has been warned", color=0x2E66B6)

        embed2 = discord.Embed(title=f"Warning",
                               description=f"You have been given a warning by {mod.mention} for `{reason}`. \n Please follow the rules of the server",
                               color=0xFF0000)
        embed2.set_author(name=f"{mod}",
                          icon_url=avatar)

        message = await reports_channel.send(embed=embed)
        WARN_IDS.append(message.id)
        await message.add_reaction("\U00002705")
        await message.add_reaction("\U0000274C")
        await ctx.send(embed=embed1, mention_author=False)
        await member.send(embed=embed2)

    @commands.command()
    async def blacklist(self, ctx,
                        member:discord.Member = Option(description="The member you want to blacklist from using commands")):
        '''Blacklist a user from using commands'''
        try:
            with open("blacklist.json") as f:
                data = json.load(f)
            if member.id in data['blacklisted_ids']:
                await ctx.send(f'{member.mention} is already blacklisted from using commands!', ephemeral=True)
            else:
                data["blacklisted_ids"].append(member.id)
                with open("blacklist.json", 'w') as f:
                    json.dump(data, f)
                await ctx.send(f'Blacklisted {member.mention} from using commands!', ephemeral=True)
        except Exception:
            await ctx.send(f'Failed to blacklist {member.mention}!', ephemeral=True)

    @commands.command()
    async def unblacklist(self, ctx, member:discord.Member):
        '''Un-Blacklist a user from using commands'''
        id = member.id
        with open("blacklist.json") as f:
            data = json.load(f)
        if member.id in data['blacklisted_ids']:
            # try:
            index = data["blacklisted_ids"].index(id)
            del data["blacklisted_ids"][index]
            with open('blacklist.json', 'w') as f:
                json.dump(data, f)

                await ctx.send(f"Successfully removed command blacklist from {member.mention}", ephemeral=True)
            #
            # except Exception:
            #     await ctx.send(f"Couldn't remove command blacklist from {member.mention}", ephemeral=True)
        else:
            await ctx.send(f"{member.mention} is not blacklisted from using commands", ephemeral=True)


    # @commands.command()
    # async def cancel(self, ctx, member:discord.Member):
    #     try:
    #         with open("blacklist.json") as f:
    #             data = json.load(f)
    #         if member.id in data['canceled_ids']:
    #             await ctx.send(f'{member.mention} is already #canceled :rolling_eyes: ')
    #         else:
    #             data["canceled_ids"].append(member.id)
    #             with open("blacklist.json", 'w') as f:
    #                 json.dump(data, f)
    #             await ctx.send(f'#Canceled {member.mention} :rolling_eyes:')
    #     except Exception:
    #         await ctx.send(f'Failed to #cancel {member.mention}!')


class Staff(commands.Cog):

    '''Staff Commands'''

    print("Staff Commands Loaded")

    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        return await is_staff(ctx)

    @property
    def display_emoji(self) -> discord.PartialEmoji:
        return discord.PartialEmoji(name='mod_badge', id=900488706748731472)

    @commands.command()
    async def trial(self,
                    ctx,
                    user=Option(discord.Member, description="The user you wish promote to trial leader")):
        """Promotes/Trials a user."""
        member = ctx.message.author
        role = discord.utils.get(member.guild.roles, name=ROLE_TRIAL)
        await user.add_roles(role)
        await ctx.send(f"Successfully added {role}. Congratulations {user.mention}! :partying_face: :partying_face: ")

    @commands.command()
    async def untrial(self,
                      ctx,
                      user=Option(discord.Member, description="The user you wish to demote")):
        """Demotes/unTrials a user."""
        member = ctx.message.author
        role = discord.utils.get(member.guild.roles, name=ROLE_TRIAL)
        await user.remove_roles(role)
        await ctx.send(f"Successfully removed {role} from {user.mention}.")

    @commands.command()
    async def sudo(self, ctx, channel: Optional[discord.TextChannel], who: Union[discord.Member, discord.User], *,
                   command: str):
        """Run a command as another user optionally in another channel."""
        msg = ctx.message
        channel = channel or ctx.channel
        msg.channel = channel
        msg.author = who
        msg.content = ctx.prefix + command
        new_ctx = await self.bot.get_context(msg, cls=type(ctx))
        await self.bot.invoke(new_ctx)
        await ctx.send('sent command', ephemeral=True)

    @commands.command()
    async def embed(self, ctx,
                    channel: discord.TextChannel = Option(description="The channel to send the embed to"),
                    title=Option(description="Embed title", default=None),
                    description=Option(description="Embed description", default=None),
                    title_url=Option(description="Link that the title connects to", default=None),
                    hexcolor=Option(description="Embed color (hexcolor) if not provided defaults to purple",
                                    default=None),
                    webcolor=Option(description="Webcolor of embed/ use webcolor and hex exclusively", default=None),
                    thumbnail_url=Option(description="Thumbnail image link", default=None),
                    author_url=Option(description="Link that embed author name connects to", default=None),
                    footer_text=Option(description="Text displayed in embed footer", default=None),
                    footer_url=Option(description="Embed footer icon image-url", default=None),
                    image_url=Option(description="Embed image-link/url", default=None)
                    ):
        if title is None:
            title = ""
        else:
            title = title
        if description is None:
            description = ""
        else:
            description = description
        if title_url is None:
            titleUrl = ""
        else:
            titleUrl = title_url
        if hexcolor is None:
            hexcolor = random_hex_colors_purple[math.floor(random.random() * len(random_hex_colors_purple))]
        else:
            hexcolor = hexcolor
        if webcolor is None:
            webcolor = ""
        else:
            webcolor = webcolor
        if thumbnail_url is None:
            thumbnailUrl = ""
        else:
            thumbnailUrl = thumbnail_url
        if author_url is None:
            authorUrl = ""
        else:
            authorUrl = author_url
        if footer_text is None:
            footerText = ""
        else:
            footerText = footer_text
        if footer_url is None:
            footerUrl = ""
        else:
            footerUrl = footer_url
        if image_url is None:
            imageUrl = ""
        else:
            imageUrl = image_url

        authorName = ctx.author.name
        authorIcon = ctx.author.avatar
        embed = assemble_embed(
            title=title,
            desc=description,
            titleUrl=titleUrl,
            hexcolor=hexcolor,
            webcolor=webcolor,
            thumbnailUrl=thumbnailUrl,
            authorName=authorName,
            authorUrl=authorUrl,
            authorIcon=authorIcon,
            footerText=footerText,
            footerUrl=footerUrl,
            imageUrl=imageUrl
        )
        await channel.send(embed=embed)
        await ctx.send('Embed Sent', ephemeral=True)

    @commands.command()
    async def vip(self,
                  ctx,
                  user: discord.Member = Option(description="The user you wish to VIP")):
        """Exalts/VIPs a user."""
        member = ctx.message.author
        role = discord.utils.get(member.guild.roles, name=ROLE_VIP)
        await user.add_roles(role)
        await ctx.send(f"Successfully added VIP. Congratulations {user.mention}! :partying_face: :partying_face: ")

    @commands.command()
    async def unvip(self,
                    ctx,
                    user: discord.Member = Option(description="The user you wish to unVIP")):
        """Unexalts/unVIPs a user."""
        member = ctx.message.author
        role = discord.utils.get(member.guild.roles, name=ROLE_VIP)
        await user.remove_roles(role)
        await ctx.send(f"Successfully removed VIP from {user.mention}.")


class Meta(commands.Cog):

    '''Server utilities/Moderator Config Commands'''

    print('Meta Cog Loaded')

    @property
    def display_emoji(self) -> discord.PartialEmoji:
        return discord.PartialEmoji(name='\U00002699')

    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        return await is_staff(ctx)

    @commands.command()
    async def close(self, ctx):
        '''Manually closes a ticket channel'''

        with open('data.json') as f:
            data = json.load(f)

        if ctx.channel.id in data["ticket-channel-ids"]:

            channel_id = ctx.channel.id

            def check(message):
                return message.author == ctx.author and message.channel == ctx.channel and message.content.lower() == "close"

            try:

                em = discord.Embed(title="TMS Tickets",
                                   description="Are you sure you want to close this ticket? Reply with `close` if you are sure.",
                                   color=0x00a8ff)
                ticket_chnl = ctx.channel
                await ctx.send(embed=em)
                await self.bot.wait_for('message', check=check, timeout=60)
                await ticket_chnl.delete()

                index = data["ticket-channel-ids"].index(channel_id)
                del data["ticket-channel-ids"][index]

                with open('data.json', 'w') as f:
                    json.dump(data, f)

            except asyncio.TimeoutError:
                em = discord.Embed(title="TMS Tickets",
                                   description="You have run out of time to close this ticket. Please run the command again.",
                                   color=0x00a8ff)
                await ctx.send(embed=em)

    @commands.command()
    async def addaccess(self, ctx, role_id: int = Option(description="Role id: allow see tickets")):

        with open('data.json') as f:
            data = json.load(f)

        valid_user = False

        for role_id in data["verified-roles"]:
            try:
                if ctx.guild.get_role(role_id) in ctx.author.roles:
                    valid_user = True
            except:
                pass

        if valid_user or ctx.author.guild_permissions.administrator:
            role_id = int(role_id)

            if role_id not in data["valid-roles"]:

                try:
                    role = ctx.guild.get_role(role_id)

                    with open("data.json") as f:
                        data = json.load(f)

                    data["valid-roles"].append(role_id)

                    with open('data.json', 'w') as f:
                        json.dump(data, f)

                    em = discord.Embed(title="TMS Tickets",
                                       description="You have successfully added `{}` to the list of roles with access to tickets.".format(
                                           role.name), color=0x00a8ff)

                    await ctx.send(embed=em)

                except:
                    em = discord.Embed(title="TMS Tickets",
                                       description="That isn't a valid role ID. Please try again with a valid role ID.")
                    await ctx.send(embed=em)

            else:
                em = discord.Embed(title="TMS Tickets", description="That role already has access to tickets!",
                                   color=0x00a8ff)
                await ctx.send(embed=em)

        else:
            em = discord.Embed(title="TMS Tickets", description="Sorry, you don't have permission to run that command.",
                               color=0x00a8ff)
            await ctx.send(embed=em)

    @commands.command()
    async def delaccess(self,
                        ctx,
                        role_id: int = Option(description="Role id: delete access to see tickets")
                        ):
        with open('data.json') as f:
            data = json.load(f)

        valid_user = False

        for role_id in data["verified-roles"]:
            try:
                if ctx.guild.get_role(role_id) in ctx.author.roles:
                    valid_user = True
            except:
                pass

        if valid_user or ctx.author.guild_permissions.administrator:

            try:
                role_id = int(role_id)
                role = ctx.guild.get_role(role_id)

                with open("data.json") as f:
                    data = json.load(f)

                valid_roles = data["valid-roles"]

                if role_id in valid_roles:
                    index = valid_roles.index(role_id)

                    del valid_roles[index]

                    data["valid-roles"] = valid_roles

                    with open('data.json', 'w') as f:
                        json.dump(data, f)

                    em = discord.Embed(title="TMS Tickets",
                                       description="You have successfully removed `{}` from the list of roles with access to tickets.".format(
                                           role.name), color=0x00a8ff)

                    await ctx.send(embed=em)

                else:

                    em = discord.Embed(title="TMS Tickets",
                                       description="That role already doesn't have access to tickets!", color=0x00a8ff)
                    await ctx.send(embed=em)

            except:
                em = discord.Embed(title="TMS Tickets",
                                   description="That isn't a valid role ID. Please try again with a valid role ID.")
                await ctx.send(embed=em)

        else:
            em = discord.Embed(title="TMS Tickets", description="Sorry, you don't have permission to run that command.",
                               color=0x00a8ff)
            await ctx.send(embed=em)

    @commands.command()
    async def addpingedrole(self, ctx,
                            role_id: int = Option(description="Role id to be pinged when tickets are opened")
                            ):
        with open('data.json') as f:
            data = json.load(f)

        valid_user = False

        for role_id in data["verified-roles"]:
            try:
                if ctx.guild.get_role(role_id) in ctx.author.roles:
                    valid_user = True
            except:
                pass

        if valid_user or ctx.author.guild_permissions.administrator:

            role_id = int(role_id)

            if role_id not in data["pinged-roles"]:

                try:
                    role = ctx.guild.get_role(role_id)

                    with open("data.json") as f:
                        data = json.load(f)

                    data["pinged-roles"].append(role_id)

                    with open('data.json', 'w') as f:
                        json.dump(data, f)

                    em = discord.Embed(title="TMS Tickets",
                                       description="You have successfully added `{}` to the list of roles that get pinged when new tickets are created!".format(
                                           role.name), color=0x00a8ff)

                    await ctx.send(embed=em)

                except:
                    em = discord.Embed(title="TMS Tickets",
                                       description="That isn't a valid role ID. Please try again with a valid role ID.")
                    await ctx.send(embed=em)

            else:
                em = discord.Embed(title="TMS Tickets",
                                   description="That role already receives pings when tickets are created.",
                                   color=0x00a8ff)
                await ctx.send(embed=em)

        else:
            em = discord.Embed(title="TMS Tickets", description="Sorry, you don't have permission to run that command.",
                               color=0x00a8ff)
            await ctx.send(embed=em)

    @commands.command()
    async def delpingedrole(self,
                            ctx,
                            role_id: int = Option(description="Role id: to delete, pinged when tickets are opened")
                            ):
        with open('data.json') as f:
            data = json.load(f)

        valid_user = False

        for role_id in data["verified-roles"]:
            try:
                if ctx.guild.get_role(role_id) in ctx.author.roles:
                    valid_user = True
            except:
                pass

        if valid_user or ctx.author.guild_permissions.administrator:

            try:
                role_id = int(role_id)
                role = ctx.guild.get_role(role_id)

                with open("data.json") as f:
                    data = json.load(f)

                pinged_roles = data["pinged-roles"]

                if role_id in pinged_roles:
                    index = pinged_roles.index(role_id)

                    del pinged_roles[index]

                    data["pinged-roles"] = pinged_roles

                    with open('data.json', 'w') as f:
                        json.dump(data, f)

                    em = discord.Embed(title="TMS Tickets",
                                       description="You have successfully removed `{}` from the list of roles that get pinged when new tickets are created.".format(
                                           role.name), color=0x00a8ff)
                    await ctx.send(embed=em)

                else:
                    em = discord.Embed(title="TMS Tickets",
                                       description="That role already isn't getting pinged when new tickets are created!",
                                       color=0xff008c)
                    await ctx.send(embed=em)

            except:
                em = discord.Embed(title="TMS Tickets",
                                   description="That isn't a valid role ID. Please try again with a valid role ID.")
                await ctx.send(embed=em)

        else:
            em = discord.Embed(title="TMS Tickets", description="Sorry, you don't have permission to run that command.",
                               color=0xff008c)
            await ctx.send(embed=em)

    @commands.command()
    async def addadminrole(self,
                           ctx,
                           role_id: int = Option(description="Role id, to have admin ticket commands")
                           ):
        try:
            role_id = int(role_id)
            role = ctx.guild.get_role(role_id)

            with open("data.json") as f:
                data = json.load(f)

            data["verified-roles"].append(role_id)

            with open('data.json', 'w') as f:
                json.dump(data, f)

            em = discord.Embed(title="TMS Tickets",
                               description="You have successfully added `{}` to the list of roles that can run admin-level commands!".format(
                                   role.name), color=0xff008c)
            await ctx.send(embed=em)

        except:
            em = discord.Embed(title="TMS Tickets",
                               description="That isn't a valid role ID. Please try again with a valid role ID.")
            await ctx.send(embed=em)

    @commands.command()
    async def deladminrole(self, ctx,
                           role_id: int = Option(description="Role id, delete access to admin ticket commands")):
        try:
            role_id = int(role_id)
            role = ctx.guild.get_role(role_id)

            with open("data.json") as f:
                data = json.load(f)

            admin_roles = data["verified-roles"]

            if role_id in admin_roles:
                index = admin_roles.index(role_id)

                del admin_roles[index]

                data["verified-roles"] = admin_roles

                with open('data.json', 'w') as f:
                    json.dump(data, f)

                em = discord.Embed(title="TMS Tickets",
                                   description="You have successfully removed `{}` from the list of roles that get pinged when new tickets are created.".format(
                                       role.name), color=0x00a8ff)

                await ctx.send(embed=em)

            else:
                em = discord.Embed(title="TMS Tickets",
                                   description="That role isn't getting pinged when new tickets are created!",
                                   color=0x00a8ff)
                await ctx.send(embed=em)

        except:
            em = discord.Embed(title="TMS Tickets",
                               description="That isn't a valid role ID. Please try again with a valid role ID.")
            await ctx.send(embed=em)

    @commands.command()
    async def events1(self, ctx):
        '''Buttons for Life Science Events'''
        em1 = discord.Embed(title="What events do you want to do?",
                            description="To choose your event roles press the buttons below",
                            color=0xff008c)
        em1.set_image(
            url='https://cdn.discordapp.com/attachments/685035292989718554/724301857157283910/ezgif-1-a2a2e7173d80.gif')
        em1.set_footer(text="Life Science Events - Page 1 of 5")
        server = self.bot.get_guild(SERVER_ID)
        roles_channel = discord.utils.get(server.text_channels, id=CHANNEL_ROLES)
        await roles_channel.send(embed=em1, view=Role1())
        await ctx.send('Sent to ' + roles_channel.mention, ephemeral=True)

    @commands.command()
    async def events2(self, ctx):
        '''Buttons for Earth and Space Science Events'''
        em1 = discord.Embed(title="What events do you want to do?",
                            description="To choose your event roles press the buttons below",
                            color=0xff008c)
        em1.set_image(
            url='https://cdn.discordapp.com/attachments/685035292989718554/724301857157283910/ezgif-1-a2a2e7173d80.gif')
        em1.set_footer(text="Earth and Space Science Events - Page 2 of 5")
        server = self.bot.get_guild(SERVER_ID)
        roles_channel = discord.utils.get(server.text_channels, id=CHANNEL_ROLES)
        await roles_channel.send(embed=em1, view=Role2())
        await ctx.send('Sent to ' + roles_channel.mention, ephemeral=True)

    @commands.command()
    async def events3(self, ctx):
        '''Buttons for Physical Science & Chemistry Events'''
        em1 = discord.Embed(title="What events do you want to do?",
                            description="To choose your event roles press the buttons below",
                            color=0xff008c)
        em1.set_image(
            url='https://cdn.discordapp.com/attachments/685035292989718554/724301857157283910/ezgif-1-a2a2e7173d80.gif')
        em1.set_footer(text="Physical Science & Chemistry Events - Page 3 of 5")
        server = self.bot.get_guild(SERVER_ID)
        roles_channel = discord.utils.get(server.text_channels, id=CHANNEL_ROLES)
        await roles_channel.send(embed=em1, view=Role3())
        await ctx.send('Sent to ' + roles_channel.mention, ephemeral=True)

    @commands.command()
    async def events4(self, ctx):
        '''Buttons for Technology & Engineering Design Events'''
        em1 = discord.Embed(title="What events do you want to do?",
                            description="To choose your event roles press the buttons below",
                            color=0xff008c)
        em1.set_image(
            url='https://cdn.discordapp.com/attachments/685035292989718554/724301857157283910/ezgif-1-a2a2e7173d80.gif')
        em1.set_footer(text="Technology & Engineering Design Events - Page 4 of 5")
        server = self.bot.get_guild(SERVER_ID)
        roles_channel = discord.utils.get(server.text_channels, id=CHANNEL_ROLES)
        await roles_channel.send(embed=em1, view=Role4())
        await ctx.send('Sent to ' + roles_channel.mention, ephemeral=True)

    @commands.command()
    async def events5(self, ctx):
        '''Buttons for Inquiry & Nature'''
        em1 = discord.Embed(title="What events do you want to do?",
                            description="To choose your event roles press the buttons below",
                            color=0xff008c)
        em1.set_image(
            url='https://cdn.discordapp.com/attachments/685035292989718554/724301857157283910/ezgif-1-a2a2e7173d80.gif')
        em1.set_footer(text="Inquiry & Nature of Science Events")
        server = self.bot.get_guild(SERVER_ID)
        roles_channel = discord.utils.get(server.text_channels, id=CHANNEL_ROLES)
        await roles_channel.send(embed=em1, view=Role5())
        await ctx.send('Sent to ' + roles_channel.mention, ephemeral=True)

    @commands.command()
    async def events6(self, ctx):
        '''Buttons for All Events Role'''
        em1 = discord.Embed(title="What events do you want to do?",
                            description="Press the button below to gain access to all the event channels",
                            color=0xff008c)
        em1.set_image(
            url='https://cdn.discordapp.com/attachments/685035292989718554/724301857157283910/ezgif-1-a2a2e7173d80.gif')
        server = self.bot.get_guild(SERVER_ID)
        roles_channel = discord.utils.get(server.text_channels, id=CHANNEL_ROLES)
        await roles_channel.send(embed=em1, view=Allevents())
        await ctx.send('Sent to ' + roles_channel.mention, ephemeral=True)

    @commands.command()
    async def pronouns(self, ctx):
        '''Buttons for Pronoun Roles'''
        em1 = discord.Embed(title="What pronouns do you use?",
                            description="Press the buttons below to choose your pronoun role(s)",
                            color=0xff008c)
        em1.set_image(
            url='https://cdn.discordapp.com/attachments/685035292989718554/724301857157283910/ezgif-1-a2a2e7173d80.gif')
        em1.set_footer(text="Pronoun Roles")
        server = self.bot.get_guild(SERVER_ID)
        roles_channel = discord.utils.get(server.text_channels, id=CHANNEL_ROLES)
        await roles_channel.send(embed=em1, view=Pronouns())
        await ctx.send('Sent to ' + roles_channel.mention, ephemeral=True)

    @commands.command()
    async def eventroles(self, ctx):
        '''Creates all the event role buttons'''

        server = self.bot.get_guild(SERVER_ID)
        roles_channel = discord.utils.get(server.text_channels, id=CHANNEL_ROLES)

        em1 = discord.Embed(title="What events do you want to do?",
                            description="To choose your event roles press the buttons below",
                            color=0xff008c)
        em1.set_footer(text="Life Science Events - Page 1 of 5")

        em2 = discord.Embed(title="What events do you want to do?",
                            description="To choose your event roles press the buttons below",
                            color=0xff008c)

        em2.set_footer(text="Earth and Space Science Events - Page 2 of 5")

        em3 = discord.Embed(title="What events do you want to do?",
                            description="To choose your event roles press the buttons below",
                            color=0xff008c)

        em3.set_footer(text="Physical Science & Chemistry Events - Page 3 of 5")

        em4 = discord.Embed(title="What events do you want to do?",
                            description="To choose your event roles press the buttons below",
                            color=0xff008c)

        em4.set_footer(text="Technology & Engineering Design Events - Page 4 of 5")

        em5 = discord.Embed(title="What events do you want to do?",
                            description="To choose your event roles press the buttons below",
                            color=0xff008c)
        em5.set_footer(text="Inquiry & Nature of Science Events")

        em6 = discord.Embed(title="What pronouns do you use?",
                            description="Press the buttons below to choose your pronoun role(s)",
                            color=0xff008c)
        em6.set_footer(text="Pronoun Roles")

        await roles_channel.send(embed=em1, view=Role1())
        await roles_channel.send(embed=em2, view=Role2())
        await roles_channel.send(embed=em3, view=Role3())
        await roles_channel.send(embed=em4, view=Role4())
        await roles_channel.send(embed=em5, view=Role5())
        await roles_channel.send(embed=em6, view=Pronouns())
        await ctx.send('Sent to ' + roles_channel.mention, ephemeral=True)

    @commands.command()
    async def ticket(self, ctx):
        '''Sends the ticket button embed'''
        view = Ticket(self.bot)
        em1 = discord.Embed(title="TMS Tickets",
                            description="To create a ticket press the button below", color=0xff008c)
        em1.set_image(
            url='https://cdn.discordapp.com/attachments/685035292989718554/724301857157283910/ezgif-1-a2a2e7173d80.gif')
        em1.set_footer(text="TMS-Bot Tickets for reporting or questions")
        server = self.bot.get_guild(SERVER_ID)
        rules_channel = discord.utils.get(server.text_channels, id=CHANNEL_RULES)
        await rules_channel.send(embed=em1, view=view)
        await ctx.send('Sent to ' + rules_channel.mention, ephemeral=True)


def setup(bot):
    bot.add_cog(Moderation(bot))
    bot.add_cog(Staff(bot))
    bot.add_cog(Meta(bot))
