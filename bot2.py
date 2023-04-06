import random
import discord
from discord.ext import commands
import openai
import os
from dotenv import load_dotenv
from enum import Enum

from langchain.llms import OpenAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts.prompt import PromptTemplate

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

Persona = Enum('Persona', ['PRINCESS', 'CRONE'])
#openai prompts for tarot readings
reading_prefix_crone = "Pretend you are a wise old witch doing a tarot reading. I will pull a three card tarot spread from the deck \
and you will interpret it for me, speaking as a withered old crone. Here is my spread: \n"

general_prefix_crone = "Pretend you are a wise old witch. Respond to the following message as if you are a withered\
    old crone: \n"

reading_prefix_princess = "Pretend you are a beautiful young witch doing a tarot reading. I will pull a three card tarot spread from the deck \
and you will interpret it for me, speaking in a seductive and mysterious tone. Here is my spread: \n"

general_prefix_princess = "Pretend you are a beautiful young witch. Respond to the following message in a\
    seductive and mysterious tone: \n"

current_persona = Persona.PRINCESS
reading_prefix = reading_prefix_princess
general_prefix = general_prefix_princess

#langchain stuff for general conversation
llm = OpenAI(temperature=current_temperature)
princess_template = """The following is a conversation between a lonely traveler and a beautiful young witch. \
The witch is dark, seductive, and mysterious. She seems to possess forbidden knowledge of the occult.

Current conversation:
{history}
Traveler: {input}
Witch:"""

crone_template = """The following is a conversation between a lonely traveler and a withered old crone. \
The crone is a wise and mysterious witch. She seems to possess forbidden knowledge of the occult.

Current conversation:
{history}
Traveler: {input}
Witch:"""

current_template = princess_template

PROMPT = PromptTemplate(
    input_variables=["history", "input"], template=current_template
)
MEMORY = ConversationBufferMemory(human_prefix="Traveler", ai_prefix="Witch")
conversation = ConversationChain(
    prompt=PROMPT,
    llm=llm, 
    verbose=True, 
    memory=MEMORY
)

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

def update_chain():
    global conversation
    global llm
    global PROMPT
    # global MEMORY
    # global current_temperature
    # global current_template
    PROMPT = PromptTemplate(
        input_variables=["history", "input"], template=current_template
    )
    llm = OpenAI(temperature=current_temperature)
    conversation = ConversationChain(
        prompt=PROMPT,
        llm=llm, 
        verbose=True, 
        memory=MEMORY
    )

@bot.command(name="chat_history")
async def show_chat_history(ctx):
    global MEMORY
    await ctx.send(f"""chat history is:\n```markdown\n{MEMORY.chat_memory}\n```""")

@bot.command(name="clear_history")
async def clear_chat_history(ctx):
    global MEMORY
    MEMORY = ConversationBufferMemory(human_prefix="Traveler", ai_prefix="Witch")
    update_chain()
    await ctx.send(f"""chat history has been cleared.""")

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
    temperature = float(temperature)
    if temperature >= current_temperature:
        response = f"Cauldron heated up to: ```{temperature}```"
    else:
        response = f"Cauldron cooled down to: ```{temperature}```"
    current_temperature = temperature
    update_chain()
    await ctx.send(response)

@bot.command(name="show_temperature")
async def show_current_temperature(ctx):
    global current_temperature
    await ctx.send(f"The current temperature of the cauldron is: ```{current_temperature}```")

@bot.command(name="switch_persona")
async def change_persona(ctx):
    global current_persona
    global reading_prefix
    global general_prefix
    global PROMPT
    global current_template
    if current_persona == Persona.CRONE:
        current_persona = Persona.PRINCESS
        reading_prefix, general_prefix = reading_prefix_princess, general_prefix_princess
        current_template = princess_template
        update_chain()
        await ctx.send("You are now speaking to the princess...")
    else:
        current_persona = Persona.CRONE
        reading_prefix, general_prefix = reading_prefix_crone, general_prefix_crone
        current_template = crone_template
        update_chain()
        await ctx.send("You are now speaking to the crone...")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if bot.user.mentioned_in(message):
        text = general_prefix + message.content
        #prompt = f"{message.author.name}: {text}"
        #response = await generate_response(prompt)
        response = conversation.run(input=message.content)
        await message.channel.send(response)
    else:
        await bot.process_commands(message)

@bot.event
async def on_ready():
    print(f"logged into Discord as {bot.user}")
    activity = discord.Game(name="witchcraft", type=3)
    await bot.change_presence(status=discord.Status.online, activity=activity)

bot.run(DISCORD_TOKEN)
