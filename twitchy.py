#!/usr/bin/env python3
import asyncio, datetime, discord, discord.utils, json, linecache, pytz, sys, time, twitter
from discord.ext import commands
from printoverride import print
from twitch.api import v3 as twi
import MySQLdb as MS
#----------------------------------------------------------------------------------------------------
try:
    with open('/root/Waifu/waifu.json', 'r+') as secretfile:
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
        cur1.execute("select count(*) from information_schema.tables where table_name = '{0}'".format(tblname1))
        if not cur1.fetchone()[0] == 1:
            sqlcmd1 = cur1.execute("create table {0} (username VARCHAR(20), adddate DATETIME, addedby VARCHAR(20))".format(tblname1))
        cur1.execute("select count(*) from information_schema.tables where table_name = '{0}'".format(tblname2))
        if not cur1.fetchone()[0] == 1:
            sqlcmd1 = cur1.execute("create table {0} (channelid BIGINT, adddate DATETIME, addedby VARCHAR(20))".format(tblname2))
        cur1.execute("select count(*) from information_schema.tables where table_name = '{0}'".format(tblname3))
        if not cur1.fetchone()[0] == 1:
            sqlcmd1 = cur1.execute("create table {0} (username VARCHAR(20), game VARCHAR(60), title VARCHAR(100))".format(tblname3))
        return "MySQL: Database '{0}' and tables '{1}', '{2}', '{3}'  exist.".format(dbname1,tblname1,tblname2,tblname3)
    except:
        return "MySQL: {0}".format(ReportException())

def is_owner_check(message):
    return message.author.id == ownerid

def is_owner():
    return commands.check(lambda ctx: is_owner_check(ctx.message))
#----------------------------------------------------------------------------------------------------
class Twitch():
    def __init__(self,bot):
        self.bot = bot
        print(SQLSetup())



def setup(bot):
    bot.add_cog(Twitch(bot))
