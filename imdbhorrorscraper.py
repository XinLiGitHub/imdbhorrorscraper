from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np
import re
import dateutil.parser as dparser
from decimal import Decimal
IterList = []

TitleList = []
YearList = []
RatingList = []
LinkList = []

def first_scrape():

    for x in range(1000, 2100):
    # for x in range(1000, 1300):
        if (x % 50) == 1:
            IterList.append(x)

    for n in IterList:

        print("Scraping " + str(n))
        url = "https://www.imdb.com/search/title/?title_type=feature&num_votes=5000,&genres=horror&view=simple&sort=release_date,asc&start=%s&ref_=adv_nxt" % n
        req = requests.get(url)
        soup = BeautifulSoup(req.text, "html.parser")
        title = soup.findAll('span', {'class': 'lister-item-header'}, {'title'})
        year = soup.findAll('span', {'class': 'lister-item-year text-muted unbold'})
        rating = soup.findAll('div', {'class': 'col-imdb-rating'})
        link = soup.find_all('a')

        for i in title:
            TitleList.append(i.get_text()[7:-9].replace('\n', ' '))
            # print(i.get_text()[7:-9].replace('\n', ' '))

        for i in year:
            YearList.append(re.sub("\D", "", i.get_text()))

        for i in rating:
            # print(i.get_text().replace(' ', ''))
            RatingList.append(re.sub(r'\s+', '', i.get_text()))
            # print(re.sub(r'\s+', '', i.get_text()))

        for i in link:
            if "/title/tt" in i.get('href'):
                if (i.get('href')) not in LinkList:
                    LinkList.append(i.get('href'))

    # print(len(LinkList))
    data = {
        "Title": TitleList,
        "Year": YearList,
        "Rating": RatingList,
        "Link": LinkList
    }

    df = pd.DataFrame(data)
    print(df)
    
testList = ["/title/tt12873562/", "/title/tt13314558/"]
# second_scrape is to look thru the urls for each of the movies to get money and date data
def second_scrape():
    for n in LinkList:
    # for n in testList:
        url = "https://www.imdb.com%s" % n
        # add this header because imdb hates scrapers
        headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36"}
        req = requests.get(url, headers=headers)
        soup = BeautifulSoup(req.text, "html.parser")
        money = soup.findAll('li', {'class': 'ipc-metadata-list__item sc-6d4f3f8c-2 fJEELB'})
        date = soup.findAll('li', {'data-testid': 'title-details-releasedate'})
        
        # this is to append to the list nothing so it doesn't mess up dataframe
        budgetBool = False
        grossBool = False
        print("Scraping " + url + "...")
        for i in money:
            if "Budget" in i.get_text():
                budgetBool = True
                budgetText = i.get_text()[6:]
                # print(budgetText + " (OG)")
                budgetText = laundry_machine(budgetText)
                # print(budgetText)

            if "Gross worldwide" in i.get_text():
                grossBool = True
                grossText = i.get_text()[15:]
                grossText = laundry_machine(grossText)

        if budgetBool:
            print(budgetText)
        else:
            print("no budget")

        if grossBool:
            print(grossText)
        else:
            print("no gross")
            
        for i in date:
            print(i.get_text()[12:])
        # things to figure out, different currencies, need net, formatting it to append, 
        # do i have to adjust for inflation? lmao
        print("\n")

# this is convert and clean up currency to make it all USD
def laundry_machine(temp):
    temp.replace(' ', "")
    if "(estimated)" in temp:
        temp = temp.replace('(estimated)', '')
    if "€" in temp:
        temp = ("$" + str(float(temp[1:].replace(',', ""))*1.04))
    if "£" in temp:
        temp = ("$" + str(float(temp[1:].replace(',', ""))*1.21))
    if "NOK" in temp:
        temp = ("$" + str(float(temp[3:].replace(',', ""))*.1))
    if "A$" in temp:
        if "CA$" in temp:
            temp = ("$" + str(float(temp[3:].replace(',', ""))*.75))
        else:
            temp = ("$" + str(float(temp[2:].replace(',', ""))*.68))
    if "HK$" in temp:
        temp = ("$" + str(float(temp[3:].replace(',', ""))*.128))
    if "NZ$" in temp:
        temp = ("$" + str(float(temp[3:].replace(',', ""))*.63))
    if "MX$" in temp:
        temp = ("$" + str(float(temp[3:].replace(',', ""))*.0516))
    if "NT$" in temp:
        temp = ("$" + str(float(temp[3:].replace(',', ""))*.0325))
    if "$" in temp:
        temp = float(temp[1:].replace(',', ""))
        
    return temp

def main():
    first_scrape()
    second_scrape()
    # s1 = "2012 (United Kingdom)"

    # dparser.parse(s1, fuzzy = True)
    # print(dparser.parse(s1, fuzzy = True))
    # string = "€15"
    # if "€" in string:
    #     print(int(string[1:])*1.04)
if __name__ == "__main__":
    main()
# print(len(TitleList))
# print(len(YearList))
# print(len(RatingList))
# print(len(LinkList))
# print(YearList)
# print(RatingList)
# print(LinkList)
# print(TitleList)

 
# for i in range(len(LinkList)):
#     print(i)
#     print(LinkList[i])

# https://www.imdb.com/search/title/?title_type=feature&num_votes=1000,&genres=horror&view=simple&sort=release_date,desc
# https://www.imdb.com/search/title/?title_type=feature&num_votes=1000,&genres=horror&view=simple&sort=release_date,desc&start=1&ref_=adv_nxt