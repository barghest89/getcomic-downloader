import requests
from bs4 import BeautifulSoup
import argparse
import re
import json
import os
from urllib.parse import quote
import sys

url = "https://getcomics.info/page/{}/?s={}"
links_dict = {}

headers_dict = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-language": "en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7,fr;q=0.6",
    "sec-ch-ua": "\" Not;A Brand\";v=\"99\", \"Google Chrome\";v=\"91\", \"Chromium\";v=\"91\"",
    "sec-ch-ua-mobile": "?0",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "upgrade-insecure-requests": "1"
}

headers_dict2 = {
    "accept": "*/*",
    "accept-language": "en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7,fr;q=0.6",
    "origin": "https://disqus.com",
    "sec-ch-ua": "\" Not;A Brand\";v=\"99\", \"Google Chrome\";v=\"91\", \"Chromium\";v=\"91\"",
    "sec-ch-ua-mobile": "?0",
    "sec-fetch-dest": "script",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "cross-site",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
}



def write_to_json(json_dict, filename):
    jsonv = json.dumps(json_dict, indent=True)
    with open(filename, "w") as f:
        f.write(jsonv)


def download_file(link, filename):
    r = requests.get(link, headers=headers_dict, allow_redirects=True)
    print(r.url)
    ftype = r.url.split(".")[-1]
    filename = filename + "." + ftype
    with open(os.path.join("downloads", filename), "wb") as f:
        f.write(r.content)


def getcomic_downloader(page, search):
    download_all = False
    download_none = False
    page_num = 1
    try:
        while (page_num <= page):
            print(page_num)
            r = requests.get(url.format(page_num, search), headers=headers_dict)
            if r.status_code == 404:
                break
            parsed_data = BeautifulSoup(r.content, "html.parser")
            # print (parsed_data)
            posts_lists = parsed_data.find_all("article")
            for p in posts_lists:
                # print(p)
                page_url = p.find_all("a")[2].get("href")
                heading = p.find_all("h1")[0].text
                r2 = requests.get(page_url, headers=headers_dict)
                print(heading)
                page_parsed = BeautifulSoup(r2.content, "html.parser")
                download_button = str(page_parsed.find("div", {"class": "aio-button-center"}))
                if not download_button:
                    print("Could not download " + heading + ". Skipping.")
                    continue
                link_re = re.compile(r"https:\/\/[a-zA-Z0-9.\/\%\-\=\+\:]*")
                link = link_re.search(download_button)
                if not link:
                    print("Could not download " + heading + ". Skipping.")
                elif (link and not download_none):
                # print(link)
                    links_dict[heading] = link

                    if not download_all:
                        reply = input("Download comic {}? y/n/a/N  (a= download all and do not ask again, N = Download none but keep looking for comics)".format(heading))
                        if reply == "a":
                            download_all = True
                        if reply == "N":
                            download_none = True
                            continue
                        if download_all or reply == "y":
                            download_file(link, heading)


            page_num += 1
    except KeyboardInterrupt:
        sys.exit(0)



if __name__ == "__main__":
    getcomic_downloader(99, quote("star wars"))