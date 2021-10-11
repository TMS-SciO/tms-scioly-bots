from discord.ext import commands
from typing import Literal
from utils.checks import is_staff
from utils.variables import BASE_EXTENSIONS, INITIAL_EXTENSIONS
from utils.views import Confirm


class BaseCogs(commands.Cog):
    """Core commands for unloading and reloading"""
    print('Base Cog Loaded')

    def __init__(self, bot):
        self.bot = bot

    @commands.group()
    @commands.check(is_staff())
    async def cogs(self, ctx):
        pass

    @cogs.command()
    @commands.check(is_staff())
    async def load(self, ctx,
                   cog: Literal["cogs.mod", "cogs.listeners", "cogs.fun", "cogs.general", "cogs.tasks", "cogs.base"]):
        '''Loads a module'''
        try:
            self.bot.load_extension(cog)
            await ctx.send("Successfully loaded " + f"`{cog}`" + " module")
            print("loaded module: " + cog)
        except Exception as e:
            await ctx.send("Error with loading " + f"`{cog}`" + f"\n Error {e}")

    @cogs.command()
    @commands.check(is_staff())
    async def reload(self, ctx,
                     cog: Literal["cogs.mod", "cogs.listeners", "cogs.fun", "cogs.general", "cogs.tasks", "cogs.base"]):
        '''Reloads a module'''
        try:
            self.bot.reload_extension(cog)
            await ctx.send("Successfully reloaded " + f"`{cog}`" + " module")
            print("reloaded module: " + cog)
        except Exception as e:
            await ctx.send("Error with reloading " + f"`{cog}`" + f"\n Error {e}")

    @cogs.command()
    @commands.check(is_staff())
    async def unload(self, ctx,
                     cog: Literal["cogs.mod", "cogs.listeners", "cogs.fun", "cogs.general", "cogs.tasks", "cogs.base"]):
        '''Unloads a module'''
        try:
            self.bot.unload_extension(cog)
            await ctx.send("Successfully unloaded " + f"`{cog}`" + " module")
            print("unloaded module: " + cog)
        except Exception as e:
            await ctx.send("Error with unloading " + f"`{cog}`" + f"\n Error {e}")

    @cogs.command()
    @commands.check(is_staff())
    async def remove_cog(self, ctx,
                        cog: Literal["cogs.mod", "cogs.listeners", "cogs.fun", "cogs.general", "cogs.tasks", "cogs.base"]):
        '''Removes a module'''
        try:
            self.bot.remove_cog(cog)
            await ctx.send("Successfully removed " + f"`{cog}`" + " module")
            print("removed module: " + cog)
        except Exception as e:
            await ctx.send("Error with removing " + f"`{cog}`" + f"\n Error {e}")

    @cogs.command()
    @commands.check(is_staff())
    async def remove_listener(self, ctx,
                              listener: Literal[
                                  "on_member_join",
                                  "on_message",
                                  "on_message_edit",
                                  "on_command_error",
                                  "on_error",
                                  "on_raw_message_delete",
                                  "on_member_update",
                                  "on_raw_reaction_add"]):
        '''Removes a listener'''
        try:
            self.bot.remove_listener(func=listener, name=listener)
            await ctx.send("Successfully removed listener " + f"`{listener}`" + " module")
            print("removed listener: " + listener)
        except Exception as e:
            await ctx.send("Error with removing " + f"`{listener}`" + f"\n Error {e}")

    @cogs.command()
    @commands.check(is_staff())
    async def remove_command(self, ctx,
                             command):
        '''Removes a command'''
        try:
            self.bot.remove_command(name=command)
            await ctx.send("Successfully removed command " + f"`{command}`" + " module")
            print("removed command: " + command)
        except Exception as e:
            await ctx.send("Error with removing " + f"`{command}`" + f"\n Error {e}")

    @cogs.command()
    @commands.check(is_staff())
    async def reload_all(self, ctx):
        '''Reloads All extensions'''
        for extension in INITIAL_EXTENSIONS:
            try:
                self.bot.reload_extension(extension)
                await ctx.send('Reloaded all extensions')
            except Exception as e:
                await ctx.send(f'Failed to reload all extensions \n Error: {e}')

    @cogs.command()
    @commands.check(is_staff())
    async def unload_all(self, ctx):
        '''Unloads all Cogs except cogs/base.py'''
        for extension in BASE_EXTENSIONS:
            try:
                self.bot.unload_extension(extension)
                await ctx.send('Unloaded all extensions')
            except Exception as e:
                await ctx.send(f'Failed to unload all extensions \n Error: {e}')

    @cogs.command()
    @commands.check(is_staff())
    async def load_all(self, ctx):
        '''Loads all Cogs'''
        for extension in BASE_EXTENSIONS:
            try:
                self.bot.load_extension(extension)
                await ctx.send('Loaded all extensions')
            except Exception as e:
                await ctx.send(f'Failed to load all extensions \n Error: {e}')

    @commands.command()
    @commands.is_owner()
    async def remove_all_slash_commands(self, ctx):
        view = Confirm(ctx)
        await ctx.send("Are you sure you want to remove **ALL** slash commands?", view=view)
        await view.wait()
        if view.value is False:
            await ctx.send("Upserting of slash-commands has been aborted")
        if view.value is True:
            application_id = self.bot.application_id or (await self.bot.application_info()).id
            await self.bot.http.bulk_upsert_guild_commands(application_id, 816806329925894217, [])
            await ctx.send("**GUILD SLASH COMMANDS UPSERT COMPLETE**")
            await self.bot.http.bulk_upsert_global_commands(self.bot.application_id, [])
            await ctx.send("**GLOBAL SLASH COMMANDS UPSERT COMPLETE**")



def setup(bot):
    bot.add_cog(BaseCogs(bot))






