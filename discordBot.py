import discord
from discord.ext import commands
import json
from pathlib import Path

bot = commands.Bot(command_prefix='$')

initialExtensions = ['startup','commands','redditVideoConverter','logging']

for extension in initialExtensions:
    bot.load_extension(f'extensions.{extension}')

with open(Path.cwd() / 'secrets/discordBot.secret') as secretFile:
    secrets = json.loads(secretFile.read())
    botAuthToken = secrets['botAuthToken']

bot.run(botAuthToken)
