#!/usr/bin/env python3
from urllib.request import Request, urlopen
from urllib.error import URLError
import discord, discord.utils, datetime, json, time, asyncio, inspect
from discord.ext import commands
from io import StringIO
from contextlib import redirect_stdout
from printoverride import print

try:
    with open('./waifu.json', 'r+') as secretfile:
        sec = json.load(secretfile)
        ownerid = sec['bot']['ownerid']
except FileNotFoundError:
    exit("waifu.json is not in the current bot directory.")

def is_owner_check(message):
    return message.author.id == ownerid

def is_owner():
    return commands.check(lambda ctx: is_owner_check(ctx.message))


class ADMIN():
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True, hidden=True)
    @is_owner()
    async def status(self,ctx):
        """Set the status of the bot. Owner only."""
        await self.bot.change_presence(game=discord.Game(name="{0}".format(ctx.message.content[10:])))
        return

    @commands.command(pass_context=True,hidden=True)
    @is_owner()
    async def ping(self,ctx):
        await self.bot.say("`Pong! ({0}.{1})`".format((datetime.datetime.now()-(ctx.message.timestamp-datetime.timedelta(hours=4))).seconds,str((datetime.datetime.now()-ctx.message.timestamp).microseconds)[:2]))
        return

    @commands.command(pass_context=True, hidden=True)
    @is_owner()
    async def load(self,ctx,extension_name : str):
        'Load an extension/category.'
        try:
            self.bot.load_extension(extension_name)
        except (AttributeError, ImportError) as e:
            readysend = discord.Embed(title="\U0000274C LOAD ERROR: {0}".format(extension_name),colour=0xFF0000,description="{0}: {1}".format(type(e).__name__,str(e)))
            msg = await self.bot.send_message(ctx.message.channel, embed=readysend)
            return
        except Exception as e:
            readysend = discord.Embed(title="\U0000274C UNKNOWN LOAD ERROR: {0}".format(extension_name),colour=0xFF0000,description="{0}".format(str(e)))
            msg = await self.bot.send_message(ctx.message.channel, embed=readysend)
            return
        readysend = discord.Embed(title="\U00002705 MODULE LOADED: {0}".format(extension_name),colour=0x00FF00)
        msg = await self.bot.send_message(ctx.message.channel, embed=readysend)

    @commands.command(pass_context=True, hidden=True)
    @is_owner()
    async def unload(self, ctx, extension_name : str):
        'Unload an extension/category.'
        self.bot.unload_extension(extension_name)
        readysend = discord.Embed(title="\U00002705 MODULE UNLOADED: {0}".format(extension_name),colour=0x00FF00)
        msg = await self.bot.send_message(ctx.message.channel, embed=readysend)

    @commands.command(pass_context=True, hidden=True)
    @is_owner()
    async def reload(self, ctx, extension_name : str):
        'Reload an extension/category.'
        self.bot.unload_extension(extension_name)
        try:
            self.bot.load_extension(extension_name)
        except (AttributeError, ImportError) as e:
            readysend = discord.Embed(title="\U0000274C RELOAD ERROR: {0}".format(extension_name),colour=0xFF0000,description="{0}: {1}".format(type(e).__name__,str(e)))
            msg = await self.bot.send_message(ctx.message.channel, embed=readysend)
            return
        readysend = discord.Embed(title="\U00002705 MODULE RELOADED: {0}".format(extension_name),colour=0x00FF00)
        msg = await self.bot.send_message(ctx.message.channel, embed=readysend)

    @commands.command(pass_context=True, hidden=True)
    @is_owner()
    async def say(self,ctx,*,saywhat : str):
        await self.bot.say(saywhat)
        return

    @commands.command(pass_context=True, hidden=True)
    @is_owner()
    async def debug(self, ctx, *, code : str):
        'Evaluate code.'
        code = code.strip("```\n ")
        python = "```py\n{0}\n```"
        env = {
            'bot': self.bot,
            'ctx': ctx,
            'message': ctx.message,
            'guild': ctx.message.server,
            'channel': ctx.message.channel,
            'author': ctx.message.author,
            'discord': discord,
        }
        env.update(globals())
        try:
            f = StringIO()
            with redirect_stdout(f):
                exec(code,env)
                result = str(f.getvalue())
            result = str(result)[:1014]
        except Exception as e:
            emb = {
                'color': 0xff0000,
                'field': {
                    'name': 'Exec exception "{0.__name__}":'.format(type(e)),
                    'value': str(e),
                    'inline': False
                }
            }
        else:
            emb = {
                'color': 0x00ff00,
                'field': {
                    'name': 'Exec:',
                    'value': python.format(result),
                    'inline': False
                }
            }
        try:
            result = eval(code,env)
            if inspect.isawaitable(result):
                result = await result
        except Exception as e:
            embcon = {
                'field': {
                    'name': 'Eval Exception "{0.__name__}":'.format(type(e)),
                    'value': str(e),
                    'inline': False
                }
            }
        else:
            embcon = {
                'field': {
                    'name': 'Eval:',
                    'value': python.format(result),
                    'inline': False
                }
            }
        embed = discord.Embed(title="Code:",description=python.format(code),color=emb['color'])
        embed.add_field(**emb['field'])
        embed.add_field(**embcon['field'])
        await self.bot.delete_message(ctx.message)
        await self.bot.say(embed=embed)
        return

    @load.error
    @unload.error
    @reload.error
    async def permission_error(self, error, ctw):
        error = str(error)
        if 'The check functions for command' in error:
            title = 'HIDDEN COMMAND'
            result = 'You\'ve found a hidden admin command. You do not have permissions to use it, sorry!'
        elif 'NameError' in error:
            title = 'MODULE DOES NOT EXIST'
            result = 'That module does not exist.'
        else:
            title = 'FATAL ERROR'
            result = '{} : {}\nContact Ori with the above error.'.format(error,ctw)
        readysend = discord.Embed(title="\U0000274C {0}".format(title),colour=0xFF0000,description=result)
        msg = await self.bot.say(embed=readysend)
        return

def setup(bot):
    bot.add_cog(ADMIN(bot))
