import random
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

default_temperature = 0.7
current_temperature = default_temperature

reading_prefix_1 = "Pretend you are a wise old witch doing a tarot reading. I will pull a three card tarot spread from the deck \
and you will interpret it for me, speaking as a withered old crone. Here is my spread: \n"

general_prefix_1 = "Pretend you are a wise old witch. Respond to the following message as if you are a withered\
    old crone: \n"

reading_prefix_2 = "Pretend you are a beautiful young witch doing a tarot reading. I will pull a three card tarot spread from the deck \
and you will interpret it for me, speaking in a seductive and mysterious tone. Here is my spread: \n"

general_prefix_2 = "Pretend you are a beautiful young witch. Respond to the following message in a\
    seductive and mysterious tone: \n"

current_persona = 2
reading_prefix = reading_prefix_2
general_prefix = general_prefix_2

def three_card_spread():
    suits = ['cups', 'pentacles', 'swords', 'wands']
    minor_arcana = [f'{i} of {suit}' for suit in suits for i in range(1, 11)] + \
                   [f'{rank} of {suit}' for suit in suits for rank in ['page', 'knight', 'queen', 'king']]

    major_arcana = ['the fool', 'the magician', 'the high priestess', 'the empress', 'the emperor',
                    'the hierophant', 'the lovers', 'the chariot', 'strength', 'the hermit',
                    'wheel of fortune', 'justice', 'the hanged man', 'death', 'temperance',
                    'the devil', 'the tower', 'the star', 'the moon', 'the sun', 'judgment', 'the world']

    tarot_deck = minor_arcana + major_arcana
    random.shuffle(tarot_deck)

    return [tarot_deck.pop() for _ in range(3)]

async def generate_response(prompt, temperature=current_temperature):
    response = openai.Completion.create(
        engine="text-davinci-003",  # Use your desired model, e.g., "text-davinci-002", "text-curie", etc.
        prompt=prompt,
        max_tokens=999,
        n=1,
        stop=None,
        temperature=temperature,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )
    return response.choices[0].text.strip()

@bot.command(name="read_tarot")
async def tarot_reading(ctx):
    spread = three_card_spread()
    prompt = reading_prefix + str(spread)
    response = await generate_response(prompt)
    output = "Your spread:\n" + str(spread) + "\n\n" + response
    await ctx.send(output)

@bot.command
async def pull_spread(ctx):
    pass

@bot.command()
async def update_temperature(ctx, temperature):
    global current_temperature
    if temperature >= current_temperature:
        current_temperature = temperature
        await ctx.send(f"Cauldron heated up to: ```{temperature}```")
    else:
        current_temperature = temperature
        await ctx.send(f"Cauldron cooled down to: ```{temperature}```")

@bot.command(name="show_temperature")
async def show_current_temperature(ctx):
    global current_temperature
    await ctx.send(f"The current temperature of the cauldron is: ```{current_temperature}```")

@bot.command()
async def change_persona(ctx):
    global current_persona
    global reading_prefix
    global general_prefix
    if current_persona == 1:
        current_persona = 2
        reading_prefix, general_prefix = reading_prefix_2, general_prefix_2
        await ctx.send("You are now speaking to the princess...")
    else:
        current_persona = 1
        reading_prefix, general_prefix = reading_prefix_1, general_prefix_1
        await ctx.send("You are now speaking to the crone...")

@bot.event
async def on_message(message):
    #add conversational memory ... langchain? 
    if message.author == bot.user:
        return

    if bot.user.mentioned_in(message):
        text = general_prefix + message.content
        prompt = f"{message.author.name}: {text}"
        response = await generate_response(prompt)
        await message.channel.send(response)
    else:
        await bot.process_commands(message)

@bot.event
async def on_ready():
    print(f"logged into Discord as {bot.user}")
    activity = discord.Game(name="witchcraft", type=3)
    await bot.change_presence(status=discord.Status.online, activity=activity)

bot.run(DISCORD_TOKEN)
