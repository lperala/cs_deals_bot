import requests
import json
from bs4 import BeautifulSoup
from selenium import webdriver
import time
import re
import pandas as pd
from api_key import api_key, chat_id

# Going through the example provided in:
# https://brightdata.com/blog/how-tos/web-scraping-with-python

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
}

while True:
    browser = webdriver.Firefox()
    url = 'https://cs.deals/fi/market/csgo/?sort=discount&sort_desc=1'
    browser.get(url)
    browser.implicitly_wait(0.5)
    time.sleep(10)
    html = browser.page_source
    soup = BeautifulSoup(html, features="html.parser")
    courts_list = soup.find_all("div", class_ = "item csgo")
    #print(courts_list)
    browser.close()

    # Create a list of 100 first items ordered by discount
    # [name, price, discount]
    complete_list = []
    str_courts_list = str(courts_list)

    # Add item discounts to the list
    discounts_list = re.findall("\"discount\">(.*?)%</span>", str_courts_list)
    discounts_list_rdy = []
    for discount in discounts_list:
        if discount != "?":
            i_float = float(discount) # Discounts are needed in float
            discounts_list_rdy.append(i_float)

    # Add item prices to the list
    prices_list = re.findall("(price\">|small\">)(.*?)€", str_courts_list)
    prices_list_rdy = []
    for j,prices in prices_list:
        prices_changed = prices.replace(",","")
        prices_changed2 = prices_changed.replace(" ", "")
        prices_list_rdy.append(float(prices_changed2)) # Prices are also needed in float

    # Add item names to the list
    names_list_rdy = re.findall("<img alt=\"(.*?)\"", str_courts_list)
    for name in names_list_rdy:
        if name == "CSGO":
            names_list_rdy.remove(name)
        elif name == "sticker":
            names_list_rdy.remove(name)

    # Combine all lists
    for row in range(len(discounts_list_rdy)):
        complete_list.append([names_list_rdy[row], prices_list_rdy[row], discounts_list_rdy[row]])

    #   for item in complete_list:
    #        print(item)

    # Categorize the interesting items
    interesting_list = []
    for item in complete_list:
        if item[1] > 5 and item[2] <= -30: # Interested in high enough price and low enough discount
            interesting_list.append(item)

    # Print interesting items to the terminal
    if interesting_list != None:
        print("\n*******INTERESTING ITEMS*******")
        for i in interesting_list:
            print(i)
        print("*******************************\n")
    else:
        print("\n*****NO INTERESTING ITEMS*****\n")

    # Send interesting items as a telegram message
    bot_token = api_key
    bot_chatID = chat_id
    if interesting_list != None:
        send_intro = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + "name, price, discount"
        response = requests.get(send_intro)
        for i in interesting_list:
            send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + str(i)
            response = requests.get(send_text)

    # Repeat loop every 5 minutes
    time.sleep(300)

