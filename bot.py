import asyncio
import http.client
import os
import discord
from discord.ext import commands
from urllib.parse import quote
from dotenv import load_dotenv


# Grab and parse audio from voicerss tts api
async def grabAudio(text):
	'''Takes inputed text, parses it and sends it to the voicerss api.
		Saves return as output.mp3 and returns the file name'''

	# Api options config
	TTS_key = "031a73b47f2a4df698665cb2973c2d3c"
	Base_URL = "api.voicerss.org"
	hl = "en-us"
	src = quote(text)
	c = "MP3"
	v = "John"
	f = "48khz_16bit_stereo"
	filename = "output.mp3"

	options = "/?key={0}&src={1}&hl={2}&c={3}&v={4}&f={5}".format(TTS_key, src, hl, c, v, f)

	# Connects to url and reads response
	conn = http.client.HTTPSConnection(Base_URL)
	conn.request("GET", options)
	res = conn.getresponse()
	data = res.read()

	# Saves response as mp3 file
	file = open(filename, 'wb')
	file.write(data)
	file.close()

	return filename

# Load token for discord api
load_dotenv()
Token = os.getenv('DISCORD_TOKEN')

# bot options
bot = commands.Bot(command_prefix='$')

# Prints when bot has connected to the discord
@bot.event
async def on_ready():
	print(f'{bot.user} has connected to Discord')

# Takes text and plays it through voice channel
@bot.command(name='tts', help='Text-To-Speech')
async def tts(ctx, *, text):
	'''Takes text input, converts it to TTS and then plays
		the resulting mp3 file in the voice channel of the
		user who made the command'''
	
	# Convert text to tts
	filename = await grabAudio(text)

	# Connect to the voice channel of the user who called the command
	if not ctx.message.author.voice:
		await ctx.send("{} is not connected to a voice channel".format(ctx.message.author.name))
		return
	else:
		channel = ctx.message.author.voice.channel
	voice_client = await channel.connect()

	# Play tts in voice channel
	source = discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(source=filename), volume=10.0)

	# Disconnect bot from voice channel
	voice_client.play(source=source,
		after=lambda _: asyncio.run_coroutine_threadsafe(
        	coro=voice_client.disconnect(),
        	loop=voice_client.loop
   			).result()
		)

# Run bot
bot.run(Token)
