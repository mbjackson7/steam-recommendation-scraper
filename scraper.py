import requests
import json
import re
import networkx as nx
from bs4 import BeautifulSoup
import time
import html


def get_price(soup):
    price = -1.0
    discount = 0
    purchaseTag = soup.find("div", class_="game_purchase_action_bg")
    if purchaseTag is not None:
        priceTag = purchaseTag.find("div", class_="game_purchase_price price")
        disPriceTag = purchaseTag.find("div", class_="discount_final_price")
        discountTag = purchaseTag.find("div", class_="discount_pct")
        if priceTag is None:
            if disPriceTag is None or discountTag is None:
                price = -2.0
            else:
                price = float(disPriceTag.text.strip().replace("$", ""))
                discount = int(discountTag.text.strip().replace(
                    "%", "").replace("-", ""))
        elif priceTag.text.strip().find("Free") != -1:
            price = 0.0
        elif priceTag.text.strip()[0] != "$":
            price = -1.0
        else:
            price = float(priceTag.text.strip().replace("$", ""))
    return (price, discount)


def get_tags(soup):
    tagsTags = soup.find_all("a", class_="app_tag")
    tags = ["", "", ""]
    for i in range(3):
        if i < len(tagsTags):
            tags[i] = tagsTags[i].text.strip()
    return tags


def get_review_data(soup):
    reviewData = soup.find("div", id="userReviews")
    recentRating = "N/A"
    recentReviews = -1
    allRating = "N/A"
    allReviews = -1
    recentRatio = 0.0
    if reviewData is not None:
        data = reviewData.find_all("div", class_="user_reviews_summary_row")
        if len(data) > 0:
            recentRatingTag = data[0].find(
                "span", class_="game_review_summary")
            if recentRatingTag is not None:
                recentRating = recentRatingTag.text.strip()
            recentReviewsTag = data[0].find("span", class_="responsive_hidden")
            if recentReviewsTag is not None:
                recentReviews = int(re.sub('[(),]', "", recentReviewsTag.text.strip()))
        if len(data) == 2:
            allRatingTag = data[1].find(
                "span", class_="game_review_summary")
            if allRatingTag is not None:
                allRating = allRatingTag.text.strip()
            allReviewsTag = data[1].find("span", class_="responsive_hidden")
            if allReviewsTag is not None:
                allReviews = int(re.sub('[(),]', "", allReviewsTag.text.strip()))
            if allReviews != 0:
                recentRatio = float(recentReviews / allReviews)
        else:
            allRating = recentRating
            allReviews = recentReviews
    return (recentRating, recentReviews, allRating, allReviews, recentRatio)


def get_release_data(soup):
    releaseDate = ""
    year = 0
    releaseData = soup.find("div", class_="date")
    if releaseData is not None:
        releaseDate = releaseData.text.strip()
        if releaseDate[-4:].isnumeric():
            year = int(releaseDate[-4:])
    return releaseDate, year


def get_genres_and_developer(soup):
    genres = ["", "", ""]
    developer = ""
    publisher = ""
    franchise = ""
    allData = soup.find("div", id="genresAndManufacturer")
    if allData is not None:
        genreBlock = allData.find("span")
        if genreBlock is not None:
            genreTags = genreBlock.find_all("a")
            for i in range(3):
                if i < len(genreTags):
                    genres[i] = genreTags[i].text.strip()
        developerData = allData.find_all("div", class_="dev_row")
        if developerData is not None:
            developer = developerData[0].find("a").text.strip()
            if len(developerData) > 1:
                publisher = developerData[1].find("a").text.strip()
            if len(developerData) > 2:
                franchise = developerData[2].find("a").text.strip()
    return genres, developer, publisher, franchise


def add_node(G, id, name, soup=None):
    #print("Name: " + name)
    if soup is None:
        page = requests.get("http://store.steampowered.com/app/" + str(id))
        soup = BeautifulSoup(page.text, 'html.parser')
    price, discount = get_price(soup)
    tags = get_tags(soup)
    releaseDate, year = get_release_data(soup)
    recentRating, recentReviews, allRating, allReviews, recentRatio = get_review_data(
        soup)
    genres, developer, publisher, franchise = get_genres_and_developer(soup)

    G.add_node(
        html.unescape(name),
        id=id,
        price=price,
        discount=discount,
        releaseDate=releaseDate,
        year=year, tag1=tags[0],
        tag2=tags[1],
        tag3=tags[2],
        recentRating=recentRating,
        recentReviews=recentReviews,
        allRating=allRating,
        allReviews=allReviews,
        recentRatio=recentRatio,
        genre1=genres[0],
        genre2=genres[1],
        genre3=genres[2],
        developer=developer,
        publisher=publisher,
        franchise=franchise
    )


URL = "http://store.steampowered.com/explore/random/"
G = nx.DiGraph()

nodes = int(input("How many nodes? "))

start = time.time()

try:
    for z in range(nodes):
        if (z+1) % 10 == 0:
            print("Node " + str(z+1) + " of " + str(nodes))
        if z % 100 == 0:
            print("Saving...")
            nx.write_gexf(G, path=f"./.graphs/steam{str(nodes)}.gexf")
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
            add_node(G, id, name, soup)

        recList = []
        recommendations = re.search("{\"rgApps\".*", page.text)
        recString = recommendations.group(0)
        recString = recString.replace(");", "")
        recsDict = json.loads(recString)['rgApps']

        for i in range(5):
            if i < len(recsDict):
                id = list(recsDict.keys())[i]
                recList.append((recsDict[id]['name'], id))

        # print(nameTag.text)
        # print(idTag['value'])
        # print(recList)
        for rec in recList:
            if not G.has_node(rec[0]):
                add_node(G, rec[1], rec[0])
            # print(html.unescape(name) + " -> " + html.unescape(rec[0]))
            G.add_edge(html.unescape(name), html.unescape(rec[0]))
except KeyboardInterrupt:
    print("Exiting Loop...")
except AttributeError as e:
    print(e)
    print("❌ AttributeError: saving current progress...")

# nx.write_gml(G, path=f"./.graphs/steam{str(nodes)}.gml")
nx.write_gexf(G, path=f"./.graphs/steam{str(nodes)}.gexf")

end = time.time()

print("Complete!\nFinished in: " + str(end - start))
