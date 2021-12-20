import datetime
import re

import discord
import json
import asyncio
from typing import List
from utils.variables import *


class Confirm(discord.ui.View):
    def __init__(self, ctx):
        super().__init__()
        self.value = None
        self.author = ctx.author

    async def interaction_check(self, interaction: discord.Interaction) -> bool:

        if interaction.user == self.author or interaction.user.id == 747126643587416174:
            return True
        else:
            await interaction.response.send_message('This confirmation dialog is not for you.', ephemeral=True)
            return False

    @discord.ui.button(label='Confirm', style=discord.ButtonStyle.green)
    async def confirm(self, button: discord.ui.Button, interaction: discord.Interaction):
        for child in self.children:
            child.disabled = True
            button.label = "Confirmed"
        self.value = True
        await interaction.response.edit_message(view=self)
        self.stop()

    # This one is similar to the confirmation button except sets the inner value to `False`
    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.red)
    async def cancel(self, button: discord.ui.Button, interaction: discord.Interaction):
        for child in self.children:
            child.disabled = True
            button.label = "Canceled"
        self.value = False
        await interaction.response.edit_message(view=self)
        self.stop()


class Counter(discord.ui.View):

    @discord.ui.button(label='0', style=discord.ButtonStyle.red, custom_id="counter")
    async def count(self, button: discord.ui.Button, interaction: discord.Interaction):
        number = int(button.label) if button.label else 0
        button.label = str(number + 1)

        await interaction.response.edit_message(view=self)


class Ticket(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.value = None
        self.bot = bot

    @discord.ui.button(label='\U0001f4e9 Create Ticket', custom_id="ticket", style=discord.ButtonStyle.secondary)
    async def ticket(self, button: discord.ui.Button, interaction: discord.Interaction):
        with open("data.json") as f:
            data = json.load(f)

            ticket_number = int(data["ticket-counter"])
            ticket_number += 1

            ticket_channel = await interaction.guild.create_text_channel("\U0001f4e9│ticket-{}".format(ticket_number))
            await ticket_channel.set_permissions(interaction.guild.get_role(interaction.guild.id), send_messages=False,
                                                 read_messages=False)

            for role_id in data["valid-roles"]:
                role = interaction.guild.get_role(role_id)

                await ticket_channel.set_permissions(role, send_messages=True, read_messages=True,
                                                     add_reactions=True,
                                                     embed_links=True, attach_files=True,
                                                     read_message_history=True,
                                                     external_emojis=True)

                await ticket_channel.set_permissions(interaction.user, send_messages=True, read_messages=True,
                                                     add_reactions=True,
                                                     embed_links=True, attach_files=True,
                                                     read_message_history=True,
                                                     external_emojis=True)

                pinged_msg_content = ""
                non_mentionable_roles = []

                if data["pinged-roles"] != []:

                    for role_id in data["pinged-roles"]:
                        role = interaction.guild.get_role(role_id)

                        pinged_msg_content += role.mention
                        pinged_msg_content += " "

                        if role.mentionable:
                            pass
                        else:
                            await role.edit(mentionable=True)
                            non_mentionable_roles.append(role)

                message_content = "Please wait and a moderator will assist you! To close this ticket press the `Close` button below"
                em = discord.Embed(
                    title="New ticket from {}#{}".format(interaction.user.name, interaction.user.discriminator),
                    description=f"{message_content} {pinged_msg_content}", color=0x00a8ff)
                view1 = Close(self.bot)

                data["ticket-channel-ids"].append(ticket_channel.id)
                data["ticket-counter"] = int(ticket_number)
                with open("data.json", 'w') as f:
                    json.dump(data, f)

                    em3 = discord.Embed(title="TMS Tickets",
                                        description="Your ticket has been created at {}".format(
                                            ticket_channel.mention),
                                        color=0x00a8ff)
                    await interaction.response.send_message(embed=em3, ephemeral=True)
                return await ticket_channel.send(embed=em, view=view1)


class Close(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.value = None
        self.bot = bot

    @discord.ui.button(label='Close', custom_id="close", style=discord.ButtonStyle.danger)
    async def close(self, button: discord.ui.Button, interaction: discord.Interaction):
        with open('data.json') as f:
            data = json.load(f)

            if interaction.channel.id in data["ticket-channel-ids"]:

                channel_id = interaction.channel.id
                channel = interaction.channel

                def check(message):
                    return message.author == interaction.user and message.channel == interaction.channel and message.content.lower() == "close"

                try:

                    em = discord.Embed(title="TMS Tickets",
                                       description="Are you sure you want to close this ticket? Reply with `close` if you are sure.",
                                       color=0x00a8ff)

                    await interaction.response.send_message(embed=em)
                    await self.bot.wait_for('message', check=check, timeout=60)
                    await channel.delete()

                    index = data["ticket-channel-ids"].index(channel_id)
                    del data["ticket-channel-ids"][index]

                    with open('data.json', 'w') as f:
                        json.dump(data, f)

                except asyncio.TimeoutError:
                    em = discord.Embed(title="TMS Tickets",
                                       description="You have run out of time to close this ticket. Please press the red `Close` button again.",
                                       color=0x00a8ff)
                    await channel.send(embed=em)


class TicTacToeButton(discord.ui.Button['TicTacToe']):
    def __init__(self, x: int, y: int):
        # A label is required, but we don't need one so a zero-width space is used
        # The row parameter tells the View which row to place the button under.
        # A View can only contain up to 5 rows -- each row can only have 5 buttons.
        # Since a Tic Tac Toe grid is 3x3 that means we have 3 rows and 3 columns.
        super().__init__(style=discord.ButtonStyle.secondary, label='\u200b', row=y)
        self.x = x
        self.y = y

    # This function is called whenever this particular button is pressed
    # This is part of the "meat" of the game logic
    async def callback(self, interaction: discord.Interaction):
        assert self.view is not None
        view: TicTacToe = self.view
        state = view.board[self.y][self.x]
        if state in (view.X, view.O):
            return

        if view.current_player == view.X:
            self.style = discord.ButtonStyle.danger
            self.label = 'X'
            self.disabled = True
            view.board[self.y][self.x] = view.X
            view.current_player = view.O
            content = "It is now O's turn"
        else:
            self.style = discord.ButtonStyle.success
            self.label = 'O'
            self.disabled = True
            view.board[self.y][self.x] = view.O
            view.current_player = view.X
            content = "It is now X's turn"

        winner = view.check_board_winner()
        if winner is not None:
            if winner == view.X:
                content = 'X won!'
            elif winner == view.O:
                content = 'O won!'
            else:
                content = "It's a tie!"

            for child in view.children:
                child.disabled = True

            view.stop()

        await interaction.response.edit_message(content=content, view=view)


# This is our actual board View
class TicTacToe(discord.ui.View):
    # This tells the IDE or linter that all our children will be TicTacToeButtons
    # This is not required
    children: List[TicTacToeButton]
    X = -1
    O = 1
    Tie = 2

    def __init__(self):
        super().__init__()
        self.current_player = self.X
        self.board = [
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0],
        ]

        for x in range(3):
            for y in range(3):
                self.add_item(TicTacToeButton(x, y))

    # This method checks for the board winner -- it is used by the TicTacToeButton
    def check_board_winner(self):
        for across in self.board:
            value = sum(across)
            if value == 3:
                return self.O
            elif value == -3:
                return self.X

        # Check vertical
        for line in range(3):
            value = self.board[0][line] + self.board[1][line] + self.board[2][line]
            if value == 3:
                return self.O
            elif value == -3:
                return self.X

        # Check diagonals
        diag = self.board[0][2] + self.board[1][1] + self.board[2][0]
        if diag == 3:
            return self.O
        elif diag == -3:
            return self.X

        diag = self.board[0][0] + self.board[1][1] + self.board[2][2]
        if diag == 3:
            return self.O
        elif diag == -3:
            return self.X

        # If we're here, we need to check if a tie was made
        if all(i != 0 for row in self.board for i in row):
            return self.Tie

        return None


class Role1(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="\U0001f9e0 Anatomy & Physiology", custom_id='ap', row=1)
    async def anatomy(self, button: discord.ui.Button, interaction: discord.Interaction):
        role = discord.utils.get(interaction.guild.roles, name=ROLE_AP)
        if role in interaction.user.roles:
            member = await interaction.guild.fetch_member(interaction.user.id)
            await member.remove_roles(role)
            await interaction.response.send_message(f'Removed Roles {role.mention}', ephemeral=True)
        else:
            member = await interaction.guild.fetch_member(interaction.user.id)
            await member.add_roles(role)
            await interaction.response.send_message(f'Added Roles {role.mention}', ephemeral=True)

    @discord.ui.button(label="\U0001f9ec Bio Process Lab", custom_id='bpl', row=1)
    async def bpl(self, button: discord.ui.Button, interaction: discord.Interaction):
        role = discord.utils.get(interaction.guild.roles, name=ROLE_BPL)
        if role in interaction.user.roles:
            member = await interaction.guild.fetch_member(interaction.user.id)
            await member.remove_roles(role)
            await interaction.response.send_message(f'Removed Roles {role.mention}', ephemeral=True)
        else:
            member = await interaction.guild.fetch_member(interaction.user.id)
            await member.add_roles(role)
            await interaction.response.send_message(f'Added Roles {role.mention}', ephemeral=True)

    @discord.ui.button(label="\U0001f9a0 Disease Detectives", custom_id='dd', row=1)
    async def dd(self, button: discord.ui.Button, interaction: discord.Interaction):
        role = discord.utils.get(interaction.guild.roles, name=ROLE_DD)
        if role in interaction.user.roles:
            member = await interaction.guild.fetch_member(interaction.user.id)
            await member.remove_roles(role)
            await interaction.response.send_message(f'Removed Roles {role.mention}', ephemeral=True)
        else:
            member = await interaction.guild.fetch_member(interaction.user.id)
            await member.add_roles(role)
            await interaction.response.send_message(f'Added Roles {role.mention}', ephemeral=True)

    @discord.ui.button(label="\U0001f333 Green Generation", custom_id='gg', row=2)
    async def gg(self, button: discord.ui.Button, interaction: discord.Interaction):
        role = discord.utils.get(interaction.guild.roles, name=ROLE_GG)
        if role in interaction.user.roles:
            member = await interaction.guild.fetch_member(interaction.user.id)
            await member.remove_roles(role)
            await interaction.response.send_message(f'Removed Roles {role.mention}', ephemeral=True)
        else:
            member = await interaction.guild.fetch_member(interaction.user.id)
            await member.add_roles(role)
            await interaction.response.send_message(f'Added Roles {role.mention}', ephemeral=True)

    @discord.ui.button(label="\U0001f985 Ornithology", custom_id='o', row=2)
    async def orni(self, button: discord.ui.Button, interaction: discord.Interaction):
        role = discord.utils.get(interaction.guild.roles, name=ROLE_O)
        if role in interaction.user.roles:
            member = await interaction.guild.fetch_member(interaction.user.id)
            await member.remove_roles(role)
            await interaction.response.send_message(f'Removed Roles {role.mention}', ephemeral=True)
        else:
            member = await interaction.guild.fetch_member(interaction.user.id)
            await member.add_roles(role)
            await interaction.response.send_message(f'Added Roles {role.mention}', ephemeral=True)


class Role2(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="\U0001f30e Dynamic Planet", custom_id='dp', row=1)
    async def dp(self, button: discord.ui.Button, interaction: discord.Interaction):
        role = discord.utils.get(interaction.guild.roles, name=ROLE_DP)
        if role in interaction.user.roles:
            member = await interaction.guild.fetch_member(interaction.user.id)
            await member.remove_roles(role)
            await interaction.response.send_message(f'Removed Roles {role.mention}', ephemeral=True)
        else:
            member = await interaction.guild.fetch_member(interaction.user.id)
            await member.add_roles(role)
            await interaction.response.send_message(f'Added Roles {role.mention}', ephemeral=True)

    @discord.ui.button(label="\U000026c8 Meteorology", custom_id='meteo', row=1)
    async def m(self, button: discord.ui.Button, interaction: discord.Interaction):
        role = discord.utils.get(interaction.guild.roles, name=ROLE_M)
        if role in interaction.user.roles:
            member = await interaction.guild.fetch_member(interaction.user.id)
            await member.remove_roles(role)
            await interaction.response.send_message(f'Removed Roles {role.mention}', ephemeral=True)
        else:
            member = await interaction.guild.fetch_member(interaction.user.id)
            await member.add_roles(role)
            await interaction.response.send_message(f'Added Roles {role.mention}', ephemeral=True)

    @discord.ui.button(label="\U000026f0 Road Scholar", custom_id='rs', row=1)
    async def rs(self, button: discord.ui.Button, interaction: discord.Interaction):
        role = discord.utils.get(interaction.guild.roles, name=ROLE_RS)
        if role in interaction.user.roles:
            member = await interaction.guild.fetch_member(interaction.user.id)
            await member.remove_roles(role)
            await interaction.response.send_message(f'Removed Roles {role.mention}', ephemeral=True)
        else:
            member = await interaction.guild.fetch_member(interaction.user.id)
            await member.add_roles(role)
            await interaction.response.send_message(f'Added Roles {role.mention}', ephemeral=True)

    @discord.ui.button(label="\U0001f48e Rocks & Minerals", custom_id='rm', row=2)
    async def rm(self, button: discord.ui.Button, interaction: discord.Interaction):
        role = discord.utils.get(interaction.guild.roles, name=ROLE_RM)
        if role in interaction.user.roles:
            member = await interaction.guild.fetch_member(interaction.user.id)
            await member.remove_roles(role)
            await interaction.response.send_message(f'Removed Roles {role.mention}', ephemeral=True)
        else:
            member = await interaction.guild.fetch_member(interaction.user.id)
            await member.add_roles(role)
            await interaction.response.send_message(f'Added Roles {role.mention}', ephemeral=True)

    @discord.ui.button(label="\U0001f52d Solar System", custom_id='ss', row=2)
    async def ss(self, button: discord.ui.Button, interaction: discord.Interaction):
        role = discord.utils.get(interaction.guild.roles, name=ROLE_SS)
        if role in interaction.user.roles:
            member = await interaction.guild.fetch_member(interaction.user.id)
            await member.remove_roles(role)
            await interaction.response.send_message(f'Removed Roles {role.mention}', ephemeral=True)
        else:
            member = await interaction.guild.fetch_member(interaction.user.id)
            await member.add_roles(role)
            await interaction.response.send_message(f'Added Roles {role.mention}', ephemeral=True)


class Role3(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="\U0001f30a Crave the Wave", custom_id='ctw', row=1)
    async def ctw(self, button: discord.ui.Button, interaction: discord.Interaction):
        role = discord.utils.get(interaction.guild.roles, name=ROLE_CTW)
        if role in interaction.user.roles:
            member = await interaction.guild.fetch_member(interaction.user.id)
            await member.remove_roles(role)
            await interaction.response.send_message(f'Removed Roles {role.mention}', ephemeral=True)
        else:
            member = await interaction.guild.fetch_member(interaction.user.id)
            await member.add_roles(role)
            await interaction.response.send_message(f'Added Roles {role.mention}', ephemeral=True)

    @discord.ui.button(label="\U0001f3b5 Sounds of Music", custom_id='som', row=1)
    async def som(self, button: discord.ui.Button, interaction: discord.Interaction):
        role = discord.utils.get(interaction.guild.roles, name=ROLE_SOM)
        if role in interaction.user.roles:
            member = await interaction.guild.fetch_member(interaction.user.id)
            await member.remove_roles(role)
            await interaction.response.send_message(f'Removed Roles {role.mention}', ephemeral=True)
        else:
            member = await interaction.guild.fetch_member(interaction.user.id)
            await member.add_roles(role)
            await interaction.response.send_message(f'Added Roles {role.mention}', ephemeral=True)

    @discord.ui.button(label="\U0001f3af Storm the Castle", custom_id='stc', row=1)
    async def stc(self, button: discord.ui.Button, interaction: discord.Interaction):
        role = discord.utils.get(interaction.guild.roles, name=ROLE_STC)
        if role in interaction.user.roles:
            member = await interaction.guild.fetch_member(interaction.user.id)
            await member.remove_roles(role)
            await interaction.response.send_message(f'Removed Roles {role.mention}', ephemeral=True)
        else:
            member = await interaction.guild.fetch_member(interaction.user.id)
            await member.add_roles(role)
            await interaction.response.send_message(f'Added Roles {role.mention}', ephemeral=True)

    @discord.ui.button(label="\U0001f349 Food Science", custom_id='fs', row=2)
    async def fs(self, button: discord.ui.Button, interaction: discord.Interaction):
        role = discord.utils.get(interaction.guild.roles, name=ROLE_FS)
        if role in interaction.user.roles:
            member = await interaction.guild.fetch_member(interaction.user.id)
            await member.remove_roles(role)
            await interaction.response.send_message(f'Removed Roles {role.mention}', ephemeral=True)
        else:
            member = await interaction.guild.fetch_member(interaction.user.id)
            await member.add_roles(role)
            await interaction.response.send_message(f'Added Roles {role.mention}', ephemeral=True)

    @discord.ui.button(label="\U0001f9ea Crime Busters", custom_id='cb', row=2)
    async def cb(self, button: discord.ui.Button, interaction: discord.Interaction):
        role = discord.utils.get(interaction.guild.roles, name=ROLE_CB)
        if role in interaction.user.roles:
            member = await interaction.guild.fetch_member(interaction.user.id)
            await member.remove_roles(role)
            await interaction.response.send_message(f'Removed Roles {role.mention}', ephemeral=True)
        else:
            member = await interaction.guild.fetch_member(interaction.user.id)
            await member.add_roles(role)
            await interaction.response.send_message(f'Added Roles {role.mention}', ephemeral=True)


class Role4(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="\U0001f309 Bridges", custom_id='bridge', row=1)
    async def b(self, button: discord.ui.Button, interaction: discord.Interaction):
        role = discord.utils.get(interaction.guild.roles, name=ROLE_B)
        if role in interaction.user.roles:
            member = await interaction.guild.fetch_member(interaction.user.id)
            await member.remove_roles(role)
            await interaction.response.send_message(f'Removed Roles {role.mention}', ephemeral=True)
        else:
            member = await interaction.guild.fetch_member(interaction.user.id)
            await member.add_roles(role)
            await interaction.response.send_message(f'Added Roles {role.mention}', ephemeral=True)

    @discord.ui.button(label="\U00002708 Electric Wright Stuff", custom_id='ews', row=1)
    async def ews(self, button: discord.ui.Button, interaction: discord.Interaction):
        role = discord.utils.get(interaction.guild.roles, name=ROLE_EWS)
        if role in interaction.user.roles:
            member = await interaction.guild.fetch_member(interaction.user.id)
            await member.remove_roles(role)
            await interaction.response.send_message(f'Removed Roles {role.mention}', ephemeral=True)
        else:
            member = await interaction.guild.fetch_member(interaction.user.id)
            await member.add_roles(role)
            await interaction.response.send_message(f'Added Roles {role.mention}', ephemeral=True)

    @discord.ui.button(label="\U000023f1 Mission Possible", custom_id='mp', row=2)
    async def mp(self, button: discord.ui.Button, interaction: discord.Interaction):
        role = discord.utils.get(interaction.guild.roles, name=ROLE_MP)
        if role in interaction.user.roles:
            member = await interaction.guild.fetch_member(interaction.user.id)
            await member.remove_roles(role)
            await interaction.response.send_message(f'Removed Roles {role.mention}', ephemeral=True)
        else:
            member = await interaction.guild.fetch_member(interaction.user.id)
            await member.add_roles(role)
            await interaction.response.send_message(f'Added Roles {role.mention}', ephemeral=True)

    @discord.ui.button(label="\U0001faa4 Mousetrap Vehicle", custom_id='mtv', row=2)
    async def mtv(self, button: discord.ui.Button, interaction: discord.Interaction):
        role = discord.utils.get(interaction.guild.roles, name=ROLE_MV)
        if role in interaction.user.roles:
            member = await interaction.guild.fetch_member(interaction.user.id)
            await member.remove_roles(role)
            await interaction.response.send_message(f'Removed Roles {role.mention}', ephemeral=True)
        else:
            member = await interaction.guild.fetch_member(interaction.user.id)
            await member.add_roles(role)
            await interaction.response.send_message(f'Added Roles {role.mention}', ephemeral=True)


class Role5(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="\U0001f513 Codebusters", custom_id='code', row=1)
    async def code(self, button: discord.ui.Button, interaction: discord.Interaction):
        role = discord.utils.get(interaction.guild.roles, name=ROLE_C)
        if role in interaction.user.roles:
            member = await interaction.guild.fetch_member(interaction.user.id)
            await member.remove_roles(role)
            await interaction.response.send_message(f'Removed Roles {role.mention}', ephemeral=True)
        else:
            member = await interaction.guild.fetch_member(interaction.user.id)
            await member.add_roles(role)
            await interaction.response.send_message(f'Added Roles {role.mention}', ephemeral=True)

    @discord.ui.button(label="\U0001f97d Experimental Design", custom_id='expd', row=1)
    async def exp(self, button: discord.ui.Button, interaction: discord.Interaction):
        role = discord.utils.get(interaction.guild.roles, name=ROLE_ED)
        if role in interaction.user.roles:
            member = await interaction.guild.fetch_member(interaction.user.id)
            await member.remove_roles(role)
            await interaction.response.send_message(f'Removed Roles {role.mention}', ephemeral=True)
        else:
            member = await interaction.guild.fetch_member(interaction.user.id)
            await member.add_roles(role)
            await interaction.response.send_message(f'Added Roles {role.mention}', ephemeral=True)

    @discord.ui.button(label="\U0001fa82 Ping Pong Parachute", custom_id='ppp', row=2)
    async def ppp(self, button: discord.ui.Button, interaction: discord.Interaction):
        role = discord.utils.get(interaction.guild.roles, name=ROLE_PPP)
        if role in interaction.user.roles:
            member = await interaction.guild.fetch_member(interaction.user.id)
            await member.remove_roles(role)
            await interaction.response.send_message(f'Removed Roles {role.mention}', ephemeral=True)
        else:
            member = await interaction.guild.fetch_member(interaction.user.id)
            await member.add_roles(role)
            await interaction.response.send_message(f'Added Roles {role.mention}', ephemeral=True)

    @discord.ui.button(label="\U0001f4dd Write it, Do it", custom_id='widi', row=2)
    async def widi(self, button: discord.ui.Button, interaction: discord.Interaction):
        role = discord.utils.get(interaction.guild.roles, name=ROLE_WIDI)
        if role in interaction.user.roles:
            member = await interaction.guild.fetch_member(interaction.user.id)
            await member.remove_roles(role)
            await interaction.response.send_message(f'Removed Roles {role.mention}', ephemeral=True)
        else:
            member = await interaction.guild.fetch_member(interaction.user.id)
            await member.add_roles(role)
            await interaction.response.send_message(f'Added Roles {role.mention}', ephemeral=True)


class Pronouns(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="\U0001f9e1 He/Him", custom_id='he', row=1)
    async def he(self, button: discord.ui.Button, interaction: discord.Interaction):
        role = discord.utils.get(interaction.guild.roles, name=ROLE_HE)
        if role in interaction.user.roles:
            member = await interaction.guild.fetch_member(interaction.user.id)
            await member.remove_roles(role)
            await interaction.response.send_message(f'Removed Roles {role.mention}', ephemeral=True)
        else:
            member = await interaction.guild.fetch_member(interaction.user.id)
            await member.add_roles(role)
            await interaction.response.send_message(f'Added Roles {role.mention}', ephemeral=True)

    @discord.ui.button(label="\U0001f49b She/Her", custom_id='she', row=1)
    async def she(self, button: discord.ui.Button, interaction: discord.Interaction):
        role = discord.utils.get(interaction.guild.roles, name=ROLE_SHE)
        if role in interaction.user.roles:
            member = await interaction.guild.fetch_member(interaction.user.id)
            await member.remove_roles(role)
            await interaction.response.send_message(f'Removed Roles {role.mention}', ephemeral=True)
        else:
            member = await interaction.guild.fetch_member(interaction.user.id)
            await member.add_roles(role)
            await interaction.response.send_message(f'Added Roles {role.mention}', ephemeral=True)

    @discord.ui.button(label="\U0001f49c They/Them", custom_id='they', row=1)
    async def they(self, button: discord.ui.Button, interaction: discord.Interaction):
        role = discord.utils.get(interaction.guild.roles, name=ROLE_THEY)
        if role in interaction.user.roles:
            member = await interaction.guild.fetch_member(interaction.user.id)
            await member.remove_roles(role)
            await interaction.response.send_message(f'Removed Roles {role.mention}', ephemeral=True)
        else:
            member = await interaction.guild.fetch_member(interaction.user.id)
            await member.add_roles(role)
            await interaction.response.send_message(f'Added Roles {role.mention}', ephemeral=True)

    @discord.ui.button(label="\U0001f49a Ask", custom_id='ask', row=1)
    async def ask(self, button: discord.ui.Button, interaction: discord.Interaction):
        role = discord.utils.get(interaction.guild.roles, name=ROLE_ASK)
        if role in interaction.user.roles:
            member = await interaction.guild.fetch_member(interaction.user.id)
            await member.remove_roles(role)
            await interaction.response.send_message(f'Removed Roles {role.mention}', ephemeral=True)
        else:
            member = await interaction.guild.fetch_member(interaction.user.id)
            await member.add_roles(role)
            await interaction.response.send_message(f'Added Roles {role.mention}', ephemeral=True)


class Allevents(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="\U0001f499 All Events ", custom_id='ae')
    async def allevents(self, button: discord.ui.Button, interaction: discord.Interaction):
        role = discord.utils.get(interaction.guild.roles, name=ROLE_AE)
        if role in interaction.user.roles:
            member = await interaction.guild.fetch_member(interaction.user.id)
            await member.remove_roles(role)
            await interaction.response.send_message(f'Removed Roles {role.mention}', ephemeral=True)
        else:
            member = await interaction.guild.fetch_member(interaction.user.id)
            await member.add_roles(role)
            await interaction.response.send_message(f'Added Roles {role.mention}', ephemeral=True)


# class Google(discord.ui.View):
#     def __init__(self, query: str):
#         super().__init__()
#         # we need to quote the query string to make a valid url. Discord will raise an error if it isn't valid.
#         query = quote_plus(query)
#         url = f'https://www.google.com/search?q={query}'
#         self.add_item(discord.ui.Button(label='Click Here', url=url))


class NukeStopButton(discord.ui.Button["Nuke"]):

    def __init__(self, nuke, ctx):
        super().__init__(label="ABORT", style=discord.ButtonStyle.danger)
        self.nuke = nuke
        self.author = ctx.author

    async def callback(self, interaction: discord.Interaction):
        self.nuke.stopped = True
        self.style = discord.ButtonStyle.green
        self.label = "ABORTED"
        self.disabled = True
        embed = discord.Embed()
        embed.description = f"""
        NUKE ABORTED COMMANDER \n Nuke request canceled by {interaction.user.mention} in {interaction.channel.mention}
        """
        embed.title = "NUKE COMMAND PANEL"
        embed.colour = discord.Colour.brand_green()
        embed.timestamp = discord.utils.utcnow()
        await interaction.response.edit_message(embed=embed, view=None, content=None)
        self.nuke.stop()


class Nuke(discord.ui.View):
    stopped = False

    def __init__(self, ctx):
        super().__init__()
        button = NukeStopButton(self, ctx)
        self.add_item(button)
        self.author = ctx.author

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user == self.author or interaction.user.id == 747126643587416174:
            return True
        await interaction.response.send_message('This confirmation dialog is not for you.', ephemeral=True)


class AllEventsSelect(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    options = [
        discord.SelectOption(label="Anatomy and Physiology", value="anatomy", emoji="\U0001f9e0"),
        discord.SelectOption(label="Bio Process Lab", value="bpl", emoji="\U0001f9ec"),
        discord.SelectOption(label="Bridges", value="bridges", emoji="\U0001f309"),
        discord.SelectOption(label="Codebusters", value="code", emoji="\U0001f512"),
        discord.SelectOption(label="Crave the Wave", value="wave", emoji="\U0001f30a"),
        discord.SelectOption(label="Crime Busters", value="crime", emoji="\U0001f9ea"),
        discord.SelectOption(label="Disease Detectives", value="dd", emoji="\U0001f9a0"),
        discord.SelectOption(label="Dynamic Planet", value="dp", emoji="\U0001f30e"),
        discord.SelectOption(label="Electric Wright Stuff", value="ews", emoji="\U0001f6e9"),
        discord.SelectOption(label="Experimental Design", value="expd", emoji="\U0001f97d"),
        discord.SelectOption(label="Food Science", value="fs", emoji="\U0001f349"),
        discord.SelectOption(label="Green Generation", value="gg", emoji="\U0001f333"),
        discord.SelectOption(label="Meteorology", value="meteo", emoji="\U000026c8"),
        discord.SelectOption(label="Mission Possible", value="mission", emoji="\U000023f2"),
        discord.SelectOption(label="Mousetrap Vehicle", value="mouse", emoji="\U0001faa4"),
        discord.SelectOption(label="Ornithology", value="orni", emoji="\U0001f985"),
        discord.SelectOption(label="Ping Pong Parachute", value="ppp", emoji="\U0001fa82"),
        discord.SelectOption(label="Road Scholar", value="road", emoji="\U0001f3d4"),
        discord.SelectOption(label="Rocks and Minerals", value="rocks", emoji="\U0001f48e"),
        discord.SelectOption(label="Solar System", value="solar", emoji="\U0001fa90"),
        discord.SelectOption(label="Sounds of Music", value="music", emoji="\U0001f3b5"),
        discord.SelectOption(label="Storm the Castle", value="castle", emoji="\U0001f3af"),
        discord.SelectOption(label="Write It Do It", value="widi", emoji="\U0001f4dd")
    ]

    @discord.ui.select(
        placeholder="Chose what events you're participating in!",
        max_values=1,
        min_values=0,
        options=options,
        custom_id="events_select")
    async def event_select(self, select: discord.ui.Select, interaction: discord.Interaction):
        roles = {"anatomy": ROLE_AP,
                 "bpl": ROLE_BPL,
                 "bridges": ROLE_B,
                 "code": ROLE_C,
                 "crime": ROLE_CB,
                 "wave": ROLE_CTW,
                 "dd": ROLE_DD,
                 "dp": ROLE_DP,
                 "ews": ROLE_EWS,
                 "expd": ROLE_ED,
                 "fs": ROLE_FS,
                 "gg": ROLE_GG,
                 "meteo": ROLE_M,
                 "mission": ROLE_MP,
                 "mouse": ROLE_MV,
                 "orni": ROLE_O,
                 "ppp": ROLE_PPP,
                 "road": ROLE_RS,
                 "rocks": ROLE_RM,
                 "solar": ROLE_SS,
                 "music": ROLE_SOM,
                 "castle": ROLE_STC,
                 "widi": ROLE_WIDI
                 }
        values = select.values[0]
        role_name = roles[values]
        role = discord.utils.get(interaction.guild.roles, name=role_name)
        if role in interaction.user.roles:
            await interaction.user.remove_roles(role)
            await interaction.response.send_message(
                f'Removed Roles {role.mention}, if you accidentally added this role click the option again to remove it',
                ephemeral=True)
        else:
            await interaction.user.add_roles(role)
            await interaction.response.send_message(
                f'Added Roles {role.mention}, if you accidentally added this role click the option again to remove it',
                ephemeral=True)


class ReportView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="\U00002705", custom_id="green_check", style=discord.ButtonStyle.green)
    async def green_check(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.channel.id == CHANNEL_REPORTS:
            await interaction.response.defer()
            await interaction.message.delete()
            print("Handled by staff")
        else:
            await interaction.response.defer()

    @discord.ui.button(label="\U0000274c", custom_id="red_x", style=discord.ButtonStyle.red)
    async def red_x(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.channel.id == CHANNEL_REPORTS:
            await interaction.response.defer()
            await interaction.message.delete()
            print("Cleared with no action")
        else:
            await interaction.response.defer()


class CronView(discord.ui.View):

    def __init__(self, docs, bot):
        super().__init__()
        self.add_item(CronSelect(docs, bot))


class CronSelect(discord.ui.Select):
    def __init__(self, docs, bot):
        options = []
        docs.sort(key=lambda d: d['time'])
        print([d['time'] for d in docs])
        counts = {}
        for doc in docs[:20]:
            timeframe = (doc['time'] - datetime.datetime.utcnow()).days
            if abs(timeframe) < 1:
                timeframe = f"{(doc['time'] - datetime.datetime.utcnow()).total_seconds() // 3600} hours"
            else:
                timeframe = f"{(doc['time'] - datetime.datetime.utcnow()).days} days"
            tag_name = f"{doc['type'].title()} {doc['tag']}"
            if tag_name in counts:
                counts[tag_name] = counts[tag_name] + 1
            else:
                counts[tag_name] = 1
            if counts[tag_name] > 1:
                tag_name = f"{tag_name} (#{counts[tag_name]})"
            option = discord.SelectOption(
                label=tag_name,
                description=f"Occurs in {timeframe}."
            )
            options.append(option)

        super().__init__(
            placeholder="View potential actions to modify...",
            min_values=1,
            max_values=1,
            options=options
        )
        self.docs = docs
        self.bot = bot

    async def callback(self, interaction: discord.Interaction):
        value = self.values[0]
        num = re.findall(r'\(#(\d*)', value)
        value = re.sub(r' \(#\d*\)', '', value)
        relevant_doc = [d for d in self.docs if f"{d['type'].title()} {d['tag']}" == value]
        if len(relevant_doc) == 1:
            relevant_doc = relevant_doc[0]
        else:
            if not len(num):
                relevant_doc = relevant_doc[0]
            else:
                num = num[0]
                relevant_doc = relevant_doc[int(num) - 1]
        view = CronConfirm(relevant_doc, self.bot)
        await interaction.response.edit_message(
            content=f"Okay! What would you like me to do with this CRON item?\n> {self.values[0]}",
            view=view,
            embed=None)


class CronConfirm(discord.ui.View):

    def __init__(self, doc, bot):
        super().__init__()
        self.doc = doc
        self.bot = bot

    @discord.ui.button(label="Remove", style=discord.ButtonStyle.danger)
    async def remove_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        CRON_LIST.remove(self.doc)
        await interaction.response.edit_message(
            content="Awesome! I successfully removed the action from the CRON list.", view=None)

    @discord.ui.button(label="Complete Now", style=discord.ButtonStyle.green)
    async def complete_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        server = self.bot.get_guild(SERVER_ID)
        if self.doc["type"] == "UNBAN":
            # User needs to be unbanned
            try:
                await server.unban(self.doc["user"])
            except:
                pass
            await interaction.response.edit_message(
                content="Attempted to unban the user. Checking to see if operation was succesful...", view=None)
            bans = await server.bans()
            for ban in bans:
                if ban.user.id == self.doc["user"]:
                    return await interaction.edit_original_message(
                        content="Uh oh! The operation was not succesful - the user remains banned.")
            CRON_LIST.remove(self.doc)
            return await interaction.edit_original_message(
                content="The operation was verified - the user can now rejoin the server.")
        elif self.doc["type"] == "UNMUTE":
            # User needs to be unmuted.
            member = server.get_member(self.doc["user"])
            if member is None:
                return await interaction.response.edit_message(
                    content="The user is no longer in the server, so I was not able to unmute them. The task remains in the CRON list in case the user rejoins the server.",
                    view=None)
            else:
                role = discord.utils.get(server.roles, name=ROLE_MUTED)
                try:
                    await member.remove_roles(role)
                except:
                    pass
                await interaction.response.edit_message(
                    content="Attempted to unmute the user. Checking to see if the operation was succesful...",
                    view=None)
                if role not in member.roles:
                    CRON_LIST.remove(self.doc)
                    return await interaction.edit_original_message(
                        content="The operation was verified - the user can now speak in the server again.")
                else:
                    return await interaction.edit_original_message(
                        content="Uh oh! The operation was not successful - the user is still muted.")
