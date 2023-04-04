import discord
from discord.ext import commands
import openai
import os
from dotenv import load_dotenv

# Load Discord token and OpenAI API key from .env file
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Set up OpenAI API client
openai.api_key = OPENAI_API_KEY

# Create a new bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="$", intents=intents)

async def generate_response(prompt, temperature=0.5):
    response = openai.Completion.create(
        engine="text-davinci-002",  # Use your desired model, e.g., "text-davinci-002", "text-curie", etc.
        prompt=prompt,
        max_tokens=50,
        n=1,
        stop=None,
        temperature=temperature,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    return response.choices[0].text.strip()

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if bot.user.mentioned_in(message):
        prompt = f"{message.author.name}: {message.content}"
        response = await generate_response(prompt)
        await message.channel.send(response)
    else:
        await bot.process_commands(message)

@bot.event
async def on_ready():
    print(f"Logged into Discord as {bot.user}")
    activity = discord.Game(name="Generating text with OpenAI API", type=3)
    await bot.change_presence(status=discord.Status.online, activity=activity)

bot.run(DISCORD_TOKEN)
