import discord
from discord.ext import commands
import random
import asyncio
import sqlite3

class GeneralCommands(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def birthday(self, ctx, person: str):
        """
        Sings happy birthday
        Usage: $birthday <username>
        """
        await ctx.send(f'Happy Birthday to you\nHappy Birthday to you\nHappy Birthday dear'
                       f' {person}\nHappy Birthday to you')

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def echo(self, ctx, channel: discord.TextChannel):
        """
        Sends the message to a given channel.
        Usage: echo #channel <message here>
        """
        message = ctx.message.content.split(" ", 2)[2]  # TODO
        await channel.send(message)
        await ctx.message.add_reaction('✅')

    @commands.command(hidden=True)
    @commands.has_permissions(administrator=True)
    async def edit(self, ctx, link: str):
        new_message = ctx.message.content.split(" ", 2)[2]
        [guild_id, channel_id, message_id] = [int(x) for x in link.split("/")[-3:]]
        guild = self.bot.get_guild(guild_id)
        channel = guild.get_channel(channel_id)
        message = await channel.fetch_message(message_id)
        await message.edit(content=new_message)
        await ctx.message.add_reaction('✅')

    @commands.command()
    async def roll(self, ctx, dice: str):
        """
        Rolls dice for you and sums the result
        Usage: roll <NdN>
        """
        try:
            rolls, limit = map(int, dice.split('d'))
            if rolls <= 750:
                dice = list(random.randint(1, limit) for r in range(rolls))
                await ctx.send(', '.join(str(die) for die in dice) + f'\ntotal: {sum(dice)}')
            else:
                raise ValueError('>750 dice')
        except (discord.errors.HTTPException, ValueError):
            await ctx.send('Too many dice to show')

    @commands.command()
    async def convert(self, ctx, video: str):
        """
        Converts reddit videos and then uploads them to streamable
        Usage $convert https://www.reddit.com/r/<some video post here>
        """
        async with ctx.message.channel.typing():
            try:
                reddit_video_converter = self.bot.get_cog('RedditVideoConverter')
                video_link = await reddit_video_converter.convertRedditLink(video)
                await asyncio.sleep(15) #TODO
                await ctx.send(f"{video_link} was posted to discord by {ctx.message.author.mention}")
            except Exception as exception:
                await ctx.send(f"{exception}")

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def details(self,ctx):
        guild_id = ctx.message.guild.id
        db_connection = sqlite3.connect(f'file:{guild_id}.sql?mode=rw', uri=True)
        db = db_connection.cursor()
        db.execute('SELECT * from stored_values')
        for row in db.fetchall():
            variable = row[0]
            try:
                value = self.bot.get_channel(row[1]).mention
            except AttributeError:
                value = 'Channel not set'

            await ctx.send(f'{variable}: {value}')

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def update(self, ctx, string, channel: discord.TextChannel):
        channel_id = channel.id
        guild_id = ctx.message.guild.id
        db_connection = sqlite3.connect(f'file:{guild_id}.sql?mode=rw', uri=True)
        db = db_connection.cursor()
        db.execute('UPDATE stored_values set value = ? WHERE name = ?', [channel_id, string])
        db_connection.commit()

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def purge(self, ctx, amount = 100):
        amount = min(100,amount)
        await ctx.channel.delete_messages([x async for x in ctx.channel.history(limit=amount)])

def setup(bot):
    bot.add_cog(GeneralCommands(bot))