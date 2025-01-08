import discord
from discord.ui import Select, View
from discord.ext import commands
import sqlite3
import re

class EmailList(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
    
    @commands.slash_command(name="subscribe", description="V DELU!!! Dodaj elektronski naslov za obveščanje!")
    async def subscribe(self, ctx: discord.ApplicationContext, email: str):

        valid = re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email)

        if valid:
            connection = sqlite3.connect("./cogs/nadomescanja.db")
            cursor = connection.cursor()

            cursor.execute("SELECT duid, email FROM Email_list WHERE duid=? OR email=?", (ctx.author.id, email))
            result = cursor.fetchone()

            if result:
                await ctx.respond(
                    embed=discord.Embed(
                        title="Napaka!", 
                        description=f"Uporabnik že obstaja ali že obstaja elektrosnka pošta!", 
                        color=discord.Colour.from_rgb(255,0,0)), 
                    ephemeral=True)
                
            else:
                cursor.execute("INSERT INTO Email_list VALUES (?, ?)", (ctx.author.id, email))

                await ctx.respond(
                    embed=discord.Embed(
                        title=f"{ctx.author.name} Subscribed!", 
                        description=f"Vpisana elektronska pošta ({email}), je bila dodana na elektronsko listo sporočevanja!", 
                        color=discord.Colour.from_rgb(0,255,0)), 
                    ephemeral=True)
                
            connection.commit()
            connection.close()
        elif not valid:

            await ctx.respond(
                embed=discord.Embed(
                    title="Napaka!", 
                    description=f"Vpisana elektronska pošta ({email}) ni sprejemljiva!", 
                    color=discord.Colour.from_rgb(255,0,0)), 
                ephemeral=True )
            return
        
        else:
            await ctx.respond(
                embed=discord.Embed(
                    title="Napaka!", 
                    description=f"Kontaktirajte administratorje...", 
                    color=discord.Colour.from_rgb(255,0,0)), 
                ephemeral=True)
        
        
    
    @commands.slash_command(name = "unsubscribe", description="V DELU!!! Umakni elektronski naslov za obveščanje!")
    async def unsubscribe(self, ctx: discord.ApplicationContext):
        connection = sqlite3.connect("./cogs/nadomescanja.db")
        cursor = connection.cursor()

        cursor.execute("SELECT email FROM Email_list WHERE duid=?", (ctx.author.id,))
        result = cursor.fetchone()

        if result:
            cursor.execute("DELETE FROM Email_list WHERE duid=?", (ctx.author.id,))
            await ctx.respond(
                embed=discord.Embed(
                    title=f"{ctx.author.name} unsubscribed!", 
                    description=f"Vpisana elektronska pošta ({str(result)[2:-3]}), je izbirsana iz elektronske liste sporočevanja!", 
                    color=discord.Colour.from_rgb(0,255,0)
                    ),
                ephemeral=True)
        else:
            await ctx.respond(
                embed=discord.Embed(
                    title="Napaka!", 
                    description=f"Uporabnik ni prijavil elektronskega naslova!", 
                    color=discord.Colour.from_rgb(255,0,0)),
                ephemeral=True)
        connection.commit()


def setup(bot):
    bot.add_cog(EmailList(bot))