import discord
import time
import datetime

def get_channel(channels, channel_name):
    for channel in client.get_all_channels():
        # print(channel)
        if channel.name == channel_name:
            return channel
    return None

client = discord.Client()
count = 0

@client.event
async def on_ready():
    global count
    general_channel = get_channel(client.get_all_channels(), 'normal2')

    c_time = time.localtime()
    tday = c_time.tm_wday
    thour = c_time.tm_hour
    tmin = c_time.tm_min
    tsec = c_time.tm_sec

    print(tsec)
    # await general_channel.send("hhel2lo")
    print("ready")
    count = count + 1

    game = discord.Game("상태메시지")
    await client.change_presence(status=discord.Status.online, activity=game)

@client.event
async def on_message(message):
    if message.content.startswith("!안녕"):
        await message.channel.send("안녕하세요")

    if message.content.startswith("!안녕2"):
        await message.channel.send("안녕하세요2")

client.run("NzExMjQzMDk0MTA4MTQzNjM3.XsALUg.HKEf9XASf9vMf9DuATxyDTqhmgY")