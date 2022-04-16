from __future__ import annotations

import datetime
import json

import discord
from discord.ext import commands
from utils import SERVER_ID, Channel

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bot import TMS

"""
Relevant views.
"""


class IgnoreButton(discord.ui.Button):
    """
    A button to mark the report as ignored. This causes the report message to be deleted, an informational message to
    be posted in closed-reports, and the report database to be updated
    """

    view = None

    def __init__(self, view):
        self.view = view
        super().__init__(
            style=discord.ButtonStyle.gray,
            label="Ignore",
            custom_id=f"{view.report_id}:ignore"
        )

    async def callback(self, interaction: discord.Interaction):
        # Delete the original report
        await interaction.message.delete()

        # Send an informational message about the report being ignored
        closed_reports = interaction.guild.get_channel(Channel.CLOSED_REPORTS)
        await closed_reports.send(
            f"**Report was ignored** by {interaction.user.mention} - {self.view.member.mention} had the inappropriate "
            f"username `{self.view.offending_username}`, but the report was ignored.")


class ChangeInappropriateUsername(discord.ui.Button):
    """
    A button that changes the username of a user. This causes the report message to be deleted, an informational
    message to be posted in closed-reports, and the report database to be updated.
    """

    view = None

    def __init__(self, view):
        self.view = view
        super().__init__(
            style=discord.ButtonStyle.green,
            label="Change Username",
            custom_id=f"{view.report_id}:change_username"
        )

    async def callback(self, interaction: discord.Interaction):
        # Delete the original message
        await interaction.message.delete()

        # Check to make sure user is still in server before taking action
        member_still_here = self.view.member in self.view.member.guild.members

        closed_reports = interaction.guild.get_channel(Channel.CLOSED_REPORTS)
        if member_still_here:
            await closed_reports.send(
                f"**Member's username was changed** by {interaction.user.mention} - {self.view.member.mention} had "
                f"the inappropriate username `{self.view.offending_username}`, and their username was changed to "
                f"`Scientist`.")

            # Change the user's username
            await self.view.member.edit(nick="Scientist")

        else:
            await closed_reports.send(
                f"**Member's username was attempted to be changed** by {interaction.user.mention} - "
                f"{self.view.member.mention} had the inappropriate username `{self.view.offending_username}`, and "
                f"their username was attempted to be changed to `Scientist`, however, the user had left the server.")


class KickUserButton(discord.ui.Button):
    view = None

    def __init__(self, view):
        self.view = view
        super().__init__(style=discord.ButtonStyle.red, label="Kick User", custom_id=f"{view.report_id}:kick")

    async def callback(self, interaction: discord.Interaction):

        # Delete the original message
        await interaction.message.delete()

        # Check to make sure user is still in server before taking action
        member_still_here = self.view.member in self.view.member.guild.members

        # Send an informational message about the report being updated
        closed_reports = interaction.guild.get_channel(Channel.CLOSED_REPORTS)
        if member_still_here:
            await closed_reports.send(
                f"**Member was kicked** by {interaction.user.mention} - {self.view.member.mention} had the "
                f"inappropriate username `{self.view.offending_username}`, and the user was kicked from the server.")

            # Kick the user
            await self.view.member.kick()

        else:
            await closed_reports.send(
                f"**Attempted to kick member* by {interaction.user.mention} - {self.view.member.mention} had the "
                f"inappropriate username `{self.view.offending_username}` and a kick was attempted on the user, "
                f"however, the user had left the server.")


class InappropriateUsername(discord.ui.View):
    member: discord.Member
    offending_username: str
    report_id: int

    def __init__(self, member: discord.Member, report_id: int, offending_username: str):
        self.member = member
        self.report_id = report_id
        self.offending_username = offending_username
        super().__init__(timeout=86400)  # Timeout after one day

        # Add relevant buttons
        super().add_item(IgnoreButton(self))
        super().add_item(ChangeInappropriateUsername(self))
        super().add_item(KickUserButton(self))


class Reporter(commands.Cog):

    def __init__(self, bot: TMS):
        self.bot = bot
        print("Initialized Reporter cog.")

    async def create_staff_message(self, embed: discord.Embed):
        guild = self.bot.get_guild(SERVER_ID)
        reports_channel = guild.get_channel(Channel.REPORTS)
        await reports_channel.send(embed=embed)

    async def create_inappropriate_username_report(self, member: discord.Member, offending_username: str):
        guild = self.bot.get_guild(SERVER_ID)
        reports_channel = guild.get_channel(Channel.REPORTS)

        # Assemble relevant embed
        embed = discord.Embed(
            title="Inappropriate Username Detected",
            color=discord.Color.brand_red(),
            description=f"""{member.mention} was found to have the offending username: `{offending_username}`.
            You can take some action by using the buttons below.
            """
        )
        with open("data.json") as f:
            data = json.load(f)

            report_id = int(data["report_id"])
            report_id += 1

        await reports_channel.send(embed=embed, view=InappropriateUsername(member, report_id, offending_username))
        data["report_id"] = int(report_id)
        with open("data.json", 'w') as f:
            json.dump(data, f)

    async def create_cron_task_report(self, task: dict):
        guild = self.bot.get_guild(SERVER_ID)
        reports_channel = guild.get_channel(Channel.REPORTS)

        # Serialize values
        task['_id'] = str(task['_id'])  # ObjectID is not serializable by default
        if 'time' in task:
            task['time'] = datetime.datetime.strftime(task['time'],
                                                      "%m/%d/%Y, %H:%M:%S")  # datetime.datetime is not serializable
            # by default

        # Assemble the embed
        embed = discord.Embed(
            title="Error with CRON Task",
            description=f"""
               There was an error with the following CRON task:
               ```py
               {json.dumps(task, indent=4)} ``` Because this likely a development error, no actions can immediately 
               be taken. Please contact a developer to learn more. """,
            color=discord.Color.brand_red()
        )
        await reports_channel.send(embed=embed)


async def setup(bot: TMS):
    await bot.add_cog(Reporter(bot))
