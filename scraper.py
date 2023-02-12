import requests
import json
import re
import networkx as nx
from bs4 import BeautifulSoup
import time
import html

def getPrice(soup):
  price = -1
  discount = 0
  purchaseTag = soup.find("div", class_="game_purchase_action_bg")
  if purchaseTag is not None:
    priceTag = purchaseTag.find("div", class_="game_purchase_price price")
    disPriceTag = purchaseTag.find("div", class_="discount_final_price")
    discountTag = purchaseTag.find("div", class_="discount_pct")
    if priceTag is None:
      if disPriceTag is None or discountTag is None:
        price = -2
      else:
        price = float(disPriceTag.text.strip().replace("$", ""))
        discount = float(discountTag.text.strip().replace("%", "").replace("-", ""))
    elif priceTag.text.strip().find("Free") != -1:
      price = 0  
    elif priceTag.text.strip()[0] != "$":
      price = -1
    else:
      price = float(priceTag.text.strip().replace("$", ""))
  return (price, discount)

def getTags(soup):
  tagsTags = soup.find_all("a", class_="app_tag")
  tags = ["", "", ""]
  for i in range(3):
    if i < len(tagsTags):
      tags[i]= tagsTags[i].text.strip()
  return tags

def addNode(G, id, name, soup=None):
  if soup is None:
    page = requests.get("http://store.steampowered.com/app/" + str(id))
    soup = BeautifulSoup(page.text, 'html.parser')
  price, discount = getPrice(soup)
  tags = getTags(soup)

  G.add_node(html.unescape(name), id=id, price=price, discount=discount, tag1=tags[0], tag2=tags[1], tag3=tags[2])


URL = "http://store.steampowered.com/explore/random/"
G = nx.DiGraph()

nodes = int(input("How many nodes? "))

start = time.time()

try:
  for z in range(nodes):
    print(z+1)
    recList = []

    page = requests.get(URL)
    soup = BeautifulSoup(page.text, 'html.parser')
    nameTag = soup.find("div", class_="apphub_AppName")
    if nameTag is None:
      continue
    name = nameTag.text.strip()
    idTag = soup.find("div", class_="glance_tags popular_tags")
    if idTag is None:
      continue
    id = idTag['data-appid']
    if not G.has_node(name):
      addNode(G, id, name, soup)

    recommendations = re.search("{\"rgApps\".*", page.text)
    recString = recommendations.group(0)
    recString = recString.replace(");", "")
    recsDict = json.loads(recString)['rgApps']

    for i in range(5):
      if i < len(recsDict):
        id = list(recsDict.keys())[i]
        recList.append((recsDict[id]['name'], id))

    #print(nameTag.text)
    #print(idTag['value'])
    #print(recList)
    for rec in recList:
      if not G.has_node(rec[0]):
        addNode(G, rec[1], rec[0])
      #print(html.unescape(name) + " -> " + html.unescape(rec[0]))
      G.add_edge(html.unescape(name), html.unescape(rec[0]))
except KeyboardInterrupt:
  print("Exiting Loop...")
except AttributeError:
  print("❌ AttributeError: saving current progress...")

#nx.write_gml(G, path=f"./.graphs/steam{str(nodes)}.gml")
nx.write_gexf(G, path=f"./.graphs/steam{str(nodes)}.gexf")

end = time.time()

print("Complete!\nFinished in: " + str(end - start))
