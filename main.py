import discord
from discord.ext import commands

bot = commands.Bot(command_prefix='!')

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

@bot.command(name='rate_pokemon', help='Get the rating of a Pokemon from the website')
async def rate_pokemon(ctx, pokemon_name):
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
        # If the rating is not found, try using OCR on the website's image
        await ocr_pokemon_rating(ctx, url)

async def ocr_pokemon_rating(ctx, url):
    try:
        # Fetch the image URL from the website
        image_url = 'https://pks.raenonx.cc/en/rating/' + url.split('/')[-1] + '/r'
        image_response = requests.get(image_url)
        image_response.raise_for_status()

        # Save the image locally
        with open('pokemon_image.png', 'wb') as image_file:
            image_file.write(image_response.content)

        # Use Tesseract OCR to extract text from the image
        image = Image.open('pokemon_image.png')
        ocr_result = pytesseract.image_to_string(image)

        # Send the OCR result to Discord
        await ctx.send(f'The OCR result for {url} is: {ocr_result}')
    except Exception as e:
        await ctx.send(f"Error during OCR: {e}")
    finally:
        # Clean up: delete the temporary image file
        try:
            os.remove('pokemon_image.png')
        except OSError:
            pass

bot.run('YOUR_BOT_TOKEN')
