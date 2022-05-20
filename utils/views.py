from __future__ import annotations

import datetime
import re

import discord
import json
import asyncio
from typing import List, TYPE_CHECKING
from utils.variables import *
import mongo

if TYPE_CHECKING:
    from bot import TMS


class LatexModal(discord.ui.Modal):

    def __init__(
            self, bot: TMS, message: discord.Message
    ):
        self.bot = bot
        super().__init__(title="Edit Your LaTeX")
        self._message = message

        self.edited_latex = self.add_item(
            discord.ui.TextInput(
                label="Your LaTeX",
                default=self._message.content.split(r"{\color{Gray}")[1][:-1],
                style=discord.TextStyle.short
            )
        )

    async def on_submit(self, interaction: discord.Interaction) -> None:
        _item = self.children[0]
        assert isinstance(_item, discord.ui.TextInput)
        url = r"https://latex.codecogs.com/png.latex?\dpi{150}{\color{Gray}" + f"{_item.value}" + r"}"
        await self._message.edit(content=url.replace(" ", r"&space;"))
        await interaction.response.defer()


class LatexView(discord.ui.View):
    def __init__(
            self, bot: TMS, _interaction: discord.Interaction
    ):
        super().__init__(timeout=500)
        self.bot: TMS = bot
        self._interaction: discord.Interaction = _interaction

    async def on_timeout(self) -> None:
        self.clear_items()

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        return interaction.user == self._interaction.user

    @discord.ui.button(label="✏️", style=discord.ButtonStyle.blurple)
    async def edit_button(self, interaction: discord.Interaction, _: discord.ui.Button):
        message = interaction.message
        modal = LatexModal(self.bot, message)
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="🗑️️", style=discord.ButtonStyle.red)
    async def delete_button(self, interaction: discord.Interaction, _: discord.ui.Button):
        await interaction.response.defer()
        await interaction.delete_original_message()

    @discord.ui.button(label="✅", style=discord.ButtonStyle.green)
    async def save_button(self, interaction: discord.Interaction, _: discord.ui.Button):
        await interaction.response.edit_message(view=None)


class Confirm(discord.ui.View):
    def __init__(self, _interaction: discord.Interaction):
        super().__init__()
        self.value = None
        self.author = _interaction.user

    async def interaction_check(self, interaction: discord.Interaction) -> bool:

        if interaction.user == self.author or interaction.user.id == 747126643587416174:
            return True
        else:
            await interaction.response.send_message(
                "This confirmation dialog is not for you.", ephemeral=True
            )
            return False

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
    async def confirm(
            self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        for child in self.children:
            child.disabled = True
            button.label = "Confirmed"
        self.value = True
        await interaction.response.edit_message(view=self)
        self.stop()

    # This one is similar to the confirmation button except sets the inner value to `False`
    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        for child in self.children:
            child.disabled = True
            button.label = "Canceled"
        self.value = False
        await interaction.response.edit_message(view=self)
        self.stop()


class Counter(discord.ui.View):
    @discord.ui.button(label="0", style=discord.ButtonStyle.red, custom_id="counter")
    async def count(self, interaction: discord.Interaction, button: discord.ui.Button):
        number = int(button.label) if button.label else 0
        button.label = str(number + 1)

        await interaction.response.edit_message(view=self)


class Ticket(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.value = None
        self.bot = bot

    @discord.ui.button(
        label="\U0001f4e9 Create Ticket",
        custom_id="ticket",
        style=discord.ButtonStyle.secondary,
    )
    async def ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        with open("data.json") as f:
            data = json.load(f)

            ticket_number = int(data["ticket-counter"])
            ticket_number += 1

            ticket_channel = await interaction.guild.create_text_channel(
                "\U0001f4e9│ticket-{}".format(ticket_number)
            )
            await ticket_channel.set_permissions(
                interaction.guild.get_role(interaction.guild.id),
                send_messages=False,
                read_messages=False,
            )

            for role_id in data["valid-roles"]:
                role = interaction.guild.get_role(role_id)

                await ticket_channel.set_permissions(
                    role,
                    send_messages=True,
                    read_messages=True,
                    add_reactions=True,
                    embed_links=True,
                    attach_files=True,
                    read_message_history=True,
                    external_emojis=True,
                )

                await ticket_channel.set_permissions(
                    interaction.user,
                    send_messages=True,
                    read_messages=True,
                    add_reactions=True,
                    embed_links=True,
                    attach_files=True,
                    read_message_history=True,
                    external_emojis=True,
                )

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
                    title="New ticket from {}#{}".format(
                        interaction.user.name, interaction.user.discriminator
                    ),
                    description=f"{message_content} {pinged_msg_content}",
                    color=0x00A8FF,
                )
                view1 = Close(self.bot)

                data["ticket-channel-ids"].append(ticket_channel.id)
                data["ticket-counter"] = int(ticket_number)
                with open("data.json", "w") as f:
                    json.dump(data, f)

                    em3 = discord.Embed(
                        title="TMS Tickets",
                        description="Your ticket has been created at {}".format(
                            ticket_channel.mention
                        ),
                        color=0x00A8FF,
                    )
                    await interaction.response.send_message(embed=em3, ephemeral=True)
                return await ticket_channel.send(embed=em, view=view1)


class Close(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.value = None
        self.bot = bot

    @discord.ui.button(
        label="Close", custom_id="close", style=discord.ButtonStyle.danger
    )
    async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
        with open("data.json") as f:
            data = json.load(f)

            if interaction.channel.id in data["ticket-channel-ids"]:

                channel_id = interaction.channel.id
                channel = interaction.channel

                def check(message):
                    return (
                            message.author == interaction.user
                            and message.channel == interaction.channel
                            and message.content.lower() == "close"
                    )

                try:

                    em = discord.Embed(
                        title="TMS Tickets",
                        description="Are you sure you want to close this ticket? Reply with `close` if you are sure.",
                        color=0x00A8FF,
                    )

                    await interaction.response.send_message(embed=em)
                    await self.bot.wait_for("message", check=check, timeout=60)
                    await channel.delete()

                    index = data["ticket-channel-ids"].index(channel_id)
                    del data["ticket-channel-ids"][index]

                    with open("data.json", "w") as f:
                        json.dump(data, f)

                except asyncio.TimeoutError:
                    em = discord.Embed(
                        title="TMS Tickets",
                        description="You have run out of time to close this ticket. Please press the red `Close` button again.",
                        color=0x00A8FF,
                    )
                    await channel.send(embed=em)


#
# class TicTacToeButton(discord.ui.Button['TicTacToe']):
#     def __init__(self, x: int, y: int):
#         # A label is required, but we don't need one so a zero-width space is used
#         # The row parameter tells the View which row to place the button under.
#         # A View can only contain up to 5 rows -- each row can only have 5 buttons.
#         # Since a Tic Tac Toe grid is 3x3 that means we have 3 rows and 3 columns.
#         super().__init__(style=discord.ButtonStyle.secondary, label='\u200b', row=y)
#         self.x = x
#         self.y = y
#
#     # This function is called whenever this particular button is pressed
#     # This is part of the "meat" of the game logic
#     async def callback(self, interaction: discord.Interaction):
#         assert self.view is not None
#         view: TicTacToe = self.view
#         state = view.board[self.y][self.x]
#         if state in (view.X, view.O):
#             return
#
#         if view.current_player == view.X:
#             self.style = discord.ButtonStyle.danger
#             self.label = 'X'
#             self.disabled = True
#             view.board[self.y][self.x] = view.X
#             view.current_player = view.O
#             content = "It is now O's turn"
#         else:
#             self.style = discord.ButtonStyle.success
#             self.label = 'O'
#             self.disabled = True
#             view.board[self.y][self.x] = view.O
#             view.current_player = view.X
#             content = "It is now X's turn"
#
#         winner = view.check_board_winner()
#         if winner is not None:
#             if winner == view.X:
#                 content = 'X won!'
#             elif winner == view.O:
#                 content = 'O won!'
#             else:
#                 content = "It's a tie!"
#
#             for child in view.children:
#                 child.disabled = True
#
#             view.stop()
#
#         await interaction.response.edit_message(content=content, view=view)
#
#
# # This is our actual board View
# class TicTacToe(discord.ui.View):
#     # This tells the IDE or linter that all our children will be TicTacToeButtons
#     # This is not required
#     children: List[TicTacToeButton]
#     X = -1
#     O = 1
#     Tie = 2
#
#     def __init__(self):
#         super().__init__()
#         self.current_player = self.X
#         self.board = [
#             [0, 0, 0],
#             [0, 0, 0],
#             [0, 0, 0],
#         ]
#
#         for x in range(3):
#             for y in range(3):
#                 self.add_item(TicTacToeButton(x, y))
#
#     # This method checks for the board winner -- it is used by the TicTacToeButton
#     def check_board_winner(self):
#         for across in self.board:
#             value = sum(across)
#             if value == 3:
#                 return self.O
#             elif value == -3:
#                 return self.X
#
#         # Check vertical
#         for line in range(3):
#             value = self.board[0][line] + self.board[1][line] + self.board[2][line]
#             if value == 3:
#                 return self.O
#             elif value == -3:
#                 return self.X
#
#         # Check diagonals
#         diag = self.board[0][2] + self.board[1][1] + self.board[2][0]
#         if diag == 3:
#             return self.O
#         elif diag == -3:
#             return self.X
#
#         diag = self.board[0][0] + self.board[1][1] + self.board[2][2]
#         if diag == 3:
#             return self.O
#         elif diag == -3:
#             return self.X
#
#         # If we're here, we need to check if a tie was made
#         if all(i != 0 for row in self.board for i in row):
#             return self.Tie
#
#         return None


class TicTacToeButton(discord.ui.Button["TicTacToe"]):
    def __init__(self, x: int, y: int, user_x: discord.User, user_y: discord.User):
        super().__init__(style=discord.ButtonStyle.secondary, label="\u200b", row=y)
        self.x = x
        self.xUser = user_x

        self.y = y
        self.yUser = user_y

    async def callback(self, interaction: discord.Interaction):
        assert self.view is not None
        view: TicTacToe = self.view
        state = view.board[self.y][self.x]
        if state in (view.X, view.O):
            return
        if view.current_player == view.X and self.xUser.id == interaction.user.id:
            self.style = discord.ButtonStyle.danger
            self.label = "X"
            self.disabled = True
            view.board[self.y][self.x] = view.X
            view.current_player = view.O
            content = f"It is now {self.yUser.mention}'s turn"

        elif view.current_player == view.O and self.yUser.id == interaction.user.id:
            self.style = discord.ButtonStyle.success
            self.label = "O"
            self.disabled = True
            view.board[self.y][self.x] = view.O
            view.current_player = view.X
            content = f"It is now {self.xUser.mention}'s turn"

        elif not interaction.user.id == view.current_player and interaction.user in [
            self.yUser,
            self.xUser,
        ]:
            return await interaction.response.send_message(
                f"It's not your turn!", ephemeral=True
            )
        else:
            return await interaction.response.send_message(
                f"Woah! You can't join this game "
                f"as you weren't invited, if you'd like to play you can start "
                f"a session by doing `/tictactoe!",
                ephemeral=True,
            )

        winner = view.check_board_winner()
        if winner is not None:
            if winner == view.X:
                content = f"{self.xUser.mention} won!"
            elif winner == view.O:
                content = f"{self.yUser.mention} won!"
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

    def __init__(self, XPlayer, OPlayer):
        super().__init__(timeout=None)
        self.current_player = self.X
        self.board = [
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0],
        ]
        self.XPlayer = XPlayer
        self.OPlayer = OPlayer

        # Our board is made up of 3 by 3 TicTacToeButtons
        # The TicTacToeButton maintains the callbacks and helps steer
        # the actual game.
        for x in range(3):
            for y in range(3):
                self.add_item(TicTacToeButton(x, y, XPlayer, OPlayer))

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

    @discord.ui.button(label="\U0001f9e0 Anatomy & Physiology", custom_id="ap", row=1)
    async def anatomy(
            self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        role = discord.utils.get(interaction.guild.roles, id=Role.AP)
        if role in interaction.user.roles:
            member = interaction.guild.get_member(interaction.user.id)
            await member.remove_roles(role)
            await interaction.response.send_message(
                f"Removed Roles {role.mention}", ephemeral=True
            )
        else:
            member = interaction.guild.get_member(interaction.user.id)
            await member.add_roles(role)
            await interaction.response.send_message(
                f"Added Roles {role.mention}", ephemeral=True
            )

    @discord.ui.button(label="\U0001f9ec Bio Process Lab", custom_id="bpl", row=1)
    async def bpl(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = discord.utils.get(interaction.guild.roles, id=Role.BPL)
        if role in interaction.user.roles:
            member = interaction.guild.get_member(interaction.user.id)
            await member.remove_roles(role)
            await interaction.response.send_message(
                f"Removed Roles {role.mention}", ephemeral=True
            )
        else:
            member = interaction.guild.get_member(interaction.user.id)
            await member.add_roles(role)
            await interaction.response.send_message(
                f"Added Roles {role.mention}", ephemeral=True
            )

    @discord.ui.button(label="\U0001f9a0 Disease Detectives", custom_id="dd", row=1)
    async def dd(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = discord.utils.get(interaction.guild.roles, id=Role.DD)
        if role in interaction.user.roles:
            member = interaction.guild.get_member(interaction.user.id)
            await member.remove_roles(role)
            await interaction.response.send_message(
                f"Removed Roles {role.mention}", ephemeral=True
            )
        else:
            member = interaction.guild.get_member(interaction.user.id)
            await member.add_roles(role)
            await interaction.response.send_message(
                f"Added Roles {role.mention}", ephemeral=True
            )

    @discord.ui.button(label="\U0001f333 Green Generation", custom_id="gg", row=2)
    async def gg(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = discord.utils.get(interaction.guild.roles, id=Role.GG)
        if role in interaction.user.roles:
            member = interaction.guild.get_member(interaction.user.id)
            await member.remove_roles(role)
            await interaction.response.send_message(
                f"Removed Roles {role.mention}", ephemeral=True
            )
        else:
            member = interaction.guild.get_member(interaction.user.id)
            await member.add_roles(role)
            await interaction.response.send_message(
                f"Added Roles {role.mention}", ephemeral=True
            )

    @discord.ui.button(label="\U0001f985 Ornithology", custom_id="o", row=2)
    async def orni(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = discord.utils.get(interaction.guild.roles, id=Role.O)
        if role in interaction.user.roles:
            member = interaction.guild.get_member(interaction.user.id)
            await member.remove_roles(role)
            await interaction.response.send_message(
                f"Removed Roles {role.mention}", ephemeral=True
            )
        else:
            member = interaction.guild.get_member(interaction.user.id)
            await member.add_roles(role)
            await interaction.response.send_message(
                f"Added Roles {role.mention}", ephemeral=True
            )


class Role2(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="\U0001f30e Dynamic Planet", custom_id="dp", row=1)
    async def dp(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = discord.utils.get(interaction.guild.roles, id=Role.DP)
        if role in interaction.user.roles:
            member = interaction.guild.get_member(interaction.user.id)
            await member.remove_roles(role)
            await interaction.response.send_message(
                f"Removed Roles {role.mention}", ephemeral=True
            )
        else:
            member = interaction.guild.get_member(interaction.user.id)
            await member.add_roles(role)
            await interaction.response.send_message(
                f"Added Roles {role.mention}", ephemeral=True
            )

    @discord.ui.button(label="\U000026c8 Meteorology", custom_id="meteo", row=1)
    async def m(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = discord.utils.get(interaction.guild.roles, id=Role.M)
        if role in interaction.user.roles:
            member = interaction.guild.get_member(interaction.user.id)
            await member.remove_roles(role)
            await interaction.response.send_message(
                f"Removed Roles {role.mention}", ephemeral=True
            )
        else:
            member = interaction.guild.get_member(interaction.user.id)
            await member.add_roles(role)
            await interaction.response.send_message(
                f"Added Roles {role.mention}", ephemeral=True
            )

    @discord.ui.button(label="\U000026f0 Road Scholar", custom_id="rs", row=1)
    async def rs(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = discord.utils.get(interaction.guild.roles, id=Role.RS)
        if role in interaction.user.roles:
            member = interaction.guild.get_member(interaction.user.id)
            await member.remove_roles(role)
            await interaction.response.send_message(
                f"Removed Roles {role.mention}", ephemeral=True
            )
        else:
            member = interaction.guild.get_member(interaction.user.id)
            await member.add_roles(role)
            await interaction.response.send_message(
                f"Added Roles {role.mention}", ephemeral=True
            )

    @discord.ui.button(label="\U0001f48e Rocks & Minerals", custom_id="rm", row=2)
    async def rm(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = discord.utils.get(interaction.guild.roles, id=Role.RM)
        if role in interaction.user.roles:
            member = interaction.guild.get_member(interaction.user.id)
            await member.remove_roles(role)
            await interaction.response.send_message(
                f"Removed Roles {role.mention}", ephemeral=True
            )
        else:
            member = interaction.guild.get_member(interaction.user.id)
            await member.add_roles(role)
            await interaction.response.send_message(
                f"Added Roles {role.mention}", ephemeral=True
            )

    @discord.ui.button(label="\U0001f52d Solar System", custom_id="ss", row=2)
    async def ss(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = discord.utils.get(interaction.guild.roles, id=Role.SS)
        if role in interaction.user.roles:
            member = interaction.guild.get_member(interaction.user.id)
            await member.remove_roles(role)
            await interaction.response.send_message(
                f"Removed Roles {role.mention}", ephemeral=True
            )
        else:
            member = interaction.guild.get_member(interaction.user.id)
            await member.add_roles(role)
            await interaction.response.send_message(
                f"Added Roles {role.mention}", ephemeral=True
            )


class Role3(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="\U0001f30a Crave the Wave", custom_id="ctw", row=1)
    async def ctw(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = discord.utils.get(interaction.guild.roles, id=Role.CTW)
        if role in interaction.user.roles:
            member = interaction.guild.get_member(interaction.user.id)
            await member.remove_roles(role)
            await interaction.response.send_message(
                f"Removed Roles {role.mention}", ephemeral=True
            )
        else:
            member = interaction.guild.get_member(interaction.user.id)
            await member.add_roles(role)
            await interaction.response.send_message(
                f"Added Roles {role.mention}", ephemeral=True
            )

    @discord.ui.button(label="\U0001f3b5 Sounds of Music", custom_id="som", row=1)
    async def som(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = discord.utils.get(interaction.guild.roles, id=Role.SOM)
        if role in interaction.user.roles:
            member = interaction.guild.get_member(interaction.user.id)
            await member.remove_roles(role)
            await interaction.response.send_message(
                f"Removed Roles {role.mention}", ephemeral=True
            )
        else:
            member = interaction.guild.get_member(interaction.user.id)
            await member.add_roles(role)
            await interaction.response.send_message(
                f"Added Roles {role.mention}", ephemeral=True
            )

    @discord.ui.button(label="\U0001f3af Storm the Castle", custom_id="stc", row=1)
    async def stc(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = discord.utils.get(interaction.guild.roles, id=Role.STC)
        if role in interaction.user.roles:
            member = interaction.guild.get_member(interaction.user.id)
            await member.remove_roles(role)
            await interaction.response.send_message(
                f"Removed Roles {role.mention}", ephemeral=True
            )
        else:
            member = interaction.guild.get_member(interaction.user.id)
            await member.add_roles(role)
            await interaction.response.send_message(
                f"Added Roles {role.mention}", ephemeral=True
            )

    @discord.ui.button(label="\U0001f349 Food Science", custom_id="fs", row=2)
    async def fs(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = discord.utils.get(interaction.guild.roles, id=Role.FS)
        if role in interaction.user.roles:
            member = interaction.guild.get_member(interaction.user.id)
            await member.remove_roles(role)
            await interaction.response.send_message(
                f"Removed Roles {role.mention}", ephemeral=True
            )
        else:
            member = interaction.guild.get_member(interaction.user.id)
            await member.add_roles(role)
            await interaction.response.send_message(
                f"Added Roles {role.mention}", ephemeral=True
            )

    @discord.ui.button(label="\U0001f9ea Crime Busters", custom_id="cb", row=2)
    async def cb(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = discord.utils.get(interaction.guild.roles, id=Role.CB)
        if role in interaction.user.roles:
            member = interaction.guild.get_member(interaction.user.id)
            await member.remove_roles(role)
            await interaction.response.send_message(
                f"Removed Roles {role.mention}", ephemeral=True
            )
        else:
            member = interaction.guild.get_member(interaction.user.id)
            await member.add_roles(role)
            await interaction.response.send_message(
                f"Added Roles {role.mention}", ephemeral=True
            )


class Role4(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="\U0001f309 Bridges", custom_id="bridge", row=1)
    async def b(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = discord.utils.get(interaction.guild.roles, id=Role.B)
        if role in interaction.user.roles:
            member = interaction.guild.get_member(interaction.user.id)
            await member.remove_roles(role)
            await interaction.response.send_message(
                f"Removed Roles {role.mention}", ephemeral=True
            )
        else:
            member = interaction.guild.get_member(interaction.user.id)
            await member.add_roles(role)
            await interaction.response.send_message(
                f"Added Roles {role.mention}", ephemeral=True
            )

    @discord.ui.button(label="\U00002708 Electric Wright Stuff", custom_id="ews", row=1)
    async def ews(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = discord.utils.get(interaction.guild.roles, id=Role.EWS)
        if role in interaction.user.roles:
            member = interaction.guild.get_member(interaction.user.id)
            await member.remove_roles(role)
            await interaction.response.send_message(
                f"Removed Roles {role.mention}", ephemeral=True
            )
        else:
            member = interaction.guild.get_member(interaction.user.id)
            await member.add_roles(role)
            await interaction.response.send_message(
                f"Added Roles {role.mention}", ephemeral=True
            )

    @discord.ui.button(label="\U000023f1 Mission Possible", custom_id="mp", row=2)
    async def mp(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = discord.utils.get(interaction.guild.roles, id=Role.MP)
        if role in interaction.user.roles:
            member = interaction.guild.get_member(interaction.user.id)
            await member.remove_roles(role)
            await interaction.response.send_message(
                f"Removed Roles {role.mention}", ephemeral=True
            )
        else:
            member = interaction.guild.get_member(interaction.user.id)
            await member.add_roles(role)
            await interaction.response.send_message(
                f"Added Roles {role.mention}", ephemeral=True
            )

    @discord.ui.button(label="\U0001faa4 Mousetrap Vehicle", custom_id="mtv", row=2)
    async def mtv(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = discord.utils.get(interaction.guild.roles, id=Role.MV)
        if role in interaction.user.roles:
            member = interaction.guild.get_member(interaction.user.id)
            await member.remove_roles(role)
            await interaction.response.send_message(
                f"Removed Roles {role.mention}", ephemeral=True
            )
        else:
            member = interaction.guild.get_member(interaction.user.id)
            await member.add_roles(role)
            await interaction.response.send_message(
                f"Added Roles {role.mention}", ephemeral=True
            )


class Role5(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="\U0001f513 Codebusters", custom_id="code", row=1)
    async def code(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = discord.utils.get(interaction.guild.roles, id=Role.C)
        if role in interaction.user.roles:
            member = interaction.guild.get_member(interaction.user.id)
            await member.remove_roles(role)
            await interaction.response.send_message(
                f"Removed Roles {role.mention}", ephemeral=True
            )
        else:
            member = interaction.guild.get_member(interaction.user.id)
            await member.add_roles(role)
            await interaction.response.send_message(
                f"Added Roles {role.mention}", ephemeral=True
            )

    @discord.ui.button(label="\U0001f97d Experimental Design", custom_id="expd", row=1)
    async def exp(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = discord.utils.get(interaction.guild.roles, id=Role.ED)
        if role in interaction.user.roles:
            member = interaction.guild.get_member(interaction.user.id)
            await member.remove_roles(role)
            await interaction.response.send_message(
                f"Removed Roles {role.mention}", ephemeral=True
            )
        else:
            member = interaction.guild.get_member(interaction.user.id)
            await member.add_roles(role)
            await interaction.response.send_message(
                f"Added Roles {role.mention}", ephemeral=True
            )

    @discord.ui.button(label="\U0001fa82 Ping Pong Parachute", custom_id="ppp", row=2)
    async def ppp(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = discord.utils.get(interaction.guild.roles, id=Role.PPP)
        if role in interaction.user.roles:
            member = interaction.guild.get_member(interaction.user.id)
            await member.remove_roles(role)
            await interaction.response.send_message(
                f"Removed Roles {role.mention}", ephemeral=True
            )
        else:
            member = interaction.guild.get_member(interaction.user.id)
            await member.add_roles(role)
            await interaction.response.send_message(
                f"Added Roles {role.mention}", ephemeral=True
            )

    @discord.ui.button(label="\U0001f4dd Write it, Do it", custom_id="widi", row=2)
    async def widi(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = discord.utils.get(interaction.guild.roles, id=Role.WIDI)
        if role in interaction.user.roles:
            member = interaction.guild.get_member(interaction.user.id)
            await member.remove_roles(role)
            await interaction.response.send_message(
                f"Removed Roles {role.mention}", ephemeral=True
            )
        else:
            member = interaction.guild.get_member(interaction.user.id)
            await member.add_roles(role)
            await interaction.response.send_message(
                f"Added Roles {role.mention}", ephemeral=True
            )


class Pronouns(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="\U0001f9e1 He/Him", custom_id="he", row=1)
    async def he(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = discord.utils.get(interaction.guild.roles, id=Role.HE)
        if role in interaction.user.roles:
            member = interaction.guild.get_member(interaction.user.id)
            await member.remove_roles(role)
            await interaction.response.send_message(
                f"Removed Roles {role.mention}", ephemeral=True
            )
        else:
            member = interaction.guild.get_member(interaction.user.id)
            await member.add_roles(role)
            await interaction.response.send_message(
                f"Added Roles {role.mention}", ephemeral=True
            )

    @discord.ui.button(label="\U0001f49b She/Her", custom_id="she", row=1)
    async def she(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = discord.utils.get(interaction.guild.roles, id=Role.SHE)
        if role in interaction.user.roles:
            member = interaction.guild.get_member(interaction.user.id)
            member = interaction.guild.get_member(interaction.user.id)
            await member.remove_roles(role)
            await interaction.response.send_message(
                f"Removed Roles {role.mention}", ephemeral=True
            )
        else:
            member = interaction.guild.get_member(interaction.user.id)
            await member.add_roles(role)
            await interaction.response.send_message(
                f"Added Roles {role.mention}", ephemeral=True
            )

    @discord.ui.button(label="\U0001f49c They/Them", custom_id="they", row=1)
    async def they(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = discord.utils.get(interaction.guild.roles, id=Role.THEY)
        if role in interaction.user.roles:
            member = interaction.guild.get_member(interaction.user.id)
            await member.remove_roles(role)
            await interaction.response.send_message(
                f"Removed Roles {role.mention}", ephemeral=True
            )
        else:
            member = interaction.guild.get_member(interaction.user.id)
            await member.add_roles(role)
            await interaction.response.send_message(
                f"Added Roles {role.mention}", ephemeral=True
            )

    @discord.ui.button(label="\U0001f49a Ask", custom_id="ask", row=1)
    async def ask(self, interaction: discord.Interaction, button: discord.ui.Button):
        role = discord.utils.get(interaction.guild.roles, id=Role.ASK)
        if role in interaction.user.roles:
            member = interaction.guild.get_member(interaction.user.id)
            await member.remove_roles(role)
            await interaction.response.send_message(
                f"Removed Roles {role.mention}", ephemeral=True
            )
        else:
            member = interaction.guild.get_member(interaction.user.id)
            await member.add_roles(role)
            await interaction.response.send_message(
                f"Added Roles {role.mention}", ephemeral=True
            )


#
# class Allevents(discord.ui.View):
#     def __init__(self):
#         super().__init__(timeout=None)
#
#     @discord.ui.button(label="\U0001f499 All Events ", custom_id='ae')
#     async def allevents(self, interaction: discord.Interaction, button: discord.ui.Button):
#         role = discord.utils.get(interaction.guild.roles, id=...)
#         if role in interaction.user.roles:
#             member = interaction.guild.get_member(interaction.user.id)
#             await member.remove_roles(role)
#             await interaction.response.send_message(f'Removed Roles {role.mention}', ephemeral=True)
#         else:
#             member = interaction.guild.get_member(interaction.user.id)
#             await member.add_roles(role)
#             await interaction.response.send_message(f'Added Roles {role.mention}', ephemeral=True)


# class Google(discord.ui.View):
#     def __init__(self, query: str):
#         super().__init__()
#         # we need to quote the query string to make a valid url. Discord will raise an error if it isn't valid.
#         query = quote_plus(query)
#         url = f'https://www.google.com/search?q={query}'
#         self.add_item(discord.ui.Button(label='Click Here', url=url))


class NukeStopButton(discord.ui.Button["Nuke"]):
    def __init__(self, nuke, ctx: discord.Interaction):
        super().__init__(label="ABORT", style=discord.ButtonStyle.danger)
        self.nuke = nuke
        self.author = ctx.user

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

    def __init__(self, ctx: discord.Interaction):
        super().__init__()
        button = NukeStopButton(self, ctx)
        self.add_item(button)
        self.author = ctx.user

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user == self.author or interaction.user.id == 747126643587416174:
            return True
        await interaction.response.send_message(
            "This confirmation dialog is not for you.", ephemeral=True
        )


# class AllEventsSelect(discord.ui.View):
#     def __init__(self):
#         super().__init__(timeout=None)
#
#     options = [
#         discord.SelectOption(label="Anatomy and Physiology", value="anatomy", emoji="\U0001f9e0"),
#         discord.SelectOption(label="Bio Process Lab", value="bpl", emoji="\U0001f9ec"),
#         discord.SelectOption(label="Bridges", value="bridges", emoji="\U0001f309"),
#         discord.SelectOption(label="Codebusters", value="code", emoji="\U0001f512"),
#         discord.SelectOption(label="Crave the Wave", value="wave", emoji="\U0001f30a"),
#         discord.SelectOption(label="Crime Busters", value="crime", emoji="\U0001f9ea"),
#         discord.SelectOption(label="Disease Detectives", value="dd", emoji="\U0001f9a0"),
#         discord.SelectOption(label="Dynamic Planet", value="dp", emoji="\U0001f30e"),
#         discord.SelectOption(label="Electric Wright Stuff", value="ews", emoji="\U0001f6e9"),
#         discord.SelectOption(label="Experimental Design", value="expd", emoji="\U0001f97d"),
#         discord.SelectOption(label="Food Science", value="fs", emoji="\U0001f349"),
#         discord.SelectOption(label="Green Generation", value="gg", emoji="\U0001f333"),
#         discord.SelectOption(label="Meteorology", value="meteo", emoji="\U000026c8"),
#         discord.SelectOption(label="Mission Possible", value="mission", emoji="\U000023f2"),
#         discord.SelectOption(label="Mousetrap Vehicle", value="mouse", emoji="\U0001faa4"),
#         discord.SelectOption(label="Ornithology", value="orni", emoji="\U0001f985"),
#         discord.SelectOption(label="Ping Pong Parachute", value="ppp", emoji="\U0001fa82"),
#         discord.SelectOption(label="Road Scholar", value="road", emoji="\U0001f3d4"),
#         discord.SelectOption(label="Rocks and Minerals", value="rocks", emoji="\U0001f48e"),
#         discord.SelectOption(label="Solar System", value="solar", emoji="\U0001fa90"),
#         discord.SelectOption(label="Sounds of Music", value="music", emoji="\U0001f3b5"),
#         discord.SelectOption(label="Storm the Castle", value="castle", emoji="\U0001f3af"),
#         discord.SelectOption(label="Write It Do It", value="widi", emoji="\U0001f4dd")
#     ]
#
#     @discord.ui.select(
#         placeholder="Chose what events you're participating in!",
#         max_values=1,
#         min_values=0,
#         options=options,
#         custom_id="events_select")
#     async def event_select(self, select: discord.ui.Select, interaction: discord.Interaction):
#         roles = {"anatomy": ROLE_AP,
#                  "bpl": ROLE_BPL,
#                  "bridges": ROLE_B,
#                  "code": ROLE_C,
#                  "crime": ROLE_CB,
#                  "wave": ROLE_CTW,
#                  "dd": ROLE_DD,
#                  "dp": ROLE_DP,
#                  "ews": ROLE_EWS,
#                  "expd": ROLE_ED,
#                  "fs": ROLE_FS,
#                  "gg": ROLE_GG,
#                  "meteo": ROLE_M,
#                  "mission": ROLE_MP,
#                  "mouse": ROLE_MV,
#                  "orni": ROLE_O,
#                  "ppp": ROLE_PPP,
#                  "road": ROLE_RS,
#                  "rocks": ROLE_RM,
#                  "solar": ROLE_SS,
#                  "music": ROLE_SOM,
#                  "castle": ROLE_STC,
#                  "widi": ROLE_WIDI
#                  }
#         values = select.values[0]
#         role_name = roles[values]
#         role = discord.utils.get(interaction.guild.roles, id=role_name)
#         if role in interaction.user.roles:
#             await interaction.user.remove_roles(role)
#             await interaction.response.send_message(
#                 f'Removed Roles {role.mention}, if you accidentally added this role click the option again to remove it',
#                 ephemeral=True)
#         else:
#             await interaction.user.add_roles(role)
#             await interaction.response.send_message(
#                 f'Added Roles {role.mention}, if you accidentally added this role click the option again to remove it',
#                 ephemeral=True)


class ReportView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="\U00002705", custom_id="green_check", style=discord.ButtonStyle.green
    )
    async def green_check(
            self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        if interaction.channel.id == Channel.REPORTS:
            await interaction.response.defer()
            await interaction.message.delete()
            print("Handled by staff")
        else:
            await interaction.response.defer()

    @discord.ui.button(
        label="\U0000274c", custom_id="red_x", style=discord.ButtonStyle.red
    )
    async def red_x(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.channel.id == Channel.REPORTS:
            await interaction.response.defer()
            await interaction.message.delete()
            print("Cleared with no action")
        else:
            await interaction.response.defer()


class CronView(discord.ui.View):
    def __init__(self, docs, bot, ctx: discord.Interaction):
        super().__init__()
        self.add_item(CronSelect(docs, bot, ctx))
        self.ctx = ctx

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user == self.ctx.user:
            return True
        else:
            await interaction.response.send_message(
                "Sorry, this menu cannot be controlled by you", ephemeral=True
            )
            return False


class CronSelect(discord.ui.Select):
    def __init__(self, docs, bot, ctx):
        options = []
        docs.sort(key=lambda d: d["time"])
        print([d["time"] for d in docs])
        counts = {}
        for doc in docs[:20]:
            timeframe = (doc["time"] - discord.utils.utcnow()).days
            if abs(timeframe) < 1:
                timeframe = f"{((doc['time']) - discord.utils.utcnow()).total_seconds() // 3600} hours"
            else:
                timeframe = f"{((doc['time']) - discord.utils.utcnow()).days} days"
            tag_name = f"{doc['type'].title()} {doc['tag']}"
            if tag_name in counts:
                counts[tag_name] = counts[tag_name] + 1
            else:
                counts[tag_name] = 1
            if counts[tag_name] > 1:
                tag_name = f"{tag_name} (#{counts[tag_name]})"
            option = discord.SelectOption(
                label=tag_name, description=f"Occurs in {timeframe}."
            )
            options.append(option)

        super().__init__(
            placeholder="View potential actions to modify...",
            min_values=1,
            max_values=1,
            options=options,
        )
        self.docs = docs
        self.bot = bot
        self.ctx = ctx

    async def callback(self, interaction: discord.Interaction):
        value = self.values[0]
        num = re.findall(r"\(#(\d*)", value)
        value = re.sub(r" \(#\d*\)", "", value)
        relevant_doc = [
            d for d in self.docs if f"{d['type'].title()} {d['tag']}" == value
        ]
        if len(relevant_doc) == 1:
            relevant_doc = relevant_doc[0]
        else:
            if not len(num):
                relevant_doc = relevant_doc[0]
            else:
                num = num[0]
                relevant_doc = relevant_doc[int(num) - 1]
        view = CronConfirm(relevant_doc, self.bot, self.ctx)
        embed = discord.Embed(
            title="Action Dashboard",
            description=f"Okay! What would you like me to do with this CRON item?\n> {self.values[0]}",
            color=discord.Color.fuchsia(),
        )
        await interaction.response.edit_message(view=view, embed=embed)


class CronConfirm(discord.ui.View):
    def __init__(self, doc, bot: TMS, ctx: discord.Interaction):
        super().__init__()
        self.doc = doc
        self.bot = bot
        self.ctx = ctx

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user == self.ctx.user:
            return True
        else:
            await interaction.response.send_message(
                "Sorry, this menu cannot be controlled by you", ephemeral=True
            )
            return False

    @discord.ui.button(label="Remove", style=discord.ButtonStyle.danger)
    async def remove_button(
            self, interaction: discord.Interaction, button: discord.ui.Button
    ):
        await self.bot.mongo.remove_doc("bot", "cron", self.doc["_id"])
        embed = discord.Embed(
            title="Action Dashboard",
            description="Awesome! I successfully removed the action from the CRON list.",
            color=discord.Color.brand_green(),
        )
        await interaction.response.edit_message(embed=embed, view=None, content=None)

    @discord.ui.button(label="Complete Now", style=discord.ButtonStyle.green)
    async def complete_button(
            self, interaction: discord.Interaction, button: discord.ui.Button
    ):

        server = self.bot.get_guild(SERVER_ID)
        embed = discord.Embed()

        if self.doc["type"] == "UNBAN":

            embed.title = "Checking..."
            embed.description = "Attempting to unban the user. Checking to see if operation was successful..."
            embed.colour = discord.Colour.yellow()

            await interaction.response.edit_message(embed=embed, view=None)

            # User needs to be unbanned
            member = self.bot.get_user(self.doc["user"])
            await server.unban(member)

            bans = [b async for b in server.bans()]
            for ban in bans:
                if ban.user.id == self.doc["user"]:
                    embed.title = "\U000026a0 Failed to unban"
                    embed.description = "Uh oh! The operation was not successful - the user remains banned."
                    embed.colour = discord.Colour.brand_red()
                    return await interaction.edit_original_message(
                        embed=embed, content=None
                    )

            await self.bot.mongo.remove_doc("bot", "cron", self.doc["_id"])
            embed.title = "Completed Unban"
            embed.description = (
                "The operation was verified - the user can now rejoin the server."
            )
            embed.colour = discord.Colour.brand_green()
            return await interaction.edit_original_message(embed=embed, content=None)

        elif self.doc["type"] == "UNMUTE":
            # User needs to be unmuted.
            member = server.get_member(self.doc["user"])
            if member is None:
                embed.title = "\U000026a0 Unable to unmute user"
                embed.description = (
                    "The user is no longer in the server, so I was not able to unmute them. The task "
                    "remains in the CRON list in case the user rejoins the server. "
                )
                embed.colour = discord.Colour.yellow()
                return await interaction.response.edit_message(
                    embed=embed, content=None, view=None
                )
            else:
                embed.title = "Checking..."
                embed.description = "Attempting to unmute the user. Checking to see if the operation was successful..."
                embed.colour = discord.Colour.yellow()
                await interaction.response.edit_message(embed=embed, view=None)

                try:
                    role = server.get_role(Role.MUTED)
                    await member.remove_roles(role)
                except:
                    embed.title = "\U000026a0 Failed to unmute"
                    embed.description = "Uh oh! The operation was not successful - the user is still muted."
                    embed.colour = discord.Colour.brand_red()
                    return await interaction.edit_original_message(
                        embed=embed, content=None
                    )

                await self.bot.mongo.remove_doc("bot", "cron", self.doc["_id"])
                embed.title = "Success!"
                embed.description = (
                    f"The operation was verified - the user ({member.mention}) can now speak in "
                    f"the server again. "
                )
                embed.colour = discord.Colour.brand_green()
                return await interaction.edit_original_message(
                    content=None, embed=embed
                )

        elif self.doc["type"] == "UNSTEALCANDYBAN":
            member = self.bot.get_user(self.doc["user"])
            embed.title = "Checking..."
            embed.description = "Attempting to unban the user. Checking to see if operation was successful..."
            embed.colour = discord.Colour.yellow()

            await interaction.response.edit_message(embed=embed, view=None)

            try:
                STEALFISH_BAN.remove(self.doc["user"])
                await self.bot.mongo.remove_doc("bot", "cron", self.doc["_id"])
                embed.title = "\U0001f36c Success! \U0001f36c"
                embed.description = (
                    f"Successfully unbanned {member} from stealing candy!"
                )
                embed.colour = discord.Colour.brand_green()
                return await interaction.edit_original_message(
                    embed=embed, content=None
                )

            except Exception as e:
                print(e)
                embed.title = "\U0001f36c Failed!"
                embed.description = (
                    "Uh oh! The operation was not successful - the user remains banned from stealing "
                    "candy. "
                )
                embed.colour = discord.Colour.brand_red()
                return await interaction.edit_original_message(
                    embed=embed, content=None
                )
