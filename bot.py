import asyncio
import http.client
import os
import discord
from discord.ext import commands
from urllib.parse import quote
from dotenv import load_dotenv


class Audio:
	def __init__(self, src="", hl="en-us", v="John", r="0"):
		self.src = src
		self.hl = hl
		self.v = v
		self.r = r

		self.TTS_key = os.getenv('TTS_KEY')
		self.Base_URL = "api.voicerss.org"
		self.f = "48khz_16bit_stereo"
		self.c = "MP3"
		self.filename = "output.mp3"

	async def grabAudio(self):
		options = "/?key={0}&src={1}&hl={2}&c={3}&v={4}&f={5}&r={6}".format(self.TTS_key, self.src, self.hl, self.c, self.v, self.f, self.r)
		conn = http.client.HTTPSConnection(self.Base_URL)
		conn.request("GET", options)
		res = conn.getresponse()
		data = res.read()

		# Saves response as mp3 file
		file = open(self.filename, 'wb')
		file.write(data)
		file.close()

		return self.filename

	async def setVoice(self, voice):
		self.v = voice

	async def setRate(self, rate):
		self.r = rate

	async def setSrc(self, text):
		self.src = quote(text)

	async def setHL(self, lang):
		self.hl = lang


# Load token for discord api
load_dotenv()
Token = os.getenv('DISCORD_TOKEN')

speech = Audio()

# bot options
bot = commands.Bot(command_prefix='$')

# Prints when bot has connected to the discord
@bot.event
async def on_ready():
	print(f'{bot.user} has connected to Discord')

# Command to change voice
@bot.command(name="setvoice", help="Set the voice")
async def setVoice(ctx, voice):
	try:
		await speech.setVoice(voice)
		await ctx.send("Voice changed to " + voice)
	except:
		await ctx.send("Error: Voice does not exist")

# Command to change language
@bot.command(name="setlang", help="Set the language")
async def setLang(ctx, lang):
	try:
		await speech.setHL(lang)
		await ctx.send("Language changed to " + lang)
	except:
		await ctx.send("Error: Langauge does not exist")

# Command to change speech rate
@bot.command(name="setrate", help="Set the rate of speech")
async def setRate(ctx, rate):
	rate = int(rate)
	if rate > -11 and rate < 11:
		await speech.setRate(rate)
		await ctx.send("Speech rate changed to " + str(rate))
	else:
		await ctx.send("Error: Rate must be between -10 and 10")

# Command to change all options to default
@bot.command(name="setdefault", help="Set all options to defualt values")
async def setDefualt(ctx):
	try:
		await speech.setHL("en-us")
		await speech.setRate(0)
		await speech.setVoice("John")
		await ctx.send("Default options applied")
	except:
		await ctx.send("Error: Failed to set defualt values")

# todo: Add command to print menu of voices/langauges?

# todo: Convert to slash commands?

# Takes text and plays it through voice channel
@bot.command(name='tts', help='Text-To-Speech')
async def tts(ctx, *, text):
	'''Takes text input, converts it to TTS and then plays
		the resulting mp3 file in the voice channel of the
		user who made the command'''
	
	# Convert text to tts
	await speech.setSrc(text)
	filename = await speech.grabAudio()

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
