import requests
import json
import re
import networkx as nx
from bs4 import BeautifulSoup
import time

URL = "http://store.steampowered.com/explore/random/"
G = nx.DiGraph()

nodes = int(input("How many nodes?"))

start = time.time()

try:
  for z in range(nodes):
    print(z)
    recList = []

    page = requests.get(URL)
    soup = BeautifulSoup(page.text, 'html.parser')
    nameTag = soup.find("div", class_="apphub_AppName")
    idTag = soup.find("input", id="review_appid")

    recommendations = re.search("{\"rgApps\".*", page.text)
    recString = recommendations.group(0)
    recString = recString.replace(");", "")
    recsDict = json.loads(recString)['rgApps']

    for i in range(5):
      if i < len(recsDict):
        recList.append((recsDict[list(recsDict.keys())[i]]['name'], list(recsDict.keys())[i]))

    #print(nameTag.text)
    #print(idTag['value'])
    #print(recList)
    for rec in recList:
      G.add_edge(nameTag.text, rec[0])
except KeyboardInterrupt:
  print("Exiting Loop...")

nx.write_gml(G, path=f"./.graphs/steam{str(nodes)}.gml")

end = time.time()

print("Complete!\nFinished in: " + str(end - start))
