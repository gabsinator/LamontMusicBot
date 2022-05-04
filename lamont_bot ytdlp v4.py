#lamont discord bot

import asyncio
import os
import random
import nacl
import validators

import discord
from discord.ext import commands, tasks

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

import urllib.parse as p
import re
import pickle

import yt_dlp
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]

client = discord.Client()
bot = commands.Bot(command_prefix= "!")

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '/songs/%(title)s.%(ext)s',
    'restrictfilenames': True,
    'nooverwrites': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

ffmpeg_options = {
    "options": "-vn"
}

ytdl = yt_dlp.YoutubeDL(ytdl_format_options)

queue = []

#tictactoe vars
tictactoe_mode = False

turn = 1

player1 = ""
player2 = ""

topleft_state = [False, ""]
topmid_state = [False, ""]
topright_state = [False, ""]
left_state = [False, ""]
mid_state = [False, ""]
right_state = [False, ""]
botleft_state = [False, ""]
botmid_state = [False, ""]
botright_state = [False, ""]

list_of_lists = [
    topleft_state,
    topmid_state,
    topright_state,
    left_state,
    mid_state,
    right_state,
    botleft_state,
    botmid_state,
    botright_state,
]

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.2):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get("title")
        self.url = ""

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        if "entries" in data:
            data = data["entries"][0]
        filename = data["title"] if stream else ytdl.prepare_filename(data)
        return filename

def youtube_authenticate():
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
    api_service_name = "youtube"
    api_version = "v3"
    client_secrets_file = "yt_api_creds.json"
    creds = None

    # the file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time

    if os.path.exists("token2.pickle"):
        with open("token2.pickle", "rb") as token:
            creds = pickle.load(token)

    # if there are no (valid) credentials availablle, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file, SCOPES)
            creds = flow.run_local_server(port=0)

        # save the credentials for the next run
        with open("token2.pickle", "wb") as token:
            pickle.dump(creds, token)

    return build(api_service_name, api_version, credentials=creds)

#code for tictactoe mode

@bot.command(name= "tictactoe")
async def tictactoe(ctx):
    global tictactoe_mode

    if tictactoe_mode == False:
        tictactoe_mode = True
        #declaring tictactoe vars
            
        print("tictactoe mode enabled")
        await ctx.send("tictactoe mod now enabled!")
    else:
        set_tictactoe_vars()
        print("tictactoe mode disabled")
        await ctx.send("tictactoe mode now disabled.")

def set_tictactoe_vars():
    global tictactoe_mode

    global turn
    global player1
    global player2

    tictactoe_mode = False

    turn = 1

    player1 = ""
    player2 = ""

    for i in list_of_lists:
        i[0] = False
        i[1] = ""
    print("tictactoe vars reset")

async def check_win(ctx):

    global turn

    if topleft_state[0] == topmid_state[0] == topright_state[0] == True and topleft_state[1] == topmid_state[1] == topright_state[1]:
        await ctx.send("{0} won the game! congrats".format(topleft_state[1]))
        await draw_game(ctx)
        set_tictactoe_vars()
        return True

    elif left_state[0] == mid_state[0] == right_state[0] == True and left_state[1] == mid_state[1] == right_state[1]:
        await ctx.send("{0} won the game! congrats".format(left_state[1]))
        await draw_game(ctx)
        set_tictactoe_vars()
        return True

    elif botleft_state[0] == botmid_state[0] == botright_state[0] == True and botleft_state[1] == botmid_state[1] == botright_state[1]:
        await ctx.send("{0} won the game! congrats".format(botleft_state[1]))
        await draw_game(ctx)
        set_tictactoe_vars()
        return True

    elif topleft_state[0] == left_state[0] == botleft_state[0] == True and topleft_state[1] == left_state[1] == botleft_state[1]:
        await ctx.send("{0} won the game! congrats".format(topleft_state[1]))
        await draw_game(ctx)
        set_tictactoe_vars()
        return True

    elif topmid_state[0] == mid_state[0] == botmid_state[0] == True and topmid_state[1] == mid_state[1] == botmid_state[1]:
        await ctx.send("{0} won the game! congrats".format(topmid_state[1]))
        await draw_game(ctx)
        set_tictactoe_vars()
        return True

    elif topright_state[0] == right_state[0] == botright_state[0] == True and topright_state[1] == right_state[1] == botright_state[1]:
        await ctx.send("{0} won the game! congrats".format(topright_state[1]))
        await draw_game(ctx)
        set_tictactoe_vars()
        return True

    elif topleft_state[0] == mid_state[0] == botright_state[0] == True and topleft_state[1] == mid_state[1] == botright_state[1]:
        await ctx.send("{0} won the game! congrats".format(topleft_state[1]))
        await draw_game(ctx)
        set_tictactoe_vars()
        return True

    elif topright_state[0] == mid_state[0] == botleft_state[0] == True and topright_state[1] == mid_state[1] == botleft_state[1]:
        await ctx.send("{0} won the game! congrats".format(topright_state[1]))
        await draw_game(ctx)
        set_tictactoe_vars()
        return True

    else:
        turn += 1
        await draw_game(ctx)
        return False

#draw game
async def draw_game(ctx):
    global player1
    global player2

    global topleft_state
    global topmid_state
    global topright_state
    global left_state
    global mid_state
    global right_state
    global botleft_state
    global botmid_state
    global botright_state

    a1 = ""
    a2 = ""
    a3 = ""

    b1 = ""
    b2 = ""
    b3 = ""

    c1 = ""
    c2 = ""
    c3 = ""

    not_used = "⬜"

    p1 = "🟥"
    p2 = "🟦"

#check and draw 1st row
    if topleft_state[0] == True:
        if topleft_state[1] == player1:
            a1 = p1
        elif topleft_state[1] == player2:
            a1 = p2
    else:
        a1 = not_used

    if topmid_state[0] == True:
        if topmid_state[1] == player1:
            a2 = p1
        elif topmid_state[1] == player2:
            a2 = p2
    else:
        a2 = not_used

    if topright_state[0] == True:
        if topright_state[1] == player1:
            a3 = p1
        elif topright_state[1] == player2:
            a3 = p2
    else:
        a3 = not_used

#check and draw 2nd row
    if left_state[0] == True:
        if left_state[1] == player1:
            b1 = p1
        elif left_state[1] == player2:
            b1 = p2
    else:
        b1 = not_used

    if mid_state[0] == True:
        if mid_state[1] == player1:
            b2 = p1
        elif mid_state[1] == player2:
            b2 = p2
    else:
        b2 = not_used

    if right_state[0] == True:
        if right_state[1] == player1:
            b3 = p1
        elif right_state[1] == player2:
            b3 = p2
    else:
        b3 = not_used

#check and draw 3rd row
    if botleft_state[0] == True:
        if botleft_state[1] == player1:
            c1 = p1
        elif botleft_state[1] == player2:
            c1 = p2
    else:
        c1 = not_used

    if botmid_state[0] == True:
        if botmid_state[1] == player1:
            c2 = p1
        elif botmid_state[1] == player2:
            c2 = p2
    else:
        c2 = not_used

    if botright_state[0] == True:
        if botright_state[1] == player1:
            c3 = p1
        elif botright_state[1] == player2:
            c3 = p2
    else:
        c3 = not_used

#send message with playfield to discord
    await ctx.send(
        "{0}{1}{2}\n{3}{4}{5}\n{6}{7}{8}".format(a1, a2, a3,
                                                b1, b2, b3,
                                                c1, c2, c3
                                                )
    )


@bot.command(name="topleft")
async def topleft(ctx):
    global tictactoe_mode
    global topleft_state
    global turn
    global player1
    global player2

    author = ctx.message.author.name

    if tictactoe_mode and not topleft_state[0]:

        #turn += 1

        if turn == 1:
            player1 = author
        elif turn == 2:
            if player1 == author:
                await ctx.send("not ur turn")
            else:
                player2 = author

        if (turn % 2) == 0 and player2 == author:
            topleft_state[0] = True
            topleft_state[1] = author
            if not await check_win(ctx) == True:
                await ctx.send("topleft")
        
        elif (turn % 2) != 0 and player1 == author:
            topleft_state[0] = True
            topleft_state[1] = author
            if not await check_win(ctx) == True:
                await ctx.send("topleft")
        else:
            await ctx.send("not ur turn")

        print(turn, player1, player2, topleft_state)

    elif topleft_state[0]:
        await ctx.send("space already taken by {0}".format(topleft_state[1]))
    else:
        pass

@bot.command(name="topmid")
async def topmid(ctx):
    global tictactoe_mode
    global topmid_state
    global turn
    global player1
    global player2

    author = ctx.message.author.name

    if tictactoe_mode and not topmid_state[0]:

        #turn += 1

        if turn == 1:
            player1 = author
        elif turn == 2:
            if player1 == author:
                await ctx.send("not ur turn")
            else:
                if player1 == author:
                    await ctx.send("not ur turn")
                else:
                    player2 = author

        if (turn % 2) == 0 and player2 == author:
            topmid_state[0] = True
            topmid_state[1] = author
            if not await check_win(ctx) == True:
                await ctx.send("topmid")
        
        elif (turn % 2) != 0 and player1 == author:
            topmid_state[0] = True
            topmid_state[1] = author
            if not await check_win(ctx) == True:
                await ctx.send("topmid")
        else:
            await ctx.send("not ur turn")

        print(turn, player1, player2, topmid_state)

    elif topmid_state[0]:
        await ctx.send("space already taken by {0}".format(topmid_state[1]))
    else:
        pass


@bot.command(name="topright")
async def topright(ctx):
    global tictactoe_mode
    global topright_state
    global turn
    global player1
    global player2

    author = ctx.message.author.name

    if tictactoe_mode and not topright_state[0]:

        #turn += 1

        if turn == 1:
            player1 = author
        elif turn == 2:
            if player1 == author:
                await ctx.send("not ur turn")
            else:
                player2 = author

        if (turn % 2) == 0 and player2 == author:
            topright_state[0] = True
            topright_state[1] = author
            if not await check_win(ctx) == True:
                await ctx.send("topright")
        
        elif (turn % 2) != 0 and player1 == author:
            topright_state[0] = True
            topright_state[1] = author
            if not await check_win(ctx) == True:
                await ctx.send("topright")
        else:
            await ctx.send("not ur turn")

        print(turn, player1, player2, topright_state)

    elif topright_state[0]:
        await ctx.send("space already taken by {0}".format(topright_state[1]))
    else:
        pass


@bot.command(name="left")
async def left(ctx):
    global tictactoe_mode
    global left_state
    global turn
    global player1
    global player2

    author = ctx.message.author.name

    if tictactoe_mode and not left_state[0]:

        #turn += 1

        if turn == 1:
            player1 = author
        elif turn == 2:
            if player1 == author:
                await ctx.send("not ur turn")
            else:
                player2 = author

        if (turn % 2) == 0 and player2 == author:
            left_state[0] = True
            left_state[1] = author
            if not await check_win(ctx) == True:
                await ctx.send("left")
        
        elif (turn % 2) != 0 and player1 == author:
            left_state[0] = True
            left_state[1] = author
            if not await check_win(ctx) == True:
                await ctx.send("left")
        else:
            await ctx.send("not ur turn")

        print(turn, player1, player2, left_state)

    elif left_state[0]:
        await ctx.send("space already taken by {0}".format(left_state[1]))
    else:
        pass


@bot.command(name="mid")
async def mid(ctx):
    global tictactoe_mode
    global mid_state
    global turn
    global player1
    global player2

    author = ctx.message.author.name

    if tictactoe_mode and not mid_state[0]:

        #turn += 1

        if turn == 1:
            player1 = author
        elif turn == 2:
            if player1 == author:
                await ctx.send("not ur turn")
            else:
                player2 = author

        if (turn % 2) == 0 and player2 == author:
            mid_state[0] = True
            mid_state[1] = author
            if not await check_win(ctx) == True:
                await ctx.send("mid")
        
        elif (turn % 2) != 0 and player1 == author:
            mid_state[0] = True
            mid_state[1] = author
            if not await check_win(ctx) == True:
                await ctx.send("mid")
        else:
            await ctx.send("not ur turn")

        print(turn, player1, player2, mid_state)

    elif mid_state[0]:
        await ctx.send("space already taken by {0}".format(mid_state[1]))
    else:
        pass


@bot.command(name="right")
async def right(ctx):
    global tictactoe_mode
    global right_state
    global turn
    global player1
    global player2

    author = ctx.message.author.name

    if tictactoe_mode and not right_state[0]:

        #turn += 1

        if turn == 1:
            player1 = author
        elif turn == 2:
            if player1 == author:
                await ctx.send("not ur turn")
            else:
                player2 = author

        if (turn % 2) == 0 and player2 == author:
            right_state[0] = True
            right_state[1] = author
            if not await check_win(ctx) == True:
                await ctx.send("right")
        
        elif (turn % 2) != 0 and player1 == author:
            right_state[0] = True
            right_state[1] = author
            if not await check_win(ctx) == True:
                await ctx.send("right")
        else:
            await ctx.send("not ur turn")

        print(turn, player1, player2, right_state)

    elif right_state[0]:
        await ctx.send("space already taken by {0}".format(right_state[1]))
    else:
        pass


@bot.command(name="botleft")
async def botleft(ctx):
    global tictactoe_mode
    global botleft_state
    global turn
    global player1
    global player2

    author = ctx.message.author.name

    if tictactoe_mode and not botleft_state[0]:

        #turn += 1

        if turn == 1:
            player1 = author
        elif turn == 2:
            if player1 == author:
                await ctx.send("not ur turn")
            else:
                player2 = author

        if (turn % 2) == 0 and player2 == author:
            botleft_state[0] = True
            botleft_state[1] = author
            if not await check_win(ctx) == True:
                await ctx.send("botleft")
        
        elif (turn % 2) != 0 and player1 == author:
            botleft_state[0] = True
            botleft_state[1] = author
            if not await check_win(ctx) == True:
                await ctx.send("botleft")
        else:
            await ctx.send("not ur turn")

        print(turn, player1, player2, botleft_state)

    elif botleft_state[0]:
        await ctx.send("space already taken by {0}".format(botleft_state[1]))
    else:
        pass


@bot.command(name="botmid")
async def botmid(ctx):
    global tictactoe_mode
    global botmid_state
    global turn
    global player1
    global player2

    author = ctx.message.author.name

    if tictactoe_mode and not botmid_state[0]:

        #turn += 1

        if turn == 1:
            player1 = author
        elif turn == 2:
            if player1 == author:
                await ctx.send("not ur turn")
            else:
                player2 = author

        if (turn % 2) == 0 and player2 == author:
            botmid_state[0] = True
            botmid_state[1] = author
            if not await check_win(ctx) == True:
                await ctx.send("botmid")
        
        elif (turn % 2) != 0 and player1 == author:
            botmid_state[0] = True
            botmid_state[1] = author
            if not await check_win(ctx) == True:
                await ctx.send("botmid")
        else:
            await ctx.send("not ur turn")

        print(turn, player1, player2, botmid_state)

    elif botmid_state[0]:
        await ctx.send("space already taken by {0}".format(botmid_state[1]))
    else:
        pass


@bot.command(name="botright")
async def botright(ctx):
    global tictactoe_mode
    global botright_state
    global turn
    global player1
    global player2

    author = ctx.message.author.name

    if tictactoe_mode and not botright_state[0]:

        #turn += 1

        if turn == 1:
            player1 = author
        elif turn == 2:
            if player1 == author:
                await ctx.send("not ur turn")
            else:
                player2 = author

        if (turn % 2) == 0 and player2 == author:
            botright_state[0] = True
            botright_state[1] = author
            if not await check_win(ctx) == True:
                await ctx.send("botright")
        
        elif (turn % 2) != 0 and player1 == author:
            botright_state[0] = True
            botright_state[1] = author
            if not await check_win(ctx) == True:
                await ctx.send("botright")
        else:
            await ctx.send("not ur turn")

        print(turn, player1, player2, botright_state)

    elif botright_state[0]:
        await ctx.send("space already taken by {0}".format(botright_state[1]))
    else:
        pass


@bot.command(name="99")
async def nine_nine(ctx):

    brooklyn_99_quotes = [
        'I\'m the human form of the 💯 emoji.',
        'Bingpot!',
        (
            'Cool. Cool cool cool cool cool cool cool, '
            'no doubt no doubt no doubt no doubt.'
        ),
    ]

    response = random.choice(brooklyn_99_quotes)
    await ctx.send(response)

@bot.command(name="join", aliases=["j"])
async def join(ctx):
    if not ctx.message.author.voice:
        await ctx.send("{} is not connected to a voice channel".format(ctx.message.author.name))
        return
    else:
        channel = ctx.message.author.voice.channel
    await channel.connect()


@bot.command(name= "dc")
async def leave(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_connected():
        await ctx.send("bye")
        await voice_client.disconnect()

def queued(ctx):
    if len(queue) > 0:
        server = ctx.message.guild
        voice_channel = server.voice_client

        filename = queue.pop(0)

        voice_channel.play(
            discord.FFmpegPCMAudio(executable="ffmpeg.exe", source=filename),
            after= lambda x=None: queued(ctx)
            )


@bot.command(name="play", aliases=["p"])
async def play(ctx, *url):
    print("play song")
    print(len(url))

    if not ctx.message.author.voice:
        print("not in vc")
        await ctx.send("{} is not connected to a voice channel".format(ctx.message.author.name))
        return

    elif not ctx.message.guild.voice_client:
        await ctx.message.author.voice.channel.connect()

    else:
        pass

    if len(url) > 1:
        entry = ""
        for i in url:
            entry = entry + i + " "
        print(entry)

        print("no valid url: {0}".format(entry))
        youtube = youtube_authenticate() #authenticate request

        request = youtube.search().list(
            part="snippet",
            maxResults=1,
            q=entry
        )
        response = request.execute()

        url = "https://www.youtube.com/watch?v=" + (response["items"][0]["id"]["videoId"])
        print("entry converted to  YT url")
        print(url)

    elif not validators.url(url[0]):
        print("no valid url: {0}".format(url[0]))
        youtube = youtube_authenticate() #authenticate request

        request = youtube.search().list(
            part="snippet",
            maxResults=1,
            q=url[0]
        )
        response = request.execute()

        url = "https://www.youtube.com/watch?v=" + (response["items"][0]["id"]["videoId"])
        print("entry converted to  YT url")
        print(url)

    else:
        print("valid url")
        url = url[0]

    server = ctx.message.guild
    voice_channel = server.voice_client


    

    try:

        if not voice_channel.is_playing():
            async with ctx.typing():
                filename = await YTDLSource.from_url(url, loop=bot.loop)
                voice_channel.play(
                    discord.FFmpegPCMAudio(executable="ffmpeg.exe", source=filename),
                    after= lambda x=None: queued(ctx)
                    )
                await ctx.send("**Now playing:** {0}".format(filename.replace("songs", "")))
        else:
            filename = await YTDLSource.from_url(url, loop=bot.loop)
            queue.append(filename)
            await ctx.send("{0} songs in queue".format(len(queue)))
    
    except:
        await ctx.send("The bot is not connected to a voice channel.")



@bot.command(name="pause")
async def pause(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        voice_client.pause()
    else:
        await ctx.send("The bot is not playing anything at the moment.")

@bot.command(name='resume')
async def resume(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_paused():
        voice_client.resume()
    else:
        await ctx.send("The bot was not playing anything before this.")

@bot.command(name='stop', aliases=["skip", "s"])
async def stop(ctx):
    voice_client = ctx.message.guild.voice_client
    if voice_client.is_playing():
        print("{0} skipped the song".format(ctx.message.author))
        voice_client.stop()
    else:
        await ctx.send("The bot is not playing anything at the moment.")



bot.run(TOKEN)