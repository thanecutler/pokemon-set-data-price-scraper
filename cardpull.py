import mysql.connector
import requests
import re
import time
from uuid import uuid4
from datetime import datetime
from bs4 import BeautifulSoup

mydb = mysql.connector.connect(
  host="localhost",
  user="python",
  password= '!QAZ@WSX1qaz2wsx',
  database="set_data_schema"
)

c = mydb.cursor()

# sets and url stem
url_stem = 'https://shop.tcgplayer.com/price-guide/pokemon/'
page_raw = requests.get(url_stem)
soup = BeautifulSoup(page_raw.text, 'html.parser')

sets = soup.findAll('select', 'priceGuideDropDown')[1]
options = sets.findAll('option')

set_name_list = [option['value'] for option in options]

for set_name in set_name_list:

    html = requests.get(url_stem + set_name)
    set_url = url_stem + set_name
    print('Connecting to ' + url_stem + set_name)
    set_soup = BeautifulSoup(html.text, 'html.parser')
    rows = set_soup.find_all('tr', {'class':['odd', 'even']})
    set_price = 0
    card_count = 0

    # begin row loop

    for row in rows:
        title = row.find('div', class_ = 'productDetail').text.strip()
        rarity = row.find('td', class_ = 'rarity').text.strip()
        number = row.find('td', class_ = 'number').text.strip()
        set_name = set_name.replace('-', ' ').title()
        url = row.find('div', class_ = 'productDetail').find('a')['href']

        try:
            price = float(re.findall('([0-9,]*\.[0-9]*)', row.find('td', class_ = 'marketPrice').text.replace(',', ''))[0])
        except:
            price = 0

        set_price += price
        card_count += 1
        sql = 'INSERT INTO card_data_table (card_name, set_name, price, rarity, card_number, url) VALUES (%s, %s, %s, %s, %s, %s)'
        values = (title, set_name, price, rarity, number, url)
        c.execute(sql, values)

    set_price = round(set_price, 2)   
    set_sql = "INSERT INTO set_data_table (uuid, set_name, set_value, url, card_count) VALUES (%s, %s, %s, %s, %s)"
    set_values = (str(uuid4()), set_name, set_price, set_url, card_count)
    c.execute(set_sql, set_values)
    
    print(set_price)
    # end row loop
    
    mydb.commit()
    print('Added ' + set_name + ' to db')
    time.sleep(10)

print('Finished at ' + datetime.now())