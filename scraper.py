import requests

URL = "http://store.steampowered.com/explore/random/"
page = requests.get(URL)

print(page.text)
