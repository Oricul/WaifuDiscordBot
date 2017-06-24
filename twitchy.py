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
    return message.author.id == "107270310344024064"

def is_owner():
    return commands.check(lambda ctx: is_owner_check(ctx.message))
#----------------------------------------------------------------------------------------------------
class Twitch():
    def __init__(self,bot):
        self.bot = bot
        print(SQLSetup())
#        self.bot.loop.call_soon(self.readyupdatecheck)

#    def readyupdatecheck(self):
#        self.bot.loop.create_task(self.sendupdatecheck())

#    async def sendupdatecheck(self):
#        self.bot.loop.call_later(twitdelay,self.readyupdatecheck)

#    @commands.command(pass_context=True)
#    @is_owner()
#    async def twitch+(self,ctx,*,msg : str):
#        """Add a Twitter username to the watchlist."""
#        try:
#            sqldb1 = MS.connect(host=sqlHost,user=sqlUser,passwd=sqlPass,db=dbname1)
#            cur1 = sqldb1.cursor()
#            try:
#                cur1.execute("select * from {0};".format(tblname1))
#                msg = msg.lower()
#                for row in cur1:
#                    if row[1] == msg and str(row[4]) == str(ctx.message.server.id):
#                        sqladdby = ctx.message.server.get_member(row[3])
#                        if sqladdby == None:
#                            sqladdby = 'NULL'
#                        whenadd = datetime.datetime.strftime(row[0],"%a, %b %d, %Y %I:%M:%S %p")
#                        await self.bot.say("`{0} was already added by {1} on {2} (US/EST).`".format(msg.title(),sqladdby,whenadd))
#                        sqldb1.close()
#                        return
#                try:
#                    try:
#                        status = twitapi.GetUserTimeline(screen_name=msg,count=200,include_rts=False,exclude_replies=True)
#                    except:
#                        await self.bot.say("`User {0} does not appear to exist on Twitter.`".format(msg))
#                    preConvTwitTime = datetime.datetime.strptime(status[0].created_at,"%a %b %d %H:%M:%S %z %Y")\
#                                      .replace(tzinfo=pytz.FixedOffset(+0000)).astimezone(pytz.timezone('America/New_York'))
#                    convTwitTime = datetime.datetime.strftime(preConvTwitTime,"%Y-%m-%d %H:%M:%S")
#                    convCurTime = str(datetime.datetime.now())
#                    convCurTime = convCurTime[:-7]
#                    cur1.execute("insert into watchlist values ('{0}','{1}','{2}','{3}','{4}')".format(convCurTime,msg.lower(),convTwitTime,ctx.message.author.id,ctx.message.server.id))
#                    sqldb1.commit()
#                    convTwitTime = datetime.datetime.strftime(preConvTwitTime,"%a, %b %d, %Y %I:%M:%S %p")
#                    readyit = discord.Embed(title="{0} (@{1})".format(status[0].user.name,status[0].user.screen_name),colour=int(hex(int(status[0].user.profile_background_color,16)),16), \
#                                            url="https://www.twitter.com/{0}/status/{1}".format(status[0].user.screen_name,status[0].id_str),description="{0}".format(status[0].text))
#                    readyit.set_thumbnail(url=status[0].user.profile_image_url)
#                    readyit.set_footer(text="\U0001F4E2 {0} \U00002764 {1} | {2}".format(status[0].retweet_count,status[0].favorite_count,convTwitTime))
#                    try:
#                        for i in status[0].media:
#                            if i.type == "photo":
#                                readyit.set_image(url=i.media_url)
#                    except:
#                        pass
#                    await self.bot.say("`Added {0} (@{1}).`".format(status[0].user.name,status[0].user.screen_name))
#                    sendit = await self.bot.send_message(ctx.message.channel,embed=readyit)
#                    return
#                except:
#                    await self.bot.say("`Lv3`\n{0}".format(ReportException()))
#            except:
#                await self.bot.say("`Lv2`\n{0}".format(ReportException()))
#        except:
#            await self.bot.say("`Lv1`\n{0}".format(ReportException()))
#        sqldb1.close()
#        return

#    @commands.command(pass_context=True)
#    @is_owner()
#    async def twitch-(self,ctx,*,msg : str):
#        """Remove a Twitter username from the watchlist."""
#        try:
#            sqldb1 = MS.connect(host=sqlHost,user=sqlUser,passwd=sqlPass,db=dbname1)
#            cur1 = sqldb1.cursor()
#            cur1.execute("select username,serverid from {0};".format(tblname1))
#            msg = msg.lower()
#            for username,serverid in cur1:
#                if str(username) == str(msg) and str(serverid) == str(ctx.message.server.id):
#                    cur1.execute("delete from {0} where username like '{1}' and serverid like '{2}';".format(tblname1,msg,ctx.message.server.id))
#                    sqldb1.commit()
#                    status = twitapi.GetUserTimeline(screen_name=msg)
#                    await self.bot.say("`Removed {0} (@{1}).`".format(status[0].user.name,status[0].user.screen_name))
#                    return
#            sqldb1.close()
#            await self.bot.say("`{0} is not currently being followed on Twitter.`".format(msg.title()))
#        except:
#            await self.bot.say(ReportException())
#        return

#    @commands.command(pass_context=True)
#    @is_owner()
#    async def tchadd(self,ctx):
#        """Add a channel to receive tweet updates."""
#        try:
#            sqldb1 = MS.connect(host=sqlHost,user=sqlUser,passwd=sqlPass,db=dbname1)
#            cur1 = sqldb1.cursor()
#            try:
#                cur1.execute("select * from {0};".format(tblname2))
#                for adddate,channelid,addedby in cur1:
#                    if str(channelid) == str(ctx.message.channel.id):
#                        sqladdby = ctx.message.server.get_member(addedby)
#                        if sqladdby == None:
#                            sqladdby = 'NULL'
#                        whenadd = datetime.datetime.strftime(adddate,"%a, %b %d, %Y %I:%M:%S %p")
#                        await self.bot.say("`{0} was already added by {1} on {2} (US/EST).`".format(ctx.message.channel.name,sqladdby,whenadd))
#                        sqldb1.close()
#                        return
#            except:
#                await self.bot.say(ReportException())
#            try:
#                convCurTime = str(datetime.datetime.now())
#                convCurTime = convCurTime[:-7]
#                cur1.execute("insert into channel values ('{0}','{1}','{2}')".format(convCurTime,ctx.message.channel.id,ctx.message.author.id))
#                sqldb1.commit()
#                await self.bot.say("`{0} will now receive Twitter updates.`".format(ctx.message.channel.name))
#            except:
#                await self.bot.say(ReportException())
#        except:
#            await self.bot.say(ReportException())
#        sqldb1.close()
#        return

#    @commands.command(pass_context=True)
#    @is_owner()
#    async def tchrem(self,ctx):
#        """Remove a channel from receving tweet updates."""
#        try:
#            sqldb1 = MS.connect(host=sqlHost,user=sqlUser,passwd=sqlPass,db=dbname1)
#            cur1 = sqldb1.cursor()
#            cur1.execute("select channelid from {0};".format(tblname2))
#            for row in cur1:
#                for channelid in row:
#                    if str(channelid) == str(ctx.message.channel.id):
#                        cur1.execute("delete from {0} where channelid like '{1}';".format(tblname2,ctx.message.channel.id))
#                        sqldb1.commit()
#                        await self.bot.say("`{0} will no longer receive Twitter updates.`".format(ctx.message.channel.name))
#                        return
#            await self.bot.say("`{0} is not currently receiving Twitter updates.`".format(ctx.message.channel.name))
#        except:
#            await self.bot.say(ReportException())
#        sqldb1.close()
#        return

#    @commands.command(pass_context=True)
#    @is_owner()
#    async def tlist(self,ctx):
#        """Lists the current Twitter accounts being followed."""
#        try:
#            sqldb1 = MS.connect(host=sqlHost,user=sqlUser,passwd=sqlPass,db=dbname1)
#            cur1 = sqldb1.cursor()
#            cur1.execute("select username from {0};".format(tblname1))
#            compiled = ""
#            for row in cur1:
#                for username in row:
#                    compiled = "{0}@{1}, ".format(compiled,username)
#            compiled = compiled[:-2]
#            await self.bot.say("`Currently watched Twitter accounts:` {0}".format(compiled))
#        except:
#            await self.bot.say(ReportException())
#        sqldb1.close()
#        return
#----------------------------------------------------------------------------------------------------
def setup(bot):
    bot.add_cog(Twitch(bot))
