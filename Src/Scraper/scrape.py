import os
import time
import requests
import json
import re
from fake_headers import Headers

from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

BASE_DIR = os.path.join(os.path.dirname(__file__))

DATA = {}
chrome_options = Options()
chrome_options.add_argument("--headless")
executable_path = 'C:\Program Files\Google\Chrome\Driver\chromedriver.exe'
driver =  webdriver.Chrome( executable_path = executable_path , chrome_options=chrome_options)

def getRawHTML(name,url,num_resuls= 20):
    # Get the site
    driver =  webdriver.Chrome('chromedriver')
    driver.get(url)
    
    y = 100
    for i in range(20):
        driver.execute_script(f"window.scrollTo(0,{y});")
        y += 500
        time.sleep(0.07)

    # time.sleep(20)
    soup = BeautifulSoup(driver.page_source,'lxml')
    driver.close()
    
    with open(os.path.join(BASE_DIR,f"{name}.html"),'w') as f:
        f.write(soup.prettify())

def parseHotels(name,num_resuls=20):
    
    # Read the HTML
    raw_html = ""
    with open(os.path.join(BASE_DIR,f"{name}.html")) as f:
        raw_html = f.read()


    soup = BeautifulSoup(raw_html,'lxml')

    hotel_listings = soup.find_all('div',class_="sr_property_block")
    
    # Sanity check
    assert(num_resuls <= len(hotel_listings))

    for hotel in hotel_listings[:num_resuls]:
        hotel_name = hotel.find('span', class_="sr-hotel__name").text.strip("\n").strip(" ").strip("\n")
        link = hotel.find('a', class_="js-sr-hotel-link")["href"]
        link = f"https://www.booking.com/{link}".strip("\n").strip(" ").strip("/\n")
        link = link[:24] + link[26:]
        avg_rating = hotel.find('div', class_="bui-review-score__badge").text

        # Regex to match the hotel name from the url
        hotel_id_matcher = re.compile(r'^(https:\/\/www\.booking\.com\/hotel\/[a-zA-Z]{2}\/)([A-Za-z0-9\-]+)(\.en\-gb\.html)')
        hotel_id = hotel_id_matcher.match(link).group(2)


        DATA[name]["hotels"][hotel_id] = {
            "name": hotel_name,
            "url": link,
            "avg_rating": float(avg_rating)
        }


def parseReviewHTML(review_page_html):
    soup = BeautifulSoup(review_page_html, features="lxml")

    reviews_html = soup.findAll('li', class_="review_list_new_item_block")
    reviews = []
    for review in reviews_html:
        # Rating
        rating_num = float(review.find('div',class_='bui-review-score__badge').text)
        # description
        description = "\n".join([comment.text for comment in review.findAll('span', class_="c-review__body")]) 
        
        reviews.append({
            "rating": rating_num,
            "description": description
        })
    return reviews

def getReviewHTML(hotel_id,offset=0):
    url = f"https://www.booking.com/reviewlist.en-gb.html?;cc1=th&pagename={hotel_id}&r_lang=&review_topic_category_id=&type=total&score=&sort=&dist=1&offset={offset}&rows=25&rurl=&text=&translate=&time_of_year=&_=1618393869376"
    a = requests.get(url)
    # headers = {
    #     "Accept": "*/*",
    #     "User-Agent": "PostmanRuntime/7.26.10",
    #     "Connection": "keep-alive"
    # }

    headers = Headers(headers=True).generate()

    # print(json.dumps(headers, indent=4))
    try:
        headers.pop('Accept-Encoding')
    except Exception as e:
        pass 
    response = requests.request("GET", url, headers=headers)
    print(response.status_code)
    if (response.status_code == 200): return response.content
    return -1

def getHotelReviews(hotel_id):

    reviews = []

    for i in range(4):
        HTML = getReviewHTML(hotel_id=hotel_id, offset=(i + 1)* 25)
        if (HTML == -1):
            print("if you get here, things went wrong") 
        reviews.extend(parseReviewHTML(HTML)) 
    return reviews


def scrapeReviewsRoutine():

    with open(os.path.join(BASE_DIR,"../../Data/hotels.json"),'r') as f:
        DATA = json.load(f)

    # with open(os.path.join(BASE_DIR,"../../Data/reviews.json"),'r') as f:
    #     REVIEWS = json.load(f)
    

    REVIEWS = {}

    def saveReviews(REVIEWS):
        with open(os.path.join(BASE_DIR,"../../Data/reviews.json"),'w') as f:
            f.write(json.dumps(REVIEWS,indent=4))


    for city, data in DATA.items():
        for id,hotel_data in data['hotels'].items():
            if (id not in REVIEWS):
                try:
                    REVIEWS[id] = getHotelReviews(id)
                    saveReviews(REVIEWS)
                    print(f"DONE: {id}")
                except Exception as e:
                    print(e)
            else:
                print(f"{id} Aleady Exsists")


# def main():

#     # with open(os.path.join(BASE_DIR,"../../Data/data.json"),'r') as f:
#     #     DATA = json.load(f)

#     for city,data  in DATA.items():

#         # Get Raw HTML
#         # getRawHTML(city,data["url"])

#         # Parse the Inner HTML
#         # parseHotels(city)


    



#     with open(os.path.join(BASE_DIR,"../../Data/data.json"),'w') as f:
#         f.write(json.dumps(DATA, indent=4))


if __name__ == "__main__":
    # main()
    scrapeReviewsRoutine()