#!/usr/bin/env python3
import asyncio, datetime, discord, discord.utils, json, linecache, multiprocessing, pytz, sys, threading, twitter
from discord.ext import commands
from printoverride import print
import MySQLdb as MS
#----------------------------------------------------------------------------------------------------
try:
    with open('./waifu.json', 'r+') as secretfile:
        sec = json.load(secretfile)
        sqlHost = sec['SQL']['sqlHost']
        sqlUser = sec['SQL']['sqlUser']
        sqlPass = sec['SQL']['sqlPass']
        dbname1 = sec['tweeter']['dbname1']
        tblname1 = sec['tweeter']['tblname1']
        tblname2 = sec['tweeter']['tblname2']
        consumerkey = sec['tweeter']['consumerkey']
        consumersecret = sec['tweeter']['consumersecret']
        accesstokenkey = sec['tweeter']['accesstokenkey']
        accesstokensecret = sec['tweeter']['accesstokensecret']
except FileNotFoundError:
    exit("waifu.json is not in the current bot directory.")
twitapi = twitter.Api(consumer_key=consumerkey,
          consumer_secret=consumersecret,
          access_token_key=accesstokenkey,
          access_token_secret=accesstokensecret)
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
                sqlcmd1 = cur1.execute("create table {0} (adddate DATETIME, username VARCHAR(20), lasttweet DATETIME, addedby VARCHAR(20), serverid bigint(20))".format(tblname1))
                sqlcmd1 = cur1.execute("create table {0} (adddate DATETIME, channelid BIGINT, addedby VARCHAR(20))".format(tblname2))
                return "MySQL: Created database '{0}' and tables '{1}', '{2}'.".format(dbname1,tblname1,tblname2)
        sqlcmd1 = cur1.execute("use {0}".format(dbname1))
        cur1.execute("select count(*) from information_schema.tables where table_name = '{0}' and table_schema = '{1}'".format(tblname1,dbname1))
        if cur1.fetchone()[0] < 1:
            sqlcmd1 = cur1.execute("create table {0} (adddate DATETIME, username VARCHAR(20), lasttweet DATETIME, addedby VARCHAR(20))".format(tblname1))
        cur1.execute("select count(*) from information_schema.tables where table_name = '{0}' and table_schema = '{1}'".format(tblname2,dbname1))
        if cur1.fetchone()[0] < 1:
            sqlcmd1 = cur1.execute("create table {0} (adddate DATETIME, addedby VARCHAR(20), channelid BIGINT)".format(tblname2))
        return "MySQL: Database '{0}' and tables '{1}', '{2}' exist.".format(dbname1,tblname1,tblname2)
    except:
        return "MySQL: {0}".format(ReportException())

def TwitterLogin():
    global twitinfo
    try:
        twitinfo = twitapi.VerifyCredentials()
    except:
        return "Twitter: {0}".format(ReportException())
    return "Twitter: Logged in as {0}.".format(twitinfo.screen_name)

def is_owner_check(message):
    return message.author.id == "107270310344024064"

def is_owner():
    return commands.check(lambda ctx: is_owner_check(ctx.message))
#----------------------------------------------------------------------------------------------------
class Twitter():
    def __init__(self,bot):
        self.bot = bot
        print(TwitterLogin())
        print(SQLSetup())
        self.bot.loop.create_task(self.sendupdatecheck())

    async def sendupdatecheck(self):
        global twitdelay
        await self.bot.wait_until_ready()
        while not self.bot.is_closed:
            try:
                sqldb1 = MS.connect(host=sqlHost,user=sqlUser,passwd=sqlPass,db=dbname1)
                cur1 = sqldb1.cursor()
                cur1.execute("select username,lasttweet,serverid from {0}".format(tblname1))
                cur2 = sqldb1.cursor()
                cur2.execute("select channelid from {0}".format(tblname2))
                cur3 = sqldb1.cursor()
                cur4 = sqldb1.cursor()
                cur4.execute("select count(*) from {0}".format(tblname1))
                dbTotal = cur4.fetchone()[0]
                if dbTotal <= 0:
                    dbTotal = 1
                #await self.bot.send_message(discord.Object(id=289158431213092865),"{0}".format(cur4.fetchone()[0]))
                for username,tweetdate,serverid in cur1:
                    status = twitapi.GetUserTimeline(screen_name=username,count=200,include_rts=False,exclude_replies=True)
                    preConvTwitTime = datetime.datetime.strptime(status[0].created_at,"%a %b %d %H:%M:%S %z %Y").replace(tzinfo = pytz.FixedOffset(+0000)).astimezone(pytz.timezone('America/New_York'))
                    convTwitTime = datetime.datetime.strftime(preConvTwitTime,"%Y-%m-%d %H:%M:%S")
                    if str(tweetdate) != str(convTwitTime):
                        cur3.execute("update {0} set lasttweet='{1}' where username='{2}';".format(tblname1,convTwitTime,username))
                        convTwitTime = datetime.datetime.strftime(preConvTwitTime,"%a, %b %d, %Y %I:%M:%S %p")
                        readyit = discord.Embed(title="{0} (@{1})".format(status[0].user.name,status[0].user.screen_name),colour=int(hex(int(status[0].user.profile_background_color,16)),16), \
                                                url="https://www.twitter.com/{0}/status/{1}".format(status[0].user.screen_name,status[0].id_str), description="{0}".format(status[0].text))
                        readyit.set_thumbnail(url=status[0].user.profile_image_url)
                        readyit.set_footer(text="\U0001F4E2 {0} \U00002764 {1} | {2}".format(status[0].retweet_count,status[0].favorite_count,convTwitTime))
                        try:
                            for entry in status[0].media:
                                if entry.type == "photo":
                                    readyit.set_image(url=entry.media_url)
                        except:
                            pass
                        for server in self.bot.servers:
                            for channel in server.channels:
                                for row in cur2:
                                    for postchanid in row:
                                        if str(server.id) == str(serverid) and str(channel.id) == str(postchanid):
                                            sendit = await self.bot.send_message(discord.Object(id=postchanid),embed=readyit)
                                            await asyncio.sleep(3.5)
                sqldb1.commit()
            except Exception as e:
                error = ReportException()
                if 'Over capacity' in error:
                    twitdelay += 10
                    await self.bot.send_message(discord.Object(id=289158431213092865),"`Twitter: Woops! Rate limit reached. Increasing delay from {0} to {1}.`".format(twitdelay-10,twitdelay))
                    print("Twitter: Rate limit reached, increased to {0}.".format(twitdelay))
                else:
                    await self.bot.send_message(discord.Object(id=289158431213092865),"{0}".format(error))
                    await self.bot.send_message(discord.Object(id=289158431213092865),"{0}".format(e))
            await asyncio.sleep((900 + (dbTotal * 3.5)) / dbTotal)
        #self.bot.loop.call_later(twitdelay,self.readyupdatecheck)

    @commands.command(pass_context=True,hidden=True)
    @is_owner()
    async def tweet(self,ctx,*,msg : str):
        """Send a Tweet from the owner's Twitter account!"""
        try:
            post_update = twitapi.PostUpdate(msg)
            await self.bot.say("`Posted to {0}'s Twitter:` {1}".format(twitinfo.screen_name,msg))
        except:
            await self.bot.say("`Could not post. Probably a duplicate tweet.`")
        return

################################################################################################################################
# List of Twitter substrings.                                                                                                  #
################################################################################################################################
# status = twitapi.GetUserTimeline(screen_name=msg,count=1)                                                                    #
# NOTE: The 'count=1' means we're pulling the first tweet.                                                                     #
################################################################################################################################
# NOTE: There are more commands then listed here, but are largely not useful, so they've been removed. Use status[0] to see.   #
# NOTE: The [0] below is because it's a list, and we're pulling the only entry of that list.                                   #
################################################################################################################################
# status[0] > This is everything. Useful for debugging.                                                                        #
# status[0].user > Displays all user information for the tweet. Useful for debugging.                                          #
# status[0].user_mentions > Displays all user mention information. Useful for debugging.                                       #
################################################################################################################################
# status[0].created_at > This shows when the tweet was posted.                                                                 #
# status[0].id_str > Provides tweet ID as a string - useful for making links.                                                  #
# status[0].lang > Shows the abbreviated language the tweet is in.                                                             #
# status[0].text > Provides the text of the tweet. Most helpful of anything here.                                              #
################################################################################################################################
# status[0].user.name > Real name, or at least the name they entered. Not their Twitter handle.                                #
# status[0].user.profile_background_color > Returns the background color of their profile page. Not useful... Maybe?           #
# status[0].user.profile_background_image_url > Returns the background image of their profile, if any. Not useful... Maybe?    #
# status[0].user.profile_banner_url > Returns the upper banner url, if any. Not useful... Maybe?                               #
# status[0].user.profile_image_url > Returns the url for profile picture. This is useful for embeds.                           #
# status[0].user.screen_name > Returns username. Not useful as we're calling them via username, lolol.                         #
# status[0].user.utc_offset > Offset of +00000, maybe useful - doubt it.                                                       #
################################################################################################################################

    @commands.command(pass_context=True)
    @is_owner()
    async def twitadd(self,ctx,*,msg : str):
        """Add a Twitter username to the watchlist."""
        try:
            sqldb1 = MS.connect(host=sqlHost,user=sqlUser,passwd=sqlPass,db=dbname1)
            cur1 = sqldb1.cursor()
            try:
                cur1.execute("select * from {0};".format(tblname1))
                msg = msg.lower()
                for row in cur1:
                    if row[1] == msg and str(row[4]) == str(ctx.message.server.id):
                        sqladdby = ctx.message.server.get_member(row[3])
                        if sqladdby == None:
                            sqladdby = 'NULL'
                        whenadd = datetime.datetime.strftime(row[0],"%a, %b %d, %Y %I:%M:%S %p")
                        await self.bot.say("`{0} was already added by {1} on {2} (US/EST).`".format(msg.title(),sqladdby,whenadd))
                        sqldb1.close()
                        return
                try:
                    try:
                        status = twitapi.GetUserTimeline(screen_name=msg,count=200,include_rts=False,exclude_replies=True)
                    except:
                        await self.bot.say("`User {0} does not appear to exist on Twitter.`".format(msg))
                    preConvTwitTime = datetime.datetime.strptime(status[0].created_at,"%a %b %d %H:%M:%S %z %Y")\
                                      .replace(tzinfo=pytz.FixedOffset(+0000)).astimezone(pytz.timezone('America/New_York'))
                    convTwitTime = datetime.datetime.strftime(preConvTwitTime,"%Y-%m-%d %H:%M:%S")
                    convCurTime = str(datetime.datetime.now())
                    convCurTime = convCurTime[:-7]
                    cur1.execute("insert into watchlist values ('{0}','{1}','{2}','{3}','{4}')".format(convCurTime,msg.lower(),convTwitTime,ctx.message.author.id,ctx.message.server.id))
                    sqldb1.commit()
                    convTwitTime = datetime.datetime.strftime(preConvTwitTime,"%a, %b %d, %Y %I:%M:%S %p")
                    readyit = discord.Embed(title="{0} (@{1})".format(status[0].user.name,status[0].user.screen_name),colour=int(hex(int(status[0].user.profile_background_color,16)),16), \
                                            url="https://www.twitter.com/{0}/status/{1}".format(status[0].user.screen_name,status[0].id_str),description="{0}".format(status[0].text))
                    readyit.set_thumbnail(url=status[0].user.profile_image_url)
                    readyit.set_footer(text="\U0001F4E2 {0} \U00002764 {1} | {2}".format(status[0].retweet_count,status[0].favorite_count,convTwitTime))
                    try:
                        for i in status[0].media:
                            if i.type == "photo":
                                readyit.set_image(url=i.media_url)
                    except:
                        pass
                    await self.bot.say("`Added {0} (@{1}).`".format(status[0].user.name,status[0].user.screen_name))
                    sendit = await self.bot.send_message(ctx.message.channel,embed=readyit)
                    return
                except:
                    await self.bot.say("`Lv3`\n{0}".format(ReportException()))
            except:
                await self.bot.say("`Lv2`\n{0}".format(ReportException()))
        except:
            await self.bot.say("`Lv1`\n{0}".format(ReportException()))
        sqldb1.close()
        return

    @commands.command(pass_context=True)
    @is_owner()
    async def twitrem(self,ctx,*,msg : str):
        """Remove a Twitter username from the watchlist."""
        try:
            sqldb1 = MS.connect(host=sqlHost,user=sqlUser,passwd=sqlPass,db=dbname1)
            cur1 = sqldb1.cursor()
            cur1.execute("select username,serverid from {0};".format(tblname1))
            msg = msg.lower()
            for username,serverid in cur1:
                if str(username) == str(msg) and str(serverid) == str(ctx.message.server.id):
                    cur1.execute("delete from {0} where username like '{1}' and serverid like '{2}';".format(tblname1,msg,ctx.message.server.id))
                    sqldb1.commit()
                    status = twitapi.GetUserTimeline(screen_name=msg)
                    await self.bot.say("`Removed {0} (@{1}).`".format(status[0].user.name,status[0].user.screen_name))
                    return
#            for row in cur1:
#                for username in row:
#                    if username == msg:
#                        cur1.execute("delete from {0} where username like '{1}';".format(tblname1,msg))
#                        sqldb1.commit()
#                        status = twitapi.GetUserTimeline(screen_name=msg)
#                        await self.bot.say("`Removed {0} (@{1}).`".format(status[0].user.name,status[0].user.screen_name))
#                        return
            sqldb1.close()
            await self.bot.say("`{0} is not currently being followed on Twitter.`".format(msg.title()))
        except:
            await self.bot.say(ReportException())
        return

    @commands.command(pass_context=True)
    @is_owner()
    async def tchadd(self,ctx):
        """Add a channel to receive tweet updates."""
        try:
            sqldb1 = MS.connect(host=sqlHost,user=sqlUser,passwd=sqlPass,db=dbname1)
            cur1 = sqldb1.cursor()
            try:
                cur1.execute("select * from {0};".format(tblname2))
                for adddate,channelid,addedby in cur1:
                    if str(channelid) == str(ctx.message.channel.id):
                        sqladdby = ctx.message.server.get_member(addedby)
                        if sqladdby == None:
                            sqladdby = 'NULL'
                        whenadd = datetime.datetime.strftime(adddate,"%a, %b %d, %Y %I:%M:%S %p")
                        await self.bot.say("`{0} was already added by {1} on {2} (US/EST).`".format(ctx.message.channel.name,sqladdby,whenadd))
                        sqldb1.close()
                        return
            except:
                await self.bot.say(ReportException())
            try:
                convCurTime = str(datetime.datetime.now())
                convCurTime = convCurTime[:-7]
                cur1.execute("insert into channel values ('{0}','{1}','{2}')".format(convCurTime,ctx.message.channel.id,ctx.message.author.id))
                sqldb1.commit()
                await self.bot.say("`{0} will now receive Twitter updates.`".format(ctx.message.channel.name))
            except:
                await self.bot.say(ReportException())
        except:
            await self.bot.say(ReportException())
        sqldb1.close()
        return

    @commands.command(pass_context=True)
    @is_owner()
    async def tchrem(self,ctx):
        """Remove a channel from receving tweet updates."""
        try:
            sqldb1 = MS.connect(host=sqlHost,user=sqlUser,passwd=sqlPass,db=dbname1)
            cur1 = sqldb1.cursor()
            cur1.execute("select channelid from {0};".format(tblname2))
            for row in cur1:
                for channelid in row:
                    if str(channelid) == str(ctx.message.channel.id):
                        cur1.execute("delete from {0} where channelid like '{1}';".format(tblname2,ctx.message.channel.id))
                        sqldb1.commit()
                        await self.bot.say("`{0} will no longer receive Twitter updates.`".format(ctx.message.channel.name))
                        return
            await self.bot.say("`{0} is not currently receiving Twitter updates.`".format(ctx.message.channel.name))
        except:
            await self.bot.say(ReportException())
        sqldb1.close()
        return

    @commands.command(pass_context=True)
    @is_owner()
    async def tlist(self,ctx):
        """Lists the current Twitter accounts being followed."""
        try:
            sqldb1 = MS.connect(host=sqlHost,user=sqlUser,passwd=sqlPass,db=dbname1)
            cur1 = sqldb1.cursor()
            cur1.execute("select username from {0};".format(tblname1))
            compiled = ""
            for row in cur1:
                for username in row:
                    compiled = "{0}@{1}, ".format(compiled,username)
            compiled = compiled[:-2]
            await self.bot.say("`Currently watched Twitter accounts:` {0}".format(compiled))
        except:
            await self.bot.say(ReportException())
        sqldb1.close()
        return
#----------------------------------------------------------------------------------------------------
def setup(bot):
    bot.add_cog(Twitter(bot))
