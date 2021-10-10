from discord.ext import tasks, commands
import discord
from utils.variables import *
from utils.globalfunctions import auto_report
import datetime


class Tasks(commands.Cog):
    """Async Tasks"""
    print('Tasks Cog Loaded')

    def __init__(self, bot):
        self.bot = bot
        self.cron.start()

    @tasks.loop(seconds=60)
    async def cron(self):
        print(f"Executed cron.")
        global CRON_LIST
        for c in CRON_LIST:
            date = c['date']
            if datetime.datetime.now() > date:
                CRON_LIST.remove(c)
                await self.handle_cron(c['do'])

    async def handle_cron(self, string):
        try:
            if string.find("unban") != -1:
                iden = int(string.split(" ")[1])
                server = self.bot.get_guild(SERVER_ID)
                member = await self.bot.fetch_user(int(iden))
                await server.unban(member)
                print(f"Unbanned user ID: {iden}")
            elif string.find("unmute") != -1:
                iden = int(string.split(" ")[1])
                server = self.bot.get_guild(SERVER_ID)
                member = server.get_member(int(iden))
                role = discord.utils.get(server.roles, name=ROLE_MUTED)
                self_role = discord.utils.get(server.roles, name=ROLE_SELFMUTE)
                await member.remove_roles(role, self_role)
                print(f"Unmuted user ID: {iden}")
            elif string.find("unstealfishban") != -1:
                iden = int(string.split(" ")[1])
                STEALFISH_BAN.remove(iden)
                print(f"Un-stealfished user ID: {iden}")
            else:
                print("ERROR:")
                await auto_report(self.bot ,"Error with a cron task", "red", f"Error: `{string}`")
        except Exception as e:
            await auto_report(self.bot, "Error with a cron task", "red", f"Error: `{e}`\nOriginal task: `{string}")


def setup(bot):
    bot.add_cog(Tasks(bot))
