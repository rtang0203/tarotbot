import random
import openai
import os
from dotenv import load_dotenv
import asyncio

# Load Discord token and OpenAI API key from .env file
load_dotenv()
#DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

prefix = "Pretend you are a wise old witch doing a tarot reading. I will pull a three card tarot spread from the deck \
and you will interpret it for me, speaking like a withered old crone. Here is my spread: \n"

prefix = "Pretend you are a young gothic witch doing a tarot reading. I will pull a three card tarot spread from the deck \
and you will interpret it for me, speaking in a seductive and flirtatious tone. Here is my spread: \n"

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

async def generate_response(prompt, temperature=0.7):
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

async def tarot_reading(spread):
    #spread = three_card_spread()
    prompt = prefix + str(spread)
    # name = 'randy'
    # text = f"{name}: {prompt}"
    # print(text)
    # response = await generate_response(text)
    # return response
    return await generate_response(prompt)

async def main():
    spread = three_card_spread()
    print(spread)
    reading = await tarot_reading(spread)
    print(reading)

    # test_prompt = 'tell me something i dont know'
    # print(generate_response(test_prompt))

asyncio.run(main())