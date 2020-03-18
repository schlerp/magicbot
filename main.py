import os
import time
import datetime
import discord
from discord.ext import commands
from discord.ext.commands import Bot
import random
from dotenv import load_dotenv

# import mtg utils
from mtg_utils import *

#============================================================================
# Setup
#============================================================================

# get env variables
load_dotenv()
discord_token = os.getenv('DISCORD_TOKEN')
giphy_token = os.getenv('GIPHY_TOKEN')
bot_prefix = os.getenv('BOT_PREFIX')

# set up bot
def setup_bot(discord_token, giphy_token, bot_prefix):
    client = discord.Client()
    bot = commands.Bot(
        command_prefix=commands.when_mentioned_or(bot_prefix), 

        case_insensitive=True)
    return client, bot

client, bot = setup_bot(discord_token, giphy_token, bot_prefix)

# Specify bot owners ID for owner-only commands.
# def ownercheck(ctx):
#     return ctx.message.author.id == owner

def botcheck(ctx):
    return ctx.message.author.bot == False

# Successful API connection.
@bot.event
async def on_ready():
    print(str(datetime.datetime.now().time()) + " - Connected to Discord API.")
          

#============================================================================
# Bot Commands
#============================================================================

# ping command
@commands.check(botcheck)
@bot.command(pass_context=True)
async def ping(ctx):
    """Ping the bot."""
    now = datetime.datetime.utcnow()
    delta = ctx.message.created_at
    pingtime = now-delta
    embed = discord.Embed(
        title="Pong! {} ms".format(pingtime), 
        color=0x176cd5)
    embed.set_author(
        name="Requested by " + str(ctx.message.author), 
        icon_url=ctx.message.author.avatar_url)
    await ctx.send(embed=embed)


# weather command
@commands.check(botcheck)
@bot.command(pass_context=True)
async def weather(ctx, *, loc='darwin'):
    """Fetch the current weather of a town."""
    await ctx.send("https://wttr.in/{0}.png?m".format(loc))
            

# suggest cards command
@commands.check(botcheck)
@bot.command(pass_context=True, aliases=['sc'])
async def suggest_cards(ctx, *, card):
    '''Suggest cards that are often used with this card'''
    card = card.lower()
    for embed in handle_suggest_cards(ctx, card):
        await ctx.send(embed=embed)
    
# suggest decks command
@commands.check(botcheck)
@bot.command(pass_context=True, aliases=['sd'])
async def suggest_decks(ctx, *, card):
    '''Suggest decks that use this card'''
    card = card.lower()
    for embed in handle_suggest_decks(ctx, card):
        await ctx.send(embed=embed)


#============================================================================
# Run the bot!
#============================================================================

if __name__ == '__main__':
    # run the bot
    bot.run(discord_token)
    