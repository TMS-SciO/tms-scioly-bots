from __future__ import annotations

import asyncio

from discord.ext import tasks, commands
import discord

import datetime
from typing import List, Optional, TYPE_CHECKING, Union
from utils import Role, SERVER_ID, STEALFISH_BAN

if TYPE_CHECKING:
    from bot import TMS
    from .report import Reporter


class CronTasks(commands.Cog):
    """Cron Tasks"""
    print('Tasks Cog Loaded')

    def __init__(self, bot: TMS):
        self.bot = bot
        self.cron.start()
        self.mongo = self.bot.mongo

    @tasks.loop(minutes=1)
    async def cron(self):
        cron_list: List = await self.mongo.get_cron()
        for task in cron_list:
            if datetime.datetime.now() >= task['time']:
                try:
                    if task['type'] == "UNBAN":
                        server = self.bot.get_guild(SERVER_ID)
                        member: discord.Member = server.get_member(task['user'])
                        await server.unban(member)
                        print(f"Unbanned user ID: {member.id}")
                        await self.mongo.delete("data", "cron", task["_id"])

                    elif task['type'] == "UNMUTE":
                        server = self.bot.get_guild(SERVER_ID)
                        member: discord.Member = server.get_member(task['user'])
                        role = server.get_role(Role.M)
                        self_role = server.get_role(Role.SELFMUTE)
                        await member.remove_roles(role, self_role)
                        print(f"Unmuted user ID: {member.id}")
                        await self.mongo.delete("data", "cron", task["_id"])

                    elif task['type'] == "UNSTEALCANDYBAN":
                        STEALFISH_BAN.remove(task['user'])
                        print(f"Un-stealcandybanneded user ID: {task['user']}")
                        await self.mongo.delete("data", "cron", task["_id"])
                    else:
                        print("ERROR:")
                        reporter_cog: Union[commands.Cog, Reporter] = self.bot.get_cog('Reporter')
                        await reporter_cog.create_cron_task_report(task)
                        await self.mongo.delete("data", "cron", task["_id"])
                except Exception:
                    reporter_cog: Union[commands.Cog, Reporter] = self.bot.get_cog('Reporter')
                    await reporter_cog.create_cron_task_report(task)

        print("Executed cron.")

    @cron.before_loop
    async def _before(self):
        await self.bot.wait_until_ready()

    async def add_to_cron(self, item_dict: dict):
        """
        Adds the given document to the CRON list.
        """
        await self.mongo.insert('bot', 'cron', item_dict)
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
