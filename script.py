from contextlib import nullcontext
from dis import dis, disco
from http import client
from locale import currency
from os import link
from pickle import TRUE
from pkgutil import iter_modules
import random
import string
from turtle import color, title
from pyVinted import *
import discord
from discord.ext import commands
import requests
from flask import *
import flask
from bs4 import BeautifulSoup
import smtplib
import time
import sys
import shutil
import threading
import os
import json
from deep_translator import GoogleTranslator
from time import sleep

#python script.py
def getUserAgent():
    randomUserAgent = ""
    listOfUserAgents = []
    userAgentFile = 'ua_file.txt'
    os.chdir(r'F:\BotVinted')
    with open('ua_file.txt') as file:
        listOfUserAgents = [line.rstrip("\n") for line in file]
    return random.choice(listOfUserAgents)

class Sneaker:
    def __init__(self, name, query_id, retail_price, displayed_size, price, image_url):
        self.name = name
        self.query_id = query_id

        if(retail_price == None):
            self.retail_price = "N/A"
        else:
            self.retail_price = retail_price/100
        
        if(displayed_size == None):
            self.displayed_size = "N/A"
        else:
            self.displayed_size = displayed_size
        
        if(price == None):
            self.lowest_price = "N/A"
        else:
            self.lowest_price = price/100

        self.image_url = image_url
        
def get_sneakers(keyword=''):
    sneakers_list = []
    url = 'https://2fwotdvm2o-3.algolianet.com/1/indexes/*/queries'
    shoe_size = ''
    search_field = keyword
    for page in range(0,5):
        form_data = {
            'requests': [{
            "indexName":"product_variants_v2",
            "params":"",
            "highlightPreTag" : "<ais-highlight-0000000000>",
            "highlightPostTag": "</ais-highlight-0000000000>",
            "distinct": "true",
            "query": keyword,
            "facetFilters": [["presentation_size:" + str(shoe_size)],["product_category:shoes"]],
            "maxValuesPerFacet": 30,
            "page": page,
            "facets": ["instant_ship_lowest_price_cents","single_gender","presentation_size","shoe_condition","product_category","brand_name","color","silhouette","designer","upper_material","midsole","category","release_date_name"],
            "tagFilters":""
            }]
        }
        query_params = {
            'x-algolia-agent': 'Algolia for JavaScript (3.35.1); Browser (lite); JS Helper (3.2.2); react (16.13.1); react-instantsearch (6.8.2)',
            'x-algolia-application-id': '2FWOTDVM2O',
            'x-algolia-api-key': 'ac96de6fef0e02bb95d433d8d5c7038a'
        }
        response = requests.post(url, data=json.dumps(form_data), params=query_params).json()['results'][0]['hits']

        for sneaker in response:
            sneakers_list.append((Sneaker(sneaker['name'], sneaker['slug'], sneaker['retail_price_cents'], sneaker['size'], sneaker['lowest_price_cents'], sneaker['original_picture_url']).__dict__))
        
    return sneakers_list

def getSneaker(query_id):
    sneakerInfo = {}
    url = "https://www.goat.com/web-api/v1/product_templates/" + query_id
    user_agent = getUserAgent()
    headers = {
        "User-Agent": user_agent,
        "Accept": "application/json",
        "Referer": "https://www.goat.com/sneakers/" + query_id
        }
    for i in range(0, 10):
        try:
            headers.update({"user-agent": getUserAgent()})
            response = requests.get(url, headers=headers).json()
            print(response)
            sneakerInfo['Name'] = response['name']
            sneakerInfo['Colorway'] = response['details']
            sneakerInfo['Style ID'] = response['sku']
            sneakerInfo['Release Date'] = response['releaseDate'].split('T')[0]
            sneakerInfo['Price Map'] = getSneakerSizesAndPrices(query_id)
            sneakerInfo['Image'] = response['mainPictureUrl']
            break
        except: #runs into captcha, so retry
            sleep(random.randrange(1,3))
            continue

    else:
        return {"message": "Could not connect to GOAT.com while searching for " + query_id}
    return sneakerInfo

def getSneakerSizesAndPrices(query_id): #helper method for getSneakr to get prices via separate api call
        sizeAndPrice = {}
        url = 'https://www.goat.com/web-api/v1/product_variants'
        user_agent = getUserAgent()
        headers = {
            "user-agent": user_agent,
            "accept" : "application/json",
            "accept-encoding": "gzip, deflate, br",
            "accept-language" : "en-US,en;q=0.9",
            "referer": 'https://www.google.com/'
        }

        query_params = {
            "productTemplateId": query_id
        }
        for i in range(0, 10):
            try:
                headers.update({"user-agent": getUserAgent()})
                response = requests.get(url, headers=headers, params=query_params, timeout=10)
                # print(response.text)
                if(response.status_code >= 200 and response.status_code < 400):
                    page = response.json()
                    for i in range(0, len(page)):
                        #check ONLY for new shoes with boxes in good condition
                        if(page[i]['boxCondition'] == "good_condition" and page[i]['shoeCondition'] == "new_no_defects"):
                            sizeAndPrice.update({page[i]['size']: page[i]['lowestPriceCents']['amount']/100})
                # elif (response.json()['success'] == False): #catches if query_id invalid
                elif("success" in response.json()):
                    if(response.json()['success'] == False):
                        sizeAndPrice.update({"message": "Invalid product id."})
                        break
                else:
                    raise PermissionError

            except (PermissionError):#request got blocked by captcha
                continue

            except requests.exceptions.Timeout as err:
                continue
            else:
                break

        else: # if not sizeAndPrice:
            sizeAndPrice.update({"Size_Timeout": "Price_Timeout"})

        return sizeAndPrice

def get_vinted_info(url):
    headers = requests.utils.default_headers()
    headers.update({'User-agent': 'Mozilla/5.0'})
    
    reponse = requests.get(str(url), headers=headers)
    soup = BeautifulSoup(reponse.text, "html.parser")
    res = soup.findAll('script', {"class": "js-react-on-rails-component"})

    userinfo = json.loads(res[19].text.replace(
        '<script class="js-react-on-rails-component" data-component-name="ItemUserInfo" data-dom-id="ItemUserInfo-react-component-2105d904-b161-47d1-bfce-9b897a8c1cc6" type="application/json">',
        '').replace("</script>", ''))

    positive = userinfo["user"]["positive_feedback_count"]
    negative = userinfo["user"]["negative_feedback_count"]
    username = userinfo["user"]["login"]
    ville = userinfo["user"]["city"]
    pays = userinfo["user"]["country_title"]
    trad = GoogleTranslator(source="auto", target="fr").translate(pays)

    infs = {}

    if positive == "":
        positive = "N/A"
    if negative == "":
        negative = "N/A"
    if username == "":
        username = "N/A"
    if pays == "":
        pays = "N/A"
    if ville == "":
        ville = "N/A"

    try:
        infs["positive"] = positive
        infs["negative"] = negative
        infs["username"] = username
        infs["pays"] = trad
        infs["ville"] = ville
        with open("test.json",'w+') as testjson:
            json.dump(infs,testjson,indent=4)
    except Exception as err:
            print(err)
    return infs

vinted = Vinted('fr')

bot = commands.Bot(command_prefix='?', description='Prefix : ?')

@bot.command()
async def helpcommands(ctx):
    await ctx.send("?searchshoe [adidas,nike,guess,jordan,sneakers] [price min price max] \n?searchapple [coque,airpods] [price min price max]")

@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(name="Cinco Noches Con Alfredo"))
    await bot.change_presence(activity=discord.Streaming(name="Cinco Noches Con Alfredo", url='https://www.youtube.com/watch?v=dQw4w9WgXcQ'))

    print(""""
    ██████╗  ██████╗ ████████╗
    ██╔══██╗██╔═══██╗╚══██╔══╝
    ██████╔╝██║   ██║   ██║   
    ██╔══██╗██║   ██║   ██║   
    ██████╔╝╚██████╔╝   ██║   
    ╚═════╝  ╚═════╝    ╚═╝ 
            /$$    /$$ /$$             /$$                     /$$
            | $$   | $$|__/            | $$                    | $$
            | $$   | $$ /$$ /$$$$$$$  /$$$$$$    /$$$$$$   /$$$$$$$
            |  $$ / $$/| $$| $$__  $$|_  $$_/   /$$__  $$ /$$__  $$
             \  $$ $$/ | $$| $$  \ $$  | $$    | $$$$$$$$| $$  | $$
              \  $$$/  | $$| $$  | $$  | $$ /$$| $$_____/| $$  | $$
               \  $/   | $$| $$  | $$  |  $$$$/|  $$$$$$$|  $$$$$$$
                \_/    |__/|__/  |__/   \___/   \_______/ \_______/, 𝔼𝕟𝕛𝕠𝕪
    
    
                    𝕭𝖄 𝕾𝖕𝖞𝖈#3009""") 

@bot.command()
async def searchshoe(ctx, value1, value2, value3):
    shoe = ""
    sneakers = "sneakers"
    jordan = "jordan"

    brand = ""
    nike = "nike"
    adidas = "adidas"

    minPrice = value2
    maxPrice = value3

    if (value1 == sneakers):
        shoe = sneakers
    elif (value1 == jordan):
        shoe = jordan
    elif (value1 == nike):
        shoe = nike
    elif (value1 == adidas):
        shoe = adidas

    link = 'https://www.vinted.fr/vetement?search_text='+shoe+'&brand_id[]='+brand+'&price_from='+minPrice+'&price_to='+maxPrice+'&status[]=6&catalog[]=5&size_id[]='
    itemshoe = vinted.items.search(link,50,random.randint(1,10))
    item1 = itemshoe[random.randint(0,50)]
    infos = get_vinted_info(item1.url)
    price = "N/A"
    lowestPrice = "N/A"
    rentable = "N/A"

    if (get_sneakers(item1.title)):
        json_data = json.dumps(get_sneakers(item1.title)[0])
        data = json.loads(json_data)
        price = str(data['retail_price'])

    embed = discord.Embed(title=item1.title,color=0xB88EEA, url=item1.url)
    embed.add_field(name="Prix 💸", value=item1.price + " " + item1.currency, inline=True)
    embed.add_field(name="Date de mise en ligne 💻   ", value=item1.created_at_ts)
    embed.add_field(name="Marque 📌", value=item1.brand_title)
    embed.add_field(name="Taille 📏", value=item1.size_title)
    embed.add_field(name="Avis positifs ⭐", value=infos['positive'])
    embed.add_field(name="Avis Négatifs ⛔", value=infos['negative'])
    embed.add_field(name="Ville, Pays 🌍", value=infos['ville'] + ", " + infos['pays'])
    embed.add_field(name="Prix sur le marché 🧱", value= "de " + price + " " + item1.currency + " à " + lowestPrice + " " +item1.currency)

    if(item1.price < price):
        rentable = "Oui"
    elif(item1.price > price):
        rentable = "Non"
    else:
        rentable = "A vérifier"

    embed.add_field(name="Rentable ❓", value=rentable)
    embed.set_image(url=item1.photo)
    print("Embed send")
    await ctx.send(embed=embed)
    
@bot.command()
async def search(ctx, value1, value2, value3):
    shoe = ""
    sneakers = "sneakers"
    jordan = "jordan"

    brand = ""
    nike = "nike"
    adidas = "adidas"

    if (value1 == sneakers):
        shoe = sneakers
    elif (value1 == jordan):
        shoe = jordan
    elif (value1 == nike):
        shoe = nike
    elif (value1 == adidas):
        shoe = adidas

    minPrice = 0
    maxPrice = 0

    minPrice = value2
    maxPrice = value3

    itemsapple = vinted.items.search('https://www.vinted.fr/vetements?search_text='+shoe+'&price_from='+minPrice+'&price_to='+maxPrice)
    item1 = itemsapple[random.randint(0,20)]

    infos = get_vinted_info(item1.url)

    embed = discord.Embed(title=item1.title, color=0x8C2AE1, url=item1.url)
    embed.add_field(name="Prix 💸", value=item1.price + " " + item1.currency, inline=True)
    embed.add_field(name="Date de mise en ligne 💻   ", value=item1.created_at_ts)
    embed.add_field(name="Marque 📌", value=item1.brand_title)
    embed.add_field(name="Taille 📏", value=item1.size_title)
    embed.add_field(name="Avis positifs ⭐", value=infos['positive'])
    embed.add_field(name="Avis Négatifs ⛔", value=infos['negative'])
    embed.add_field(name="Ville, Pays 🌍", value=infos['ville'] + ", " + infos['pays'])
    embed.set_image(url=item1.photo)
    print("Embed send")
    await ctx.send(embed=embed)

@bot.command()
async def auto(ctx, value1, value2, value3, value4):
    shoe = ""
    sneakers = "sneakers"
    jordan = "jordan"

    brand = ""
    nike = "nike"
    adidas = "adidas"

    minPrice = value2
    maxPrice = value3
    price = "N/A"
    lowestPrice = "N/A"

    if (get_sneakers(item1.title)):
        json_data = json.dumps(get_sneakers(item1.title).pop(0))
        data = json.loads(json_data)
        price = str(data['retail_price'])
        lowestPrice = str(data['lowest_price'])
        
    if (value1 == sneakers):
        shoe = sneakers
    elif (value1 == jordan):
        shoe = jordan
    elif (value1 == nike):
        shoe = nike
    elif (value1 == adidas):
        shoe = adidas

    link = 'https://www.vinted.fr/vetement?search_text='+shoe+'&brand_id[]='+brand+'&price_from='+minPrice+'&price_to='+maxPrice+'&status[]=6&catalog[]=5&size_id[]='

    for i in range(int(value4)):
        itemshoe = vinted.items.search(link,50,random.randint(1,5))
        item1 = itemshoe[random.randint(0,50)]
        infos = get_vinted_info(item1.url)
        embed = discord.Embed(title=item1.title,color=0xB88EEA, url=item1.url)
        embed.add_field(name="Prix 💸", value=item1.price + " " + item1.currency, inline=True)
        embed.add_field(name="Date de mise en ligne 💻   ", value=item1.created_at_ts)
        embed.add_field(name="Marque 📌", value=item1.brand_title)
        embed.add_field(name="Taille 📏", value=item1.size_title)
        embed.add_field(name="Avis positifs ⭐", value=infos['positive'])
        embed.add_field(name="Avis Négatifs ⛔", value=infos['negative'])
        embed.add_field(name="Ville, Pays 🌍", value=infos['ville'] + ", " + infos['pays'])
        embed.add_field(name="Prix sur le marché 🧱", value=price + " " + item1.currency + " ou " + lowestPrice + item1.currency)
        embed.set_image(url=item1.photo)
        print("Embed send")

        await ctx.send(embed=embed)
        time.sleep(12)



bot.run("OTY1NTYzNjU3MTk3MDYwMTc3.Yl1BOw.LrsHBMVWP11C5J8l_jV71GVWCpw")