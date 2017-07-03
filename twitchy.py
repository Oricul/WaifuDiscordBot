#!/usr/bin/env python3
import asyncio, datetime, discord, discord.utils, json, linecache, pytz, sys, time
from discord.ext import commands
from printoverride import print
from twitch.api import v3 as twitch
import MySQLdb as MS
#----------------------------------------------------------------------------------------------------
try:
    with open('./waifu.json', 'r+') as secretfile:
        sec = json.load(secretfile)
        sqlHost = sec['SQL']['sqlHost']
        sqlUser = sec['SQL']['sqlUser']
        sqlPass = sec['SQL']['sqlPass']
        dbname1 = sec['twitchy']['dbname1']
        tblname1 = sec['twitchy']['tblname1']
        tblname2 = sec['twitchy']['tblname2']
        tblname3 = sec['twitchy']['tblname3']
        ownerid = sec['bot']['ownerid']
except FileNotFoundError:
    exit("waifu.json is not in the current bot directory.")
#----------------------------------------------------------------------------------------------------
def ReportException():
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename,lineno,f.f_globals)
    print('Error on line: {}.\nCode: {}\nException: {}'.format(lineno,line.strip(),exc_obj))
    return '`FATAL ERROR` on `line:` {}\n`Problem Code:` ```python\n{}\n````Exception Raised:` {}'.format(lineno,line.strip(),exc_obj)

def SQLSetup():
    try:
        sqldb1 = MS.connect(host=sqlHost,user=sqlUser,passwd=sqlPass)
        cur1 = sqldb1.cursor()
        sqlcmd1 = cur1.execute("show databases like '{0}'".format(dbname1))
        if sqlcmd1 == 0:
            sqlcmd1 = cur1.execute("create database if not exists {0}".format(dbname1))
            if sqlcmd1 == 0:
                return "MySQL: Failed to create database '{0}'".format(dbname1)
            else:
                sqlcmd1 = cur1.execute("use {0}".format(dbname1))
                sqlcmd1 = cur1.execute("create table {0} (username VARCHAR(20), adddate DATETIME, addedby VARCHAR(20))".format(tblname1))
                sqlcmd1 = cur1.execute("create table {0} (channelid BIGINT, adddate DATETIME, addedby VARCHAR(20))".format(tblname2))
                sqlcmd1 = cur1.execute("create table {0} (username VARCHAR(20), game VARCHAR(60), title VARCHAR(100))".format(tblname3))
                return "MySQL: Created database '{0}' and tables '{1}', '{2}', '{3}'.".format(dbname1,tblname1,tblname2,tblname3)
        sqlcmd1 = cur1.execute("use {0}".format(dbname1))
        cur1.execute("select count(*) from information_schema.tables where table_name = '{0}' and table_schema = '{1}'".format(tblname1,dbname1))
        if cur1.fetchone()[0] < 1:
            sqlcmd1 = cur1.execute("create table {0} (username VARCHAR(20), adddate DATETIME, addedby VARCHAR(20))".format(tblname1))
        cur1.execute("select count(*) from information_schema.tables where table_name = '{0}' and table_schema = '{1}'".format(tblname2,dbname1))
        if cur1.fetchone()[0] < 1:
            sqlcmd1 = cur1.execute("create table {0} (channelid BIGINT, adddate DATETIME, addedby VARCHAR(20))".format(tblname2))
        cur1.execute("select count(*) from information_schema.tables where table_name = '{0}' and table_schema = '{1}'".format(tblname3,dbname1))
        if cur1.fetchone()[0] < 1:
            sqlcmd1 = cur1.execute("create table {0} (username VARCHAR(20), game VARCHAR(60), title VARCHAR(100))".format(tblname3))
        return "MySQL: Database '{0}' and tables '{1}', '{2}', '{3}'  exist.".format(dbname1,tblname1,tblname2,tblname3)
    except:
        return "MySQL: {0}".format(ReportException())

def is_owner_check(message):
    return message.author.id == ownerid

def is_owner():
    return commands.check(lambda ctx: is_owner_check(ctx.message))

async def twitchGet(username : str,flag = 0,chOutput = None,brOutput = None):
    try:
        chOutput = twitch.channels.by_name(username)
        brOutput = twitch.streams.by_channel(username)
    except:
        flag = 1
    return [flag,chOutput,brOutput]

async def twitchFormat(format,chOutput,brOutput):
    try:
        if format == 'status':
            if brOutput['stream'] == None:
                compMSG = discord.Embed(title="[LAST LIVE]",
                                        colour=discord.Colour(0x4C0B5F),
                                        description=chOutput['updated_at'])
                compMSG.set_thumbnail(url=chOutput['logo'])
                compMSG.set_author(name="{0} is not currently streaming on Twitch.TV".format(chOutput['display_name']),
                                   url=chOutput['url'])
                compMSG.add_field(name="[FOLLOWERS]",
                                  value=chOutput['followers'],
                                  inline=True)
                compMSG.add_field(name="[TOTAL VIEWS]",
                                  value=chOutput['views'],
                                  inline=True)
            else:
                compMSG = discord.Embed(title="[TITLE]",
                                        colour=discord.Colour(0x8904B1),
                                        description=brOutput['stream']['channel']['status'])
                compMSG.set_thumbnail(url=brOutput['stream']['channel']['logo'])
                compMSG.set_image(url=brOutput['stream']['preview']['medium'])
                compMSG.set_author(name="{0} is streaming live on Twitch.TV".format(brOutput['stream']['channel']['display_name']),
                                   url=brOutput['stream']['channel']['url'])
                compMSG.add_field(name="[GAME]",
                                  value=brOutput['stream']['game'],
                                  inline=True)
                compMSG.add_field(name="[VIEWERS]",
                                value=brOutput['stream']['viewers'],
                                inline=True)
        elif format == 'update':
            compMSG = discord.Embed(title="[TITLE]",
                                    colour=discord.Colour(0x8904B1),
                                    description=brOutput['stream']['channel']['status'])
            compMSG.set_thumbnail(url=brOutput['stream']['channel']['logo'])
            compMSG.set_author(name="{0} updated their stream info on Twitch.TV".format(brOutput['stream']['channel']['display_name']),
                               url=brOutput['stream']['channel']['url'])
            compMSG.add_field(name="[GAME]",
                              value=brOutput['stream']['game'],
                              inline=True)
            compMSG.add_field(name="[VIEWERS]",
                              value=brOutput['stream']['viewers'],
                              inline=True)
        else:
            print("Invalid status when using function 'twitchFormat'.")
            return
    except:
        ReportException()
        return
    return compMSG
#----------------------------------------------------------------------------------------------------
class Twitch():
    def __init__(self,bot):
        self.bot = bot
        print(SQLSetup())

    @commands.command(pass_context=True)
    async def twitchAdd(self,ctx,username):
        """Add a Twitch username to this server's watchlist.

        Usage: ori.twitchAdd <username>
        Example: ori.twitchAdd monstercat"""
        tStatus = await twitchGet(username)
        if tStatus[0] == 1:
            outMSG = discord.Embed(colour=discord.Colour(0xFF0000))
            outMSG.set_author(name="{0} not found on Twitch.TV".format(username))
        else:
            outMSG = await twitchFormat('status',tStatus[1],tStatus[2])
        await self.bot.send_message(discord.Object(id=ctx.message.channel.id),embed=outMSG)
        return


def setup(bot):
    bot.add_cog(Twitch(bot))
