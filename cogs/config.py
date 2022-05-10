from __future__ import annotations

import asyncio
import json
from typing import Literal, TYPE_CHECKING

import discord
from discord.app_commands import checks, command, describe, Group, guilds
from discord.ext import commands

from utils import Channel, Role, SERVER_ID
from utils.views import Pronouns, Role1, Role2, Role3, Role4, Role5, Ticket

if TYPE_CHECKING:
    from bot import TMS


class Config(commands.Cog):
    """Server utilities/Moderator Config Commands"""

    print('Config Cog Loaded')

    @property
    def display_emoji(self) -> discord.PartialEmoji:
        return discord.PartialEmoji(name='\U00002699')

    def __init__(self, bot: TMS):
        self.bot = bot
        self.__cog_app_commands__.append(TicketGroup(bot))
        self.__cog_app_commands__.append(RolesGroup(bot))

    @command()
    @guilds(SERVER_ID)
    @checks.has_any_role(Role.SERVERLEADER, Role.FORMER_SL)
    async def theme(
            self,
            interaction: discord.Interaction,
            theme: Literal["Christmas", "Thanksgiving", "Aesthetic", "Party"]
    ) -> None:

        themes = {
            "Thanksgiving": "\U0001f983",
            "Aesthetic": "\U00002728",
            "Party": "\U0001f389"
        }
        await interaction.response.defer()

        if theme == "Christmas":
            general_channel = interaction.guild.get_channel(816806329925894220)
            main_category = interaction.guild.get_channel(816808800572538933)
            server_category = interaction.guild.get_channel(863055197890674759)
            admin_category = interaction.guild.get_channel(871885248223400016)
            events_category = interaction.guild.get_channel(816806329925894218)
            voice_category = interaction.guild.get_channel(878811294189375529)

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
            return await interaction.followup.send(embed=embed)
        else:
            emoji = themes[theme]
            for channel in interaction.guild.channels:
                channel_name_x = channel.name.split("│")
                channel_name = channel_name_x[1]
                await channel.edit(name=f"{emoji}" + "│" + channel_name)
        await interaction.followup.send("Theme change complete!")


class TicketGroup(Group):
    def __init__(self, bot: TMS):
        self.bot = bot
        super().__init__(
            name="ticket",
            guild_ids=[SERVER_ID]
        )

    @property
    def cog(self) -> commands.Cog:
        return self.bot.get_cog("Config")

    @command(name="button")
    @checks.has_any_role(Role.SERVERLEADER, Role.FORMER_SL)
    async def _button(self, interaction: discord.Interaction):
        """Sends the ticket button embed to the rules channel"""
        view = Ticket(self.bot)
        em1 = discord.Embed(title="TMS Tickets",
                            description="To create a ticket press the button below", color=0xff008c)
        em1.set_image(
            url='https://cdn.discordapp.com/attachments/685035292989718554/724301857157283910/ezgif-1-a2a2e7173d80.gif')
        em1.set_footer(text="TMS-Bot Tickets for reporting or questions")
        rules_channel = self.bot.get_channel(Channel.RULES)
        await rules_channel.send(embed=em1, view=view)
        await interaction.response.send_message('Sent to ' + rules_channel.mention, ephemeral=True)

    @command()
    @checks.has_any_role(Role.SERVERLEADER, Role.FORMER_SL)
    async def close(self, interaction: discord.Interaction):
        """Manually closes the ticket channel"""

        with open('data.json') as f:
            data = json.load(f)

        if interaction.channel.id in data["ticket-channel-ids"]:

            channel_id = interaction.channel.id

            def check(message) -> bool:
                return message.author == interaction.user and message.channel == interaction.channel and message.content.lower() == "close"

            try:

                em = discord.Embed(
                    title="TMS Tickets",
                    description="Are you sure you want to close this ticket? Reply with `close` if you are sure.",
                    color=0x00a8ff)

                ticket_channel = interaction.channel
                await interaction.response.send_message(embed=em)
                await self.bot.wait_for('message', check=check, timeout=60)
                await ticket_channel.delete()

                index = data["ticket-channel-ids"].index(channel_id)
                del data["ticket-channel-ids"][index]

                with open('data.json', 'w') as f:
                    json.dump(data, f)

            except asyncio.TimeoutError:
                em = discord.Embed(
                    title="TMS Tickets",
                    description="You have run out of time to close this ticket. Please run the command again.",
                    color=0x00a8ff)
                await interaction.response.send_message(embed=em)

    @command()
    @checks.has_any_role(Role.SERVERLEADER, Role.FORMER_SL)
    @describe(role="Role ID or mention role")
    async def add_access(self, interaction: discord.Interaction, role: discord.Role):
        with open('data.json') as f:
            data = json.load(f)

        valid_user = False

        for role in data["verified-roles"]:
            try:
                if interaction.guild.get_role(role) in interaction.user.roles:
                    valid_user = True
            except:
                pass

        if valid_user or interaction.user.guild_permissions.administrator:
            role = int(role)

            if role not in data["valid-roles"]:

                try:
                    role = interaction.guild.get_role(role)

                    with open("data.json") as f:
                        data = json.load(f)

                    data["valid-roles"].append(role)

                    with open('data.json', 'w') as f:
                        json.dump(data, f)

                    em = discord.Embed(
                        title="TMS Tickets",
                        description=f"You have successfully added `{role.name}` to the list of roles with access "
                                    "to tickets.", color=0x00a8ff
                    )

                    await interaction.response.send_message(embed=em)

                except:
                    em = discord.Embed(title="TMS Tickets",
                                       description="That isn't a valid role ID. Please try again with a valid role ID.")
                    await interaction.response.send_message(embed=em)

            else:
                em = discord.Embed(title="TMS Tickets", description="That role already has access to tickets!",
                                   color=0x00a8ff)
                await interaction.response.send_message(embed=em)

        else:
            em = discord.Embed(title="TMS Tickets", description="Sorry, you don't have permission to run that command.",
                               color=0x00a8ff)
            await interaction.response.send_message(embed=em)

    @command()
    @checks.has_any_role(Role.SERVERLEADER, Role.FORMER_SL)
    @describe(role="Role ID or mention role")
    async def delete_access(self, interaction: discord.Interaction, role: discord.Role):
        with open('data.json') as f:
            data = json.load(f)

        valid_user = False

        for role in data["verified-roles"]:
            try:
                if interaction.guild.get_role(role) in interaction.user.roles:
                    valid_user = True
            except:
                pass

        if valid_user or interaction.user.guild_permissions.administrator:

            try:
                role = int(role)
                role = interaction.guild.get_role(role)

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

                    await interaction.response.send_message(embed=em)

                else:

                    em = discord.Embed(title="TMS Tickets",
                                       description="That role already doesn't have access to tickets!", color=0x00a8ff)
                    await interaction.response.send_message(embed=em)

            except:
                em = discord.Embed(title="TMS Tickets",
                                   description="That isn't a valid role ID. Please try again with a valid role ID.")
                await interaction.response.send_message(embed=em)

        else:
            em = discord.Embed(title="TMS Tickets", description="Sorry, you don't have permission to run that command.",
                               color=0x00a8ff)
            await interaction.response.send_message(embed=em)

    @command()
    @checks.has_any_role(Role.SERVERLEADER, Role.FORMER_SL)
    @describe(role="Role ID or mention role")
    async def add_pinged_role(self, interaction: discord.Interaction, role: discord.Role):
        with open('data.json') as f:
            data = json.load(f)

        valid_user = False

        for role in data["verified-roles"]:
            try:
                if interaction.guild.get_role(role) in interaction.user.roles:
                    valid_user = True
            except:
                pass

        if valid_user or interaction.user.guild_permissions.administrator:

            role = int(role)

            if role not in data["pinged-roles"]:

                try:
                    role = interaction.guild.get_role(role)

                    with open("data.json") as f:
                        data = json.load(f)

                    data["pinged-roles"].append(role)

                    with open('data.json', 'w') as f:
                        json.dump(data, f)

                    em = discord.Embed(
                        title="TMS Tickets",
                        description=f"You have successfully added `{role.name}` to the list of roles that get pinged "
                                    f"when new tickets are created!",
                        color=0x00a8ff
                    )

                    await interaction.response.send_message(embed=em)

                except:
                    em = discord.Embed(
                        title="TMS Tickets",
                        description="That isn't a valid role ID. Please try again with a valid role ID."
                    )
                    await interaction.response.send_message(embed=em)

            else:
                em = discord.Embed(
                    title="TMS Tickets",
                    description="That role already receives pings when tickets are created.",
                    color=0x00a8ff
                )
                await interaction.response.send_message(embed=em)

        else:
            em = discord.Embed(
                title="TMS Tickets",
                description="Sorry, you don't have permission to run that command.",
                color=0x00a8ff
            )
            await interaction.response.send_message(embed=em)

    @command()
    @checks.has_any_role(Role.SERVERLEADER, Role.FORMER_SL)
    @describe(role="Role ID or mention role")
    async def delete_pinged_role(self, interaction, role: discord.Role):
        with open('data.json') as f:
            data = json.load(f)

        valid_user = False

        for role in data["verified-roles"]:
            try:
                if interaction.guild.get_role(role) in interaction.user.roles:
                    valid_user = True
            except:
                pass

        if valid_user or interaction.user.guild_permissions.administrator:

            try:
                role = int(role)
                role = interaction.guild.get_role(role)

                with open("data.json") as f:
                    data = json.load(f)

                pinged_roles = data["pinged-roles"]

                if role in pinged_roles:
                    index = pinged_roles.index(role)

                    del pinged_roles[index]

                    data["pinged-roles"] = pinged_roles

                    with open('data.json', 'w') as f:
                        json.dump(data, f)

                    em = discord.Embed(
                        title="TMS Tickets",
                        description=f"You have successfully removed `{role.name}` from the list of roles that get "
                                    f"pinged when new tickets are created.",
                        color=0x00a8ff
                    )
                    await interaction.response.send_message(embed=em)

                else:
                    em = discord.Embed(
                        title="TMS Tickets",
                        description="That role already isn't getting pinged when new tickets are created!",
                        color=0xff008c
                    )
                    await interaction.response.send_message(embed=em)

            except:
                em = discord.Embed(title="TMS Tickets",
                                   description="That isn't a valid role ID. Please try again with a valid role ID.")
                await interaction.response.send_message(embed=em)

        else:
            em = discord.Embed(
                title="TMS Tickets",
                description="Sorry, you don't have permission to run that command.",
                color=0xff008c
            )
            await interaction.response.send_message(embed=em)

    @command()
    @checks.has_any_role(Role.SERVERLEADER, Role.FORMER_SL)
    async def add_admin_role(self, interaction, role: discord.Role):
        try:
            with open("data.json") as f:
                data = json.load(f)

            data["verified-roles"].append(role.id)

            with open('data.json', 'w') as f:
                json.dump(data, f)

            em = discord.Embed(
                title="TMS Tickets",
                description=f"You have successfully added `{role.name}` to the list of roles that can run admin-level "
                            f"commands!",
                color=0xff008c
            )
            await interaction.response.send_message(embed=em)

        except:
            em = discord.Embed(title="TMS Tickets",
                               description="That isn't a valid role ID. Please try again with a valid role ID.")
            await interaction.response.send_message(embed=em)

    @command()
    @checks.has_any_role(Role.SERVERLEADER, Role.FORMER_SL)
    async def del_admin_role(self, interaction, role: discord.Role):
        try:
            with open("data.json") as f:
                data = json.load(f)

            admin_roles = data["verified-roles"]

            if role.id in admin_roles:
                index = admin_roles.index(role.id)

                del admin_roles[index]

                data["verified-roles"] = admin_roles

                with open('data.json', 'w') as f:
                    json.dump(data, f)

                em = discord.Embed(
                    title="TMS Tickets",
                    description=f"You have successfully removed `{role.name}` from the list of roles that get pinged "
                                f"when new tickets are created.",
                    color=0x00a8ff
                )

                await interaction.response.send_message(embed=em)

            else:
                em = discord.Embed(
                    title="TMS Tickets",
                    description="That role isn't getting pinged when new tickets are created!",
                    color=0x00a8ff
                )
                await interaction.response.send_message(embed=em)

        except:
            em = discord.Embed(title="TMS Tickets",
                               description="That isn't a valid role ID. Please try again with a valid role ID.")
            await interaction.response.send_message(embed=em)


class RolesGroup(Group):
    def __init__(self, bot: TMS):
        self.bot = bot
        super().__init__(
            name="roles",
            guild_ids=[SERVER_ID]
        )

    @property
    def cog(self) -> commands.Cog:
        return self.bot.get_cog("Config")

    @command(name="one")
    @checks.has_any_role(Role.SERVERLEADER, Role.FORMER_SL)
    async def _one(self, interaction: discord.Interaction):
        """Buttons for Life Science Events"""
        em1 = discord.Embed(
            title="Chose what events you're participating in!",
            description="To choose your event roles press the buttons below",
            color=0xff008c
        )
        em1.set_image(
            url='https://cdn.discordapp.com/attachments/685035292989718554/724301857157283910/ezgif-1-a2a2e7173d80.gif'
        )
        em1.set_footer(text="Life Science Events - Page 1 of 5")
        roles_channel: discord.abc.MessageableChannel = self.bot.get_channel(Channel.ROLES)
        await roles_channel.send(embed=em1, view=Role1())
        await interaction.response.send_message('Sent to ' + roles_channel.mention, ephemeral=True)

    @command(name="two")
    @checks.has_any_role(Role.SERVERLEADER, Role.FORMER_SL)
    async def _two(self, interaction):
        """Buttons for Earth and Space Science Events"""
        em1 = discord.Embed(title="Chose what events you're participating in!",
                            description="To choose your event roles press the buttons below",
                            color=0xff008c)
        em1.set_image(
            url='https://cdn.discordapp.com/attachments/685035292989718554/724301857157283910/ezgif-1-a2a2e7173d80.gif')
        em1.set_footer(text="Earth and Space Science Events - Page 2 of 5")
        roles_channel = self.bot.get_channel(Channel.ROLES)
        await roles_channel.send(embed=em1, view=Role2())
        await interaction.response.send_message('Sent to ' + roles_channel.mention, ephemeral=True)

    @command(name="three")
    @checks.has_any_role(Role.SERVERLEADER, Role.FORMER_SL)
    async def _three(self, interaction):
        """Buttons for Physical Science & Chemistry Events"""
        em1 = discord.Embed(title="Chose what events you're participating in!",
                            description="To choose your event roles press the buttons below",
                            color=0xff008c)
        em1.set_image(
            url='https://cdn.discordapp.com/attachments/685035292989718554/724301857157283910/ezgif-1-a2a2e7173d80.gif')
        em1.set_footer(text="Physical Science & Chemistry Events - Page 3 of 5")
        roles_channel = self.bot.get_channel(Channel.ROLES)
        await roles_channel.send(embed=em1, view=Role3())
        await interaction.response.send_message('Sent to ' + roles_channel.mention, ephemeral=True)

    @command(name="four")
    @checks.has_any_role(Role.SERVERLEADER, Role.FORMER_SL)
    async def _four(self, interaction):
        """Buttons for Technology & Engineering Design Events"""
        em1 = discord.Embed(title="Chose what events you're participating in!",
                            description="To choose your event roles press the buttons below",
                            color=0xff008c)
        em1.set_image(
            url='https://cdn.discordapp.com/attachments/685035292989718554/724301857157283910/ezgif-1-a2a2e7173d80.gif')
        em1.set_footer(text="Technology & Engineering Design Events - Page 4 of 5")
        roles_channel = self.bot.get_channel(Channel.ROLES)
        await roles_channel.send(embed=em1, view=Role4())
        await interaction.response.send_message('Sent to ' + roles_channel.mention, ephemeral=True)

    @command(name="five")
    @checks.has_any_role(Role.SERVERLEADER, Role.FORMER_SL)
    async def _five(self, interaction):
        """Buttons for Inquiry & Nature"""
        em1 = discord.Embed(title="Chose what events you're participating in!",
                            description="To choose your event roles press the buttons below",
                            color=0xff008c)
        em1.set_image(
            url='https://cdn.discordapp.com/attachments/685035292989718554/724301857157283910/ezgif-1-a2a2e7173d80.gif')
        em1.set_footer(text="Inquiry & Nature of Science Events")
        roles_channel = self.bot.get_channel(Channel.ROLES)
        await roles_channel.send(embed=em1, view=Role5())
        await interaction.response.send_message('Sent to ' + roles_channel.mention, ephemeral=True)

    @command()
    @checks.has_any_role(Role.SERVERLEADER, Role.FORMER_SL)
    async def pronouns(self, interaction: discord.Interaction):
        """Buttons for Pronoun Roles"""
        em1 = discord.Embed(title="What pronouns do you use?",
                            description="Press the buttons below to choose your pronoun role(s)",
                            color=0xff008c)
        em1.set_image(
            url='https://cdn.discordapp.com/attachments/685035292989718554/724301857157283910/ezgif-1-a2a2e7173d80.gif')
        em1.set_footer(text="Pronoun Roles")
        roles_channel = self.bot.get_channel(Channel.ROLES)
        await roles_channel.send(embed=em1, view=Pronouns())
        await interaction.response.send_message('Sent to ' + roles_channel.mention, ephemeral=True)

    @command(name="all")
    @checks.has_any_role(Role.SERVERLEADER, Role.FORMER_SL)
    async def _all(self, interaction: discord.Interaction):
        """Creates all the event role buttons"""

        await interaction.response.defer(thinking=True, ephemeral=True)

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

        roles_channel = self.bot.get_channel(Channel.ROLES)

        await roles_channel.send(embed=em1, view=Role1())
        await roles_channel.send(embed=em2, view=Role2())
        await roles_channel.send(embed=em3, view=Role3())
        await roles_channel.send(embed=em4, view=Role4())
        await roles_channel.send(embed=em5, view=Role5())
        await roles_channel.send(embed=em6, view=Pronouns())

        await interaction.followup.send('Sent to ' + roles_channel.mention, ephemeral=True)


async def setup(bot: TMS):
    await bot.add_cog(Config(bot))
