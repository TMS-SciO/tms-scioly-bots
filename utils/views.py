import discord
import json
import asyncio
from typing import List
from urllib.parse import quote_plus
from utils.variables import *


class Confirm(discord.ui.View):
    def __init__(self, ctx):
        super().__init__()
        self.value = None
        self.author = ctx.message.author

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user == self.author:
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

embedOne = discord.Embed(
    title = "Help Page",
    description = f"Hi I'm the main bot for the TMS SciOly discord server, on pages 2-3 you will find general command help and 4-5 is Server Leader commands \n \n My current status is <:online:884200464772661338>",
    color=0xff008c
)

embedTwo = discord.Embed(
    title = "Fun Commands",
    description = f"Only use these commands in <#816809336113201193>",
    color=0xff008c
)

embedTwo.add_field(name = "`!candy`", value= "Feeds Panda One or sometimes 100 pieces of candy", inline=False)
embedTwo.add_field(name = "`!stealcandy`",
                   value= "Steal candy from panda, but be warned you may be caught", inline=False)
embedTwo.add_field(name = "`!ping`", value= "Test the bots latency", inline=False)
embedTwo.add_field(name = "`!shiba @<>`", value= "Tag someone to get shiba-d", inline=False)
embedTwo.add_field(name = "`!akita @<>`", value= "Tag someone to get akita-d", inline=False)
embedTwo.add_field(name = "`!doge @<>`", value= "Tage someone to get dogee-d", inline=False)
embedTwo.add_field(name = "`!conttondetulear @<>`", value= "Tag someone to get cottondetuleared/buddy-d", inline=False)
embedTwo.add_field(name = "`!magic8ball <>`", value= "Ask the magic8ball something", inline=False)
embedTwo.add_field(name = "`!count`", value= "Counts how many members there are", inline=False)


embedThree = discord.Embed(
    title = "Server Commands",
    description = "You can use these commands anywhere but don't abuse them!",
    color=0xff008c
)
embedThree.add_field(name="`!report <reason>`",
                     value="This command is used for reporting another member or bot errors, you can use this command or open a ticket",
                     inline=False)
embedThree.add_field(name="`!latex <math code>`", value= "Input latex math-code to get an image of the equation", inline=False)
embedThree.add_field(name="`!info`", value= "Shows info about the server", inline=False)

embedFour = discord.Embed(
    title = "Moderation Commands 1/2",
    description = "Only Coaches or users with Server Leader may use these commands, put arguments `< >` in quotes",
    color=0xff008c
)
embedFour.add_field(name="`!ban <@> '<reason>' <time>`", value="Bans a user", inline=False)
embedFour.add_field(name="`!unban <user id>`", value="Unbans a user", inline=False)
embedFour.add_field(name="`!kick <@> <reason>`", value="Kicks a user", inline=False)
embedFour.add_field(name="`!mute <@> <time>`", value="Mutes a user", inline=False)
embedFour.add_field(name="`!unmute <@>`", value="Unmutes a user", inline=False)
embedFour.add_field(name="`!warn <@> <reason>`", value="Warns a user and sends a dm through the bot about the warning",
                    inline=False)
embedFour.add_field(name="`!nuke <amount>`", value="Clears a certain amount of messages", inline=False)
embedFour.add_field(name="`!stopnuke`", value="Stops a clearing of messages", inline=False)
embedFour.add_field(name="`!embed '<title>' '<description>'`", value="Creates an embed message", inline=False)
embedFour.add_field(name="`!clrreact <message id>`", value="Clears all reactions on a given message", inline=False)
embedFour.add_field(name='`!prepembed <mention channel> {see parameters below}`',
                    value='Sends an embed to a channel \n'
                    "parameters: `{'title':'<>', 'description':'<>', 'hexColor':'<>', 'webcolor':'<>', 'thumbnailUrl':'<>',"
                    " 'authorName':'<>', 'authorUrl': '<>', 'authorIcon':'<>', 'fields':'<>', 'footerText':'<>',"
                          " 'footerUrl':'<>', 'imageUrl':'<>'}`",
                    inline=False)


embedFive = discord.Embed(
    title = "Moderation Commands 2/2",
    description = "Only users with Server Leader may use these commands",
    color=0xff008c
)
embedFive.add_field(name="`!events1`", value="Creates Role buttons for Life Science Events (only use in <#863054629787664464>)", inline=False)
embedFive.add_field(name="`!events2`", value="Creates Role buttons for Earth and Space Science Events (only use in <#863054629787664464>)", inline=False)
embedFive.add_field(name="`!events3`", value="Creates Role buttons for Physical Science & Chemistry Events (only use in <#863054629787664464>)", inline=False)
embedFive.add_field(name="`!events4`", value="Creates Role buttons for Technology & Engineering Design Events (only use in <#863054629787664464>)", inline=False)
embedFive.add_field(name="`!events5`", value="Creates Role buttons for Inquiry & Nature of Science Events (only use in <#863054629787664464>)", inline=False)
embedFive.add_field(name="`!events6`", value="Creates Role buttons for All events role (only use in <#863054629787664464>)", inline=False)
embedFive.add_field(name="`!button1`", value="Sends Embed instructions for removing roles (only use in <#863054629787664464>)", inline=False)
embedFive.add_field(name="`!pronouns`", value="Creates Role buttons for Pronouns (only use in <#863054629787664464>)", inline=False)
embedFive.add_field(name="`!ticket`", value="Creates ticket button (only use in <#848996283288518718>)", inline=False)
embedFive.add_field(name="`!eventroles`", value="Creates all the button embeds (events 1-6) only use in <#863054629787664464>", inline=False)


paginationList = [embedOne, embedTwo, embedThree, embedFour, embedFive]

class HelpButtons(discord.ui.View):
    def __init__(self, ctx, current):
        super().__init__(timeout=30.0)
        self.author = ctx.message.author
        self.current = current

    options = [
        discord.SelectOption(label='Welcome Page', value="page1"),
        discord.SelectOption(label='Fun Commands', value="page2"),
        discord.SelectOption(label='Server Commands', value="page3"),
        discord.SelectOption(label='Moderation Commands 1/2', value="page4"),
        discord.SelectOption(label='Moderation Commands 2/2', value="page5")
    ]

    @discord.ui.select(placeholder='Select a category...', min_values=1, max_values=1, options=options)
    async def selecthelpmenu(self, select:discord.ui.Select, interaction: discord.Interaction):
        value = select.values[0]
        if value == "page1":
            self.current = 0
            self.pagebutton.label = f"Page {int(paginationList.index(paginationList[self.current])) + 1}/{len(paginationList)}"
            await interaction.response.edit_message(embed=paginationList[self.current], view=self)

        if value == "page2":
            self.current = 1
            self.pagebutton.label = f"Page {int(paginationList.index(paginationList[self.current])) + 1}/{len(paginationList)}"
            await interaction.response.edit_message(embed=paginationList[self.current], view=self)

        if value == "page3":
            self.current = 2
            self.pagebutton.label = f"Page {int(paginationList.index(paginationList[self.current])) + 1}/{len(paginationList)}"
            await interaction.response.edit_message(embed=paginationList[self.current], view=self)

        if value == "page4":
            self.current = 3
            self.pagebutton.label = f"Page {int(paginationList.index(paginationList[self.current])) + 1}/{len(paginationList)}"
            await interaction.response.edit_message(embed=paginationList[self.current], view=self)

        if value == "page5":
            self.current = 4
            self.pagebutton.label = f"Page {int(paginationList.index(paginationList[self.current])) + 1}/{len(paginationList)}"
            await interaction.response.edit_message(embed=paginationList[self.current], view=self)

    @discord.ui.button(emoji='<:first:886264720955437057>', custom_id="first", style=discord.ButtonStyle.blurple, row=2)
    async def first(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.current = 0
        print(self.current)
        self.pagebutton.label = f"Page {int(paginationList.index(paginationList[self.current])) + 1}/{len(paginationList)}"
        await interaction.response.edit_message(embed=paginationList[self.current], view=self)

    @discord.ui.button(emoji='<:left:886264769466732574>', custom_id="left", style=discord.ButtonStyle.blurple, row=2)
    async def left(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.current -= 1
        print(self.current)
        if self.current < 0:
            self.current = len(paginationList) - 1

        self.pagebutton.label = f"Page {int(paginationList.index(paginationList[self.current])) + 1}/{len(paginationList)}"
        await interaction.response.edit_message(embed=paginationList[self.current], view=self)

    @discord.ui.button(label="Page 1/5", disabled=True, row=2)
    async def pagebutton(self, button:discord.ui.button, interaction:discord.Interaction):
        pass

    @discord.ui.button(emoji='<:right:886264833320820747>', custom_id="right", style=discord.ButtonStyle.blurple, row=2)
    async def right(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.current += 1
        if self.current == len(paginationList):
            self.current = 0
        self.pagebutton.label = f"Page {int(paginationList.index(paginationList[self.current])) + 1}/{len(paginationList)}"
        await interaction.response.edit_message(embed=paginationList[self.current], view=self)

    @discord.ui.button(emoji='<:last:886264854523043860>', custom_id="last", style=discord.ButtonStyle.blurple, row=2)
    async def last(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.current = 4
        self.pagebutton.label = f"Page {int(paginationList.index(paginationList[self.current])) + 1}/{len(paginationList)}"
        await interaction.response.edit_message(embed=paginationList[self.current], view=self)


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

            ticket_channel = await interaction.guild.create_text_channel("ticket-{}".format(ticket_number))
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


class Nitro(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Claim")
    async def nitroclaim(self, button: discord.ui.Button, interaction: discord.Interaction):
        number = 0

        if number + 1 >= 1:
            button.style = discord.ButtonStyle.secondary
            button.disabled = True
            button.label = "Claimed"
        em1 = discord.Embed(title= "You received a gift, but...",
                            description="The gift link has either expired or has been revoked. The sender can still create a new link to send again.")
        em1.set_thumbnail(url = "https://i.imgur.com/w9aiD6F.png")
        await interaction.response.edit_message(embed= em1, view=self)
        await interaction.followup.send('https://tenor.com/view/rick-astley-rick-roll-dancing-dance-moves-gif-14097983', ephemeral=True)


class Google(discord.ui.View):
    def __init__(self, query: str):
        super().__init__()
        # we need to quote the query string to make a valid url. Discord will raise an error if it isn't valid.
        query = quote_plus(query)
        url = f'https://www.google.com/search?q={query}'

        # Link buttons cannot be made with the decorator
        # Therefore we have to manually create one.
        # We add the quoted url to the button, and add the button to the view.
        self.add_item(discord.ui.Button(label='Click Here', url=url))
