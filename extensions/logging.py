import discord
from discord.ext import commands

class Logging(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(
                f'Missing required argument, use ```$help {ctx.message.content[1:]}``` for more details')

    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild_id = member.guild.id
        current_invites = await member.guild.invites()
        old_invites = self.bot.server_data[guild_id]['invites']
        channel = member.guild.get_channel(self.bot.server_data[guild_id]['logging_channel'])
        for invite in current_invites:
            if invite.code in old_invites and invite.uses > old_invites[invite.code]:
                await channel.send(f'{member.mention} joined using link https://discordbot.gg/'
                                   f'{invite.code} created by {invite.inviter.mention}')
            elif invite.uses > 0:
                await channel.send(f'{member.mention} joined using link https://discordbot.gg/'
                                   f'{invite.code} created by {invite.inviter.mention}')
        self.bot.server_data[guild_id]['invites'] = {i.code: i.uses for i in current_invites}

    @commands.Cog.listener()
    async def on_message_delete(self,message):
        log_channel = message.guild.get_channel(self.bot.server_data[message.guild.id][
                                                    'logging_channel'])
        embed = discord.Embed.from_dict(dict(
            color=16711680,
            title='Message deleted:',
            description=message.content,
            author={'name': message.author.display_name,'icon_url': str(message.author.avatar_url)},
            footer={'text': '(this is a placeholder)'}))
        await log_channel.send('in {}'.format(message.channel.mention), embed=embed)

    @commands.Cog.listener()
    async def on_message(self,message):
        if any(x in message.content for x in ['good bot', 'Good Bot', 'Good bot', 'good Bot']):
            await message.add_reaction('😊')

def setup(bot):
    bot.add_cog(Logging(bot))