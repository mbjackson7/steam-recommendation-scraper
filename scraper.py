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
                recentReviews = int(
                    re.sub('[(),]', "", recentReviewsTag.text.strip()))
                recentRatio = 1.0
        if len(data) == 2:
            allRatingTag = data[1].find(
                "span", class_="game_review_summary")
            if allRatingTag is not None:
                allRating = allRatingTag.text.strip()
            allReviewsTag = data[1].find("span", class_="responsive_hidden")
            if allReviewsTag is not None:
                allReviews = int(
                    re.sub('[(),]', "", allReviewsTag.text.strip()))
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

def is_dlc(soup):
    dlc = False
    dlcTag = soup.find("div", class_="game_area_dlc_bubble")
    if dlcTag is not None:
        dlc = True
    return dlc

def add_node(G, id, name, soup=None):
    # print("Name: " + name)
    if soup is None:
        page = requests.get("http://store.steampowered.com/app/" + str(id))
        soup = BeautifulSoup(page.text, 'html.parser')
    if is_dlc(soup):
        return str(id)
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
    return "added"


def main():
    VERSION = "0.2.2"
    URL = "http://store.steampowered.com/explore/random/"
    G = nx.DiGraph()
    oldRecCount = False
    oldNodeCount = 0
    newPrompt = ""
    dlcList = []

    print("Welcome to Steam Recommendation Scraper v" + VERSION)
    useOld = input("Add to existing graph? (y/n) ")
    
    if useOld == "y":
        newPrompt = "new "
        oldGraphName = input("Old graph name? ")
        G = nx.read_gexf(f"./.graphs/{oldGraphName}")
        print("Loading old graph...")
        print("Loaded graph with " + str(len(G.nodes())) + " nodes")
        oldNodeCount = int(oldGraphName.split("-")[0].replace("steam", ""))
        oldSettings = input("Use previous settings? (y/n) ")
        if oldSettings == "y":
            oldRecCount = True
            recCount = int(oldGraphName.split("-")[1])

    nodes = int(input(f"How many {newPrompt}source nodes? "))
    if not oldRecCount:
        recCount = int(input("How many recommendations per source node? "))

    start = time.time()

    try:
        for z in range(nodes):
            if z+1 % 100 == 0:
                print("Node " + str(z+1) + " of " + str(nodes))
                print("Elapsed time: " + str(time.time() - start) + " seconds")
                print(
                    f"Saving steam{str(oldNodeCount+nodes)}-{str(recCount)}-{VERSION}.gexf...")
                nx.write_gexf(
                    G, path=f"./.graphs/steam{str(oldNodeCount+nodes)}-{str(recCount)}-{VERSION}.gexf")
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
            if not G.has_node(name) and id not in dlcList:
                if add_node(G, id, name, soup).isnumeric():
                    dlcList.append(id)
                    continue

            recList = []
            recommendations = re.search("{\"rgApps\".*", page.text)
            recString = recommendations.group(0)
            recString = recString.replace(");", "")
            recsDict = json.loads(recString)['rgApps']

            for i in range(recCount):
                if i < len(recsDict):
                    id = list(recsDict.keys())[i]
                    recList.append((id, recsDict[id]['name']))

            # print(nameTag.text)
            # print(idTag['value'])
            # print(recList)
            weight = recCount
            for rec in recList:
                refID, refName = rec[0], rec[1]
                if not G.has_node(refName) and refID not in dlcList:
                    if add_node(G, refID, refName).isnumeric():
                        dlcList.append(refID)
                        continue
                # print(html.unescape(name) + " -> " + html.unescape(rec[0]))
                G.add_edge(html.unescape(name), html.unescape(refName), weight=weight)
                weight -= 1
    except KeyboardInterrupt:
        print("Exiting Loop...")
    except AttributeError as e:
        print(e)
        print("❌ AttributeError: saving current progress...")

    # nx.write_gml(G, path=f"./.graphs/steam{str(nodes)}.gml")
    nx.write_gexf(
        G, path=f"./.graphs/steam{str(oldNodeCount+nodes)}-{str(recCount)}-{VERSION}.gexf")

    end = time.time()

    print(
        f"Complete!\nSaved to steam{str(oldNodeCount+nodes)}-{str(recCount)}-{VERSION}.gexf\nFinished in: {str(end - start)} seconds")


if __name__ == "__main__":
    main()
