#!/usr/bin/env python
import sys
import csv

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.sahibinden.com{}"
car_url = "https://www.sahibinden.com/{}-{}?{}"
car_url_params = "pagingOffset={}"


def return_soup(url):

    # Make get request and return html soup
    headers = {
        'User-Agent':
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1)' +
        'AppleWebKit/537.36 (KHTML, like Gecko)' +
        'Chrome/39.0.2171.95 Safari/537.36'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        return soup
    else:
        print(url)
        print("Status Code : ", str(response.status_code))
        sys.exit(-1)


def clean_value(value):
    
    # Cleans values like 125 hp, 1600 cc etc.
    # Also calculate mean value of valueslike 125 - 150 hp, 1200-1400 cc
    clean_these = [" hp", " cc", " cm3", " - "]
    for clean_this in clean_these:
        if clean_this == " - ":
            val_list = value.lower().split(clean_this)
            if len(val_list) > 1:
                value = (int(val_list[0]) + int(val_list[1])) // 2
                continue
        value = value.lower().split(clean_this)[0]
    return value


def write_csv(elements, price, address):

    details = [clean_value(e.find("span").text.strip()) for e in elements]
    details.append(price)
    details.append(address[0])
    details.append(address[1])
    details.append(address[2])
    """
    fields = [
        "id", "date", "brand", "serie", "model", "year", "fuel",
        "transmission", "km", "type", "hp", "cc", "traction",
        "color", "guarantee", "damage", "Nation", "from_whome",
        "change", "status", "price","city","county","neighborhood"]
    """
    with open("car_details.csv",
              mode='a', encoding="utf-8", newline='') as car_file:
        car_writer = csv.writer(
            car_file, delimiter=',', quotechar='"',
            quoting=csv.QUOTE_MINIMAL)

        car_writer.writerow(details)


def get_car_page(url):

    # get details of given car url
    soup = return_soup(url)
    ul = soup.find("ul", {"class": "classifiedInfoList"})
    li_children = ul.findChildren("li")
    price = soup.find("div", {"class": "classifiedInfo"}).find(
        "h3").text.split("TL")[0].strip()
    address_list = soup.find("div", {"class": "classifiedInfo"}).findAll("a")
    address = [address_list[1].text.strip(),
               address_list[2].text.strip(),
               address_list[3].text.strip()
              ]
    write_csv(li_children, price, address)


def get_list_page(current_page_value):

    #get search result list page of car
    args = sys.argv
    brand = args[1]
    model = args[2]
    model_url_params = car_url_params.format(current_page_value * 20)
    url = car_url.format(brand, model, model_url_params)
    print(url)
    response_soup = return_soup(url)
    a_links = response_soup.findAll("a", {"class": "classifiedTitle"})
    input_value = response_soup.findAll(
        "input", {"id": "currentPageValue"})
    if len(input_value) == 1:
        current_page = int(input_value[0]['value'])
        print(current_page)
    for a in a_links:
        car_link = BASE_URL.format(a['href'])
        get_car_page(car_link)
    return current_page


def main():

    args = sys.argv
    if len(args) != 3:
        print("Parameter Error !")
        print("Send BRAND and MODEL as Parameter !")
        sys.exit(-1)
    else:
        previous_page_value = -1
        current_page_value = 0
        while current_page_value != previous_page_value:
            current_page_value = get_list_page(current_page_value)
            previous_page_value = previous_page_value + 1
        # get_list_page(current_page_value)


if __name__ == "__main__":
    main()
