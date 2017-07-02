#!/usr/bin/env python3
import datetime, discord, json
from printoverride import print as print
from discord.ext import commands
#import help

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
    onlineMSG = "* Logged in as '{0}' ({1}). *".format(bot.user.name,bot.user.id)
    dversionMSG = "Discord API v{0}".format(discord.__version__)
    pversionMSG = "Python3 v{0}".format(python_version())
    ownMSG = "Owner: {0}".format(bot.owner)
    chanMSG = "Servers: {0}".format(len(bot.servers))
    userMSG = "Users: {0}".format(len(list(bot.get_all_members())))
    oauth = "OAuth URL: {0}".format(discord.utils.oauth_url(bot.user.id))
    onDIV = '*'
    while len(onDIV) < len(onlineMSG):
        onDIV = onDIV + '*'
    onLEN = len(onlineMSG) - 2
    while len(dversionMSG) < onLEN:
        dversionMSG = ' ' + dversionMSG
        if len(dversionMSG) < onLEN:
            dversionMSG = dversionMSG + ' '
    dversionMSG = '*' + dversionMSG + '*'
    while len (pversionMSG) < onLEN:
        pversionMSG = ' ' + pversionMSG
        if len(pversionMSG) < onLEN:
            pversionMSG = pversionMSG + ' '
    pversionMSG = '*' + pversionMSG + '*'
    while len(ownMSG) < onLEN:
        ownMSG = ' ' + ownMSG
        if len(ownMSG) < onLEN:
            ownMSG = ownMSG + ' '
    ownMSG = '*' + ownMSG + '*'
    while len(chanMSG) < onLEN:
        chanMSG = ' ' + chanMSG
        if len(chanMSG) < onLEN:
            chanMSG = chanMSG + ' '
    chanMSG = '*' + chanMSG + '*'
    while len(userMSG) < onLEN:
        userMSG = ' ' + userMSG
        if len(userMSG) < onLEN:
            userMSG = userMSG + ' '
    userMSG = '*' + userMSG + '*'
    while len(oauth) < onLEN:
        oauth = ' ' + oauth
        if len(oauth) < onLEN:
            oauth = oauth + ' '
    oauth = '*' + oauth + '*'
    print("{0}\n{1}\n{2}\n{3}\n{4}\n{5}\n{6}\n{7}\n{0}".format(onDIV,onlineMSG,dversionMSG,pversionMSG,ownMSG,chanMSG,userMSG,oauth))
    if __name__ == '__main__':
        for extension in startup_extensions:
            try:
                bot.load_extension(extension)
                print('Loaded extension: {}'.format(extension))
            except Exception as e:
                exc = '{}: {}'.format(type(e).__name__,e)
                print('Failed to load extension: {}\n{}'.format(extension,exc))


@bot.event
async def on_server_join(server):
    await bot.send_message(server, '```Hello! Is Ori in here?! For a list of commands, please use \'ori.help\'.```')

bot.run(token)
