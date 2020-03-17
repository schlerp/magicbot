import os
import time
import datetime
import string
import discord
from discord.ext import commands
from discord.ext.commands import Bot
import requests
#import giphy_client
#from tinydb import TinyDB
from dotenv import load_dotenv
#import gensim.models.word2vec
import networkx as nx
import pickle

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
# Setup magic stuff
#============================================================================

# set up mtg graph
G = nx.read_gpickle('./card_network.pkl')

def get_nearest(key, n=10):
    nearest_neighbours =  sorted(
        G[key].items(), 
        key=lambda x: x[1][0]["weight"],
        reverse=True
    )[:n]
    
    ret = [
        {
            'name': string.capwords(x[0]),
            'score': x[1][0]["weight"],
            'scryfall': 'https://scryfall.com/search?q=!{0}'.format(x[0].replace(' ', '_'))
        } for x in nearest_neighbours
    ]
    return ret

card_dict = pickle.load(open('./card_dict.pkl', 'rb'))
deck_dict = pickle.load(open('./deck_dict.pkl', 'rb'))


def get_card_image(name, size='normal'):
    r = requests.get(
        'https://api.scryfall.com/cards/named?exact={}'.format(name.replace(' ', '_'))
    )

    # from pprint import pprint
    # pprint(r.json())
    
    try:
        url = r.json()['image_uris']['normal']
    except KeyError:
        url = r.json()['card_faces'][0]['image_uris']['normal']
    
    return url

def handle_suggest_cards(ctx, card):
    try:
        nearest_neighbours = get_nearest(card, n=5)
    except KeyError:
        embed = discord.Embed(title='Related to {}'.format(card), 
                              description='Card not found in model! [search scryfall?](https://scryfall.com/search?q={0})'.format(card.replace(' ', '_')),
                              color=0x176cd5)
        
        try:
            embed.set_thumbnail(
                url=get_card_image(card, size='small')
            )
        except:
            pass
        
        embed.set_author(name="Requested by " + str(ctx.message.author), icon_url=ctx.message.author.avatar_url)
        yield embed
    else:
        for neighbour in nearest_neighbours:
            name = neighbour['name']
            link = neighbour['scryfall']
            score = neighbour['score']
            
            embed = discord.Embed(
                title='Related to {}'.format(string.capwords(card)),
                color=0x176cd5,
                url='https://scryfall.com/search?q=!{0}'.format(card.replace(' ', '_'))
            )

            embed.set_thumbnail(
                url=get_card_image(card, size='small')
            )

            embed.set_image(
                url=get_card_image(name)
            )

            name_link = '[scryfall]({})'.format(
                link
            )

            embed.add_field(
                name='Name', 
                value=name,
                inline=True
            )

            embed.add_field(
                name='Score', 
                value='{}'.format(score), 
                inline=True
            
            )
            embed.add_field(
                name="Card Info", 
                value=name_link,
                inline=True
            )

            embed.set_author(name="Requested by " + str(ctx.message.author), icon_url=ctx.message.author.avatar_url)
            yield embed

def handle_suggest_decks(ctx, card):
    mtggoldfish_link = 'https://www.mtggoldfish.com/deck/visual/{}'
    metggoldfish_search = 'https://www.mtggoldfish.com/q?utf8=%E2%9C%93&query_string={}'
    try:
        card_dict[card]
    except KeyError:

        embed = discord.Embed(title='Decks for {}'.format(card), 
                              description='Card not found! [search mtggoldfish?]({})'.format(metggoldfish_search).format(card.replace(' ', '_')),
                              color=0x176cd5)
        
        try:
            embed.set_thumbnail(
                url=get_card_image(card, size='small')
            )
        except:
            pass
            
        embed.set_author(name="Requested by " + str(ctx.message.author), icon_url=ctx.message.author.avatar_url)
        yield embed

    else:
        for deck in card_dict[card]:
            deck_id = deck.split('_')[0]
            deck_name = ' - '.join(deck.split(' - ')[1:])
            link = mtggoldfish_link.format(deck_id)

            embed = discord.Embed(
                title=string.capwords(deck_name),
                description='Deck for {}'.format(string.capwords(card)),
                color=0x176cd5,
                url=link,
                type='link'
            )

            embed.set_thumbnail(
                url=get_card_image(card, size='small')
            )

            embed.set_author(
                name="Requested by " + str(ctx.message.author), 
                icon_url=ctx.message.author.avatar_url
            )

            # if len(deck_dict[deck]) <= 8:

            #     for deck_item in deck_dict[deck]:
            #         embed.add_field(
            #             name='Amount', 
            #             value=deck_item['amount'], 
            #             inline=True
            #         )

            #         embed.add_field(
            #             name='Card', 
            #             value=deck_item['card_name'], 
            #             inline=True
            #         )

            #         embed.add_field(
            #             name='Card Info', 
            #             value='[scryfall]({})'.format(deck_item['scryfall']), 
            #             inline=True
            #         )

            yield embed
          

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
    embed = discord.Embed(title="Pong! {} ms".format(pingtime), color=0x176cd5)
    embed.set_author(name="Requested by " + str(ctx.message.author), icon_url=ctx.message.author.avatar_url)
    await ctx.send(embed=embed)


# weather command
@commands.check(botcheck)
@bot.command(pass_context=True)
async def weather(ctx, *, loc='darwin'):
    """Fetch the current weather of a town."""
    await ctx.send("https://wttr.in/{0}.png?m".format(loc))
            

# suggest cards command
@commands.check(botcheck)
@bot.command(pass_context=True)
async def suggest_cards(ctx, *, card):
    card = card.lower()
    for embed in handle_suggest_cards(ctx, card):
        await ctx.send(embed=embed)
    
# suggest decks command
@commands.check(botcheck)
@bot.command(pass_context=True)
async def suggest_decks(ctx, *, card):
    card = card.lower()
    for embed in handle_suggest_decks(ctx, card):
        await ctx.send(embed=embed)

#============================================================================
# Run the bot!
#============================================================================

if __name__ == '__main__':
    # run the bot
    bot.run(discord_token)
    