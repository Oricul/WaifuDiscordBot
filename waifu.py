#!/usr/bin/env python3
import datetime, discord, json
from printoverride import print as print
from discord.ext import commands

global startup_extensions
startup_extensions = ['ADMIN','tweeter']

try:
    with open('./waifu.json', 'r+') as secretfile:
        sec = json.load(secretfile)
        token = sec['bot']['token']
except FileNotFoundError:
    exit("waifu.json is not in the current bot directory.")

description = 'Created by Ori\n\nUpdated: 06/13/2017 21:14 GMT-6'
bot = commands.Bot(command_prefix='ori.', description=description)

@bot.event
async def on_ready():
    onlineMSG = '* Logged in as \'' + bot.user.name + '\' (' + bot.user.id + '). *'
    onDIV = '*'
    while len(onDIV) < len(onlineMSG):
        onDIV = onDIV + '*'
    print(onDIV + '\n' + onlineMSG + '\n' + onDIV)
    if __name__ == '__main__':
        for extension in startup_extensions:
            try:
                bot.load_extension(extension)
                print('Loaded extension: {}'.format(extension))
            except Exception as e:
                exc = '{}: {}'.format(type(e).__name__,e)
                print('Failed to load extension: {}\n{}'.format(extension, exc))


@bot.event
async def on_server_join(server):
    await bot.send_message(server, '```Hello! Is Ori in here?! For a list of commands, please use \'ori.help\'.```')

bot.run(token)
