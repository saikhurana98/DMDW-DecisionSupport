import os
import time
import requests
import json
import re
from bs4 import BeautifulSoup

from selenium import webdriver

BASE_DIR = os.path.join(os.path.dirname(__file__))


# Schema
"""
{
    "city":{
        "url":"http://
        "hotels":[
            {
             "name":"NAME_OF_THE_HOTEL",
             "avg_rating":2.5, # Average Rating of a hotel (out of 10),
             "url":"http://",
             "reviews":[
                 {
                    "rating":5, # Rating of a hotel (out of 10)
                    "comment":"Great Place to stay"
                 }
             ]
            }
        ]
    }
}
""" 


DATA = {
    "Bangkok":{
        "url": "https://www.booking.com/searchresults.html?label=gen173nr-1FCAEoggI46AdIM1gEaGyIAQGYATG4ARnIAQzYAQHoAQH4AQKIAgGoAgO4AqL1z4MGwAIB0gIkOWNiN2U0NmUtZTU4NC00NWJhLTljYmMtZDNiMTM0MjFmYmM02AIF4AIB&sid=0fed03949edb22232735e36077d1581b&sb=1&src=searchresults&src_elem=sb&error_url=https%3A%2F%2Fwww.booking.com%2Fsearchresults.html%3Flabel%3Dgen173nr-1FCAEoggI46AdIM1gEaGyIAQGYATG4ARnIAQzYAQHoAQH4AQKIAgGoAgO4AqL1z4MGwAIB0gIkOWNiN2U0NmUtZTU4NC00NWJhLTljYmMtZDNiMTM0MjFmYmM02AIF4AIB%3Bsid%3D0fed03949edb22232735e36077d1581b%3Btmpl%3Dsearchresults%3Bac_click_type%3Db%3Bac_position%3D0%3Bcheckin_month%3D4%3Bcheckin_monthday%3D19%3Bcheckin_year%3D2021%3Bcheckout_month%3D4%3Bcheckout_monthday%3D21%3Bcheckout_year%3D2021%3Bcity%3D-73635%3Bclass_interval%3D1%3Bdest_id%3D-2403010%3Bdest_type%3Dcity%3Bdtdisc%3D0%3Bfrom_sf%3D1%3Bgroup_adults%3D2%3Bgroup_children%3D0%3Biata%3DKUL%3Binac%3D0%3Bindex_postcard%3D0%3Blabel_click%3Dundef%3Bno_rooms%3D1%3Boffset%3D0%3Bpostcard%3D0%3Braw_dest_type%3Dcity%3Broom1%3DA%252CA%3Bsb_price_type%3Dtotal%3Bsearch_selected%3D1%3Bshw_aparth%3D1%3Bslp_r_match%3D0%3Bsrc%3Dsearchresults%3Bsrc_elem%3Dsb%3Bsrpvid%3D3ce33b392e280045%3Bss%3DKuala%2520Lumpur%252C%2520Kuala%2520Lumpur%2520Federal%2520Territory%252C%2520Malaysia%3Bss_all%3D0%3Bss_raw%3DKuala%3Bssb%3Dempty%3Bsshis%3D0%3Bssne%3DSingapore%3Bssne_untouched%3DSingapore%3Btop_ufis%3D1%26%3B&ss=Bangkok%2C+Bangkok+Province%2C+Thailand&is_ski_area=&ssne=Kuala+Lumpur&ssne_untouched=Kuala+Lumpur&city=-2403010&checkin_year=2021&checkin_month=4&checkin_monthday=19&checkout_year=2021&checkout_month=4&checkout_monthday=21&group_adults=2&group_children=0&no_rooms=1&from_sf=1&ss_raw=Bang&ac_position=1&ac_langcode=en&ac_click_type=b&dest_id=-3414440&dest_type=city&iata=BKK&place_id_lat=13.755838&place_id_lon=100.505638&search_pageview_id=3ce33b392e280045&search_selected=true&search_pageview_id=3ce33b392e280045&ac_suggestion_list_length=5&ac_suggestion_theme_list_length=0",
        "hotels":{}
    },
    "Singapore":{
        "url": "https://www.booking.com/searchresults.html?label=gen173nr-1FCAEoggI46AdIM1gEaGyIAQGYATG4ARnIAQzYAQHoAQH4AQKIAgGoAgO4AqL1z4MGwAIB0gIkOWNiN2U0NmUtZTU4NC00NWJhLTljYmMtZDNiMTM0MjFmYmM02AIF4AIB&sid=0fed03949edb22232735e36077d1581b&sb=1&sb_lp=1&src=index&src_elem=sb&error_url=https%3A%2F%2Fwww.booking.com%2Findex.html%3Flabel%3Dgen173nr-1FCAEoggI46AdIM1gEaGyIAQGYATG4ARnIAQzYAQHoAQH4AQKIAgGoAgO4AqL1z4MGwAIB0gIkOWNiN2U0NmUtZTU4NC00NWJhLTljYmMtZDNiMTM0MjFmYmM02AIF4AIB%3Bsid%3D0fed03949edb22232735e36077d1581b%3Bsb_price_type%3Dtotal%26%3B&ss=Singapore%2C+Singapore&is_ski_area=0&checkin_year=2021&checkin_month=4&checkin_monthday=19&checkout_year=2021&checkout_month=4&checkout_monthday=21&group_adults=2&group_children=0&no_rooms=1&b_h4u_keep_filters=&from_sf=1&ss_raw=Singapore&ac_position=0&ac_langcode=en&ac_click_type=b&dest_id=-73635&dest_type=city&iata=SIN&place_id_lat=1.29045&place_id_lon=103.85204&search_pageview_id=3627369125e30115&search_selected=true",
        "hotels":{}
    },
    "Kuala Lumpur":{
        "url":"https://www.booking.com/searchresults.html?label=gen173nr-1FCAEoggI46AdIM1gEaGyIAQGYATG4ARnIAQzYAQHoAQH4AQKIAgGoAgO4AqL1z4MGwAIB0gIkOWNiN2U0NmUtZTU4NC00NWJhLTljYmMtZDNiMTM0MjFmYmM02AIF4AIB&sid=0fed03949edb22232735e36077d1581b&sb=1&src=searchresults&src_elem=sb&error_url=https%3A%2F%2Fwww.booking.com%2Fsearchresults.html%3Flabel%3Dgen173nr-1FCAEoggI46AdIM1gEaGyIAQGYATG4ARnIAQzYAQHoAQH4AQKIAgGoAgO4AqL1z4MGwAIB0gIkOWNiN2U0NmUtZTU4NC00NWJhLTljYmMtZDNiMTM0MjFmYmM02AIF4AIB%3Bsid%3D0fed03949edb22232735e36077d1581b%3Btmpl%3Dsearchresults%3Bac_click_type%3Db%3Bac_position%3D0%3Bcheckin_month%3D4%3Bcheckin_monthday%3D19%3Bcheckin_year%3D2021%3Bcheckout_month%3D4%3Bcheckout_monthday%3D21%3Bcheckout_year%3D2021%3Bclass_interval%3D1%3Bdest_id%3D-73635%3Bdest_type%3Dcity%3Bdtdisc%3D0%3Bfrom_sf%3D1%3Bgroup_adults%3D2%3Bgroup_children%3D0%3Biata%3DSIN%3Binac%3D0%3Bindex_postcard%3D0%3Blabel_click%3Dundef%3Bno_rooms%3D1%3Boffset%3D0%3Bpostcard%3D0%3Braw_dest_type%3Dcity%3Broom1%3DA%252CA%3Bsb_price_type%3Dtotal%3Bsearch_selected%3D1%3Bshw_aparth%3D1%3Bslp_r_match%3D0%3Bsrc%3Dindex%3Bsrc_elem%3Dsb%3Bsrpvid%3D2c453b2013e20006%3Bss%3DSingapore%252C%2520Singapore%3Bss_all%3D0%3Bss_raw%3DSingapore%3Bssb%3Dempty%3Bsshis%3D0%3Btop_ufis%3D1%26%3B&ss=Kuala+Lumpur%2C+Kuala+Lumpur+Federal+Territory%2C+Malaysia&is_ski_area=&ssne=Singapore&ssne_untouched=Singapore&city=-73635&checkin_year=2021&checkin_month=4&checkin_monthday=19&checkout_year=2021&checkout_month=4&checkout_monthday=21&group_adults=2&group_children=0&no_rooms=1&from_sf=1&ss_raw=Kuala&ac_position=0&ac_langcode=en&ac_click_type=b&dest_id=-2403010&dest_type=city&iata=KUL&place_id_lat=3.154051&place_id_lon=101.707714&search_pageview_id=2c453b2013e20006&search_selected=true&search_pageview_id=2c453b2013e20006&ac_suggestion_list_length=5&ac_suggestion_theme_list_length=0",
        "hotels":{}
    }
}

driver =  webdriver.Chrome('chromedriver')


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
    headers = {
        "Accept": "*/*",
        "User-Agent": "PostmanRuntime/7.26.10",
        "Connection": "keep-alive"
    }
    response = requests.request("GET", url, headers=headers)

    if (response.status_code == 200): return response.content
    return -1

def getHotelReviews(hotel_id):

    reviews = []

    for i in range(4):
        HTML = getReviewHTML(hotel_id=hotel_id, offset=(i + 1)* 25)
        if (HTML != -1): reviews.extend(parseReviewHTML(HTML))
        print("if you get here, things went wrong")
    
    return reviews


def scrapeReviewsRoutine():

    with open(os.path.join(BASE_DIR,"../../Data/hotels.json"),'r') as f:
        DATA = json.load(f)

    with open(os.path.join(BASE_DIR,"../../Data/reviews.json"),'r') as f:
        REVIEWS = json.load(f)
    

    REVIEWS = {}

    for city, data in DATA.items():
        for id,hotel_data in data['hotels'].items():
            try:
                if (id not in REVIEWS):
                    REVIEWS[id] = getHotelReviews(id)
                    with open(os.path.join(BASE_DIR,"../../Data/reviews.json"),'w') as f:
                        f.write(json.dumps(REVIEWS,indent=4))
                    print(f"DONE: {id}")
            except:
                continue        



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