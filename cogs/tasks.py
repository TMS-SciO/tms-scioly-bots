from __future__ import annotations

from discord.ext import tasks, commands
import discord

import mongo
import datetime
from typing import TYPE_CHECKING
from utils import Role, SERVER_ID, STEALFISH_BAN


if TYPE_CHECKING:
    from bot import TMS


class CronTasks(commands.Cog):
    """Cron Tasks"""
    print('Tasks Cog Loaded')

    def __init__(self, bot: TMS):
        self.bot = bot
        self.cron.start()

    async def cog_unload(self) -> None:
        self.cron.stop()

    @tasks.loop(minutes=1)
    async def cron(self):
        print("Executed cron.")
        cron_list: list = await mongo.get_cron()

        for task in cron_list:
            if datetime.datetime.now() >= task['time']:
                try:
                    if task['type'] == "UNBAN":
                        server = self.bot.get_guild(SERVER_ID)
                        member: discord.Member = server.get_member(task['user'])
                        await server.unban(member)
                        print(f"Unbanned user ID: {member.id}")

                    elif task['type'] == "UNMUTE":
                        server = self.bot.get_guild(SERVER_ID)
                        member: discord.Member = server.get_member(task['user'])
                        role = server.get_role(Role.M)
                        self_role = server.get_role(Role.SELFMUTE)
                        await member.remove_roles(role, self_role)
                        print(f"Unmuted user ID: {member.id}")

                    elif task['type'] == "UNSTEALCANDYBAN":
                        STEALFISH_BAN.remove(task['user'])
                        print(f"Un-stealcandybanneded user ID: {task['user']}")

                    else:
                        print("ERROR:")
                        reporter_cog = self.bot.get_cog('Reporter')
                        await reporter_cog.create_cron_task_report(task)
                    await mongo.delete("data", "cron", task["_id"])
                except Exception:
                    reporter_cog = self.bot.get_cog('Reporter')
                    await reporter_cog.create_cron_task_report(task)

    @staticmethod
    async def add_to_cron(item_dict: dict):
        """
        Adds the given document to the CRON list.
        """
        await mongo.insert('bot', 'cron', item_dict)
        print(f"Added item: {item_dict} to CRON_LIST")

    async def schedule_unban(self, user: discord.User, time: datetime.datetime):
        item_dict = {
            'type': "UNBAN",
            'user': user.id,
            'time': time,
            'tag': str(user)
        }
        await self.add_to_cron(item_dict)

    async def schedule_unmute(self, user: discord.User, time: datetime.datetime):
        item_dict = {
            'type': "UNMUTE",
            'user': user.id,
            'time': time,
            'tag': str(user)
        }
        await self.add_to_cron(item_dict)

    async def schedule_unselfmute(self, user: discord.User, time: datetime.datetime):
        item_dict = {
            'type': "UNSELFMUTE",
            'user': user.id,
            'time': time,
            'tag': str(user)
        }
        await self.add_to_cron(item_dict)


async def setup(bot: TMS):
    await bot.add_cog(CronTasks(bot))
