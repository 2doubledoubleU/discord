import discord
import sqlite3
from discord.ext import commands

class StartupCog(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.bot.server_data = {}

    def database_setup(self,id):
        filename = f'{id}.sql'
        try:
            db_connection = sqlite3.connect(f'file:{filename}?mode=rw', uri=True)
        except sqlite3.OperationalError:
            db_connection = sqlite3.connect(filename)
            print(f'DB for discord server did not previously exist. Creating {filename} and '
                  f'proceeding.')
        db = db_connection.cursor()
        db.execute('CREATE TABLE IF NOT EXISTS stored_values (name TEXT UNIQUE, value INTEGER)')
        for variable in ['logging_channel','critical_logging_channel','welcome_channel']:
            db.execute('INSERT OR IGNORE INTO stored_values (name,value) values (?,?)',[variable, None])
        db_connection.commit()

    def store_database_values(self,id):
        filename = f'{id}.sql'
        db_connection = sqlite3.connect(f'file:{filename}?mode=rw', uri=True)
        db = db_connection.cursor()
        db.execute('SELECT * from stored_values')
        for each in db.fetchall():
            self.bot.server_data[id][each[0]] = each[1]

    @commands.command(hidden=True)
    @commands.is_owner()
    async def reload(self, ctx, target: str):
        """Reloads an extension (normally used when code has been changed to avoid rebooting the
        entire bot)

        :param target: The name of the module to reload.
        """
        try:
            self.bot.reload_extension(f'extensions.{target}')
            await ctx.send(f'Reloaded {target} extension')
        except discord.ext.commands.errors.ExtensionNotLoaded:
            await ctx.send(f'{target} not loaded. Try using \'load\' instead')
        except Exception as e:
            await ctx.send(f'Error reloading {target} extension - check logs')
            print(e)

    @commands.command(hidden=True)
    @commands.is_owner()
    async def load(self, ctx, target: str):
        """Loads an extension (normally used to temporarily add an extension)

        :param target: The name of the module to load.
        """
        try:
            self.bot.load_extension(f'extensions.{target}')
            await ctx.send(f'Loaded {target} extension')
        except discord.ext.commands.errors.ExtensionNotFound:
            await ctx.send(f'Sorry {target} does not appear to exist')
        except discord.ext.commands.errors.ExtensionAlreadyLoaded:
            await ctx.send(f'{target} already loaded. Try using \'reload\' instead')
        except Exception as e:
            await ctx.send(f'Error loading {target} extension - check logs')
            print(e)

    @commands.command(hidden=True)
    @commands.is_owner()
    async def unload(self, ctx, target: str):
        """Loads an extension (normally used to temporarily add an extension)

        :param target: The name of the module to load.
        """
        try:
            self.bot.unload_extension(f'extensions.{target}')
            await ctx.send(f'Unloaded {target} extension')
        except discord.ext.commands.errors.ExtensionNotLoaded:
            await ctx.send(f'{target} does not exist or is not currently loaded.')
        except Exception as e:
            await ctx.send(f'Error loading {target} extension - check logs')
            print(e)

    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            self.database_setup(guild.id)
            self.bot.server_data[guild.id] = {'invites': {i.code: i.uses for i in await guild.invites()}}
            self.store_database_values(guild.id)

        activity = discord.Activity(name='out for miscreants', type=discord.ActivityType.watching)
        await self.bot.change_presence(activity=activity)
        print(f'Logged in as: {self.bot.user.name}')
        print('----------')

def setup(bot):
    bot.add_cog(StartupCog(bot))