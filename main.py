import discord # pip install pycord
from discord.ext import commands # ^^
import os # default
from dotenv import load_dotenv # pip install python-dotenv
import sqlite3 # pip install sqlite3
import re # default
from typing import Union # default
from discord import option # že installed
from  dateutil.parser import parse # default
from datetime import * # default?


load_dotenv()
bot = discord.Bot()

@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")

non_cogs = ["nadomescanja.db"]
cogfiles = ( [f"cogs.{filename[:-3]}" for filename in os.listdir("./cogs/") if filename.endswith(".py") and filename not in non_cogs])

for cogfile in cogfiles:
    try:
        bot.load_extension(cogfile)
        print(f"{cogfile[5:]} succesffuly loaded!")
    except Exception as err:
        print(err)

# -------------------------------------------------

bot.run(os.getenv('TOKEN')) # run the bot with the token
