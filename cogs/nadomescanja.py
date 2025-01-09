import discord
import os
from typing import Union
from discord import option
from discord.ext import commands
import sqlite3
from  dateutil.parser import parse
from datetime import *
from dotenv import load_dotenv
load_dotenv()

path = "./cogs/nadomescanja.db"

def sql_update_current(uid: int, value: int): # A simple sql code used in update_database
    con = sqlite3.connect(path)
    cur = con.cursor()

    cur.execute("UPDATE Nadomescanja SET is_current = ? WHERE uid = ?", (value, uid))

    con.commit()
    con.close()

def after_today(datum):
    current_date = datetime.now().date()
    datum = (parse(datum, dayfirst=True).date())
    
    print(datum, current_date)
    if datum > current_date:
        return True
    else:
        return False
    
def upadte_database(): # Function responsible for checking, which Nadomeščanja enteries are after today and updating them
    con = sqlite3.connect(path)
    cur = con.cursor()

    cur.execute("SELECT uid, datum FROM Nadomescanja")
    results = cur.fetchall()

    con.commit
    con.close

    for result_uid, result_date in results:


        if not after_today(result_date):
            sql_update_current(result_uid, 0)
            print(f"update_database {result_uid} : Succsess ({result_date}) set to: 0")
        elif after_today(result_date):
            sql_update_current(result_uid, 1)
            print(f"update_database {result_uid} : Succsess ({result_date}) set to: 1")
        else:
            print(f"Critical error ---- : Error with updating in {result_uid}, {result_date}")
upadte_database() # Updates database on boot
        
class Nadomescanaja(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.slash_command(name="dodaj_nadomeščanje", description="Dodaj nadomeščanje")
    @option("Predmet", description="Predmet za nadomeščanje", required=True)
    @option("Datum", description="Format DD.MM.YYYY", required=True)
    @option("Ura", description="Format hh:mm", required=True)
    @option("Trajanje", description="Npr.: '2h', '2h 15min' ", required=True)
    @option("Učilnica", description="Ime učilnice", required=True)
    @option("Letnik" , Union[discord.Role], description="Nadomeščanje za kateri letnik ALI vlogo izbirnega predmeta")
    @option("Profesor", description="Ime profesorja", default="", required=False)
    @option("Komentar", description="Dodatne informacije:", default="",required=False)
    async def dodaj_nadomeščanje(
        self, 
        ctx: discord.ApplicationContext, 
        predmet: str, 
        datum: str, 
        ura: str, 
        trajanje: str,  
        učilnca: str,
        letnik: Union[discord.Role], 
        profesor: str = None,
        komentar: str = None):

        try:
            parse(datum, fuzzy=False)
        except:
            await ctx.respond(embed=discord.Embed(title="Napaka!", description=f"Vneseni datum ({datum}), ni pravilen ali razumljiv!", color=discord.Colour.from_rgb(255, 0, 0)), ephemeral = True)
            return
        
        try:
            parse(ura, fuzzy=False)
        except:
            await ctx.respond(embed=discord.Embed(title="Napaka!", description=f"Vnesena ura ({ura}), ni pravilna ali razumljiva!", color=discord.Colour.from_rgb(255, 0, 0)), ephemeral = True)
            return
        
        try:
            parse(trajanje, fuzzy=False)
        except:
            await ctx.respond(embed=discord.Embed(title="Napaka!", description=f"Vneseno trajanje ({trajanje}), ni pravilno ali razumljivo!", color=discord.Colour.from_rgb(255, 0, 0)), ephemeral = True)
            return
        
        if len(str(predmet)) < 3:
            await ctx.respond(embed=discord.Embed(title="Napaka!", description=f"Vneseni predmet ({predmet}) ima premalo znakov!", color=discord.Colour.from_rgb(255, 0, 0)), ephemeral = True)
            return
        
        if not after_today(datum=datum):
            await ctx.respond(embed=discord.Embed(title="Napaka!", description=f"Vneseni datum ({datum}) je že mimo!", color=discord.Colour.from_rgb(255, 0, 0)), ephemeral = True)
        
        con = sqlite3.connect(path)
        cur = con.cursor()

        cur.execute("INSERT INTO Nadomescanja VALUES (NULL, ?,?,?,?,?,?,?,?,1)", (predmet, datum, ura, trajanje, učilnca, int(letnik.id), profesor, komentar))

        con.commit()
        con.close()

        embed = discord.Embed(
            title="Nadomeščanja",
            description="Dodali ste nadomeščanje",
            color=discord.Colour.from_rgb(0, 255, 0),
        )
        embed.add_field(name="Predmet:", value=predmet)

        embed.add_field(name="Datum:", value=datum, inline=True)
        embed.add_field(name="Ura:", value=str(ura)+" + " + str(trajanje), inline=True)
        embed.add_field(name="Učilnica:", value=učilnca, inline=False)
        if profesor != None:
            embed.add_field(name="Profesor", value=profesor, inline=True)
        if komentar != None:
            embed.add_field(name="Komentar", value=komentar, inline=False)
    
        embed.set_footer(text="Unofficial FMF bot")
        embed.set_author(name="uFMF Bot", icon_url="https://orlic.si/luka/FMF/fmf-logo.png")
        await ctx.respond(embed=embed, ephemeral = False)
    
    @commands.slash_command()
    async def moja_nadomeščanja(self, ctx: discord.ApplicationContext):
        results_all_roles = []
        role_ids = list(ctx.author.roles)
        for i in range(len(role_ids)):
            role_ids[i] = role_ids[i].id

        con = sqlite3.connect(path)
        cur = con.cursor()

        for role in role_ids:
            cur.execute("SELECT * FROM Nadomescanja WHERE letnik = ? AND is_current = 1", (role,))
            results_all_roles.append(cur.fetchall()) # naredi seznam nadomescanj za vsaki role, ki ga ima uporabnik, in vse te sezname, da ven seznam!

        con.commit()
        con.close()

        embed = discord.Embed(
            title="Vaša nadomeščanje",
            description="Prikazana so vaša nadomeščanja!",
            color=discord.Colour.from_rgb(0, 255, 0),
        )
        
        for role_results in results_all_roles: # Gre cez vsak rezultat po role-u posebaj
            if role_results != []: # Izbrise vse sezname vlog, ki so prazni (nimajo nadomescanj)
                for result in role_results: # Za vsako nadomescanje posebi doda predel na izpisu
                
                    uid, predmet, datum, ura, trajanje, učilnica, role, profesor, komentar, is_current = result
                    embed.add_field(name="\n", value="-------------------------------", inline=False)
                    embed.add_field(name="Predmet:", value=predmet, inline=False)
                    embed.add_field(name="Datum in ura:", value= "**__Datum__** : " + str(datum) + "\n**__Ura__** : " + str(ura) + ", " + str(trajanje), inline=True)
                    embed.add_field(name="Dodatno : ", value="**__Učilnica__** :" + str(učilnica) + "\n**__Profesor__** : " + str(profesor) +"\n**__Komentar__** : " +str(komentar), inline=False)

        embed.add_field(name="\n", value="-------------------------------", inline=False)
        
        embed.set_footer(text="Unofficial FMF bot")
        embed.set_author(name="uFMF Bot", icon_url="https://orlic.si/luka/FMF/fmf-logo.png")
        await ctx.respond(embed=embed, ephemeral = True)

    @commands.slash_command()
    @discord.default_permissions(
        manage_events=True
    )
    async def vsa_nadomeščanja(self, ctx: discord.ApplicationContext):
        con = sqlite3.connect(path)
        cur = con.cursor()

        cur.execute("SELECT * FROM Nadomescanja WHERE is_current = 1")
        results = cur.fetchall()    

        con.commit()
        con.close()

        embed = discord.Embed(
            title="VSA nadomeščanje",
            description="Prikazana so VSA nadomeščanja!",
            color=discord.Colour.from_rgb(0, 0, 255),
        )
        
        for uid, predmet, datum, ura, trajanje, učilnica, role, profesor, komentar, is_current in results:
            embed.add_field(name="\n", value="-------------------------------", inline=False)
            embed.add_field(name="Predmet:", value= str(predmet) + "\n**__Tehnična oznaka__** : " + str(uid), inline=False)
            embed.add_field(name="Datum in ura:", value= "**__Datum__** : " + str(datum) + "\n**__Ura__** : " + str(ura) + ", " + str(trajanje), inline=True)
            embed.add_field(name="Dodatno : ", value="**__Učilnica__** :" + str(učilnica) + "\n**__Profesor__** : " + str(profesor) +"\n**__Komentar__** : " +str(komentar), inline=False)
        
        embed.set_footer(text="Unofficial FMF bot")
        embed.set_author(name="uFMF Bot", icon_url="https://orlic.si/luka/FMF/fmf-logo.png")
        await ctx.respond(embed=embed, ephemeral = True)

    @commands.slash_command()
    @discord.default_permissions(
        manage_events=True
    )
    @option("Tehnična oznaka", description="Vpišite tehnično oznako nadomeščanja!")
    async def izbriši_nadomeščanje(self, ctx: discord.ApplicationContext, tehnična_oznaka: int):
        con = sqlite3.connect(path)
        cur = con.cursor()

        cur.execute("SELECT * FROM Nadomescanja WHERE is_current = 1 AND uid = ?", (tehnična_oznaka,))
        results = cur.fetchall()
        if results == []:
            await ctx.respond(f"Nadomeščanje s tehnično oznako  __{tehnična_oznaka}__ NE obstaja!", ephemeral=True)
            return
        cur.execute("DELETE FROM Nadomescanja WHERE uid = ?", (tehnična_oznaka,))    

        con.commit()
        con.close()

        embed = discord.Embed(
            title="Izbrisano nadomeščanje",
            description="Prikazano je __**izbrisano**__ nadomeščanje!",
            color=discord.Colour.from_rgb(0, 0, 255),
        )
        
        for uid, predmet, datum, ura, trajanje, učilnica, role, profesor, komentar, is_current in results:
            embed.add_field(name="\n", value="-------------------------------", inline=False)
            embed.add_field(name="Tehnična oznaka", value=uid, inline=False)
            embed.add_field(name="Predmet:", value=predmet, inline=False)

            embed.add_field(name="Datum:", value=datum, inline=True)
            embed.add_field(name="Ura:", value=str(ura)+" + " + str(trajanje), inline=True)
            embed.add_field(name="Učilnica:", value=učilnica, inline=False)
            if profesor != None:
                embed.add_field(name="Profesor", value=profesor, inline=True)
            if komentar != None:
                embed.add_field(name="Komentar", value=komentar, inline=False)
            if uid != results[-1][0]:
                embed.add_field(name="\n", value="-------------------------------", inline=False)
        
        embed.set_footer(text="Unofficial FMF bot")
        embed.set_author(name="uFMF Bot", icon_url="https://orlic.si/luka/FMF/fmf-logo.png")
        await ctx.respond(embed=embed)

def setup(bot):
    bot.add_cog(Nadomescanaja(bot))
