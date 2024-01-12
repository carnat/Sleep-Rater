import discord
from discord.ext import commands
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_commands import create_option
import requests
from bs4 import BeautifulSoup
from PIL import Image
import pytesseract
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

TOKEN = os.getenv('TOKEN')
PREFIX = '!pokemon'

intents = discord.Intents.default()
intents.all()

bot = commands.Bot(command_prefix=PREFIX, intents=intents)
slash = SlashCommand(bot, sync_commands=True)

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

@slash.slash(
    name="rateps",
    description="Get the rating of a Pokemon and perform OCR on an uploaded image",
    options=[
        create_option(
            name="pokemon_name",
            description="The name of the Pokemon",
            option_type=3,  # String
            required=True
        ),
        create_option(
            name="image",
            description="Upload an image for OCR (optional)",
            option_type=3,  # String
            required=False
        )
    ]
)
async def rateps(ctx: SlashContext, pokemon_name: str, image: str = None):
    url = f'https://pks.raenonx.cc/en/rating/{pokemon_name.lower()}'

    try:
        response = requests.get(url)
        response.raise_for_status()  # Check for any HTTP errors
    except requests.RequestException as e:
        await ctx.send(f"Error fetching data from the website: {e}")
        return

    soup = BeautifulSoup(response.text, 'html.parser')
    rating_element = soup.find('span', {'class': 'rate-span'})

    if rating_element:
        rating = rating_element.text.strip()
        await ctx.send(f'The rating of {pokemon_name.capitalize()} is: {rating}')
    else:
        await ctx.send(f"Rating not found for {pokemon_name.capitalize()}.")

    # If an image is provided, perform OCR
    if image:
        await ocr_image(ctx, image)

async def ocr_image(ctx, image_url):
    try:
        # Fetch the image URL
        image_response = requests.get(image_url)
        image_response.raise_for_status()

        # Save the image locally
        with open('uploaded_image.png', 'wb') as image_file:
            image_file.write(image_response.content)

        # Use Tesseract OCR to extract text from the image
        image = Image.open('uploaded_image.png')
        ocr_result = pytesseract.image_to_string(image)

        # Send the OCR result to Discord
        await ctx.send(f'The OCR result for the uploaded image is: {ocr_result}')
    except Exception as e:
        await ctx.send(f"Error during OCR: {e}")
    finally:
        # Clean up: delete the temporary image file
        try:
            os.remove('uploaded_image.png')
        except OSError:
            pass

bot.run(TOKEN)
