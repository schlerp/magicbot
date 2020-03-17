# Magicbot

A discord bot for suggesting magic cards and decks (also for me to muck with some machine learning).

Decks were scraped from mtggoldfish. they were then processed and graph was set up using the cards as the nodes and the weight for the edges was how many times they appeared in decks together. Initially I played with deep walk algorithms but it didn't give me as good answers as what im currently getting just grabbing the top n highest weighted neighbours.

This is jsut the Discord bot. The actual code that built the graphs etc, is in another project i will upload when it is tidy.

## Installation

> git clone https://github.com/schlerp/magicbot.git
> cd magicbot
> venv venv
> source ./venv/bin/activate
> pip install -r ./requirements.txt
> # you can place the following lines in a .env file rather than exporting them
> export DISCORD_TOKEN='your token!'
> export BOT_PREFIX="~"
> python main.py