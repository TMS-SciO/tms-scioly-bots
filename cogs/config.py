import asyncio
import json

import discord
from discord import slash_command
from discord.commands import permissions
from discord.commands.commands import Option
from discord.ext import commands

from utils.checks import is_staff
from utils.variables import *
from utils.views import Allevents, AllEventsSelect, Pronouns, Role1, Role2, Role3, Role4, Role5, Ticket

#TODO MAKE EVERYTHING SLASH COMMANDS


class Config(commands.Cog):
    '''Server utilities/Moderator Config Commands'''

    print('Config Cog Loaded')

    @property
    def display_emoji(self) -> discord.PartialEmoji:
        return discord.PartialEmoji(name='\U00002699')

    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        return await is_staff(ctx)

    @commands.group()
    async def ticket(self, ctx):
        '''Ticket system commands'''
        pass

    @ticket.command()
    async def close(self, ctx):
        '''
        Manually closes the ticket channel
        '''

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
                await ctx.respond(embed=em)
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
                await ctx.respond(embed=em)

    @ticket.command()
    async def add_access(self, ctx, role: Option(discord.Role, description="Role id or mention role")):
        with open('data.json') as f:
            data = json.load(f)

        valid_user = False

        for role in data["verified-roles"]:
            try:
                if ctx.guild.get_role(role) in ctx.author.roles:
                    valid_user = True
            except:
                pass

        if valid_user or ctx.author.guild_permissions.administrator:
            role = int(role)

            if role not in data["valid-roles"]:

                try:
                    role = ctx.guild.get_role(role)

                    with open("data.json") as f:
                        data = json.load(f)

                    data["valid-roles"].append(role)

                    with open('data.json', 'w') as f:
                        json.dump(data, f)

                    em = discord.Embed(title="TMS Tickets",
                                       description="You have successfully added `{}` to the list of roles with access to tickets.".format(
                                           role.name), color=0x00a8ff)

                    await ctx.respond(embed=em)

                except:
                    em = discord.Embed(title="TMS Tickets",
                                       description="That isn't a valid role ID. Please try again with a valid role ID.")
                    await ctx.respond(embed=em)

            else:
                em = discord.Embed(title="TMS Tickets", description="That role already has access to tickets!",
                                   color=0x00a8ff)
                await ctx.respond(embed=em)

        else:
            em = discord.Embed(title="TMS Tickets", description="Sorry, you don't have permission to run that command.",
                               color=0x00a8ff)
            await ctx.respond(embed=em)

    @ticket.command()
    async def delete_access(self, ctx, role: Option(discord.Role, description="Role id or mention role")):
        with open('data.json') as f:
            data = json.load(f)

        valid_user = False

        for role in data["verified-roles"]:
            try:
                if ctx.guild.get_role(role) in ctx.author.roles:
                    valid_user = True
            except:
                pass

        if valid_user or ctx.author.guild_permissions.administrator:

            try:
                role = int(role)
                role = ctx.guild.get_role(role)

                with open("data.json") as f:
                    data = json.load(f)

                valid_roles = data["valid-roles"]

                if role in valid_roles:
                    index = valid_roles.index(role)

                    del valid_roles[index]

                    data["valid-roles"] = valid_roles

                    with open('data.json', 'w') as f:
                        json.dump(data, f)

                    em = discord.Embed(title="TMS Tickets",
                                       description="You have successfully removed `{}` from the list of roles with access to tickets.".format(
                                           role.name), color=0x00a8ff)

                    await ctx.respond(embed=em)

                else:

                    em = discord.Embed(title="TMS Tickets",
                                       description="That role already doesn't have access to tickets!", color=0x00a8ff)
                    await ctx.respond(embed=em)

            except:
                em = discord.Embed(title="TMS Tickets",
                                   description="That isn't a valid role ID. Please try again with a valid role ID.")
                await ctx.respond(embed=em)

        else:
            em = discord.Embed(title="TMS Tickets", description="Sorry, you don't have permission to run that command.",
                               color=0x00a8ff)
            await ctx.respond(embed=em)

    @ticket.command()
    async def add_pinged_role(self, ctx,
                              role: Option(discord.Role, description="Role id or mention role")):
        with open('data.json') as f:
            data = json.load(f)

        valid_user = False

        for role in data["verified-roles"]:
            try:
                if ctx.guild.get_role(role) in ctx.author.roles:
                    valid_user = True
            except:
                pass

        if valid_user or ctx.author.guild_permissions.administrator:

            role = int(role)

            if role not in data["pinged-roles"]:

                try:
                    role = ctx.guild.get_role(role)

                    with open("data.json") as f:
                        data = json.load(f)

                    data["pinged-roles"].append(role)

                    with open('data.json', 'w') as f:
                        json.dump(data, f)

                    em = discord.Embed(title="TMS Tickets",
                                       description="You have successfully added `{}` to the list of roles that get pinged when new tickets are created!".format(
                                           role.name), color=0x00a8ff)

                    await ctx.respond(embed=em)

                except:
                    em = discord.Embed(title="TMS Tickets",
                                       description="That isn't a valid role ID. Please try again with a valid role ID.")
                    await ctx.respond(embed=em)

            else:
                em = discord.Embed(title="TMS Tickets",
                                   description="That role already receives pings when tickets are created.",
                                   color=0x00a8ff)
                await ctx.respond(embed=em)

        else:
            em = discord.Embed(title="TMS Tickets", description="Sorry, you don't have permission to run that command.",
                               color=0x00a8ff)
            await ctx.respond(embed=em)

    @ticket.command()
    async def delete_pinged_role(self, ctx,
                                 role: Option(discord.Role, description="Role id or mention role")):
        with open('data.json') as f:
            data = json.load(f)

        valid_user = False

        for role in data["verified-roles"]:
            try:
                if ctx.guild.get_role(role) in ctx.author.roles:
                    valid_user = True
            except:
                pass

        if valid_user or ctx.author.guild_permissions.administrator:

            try:
                role = int(role)
                role = ctx.guild.get_role(role)

                with open("data.json") as f:
                    data = json.load(f)

                pinged_roles = data["pinged-roles"]

                if role in pinged_roles:
                    index = pinged_roles.index(role)

                    del pinged_roles[index]

                    data["pinged-roles"] = pinged_roles

                    with open('data.json', 'w') as f:
                        json.dump(data, f)

                    em = discord.Embed(title="TMS Tickets",
                                       description="You have successfully removed `{}` from the list of roles that get pinged when new tickets are created.".format(
                                           role.name), color=0x00a8ff)
                    await ctx.respond(embed=em)

                else:
                    em = discord.Embed(title="TMS Tickets",
                                       description="That role already isn't getting pinged when new tickets are created!",
                                       color=0xff008c)
                    await ctx.respond(embed=em)

            except:
                em = discord.Embed(title="TMS Tickets",
                                   description="That isn't a valid role ID. Please try again with a valid role ID.")
                await ctx.respond(embed=em)

        else:
            em = discord.Embed(title="TMS Tickets", description="Sorry, you don't have permission to run that command.",
                               color=0xff008c)
            await ctx.respond(embed=em)

    @ticket.command()
    async def addadminrole(self, ctx, role: Option(discord.Role, description="Role id or mention role")):
        try:
            role_id = int(role)
            role = ctx.guild.get_role(role_id)

            with open("data.json") as f:
                data = json.load(f)

            data["verified-roles"].append(role_id)

            with open('data.json', 'w') as f:
                json.dump(data, f)

            em = discord.Embed(title="TMS Tickets",
                               description="You have successfully added `{}` to the list of roles that can run admin-level commands!".format(
                                   role.name), color=0xff008c)
            await ctx.respond(embed=em)

        except:
            em = discord.Embed(title="TMS Tickets",
                               description="That isn't a valid role ID. Please try again with a valid role ID.")
            await ctx.respond(embed=em)

    @ticket.command()
    async def deladminrole(self, ctx, role: Option(discord.Role, description="Role id or mention role")):
        try:
            role_id = int(role)
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

                await ctx.respond(embed=em)

            else:
                em = discord.Embed(title="TMS Tickets",
                                   description="That role isn't getting pinged when new tickets are created!",
                                   color=0x00a8ff)
                await ctx.respond(embed=em)

        except:
            em = discord.Embed(title="TMS Tickets",
                               description="That isn't a valid role ID. Please try again with a valid role ID.")
            await ctx.respond(embed=em)

    @slash_command(guild_ids=[SERVER_ID])
    @permissions.has_any_role(ROLE_SERVERLEADER, guild_id=SERVER_ID)
    async def events1(self, ctx):
        '''Buttons for Life Science Events'''
        em1 = discord.Embed(title="Chose what events you're participating in!",
                            description="To choose your event roles press the buttons below",
                            color=0xff008c)
        em1.set_image(
            url='https://cdn.discordapp.com/attachments/685035292989718554/724301857157283910/ezgif-1-a2a2e7173d80.gif')
        em1.set_footer(text="Life Science Events - Page 1 of 5")
        server = self.bot.get_guild(SERVER_ID)
        roles_channel = discord.utils.get(server.text_channels, id=CHANNEL_ROLES)
        await roles_channel.send(embed=em1, view=Role1())
        await ctx.respond('Sent to ' + roles_channel.mention, ephemeral=True)

    @slash_command(guild_ids=[SERVER_ID])
    @permissions.has_any_role(ROLE_SERVERLEADER, guild_id=SERVER_ID)
    async def events2(self, ctx):
        '''Buttons for Earth and Space Science Events'''
        em1 = discord.Embed(title="Chose what events you're participating in!",
                            description="To choose your event roles press the buttons below",
                            color=0xff008c)
        em1.set_image(
            url='https://cdn.discordapp.com/attachments/685035292989718554/724301857157283910/ezgif-1-a2a2e7173d80.gif')
        em1.set_footer(text="Earth and Space Science Events - Page 2 of 5")
        server = self.bot.get_guild(SERVER_ID)
        roles_channel = discord.utils.get(server.text_channels, id=CHANNEL_ROLES)
        await roles_channel.send(embed=em1, view=Role2())
        await ctx.respond('Sent to ' + roles_channel.mention, ephemeral=True)

    @slash_command(guild_ids=[SERVER_ID])
    @permissions.has_any_role(ROLE_SERVERLEADER, guild_id=SERVER_ID)
    async def events3(self, ctx):
        '''Buttons for Physical Science & Chemistry Events'''
        em1 = discord.Embed(title="Chose what events you're participating in!",
                            description="To choose your event roles press the buttons below",
                            color=0xff008c)
        em1.set_image(
            url='https://cdn.discordapp.com/attachments/685035292989718554/724301857157283910/ezgif-1-a2a2e7173d80.gif')
        em1.set_footer(text="Physical Science & Chemistry Events - Page 3 of 5")
        server = self.bot.get_guild(SERVER_ID)
        roles_channel = discord.utils.get(server.text_channels, id=CHANNEL_ROLES)
        await roles_channel.send(embed=em1, view=Role3())
        await ctx.respond('Sent to ' + roles_channel.mention, ephemeral=True)

    @slash_command(guild_ids=[SERVER_ID])
    @permissions.has_any_role(ROLE_SERVERLEADER, guild_id=SERVER_ID)
    async def events4(self, ctx):
        '''Buttons for Technology & Engineering Design Events'''
        em1 = discord.Embed(title="Chose what events you're participating in!",
                            description="To choose your event roles press the buttons below",
                            color=0xff008c)
        em1.set_image(
            url='https://cdn.discordapp.com/attachments/685035292989718554/724301857157283910/ezgif-1-a2a2e7173d80.gif')
        em1.set_footer(text="Technology & Engineering Design Events - Page 4 of 5")
        server = self.bot.get_guild(SERVER_ID)
        roles_channel = discord.utils.get(server.text_channels, id=CHANNEL_ROLES)
        await roles_channel.send(embed=em1, view=Role4())
        await ctx.respond('Sent to ' + roles_channel.mention, ephemeral=True)

    @slash_command(guild_ids=[SERVER_ID])
    @permissions.has_any_role(ROLE_SERVERLEADER, guild_id=SERVER_ID)
    async def events5(self, ctx):
        '''Buttons for Inquiry & Nature'''
        em1 = discord.Embed(title="Chose what events you're participating in!",
                            description="To choose your event roles press the buttons below",
                            color=0xff008c)
        em1.set_image(
            url='https://cdn.discordapp.com/attachments/685035292989718554/724301857157283910/ezgif-1-a2a2e7173d80.gif')
        em1.set_footer(text="Inquiry & Nature of Science Events")
        server = self.bot.get_guild(SERVER_ID)
        roles_channel = discord.utils.get(server.text_channels, id=CHANNEL_ROLES)
        await roles_channel.send(embed=em1, view=Role5())
        await ctx.respond('Sent to ' + roles_channel.mention, ephemeral=True)

    @slash_command(guild_ids=[SERVER_ID])
    @permissions.has_any_role(ROLE_SERVERLEADER, guild_id=SERVER_ID)
    async def events6(self, ctx):
        '''Buttons for All Events Role'''
        em1 = discord.Embed(title="Chose what events you're participating in!",
                            description="Press the button below to gain access to all the event channels",
                            color=0xff008c)
        em1.set_image(
            url='https://cdn.discordapp.com/attachments/685035292989718554/724301857157283910/ezgif-1-a2a2e7173d80.gif')
        server = self.bot.get_guild(SERVER_ID)
        roles_channel = discord.utils.get(server.text_channels, id=CHANNEL_ROLES)
        await roles_channel.send(embed=em1, view=Allevents())
        await ctx.respond('Sent to ' + roles_channel.mention, ephemeral=True)

    @slash_command(guild_ids=[SERVER_ID])
    @permissions.has_any_role(ROLE_SERVERLEADER, guild_id=SERVER_ID)
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
        await ctx.respond('Sent to ' + roles_channel.mention, ephemeral=True)

    @slash_command(guild_ids=[SERVER_ID])
    @permissions.has_any_role(ROLE_SERVERLEADER, guild_id=SERVER_ID)
    async def eventroles(self, ctx):
        '''Creates all the event role buttons'''

        server = self.bot.get_guild(SERVER_ID)
        roles_channel = discord.utils.get(server.text_channels, id=CHANNEL_ROLES)

        em1 = discord.Embed(title="Chose what events you're participating in!",
                            description="To choose your event roles press the buttons below",
                            color=0xff008c)
        em1.set_footer(text="Life Science Events - Page 1 of 5")

        em2 = discord.Embed(title="Chose what events you're participating in!",
                            description="To choose your event roles press the buttons below",
                            color=0xff008c)

        em2.set_footer(text="Earth and Space Science Events - Page 2 of 5")

        em3 = discord.Embed(title="Chose what events you're participating in!",
                            description="To choose your event roles press the buttons below",
                            color=0xff008c)

        em3.set_footer(text="Physical Science & Chemistry Events - Page 3 of 5")

        em4 = discord.Embed(title="Chose what events you're participating in!",
                            description="To choose your event roles press the buttons below",
                            color=0xff008c)

        em4.set_footer(text="Technology & Engineering Design Events - Page 4 of 5")

        em5 = discord.Embed(title="Chose what events you're participating in!",
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
        await ctx.respond('Sent to ' + roles_channel.mention, ephemeral=True)

    @slash_command(guild_ids=[SERVER_ID])
    @permissions.has_any_role(ROLE_SERVERLEADER, guild_id=SERVER_ID)
    async def event_test(self, ctx):
        await ctx.respond("test", view=AllEventsSelect())

    @ticket.command()
    @permissions.has_any_role(ROLE_SERVERLEADER, guild_id=SERVER_ID)
    async def button(self, ctx):
        '''Sends the ticket button embed to the rules channel'''
        view = Ticket(self.bot)
        em1 = discord.Embed(title="TMS Tickets",
                            description="To create a ticket press the button below", color=0xff008c)
        em1.set_image(
            url='https://cdn.discordapp.com/attachments/685035292989718554/724301857157283910/ezgif-1-a2a2e7173d80.gif')
        em1.set_footer(text="TMS-Bot Tickets for reporting or questions")
        server = self.bot.get_guild(SERVER_ID)
        rules_channel = discord.utils.get(server.text_channels, id=CHANNEL_RULES)
        await rules_channel.send(embed=em1, view=view)
        await ctx.respond('Sent to ' + rules_channel.mention, ephemeral=True)

    @slash_command(guild_ids=[SERVER_ID])
    @permissions.has_any_role(ROLE_SERVERLEADER, guild_id=SERVER_ID)
    async def theme(
            self, ctx, theme: Option(str, choices=["Christmas",
                                                   "Thanksgiving",
                                                   "Aesthetic",
                                                   "Party"]
                                     )
    ) -> discord.InteractionMessage:

        themes = {"Thanksgiving": "\U0001f983",
                  "Aesthetic": "\U00002728",
                  "Party": "\U0001f389"}
        await ctx.defer()

        if theme == "Christmas":
            general_channel = ctx.guild.get_channel(816806329925894220)
            main_category = ctx.guild.get_channel(816808800572538933)
            server_category = ctx.guild.get_channel(863055197890674759)
            admin_category = ctx.guild.get_channel(871885248223400016)
            events_category = ctx.guild.get_channel(816806329925894218)
            voice_category = ctx.guild.get_channel(878811294189375529)

            for channel in main_category.channels:
                emoji = "\N{EVERGREEN TREE}"
                channel_name_x = channel.name.split("│")
                channel_name = channel_name_x[1]
                await channel.edit(name=f"{emoji}" + "│" + channel_name)

            for channel in server_category.channels:
                emoji = "\N{CHRISTMAS TREE}"
                channel_name_x = channel.name.split("│")
                channel_name = channel_name_x[1]
                await channel.edit(name=f"{emoji}" + "│" + channel_name)

            for channel in admin_category.channels:
                emoji = "\N{CHRISTMAS TREE}"
                channel_name_x = channel.name.split("│")
                channel_name = channel_name_x[1]
                await channel.edit(name=f"{emoji}" + "│" + channel_name)

            for channel in events_category.channels:
                emoji = "\N{WRAPPED PRESENT}"
                channel_name_x = channel.name.split("│")
                channel_name = channel_name_x[1]
                await channel.edit(name=f"{emoji}" + "│" + channel_name)

            for channel in voice_category.channels:
                emoji = "\N{GLOWING STAR}"
                channel_name_x = channel.name.split("│")
                channel_name = channel_name_x[1]
                await channel.edit(name=f"{emoji}" + "│" + channel_name)

            await main_category.edit(name=f"\N{EVERGREEN TREE}" + "│" + "mains")
            await server_category.edit(name=f"\N{CHRISTMAS TREE}" + "│" + "server")
            await admin_category.edit(name=f"\N{CHRISTMAS TREE}" + "│" + "admin")
            await events_category.edit(name=f"\N{WRAPPED PRESENT}" + "│" + "events")
            await general_channel.edit(name="\N{CHRISTMAS TREE}" + "│general")
            await voice_category.edit(name="\N{GLOWING STAR}" + "│voice channels")
            embed = discord.Embed()
            embed.title = "\N{CHRISTMAS TREE} Theme change complete! \N{CHRISTMAS TREE}"
            embed.description = "The server is now set to christmas mode. Happy Holidays!"
            embed.colour = 0x146B3A
            return await ctx.respond(embed=embed)
        else:
            emoji = themes[theme]
            for channel in ctx.guild.channels:
                channel_name_x = channel.name.split("│")
                channel_name = channel_name_x[1]
                await channel.edit(name=f"{emoji}" + "│" + channel_name)
        await ctx.respond("Theme change complete!")


def setup(bot):
    bot.add_cog(Config(bot))
    
