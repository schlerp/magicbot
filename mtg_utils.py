import pickle
import scipy.sparse
import discord
import requests
import string
import numpy as np


# load globals
As = scipy.sparse.load_npz('./data/As.npz')
unique_cards = pickle.load(open('./data/unique_cards.pkl', 'rb'))
card_dict = pickle.load(open('./data/card_dict.pkl', 'rb'))
deck_dict = pickle.load(open('./data/deck_dict.pkl', 'rb'))


def get_nearest(card, ntop=10):
    card = card.lower()
    card_idx = unique_cards.index(card)
    w = As[:,card_idx].toarray()
    neighbours = [(unique_cards[idx], wt) for idx, wt in enumerate(w) \
        if unique_cards[idx] not in ('island', 'mountain', 'swamp', 'forest', 'plains')]
    neighbours = sorted(neighbours, key=lambda x: x[1], reverse=True)[:ntop]
    ret = [
        {
            'name': string.capwords(x[0]),
            'score': int(x[1][0]),
            'scryfall': 'https://scryfall.com/search?q=!{0}'.format(x[0].replace(' ', '_'))
        } for x in neighbours
    ]
    return ret


def get_card_image(name, size='normal'):
    r = requests.get(
        'https://api.scryfall.com/cards/named?exact={}'.format(name.replace(' ', '_'))
    )

    try:
        url = r.json()['image_uris']['normal']
    except KeyError:
        url = r.json()['card_faces'][0]['image_uris']['normal']
    
    return url


def handle_suggest_cards(ctx, card):
    try:
        nearest_neighbours = get_nearest(card, ntop=5)
    except (KeyError, ValueError):
        embed = discord.Embed(title='Related to {}'.format(card), 
                              description='Card not found in model! [search scryfall?](https://scryfall.com/search?q={0})'.format(card.replace(' ', '_')),
                              color=0x176cd5)
        
        try:
            embed.set_thumbnail(
                url=get_card_image(card, size='small'))
            
        except:
            pass
        
        embed.set_author(
            name="Requested by " + str(ctx.message.author), 
            icon_url=ctx.message.author.avatar_url)
        
        yield embed
    else:
        for neighbour in nearest_neighbours:
            name = neighbour['name']
            link = neighbour['scryfall']
            score = neighbour['score']
            
            embed = discord.Embed(
                title='Related to {}'.format(string.capwords(card)),
                color=0x176cd5,
                url='https://scryfall.com/search?q=!{0}'.format(card.replace(' ', '_')))

            embed.set_thumbnail(url=get_card_image(card, size='small'))

            embed.set_image(url=get_card_image(name))

            name_link = '[{}]({})'.format(string.capwords(name), link)

            embed.add_field(name='Name', value=name_link, inline=True)
            embed.add_field(name='Score', value='{} common decks'.format(score), inline=True)
            #embed.add_field(name="Card Info", value=name_link, inline=True)

            embed.set_author(
                name="Requested by " + str(ctx.message.author), 
                icon_url=ctx.message.author.avatar_url)

            yield embed


def handle_suggest_decks(ctx, card):
    mtggoldfish_link = 'https://www.mtggoldfish.com/deck/visual/{}'
    mtggoldfish_search = 'https://www.mtggoldfish.com/q?utf8=%E2%9C%93&query_string={}'
    card = card.lower()

    try:
        card_dict[card]
    except KeyError:
        error_template = 'Card not found! [search mtggoldfish?]({})'
        search_link = mtggoldfish_search.format(card.replace(' ', '_'))
        error_string = error_template.format(search_link)

        embed = discord.Embed(title='Decks for {}'.format(card), 
                              description=error_string,
                              color=0x176cd5)
        
        try:
            embed.set_thumbnail(
                url=get_card_image(card, size='small'))
        except:
            pass
            
        embed.set_author(
            name="Requested by " + str(ctx.message.author), 
            icon_url=ctx.message.author.avatar_url)
        yield embed

    else:
        decks = card_dict[card]
        random.shuffle(decks)
        for deck in decks[0:5]:
            deck_id = deck.split('_')[0]
            deck_name = ' - '.join(deck.split(' - ')[1:])
            link = mtggoldfish_link.format(deck_id)

            embed = discord.Embed(
                title=string.capwords(deck_name),
                description='Deck for {}'.format(string.capwords(card)),
                color=0x176cd5,
                url=link,
                type='link')

            embed.set_thumbnail(
                url=get_card_image(card, size='small'))

            embed.set_author(
                name="Requested by " + str(ctx.message.author), 
                icon_url=ctx.message.author.avatar_url)

            yield embed