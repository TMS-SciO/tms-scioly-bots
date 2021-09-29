import discord
from discord.ext import commands, tasks
from views import Ticket, Close, Role1, Role2, Role3, Role4, Role5, Pronouns, Allevents
from globalfunctions import auto_report
from secret import TOKEN
from variables import *
import datetime
intents = discord.Intents.all()


class PersistentViewBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix=commands.when_mentioned_or(BOT_PREFIX1, BOT_PREFIX),
                         case_insensitive=True,
                         help_command=None,
                         intents=intents,
                         slash_commands=True)
        self.persistent_views_added = False

    async def on_ready(self):
        if not self.persistent_views_added:
            self.add_view(Role1())
            self.add_view(Role2())
            self.add_view(Role3())
            self.add_view(Role4())
            self.add_view(Role5())
            self.add_view(Allevents())
            self.add_view(Pronouns())
            self.add_view(Ticket(bot))
            self.add_view(Close(bot))
            self.persistent_views_added = True
        print(f'{bot.user} has connected!')
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')
        print(discord.__version__)
        await bot.change_presence(status=discord.Status.dnd, activity=discord.Game("Minecraft"))
        cron.start()


bot = PersistentViewBot()


@tasks.loop(seconds=60)
async def cron():
    print(f"Executed cron.")

    global CRON_LIST
    for c in CRON_LIST:
        date = c['date']
        if datetime.datetime.now() > date:
            CRON_LIST.remove(c)
            await handle_cron(c['do'])


async def handle_cron(string):
    try:
        if string.find("unban") != -1:
            iden = int(string.split(" ")[1])
            server = bot.get_guild(SERVER_ID)
            member = await bot.fetch_user(int(iden))
            await server.unban(member)
            print(f"Unbanned user ID: {iden}")
        elif string.find("unmute") != -1:
            iden = int(string.split(" ")[1])
            server = bot.get_guild(SERVER_ID)
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
            await auto_report(bot ,"Error with a cron task", "red", f"Error: `{string}`")
    except Exception as e:
        await auto_report(bot, "Error with a cron task", "red", f"Error: `{e}`\nOriginal task: `{string}`")


bot.load_extension('mod')
bot.load_extension('FunCommands')
bot.load_extension('GeneralCommands')
bot.load_extension('events')
bot.run(TOKEN)
