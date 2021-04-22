from bs4 import BeautifulSoup
import requests

def main():
    url = "https://www.booking.com/reviewlist.en-gb.html?;cc1=th&pagename=like-sukhumvit16&r_lang=&review_topic_category_id=&type=total&score=&sort=&dist=1&offset=0&rows=25&rurl=&text=&translate=&time_of_year=1618393869376"
    print(url)
    headers = {
        "Accept": "*/*",
        "User-Agent": "PostmanRuntime/7.26.10",
        "Connection": "keep-alive"
    }
    response = requests.get(url, headers=headers, data={})
    print(response.content)

if __name__ == '__main__':
    main()