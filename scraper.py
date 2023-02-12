import requests
import json
import re
import networkx as nx
from bs4 import BeautifulSoup
import time
import html

def addNode(G, id, soup=None):
  if soup is None:
    page = requests.get("http://store.steampowered.com/app/" + str(id))
    soup = BeautifulSoup(page.text, 'html.parser')
  name = soup.find("div", class_="apphub_AppName").text
  priceTag = soup.find("div", class_="game_purchase_price price")
  if priceTag is None:
    price = -2
  elif priceTag.text.strip()[0:3] == "Free":
    price = 0  
  elif priceTag.text.strip()[0] != "$":
    price = -1
  else:
    price = float(priceTag.text.strip().replace("$", ""))
  tagsTags = soup.find_all("a", class_="app_tag")
  tags = []
  for i in range(3):
    if i < len(tagsTags):
      tags.append(tagsTags[i].text.strip())

  G.add_node(html.unescape(name), price=price, id=id, tag1=tags[0], tag2=tags[1], tag3=tags[2])


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
    name = soup.find("div", class_="apphub_AppName").text
    id = soup.find("div", class_="glance_tags popular_tags").attrs['data-appid']
    if not G.has_node(name):
      addNode(G, id, soup)

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
        addNode(G, rec[1])
      print(html.unescape(name) + " -> " + html.unescape(rec[0]))
      G.add_edge(html.unescape(name), html.unescape(rec[0]))
except KeyboardInterrupt:
  print("Exiting Loop...")

#nx.write_gml(G, path=f"./.graphs/steam{str(nodes)}.gml")
nx.write_gexf(G, path=f"./.graphs/steam{str(nodes)}.gexf")

end = time.time()

print("Complete!\nFinished in: " + str(end - start))
