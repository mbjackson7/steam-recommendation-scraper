import requests
import json
import re
from bs4 import BeautifulSoup

URL = "http://store.steampowered.com/explore/random/"

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
    recList.append((recsDict[list(recsDict.keys())[i]]['name'], list(recsDict.keys())[i]))

print(nameTag.text)
print(idTag['value'])
print(recList)


with open('output.txt', 'w', encoding="utf-8") as f:
    f.write(page.text)
