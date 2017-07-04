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
    return

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
                sqlcmd1 = cur1.execute("create table {0} (username VARCHAR(20), adddate DATETIME, addedby BIGINT, serverid BIGINT)".format(tblname1))
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
        self.bot.loop.create_task(self.twitchUpdate())

    async def twitchUpdate(self):
        await self.bot.wait_until_ready()
        while not self.bot.is_closed:
            try:
                changed = 0
                try:
                    sqldb1 = MS.connect(host=sqlHost,user=sqlUser,passwd=sqlPass,db=dbname1)
                    cur1 = sqldb1.cursor()
                    cur1.execute("select username,serverid from {0}".format(tblname1))
                    cur2 = sqldb1.cursor()
                    cur2.execute("select channelid from {0}".format(tblname2))
                    cur3 = sqldb1.cursor()
                    cur3.execute("select * from {0}".format(tblname3))
                    cur4 = sqldb1.cursor()
                    print("SQL CONF")
                except:
                    ReportException()
                    pass
                print(cur3)
                for username,game,title in cur3:
                    print("{0} ||| {1} ||| {2}".format(username,game,title))
                    tStatus = await twitchGet(username)
                    print("STREAMING: GET STATUS ||| {0}".format(tStatus[2]['stream']))
                    if tStatus[2]['stream'] is None:
                        changed = 1
                        outMSG = await twitchFormat('status',tStatus[1],tStatus[2])
                        print("STREAMING: NO LONGER STREAMING")
                        for origuser, serverid in cur1:
                            for server in self.bot.servers:
                                for channel in server.channels:
                                    for row in cur2:
                                        for postchanid in row:
                                            if str(server.id) == str(serverid) and str(channel.id) == str(postchanid):
                                                print("STREAMING: NO LONGER STREAMING: SEND MESSAGE")
                                                await self.bot.send_message(discord.Object(id=postchanid), embed=outMSG)
                        cur4.execute("delete from {0} where username like '{1}';".format(tblname3, username))
                    else:
                        if tStatus[2]['stream']['game'] != game or tStatus[2]['stream']['channel']['status'] != title:
                            changed = 1
                            outMSG = await twitchFormat('update',tStatus[1],tStatus[2])
                            print("STREAMING: UPDATE INFO")
                            for origuser, serverid in cur1:
                                for server in self.bot.servers:
                                    for channel in server.channels:
                                        for row in cur2:
                                            for postchanid in row:
                                                if str(server.id) == str(serverid) and str(channel.id) == str(postchanid):
                                                    print("STREAMING: UPDATE INFO: SEND MESSAGE")
                                                    await self.bot.send_message(discord.Object(id=postchanid), embed=outMSG)
                            cur4.execute("update {0} set game='{1}' and title='{2}' where username='{3}';".format(tblname3,tStatus[2]['stream']['game'],tStatus[2]['stream']['channel']['status'],username))
                if changed == 0:
                    for username,serverid in cur1:
                        tStatus = await twitchGet(username)
                        print("NOT STREAMING: GET STATUS")
                        if tStatus[2]['stream'] is not None:
                            outMSG = await twitchFormat('update',tStatus[1],tStatus[2])
                            print("NOT STREAMING: NOW STREAMING")
                            for origuser, serverid in cur1:
                                for server in self.bot.servers:
                                    for channel in server.channels:
                                        for row in cur2:
                                            for postchanid in row:
                                                if str(server.id) == str(serverid) and str(channel.id) == str(postchanid):
                                                    print("NOT STREAMING: NOW STREAMING: SEND MESSAGE")
                                                    await self.bot.send_message(discord.Object(id=postchanid), embed=outMSG)
                            cur4.execute("insert into {0} values ('{1}','{2}','{3}');".format(tblname3,username,tStatus[2]['stream']['game'],tStatus[2]['stream']['channel']['status']))
                sqldb1.commit()
            except:
                ReportException()
                pass
            print("I'M HERE!!!!!!!!!!!!!!!!!!!!!!")
            await asyncio.sleep(3.5)

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
            try:
                sqldb1 = MS.connect(host=sqlHost,user=sqlUser,passwd=sqlPass,db=dbname1)
                cur1 = sqldb1.cursor()
                username = username.lower()
                try:
                    cur1.execute("select * from {0};".format(tblname1))
                    for row in cur1:
                        if row[0].lower() == username and str(row[3]) == str(ctx.message.server.id):
                            sqladdby = ctx.message.server.get_member(str(row[2]))
                            if sqladdby == None:
                                sqladdby = 'NULL'
                            whenadd = datetime.datetime.strftime(row[1],"%a, %b %d, %Y %I:%M:%S %p")
                            outMSG = discord.Embed(colour=discord.Colour(0xFFFF00))
                            outMSG.set_author(name="{0} was already added by {1} on {2} (US/EST).".format(tStatus[1]['display_name'],sqladdby,whenadd))
                            await self.bot.send_message(discord.Object(id=ctx.message.channel.id),embed=outMSG)
                            sqldb1.close()
                            return
                    TwitchAddTime = str(datetime.datetime.now())
                    TwitchAddTime = TwitchAddTime[:-7]
                    try:
                        cur1.execute("insert into {0} values ('{1}','{2}','{3}','{4}')".format(tblname1,username,TwitchAddTime,ctx.message.author.id,ctx.message.server.id))
                        sqldb1.commit()
                    except:
                        ReportException()
                        await self.bot.say("An error has been reported to the bot's owners.")
                        return
                    outMSG = await twitchFormat('status',tStatus[1],tStatus[2])
                    await self.bot.say("`Added {0} to the Twitch.TV watchlist.`".format(tStatus[1]['display_name']))
                except:
                    ReportException()
                    await self.bot.say("An error has been reported to the bot's owners.")
                    return
            except:
                ReportException()
                await self.bot.say("An error has been reported to the bot's owners.")
                return
        await self.bot.send_message(discord.Object(id=ctx.message.channel.id),embed=outMSG)
        return

    @commands.command(pass_context=True)
    async def twitchRem(self,ctx,username):
        """Remove a Twitch username from this server's watchlist.

        Usage: ori.twitchRem <username>
        Example: ori.twitchRem monstercat"""
        username = username.lower()
        try:
            sqldb1 = MS.connect(host=sqlHost,user=sqlUser,passwd=sqlPass,db=dbname1)
            cur1 = sqldb1.cursor()
            cur1.execute("select username,serverid from {0};".format(tblname1))
        except:
            ReportException()
            await self.bot.say("An error has been reported to the bot's owners.")
            return
        for sqluser,serverid in cur1:
            if sqluser.lower() == username and str(serverid) == str(ctx.message.server.id):
                try:
                    cur1.execute("delete from {0} where username like '{1}' and serverid like '{2}';".format(tblname1,username,ctx.message.server.id))
                    sqldb1.commit()
                except:
                    ReportException()
                    await self.bot.say("An error has been reported to the bot's owners.")
                    return
                await self.bot.say("`Removed {0} from this server's Twitch.TV watchlist.`".format(username))
                return
        sqldb1.close()
        await self.bot.say("`{0} is not currently on this server's Twitch.TV watchlist.".format(username))
        return

    @commands.command(pass_context=True)
    async def twitchAddCh(self,ctx):
        """Adds the current channel to post updates for Twitch.TV

        Usage: ori.twitchAddCh"""
        try:
            sqldb1 = MS.connect(host=sqlHost,user=sqlUser,passwd=sqlPass,db=dbname1)
            cur1 = sqldb1.cursor()
        except:
            sqldb1.close()
            ReportException()
            await self.bot.say("An error has been reported to the bot's owners.")
            return
        try:
            cur1.execute("select * from {0};".format(tblname2))
        except:
            sqldb1.close()
            ReportException()
            await self.bot.say("An error has been reported to the bot's owners.")
            return
        for channelid,adddate,addedby in cur1:
            if str(channelid) == str(ctx.message.channel.id):
                sqladdby = ctx.message.server.get_member(addedby)
                if sqladdby == None:
                    sqladdby = 'NULL'
                whenadd = datetime.datetime.strftime(adddate,"%a, %b %d, %Y %I:%M:%S %p")
                await self.bot.say("`{0} was already added by {1} on {2} (US/EST).`".format(ctx.message.channel.name,sqladdby,whenadd))
                sqldb1.close()
                return
        convCurTime = str(datetime.datetime.now())
        convCurTime = convCurTime[:-7]
        try:
            cur1.execute("insert into {0} values ('{1}','{2}','{3}')".format(tblname2,ctx.message.channel.id,convCurTime,ctx.message.author.id))
            sqldb1.commit()
        except:
            sqldb1.close()
            ReportException()
            await self.bot.say("An error has been reported to the bot's owners.")
            return
        await self.bot.say("`{0} will now receive Twitch.TV updates.`".format(ctx.message.channel.name))
        sqldb1.close()
        return

    @commands.command(pass_context=True)
    async def twitchRemCh(self,ctx):
        """Remove the current channel from receiving Twitch.TV updates.

        Usage: ori.twitchRemCh"""
        try:
            sqldb1 = MS.connect(host=sqlHost,user=sqlUser,passwd=sqlPass,db=dbname1)
            cur1 = sqldb1.cursor()
            cur1.execute("select channelid from {0};".format(tblname2))
        except:
            try:
                sqldb1.close()
            except:
                pass
            ReportException()
            await self.bot.say("An error has been reported to the bot's owners.")
            return
        for row in cur1:
            for channelid in row:
                if str(channelid) == str(ctx.message.channel.id):
                    try:
                        cur1.execute("delete from {0} where channelid like '{1}';".format(tblname2,ctx.message.channel.id))
                        sqldb1.commit()
                    except:
                        ReportException()
                        sqldb1.close()
                        await self.bot.say("An error has been reported to the bot's owners.")
                        return
                    await self.bot.say("`{0} will no longer receive Twitch.TV updates.`".format(ctx.message.channel.name))
                    return
        await self.bot.say("`{0} is not currently receiving Twitch.TV updates.".format(ctx.message.channel.name))
        sqldb1.close()
        return

    @commands.command(pass_context=True)
    async def twitchList(self,ctx):
        """Lists the Twitch.TV streams being watched in this server.

        Usage: ori.twitchList"""
        try:
            sqldb1 = MS.connect(host=sqlHost,user=sqlUser,passwd=sqlPass,db=dbname1)
            cur1 = sqldb1.cursor()
            cur1.execute("select * from {0}".format(tblname1))
        except:
            ReportException()
            try:
                sqldb1.close()
            except:
                pass
            await self.bot.say("An error has been reported to the bot's owners.")
            return
        compmsg = ""
        for username,adddate,addedby,serverid in cur1:
            if str(ctx.message.server.id) == str(serverid):
                sqladdby = ctx.message.server.get_member(addedby)
                if sqladdby == None:
                    sqladdby = 'NULL'
                whenadd = datetime.datetime.strftime(adddate,"%a, %b %d, %Y %I:%M:%S %p")
                compmsg = "{0}Add Date: {1}, Username: {2}, Added By: <@{3}>\n".format(compmsg,whenadd,username,addedby)
                if len(compmsg) > 1500:
                    await self.bot.say(compmsg)
                    compmsg = ""
        await self.bot.say(compmsg)
        return
#----------------------------------------------------------------------------------------------------
def setup(bot):
    bot.add_cog(Twitch(bot))
