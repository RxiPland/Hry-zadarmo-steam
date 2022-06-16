# udělal RxiPland
# python 3.9.12
# 2022

from requests import get
from re import findall

def main():

    URL = "https://store.steampowered.com/search/?maxprice=free&specials=1"

    r = get(URL, headers={"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.115 Safari/537.36"})

    html_list = (r.text).splitlines(True)

    free_hry = []

    for x, line in enumerate(html_list):
        if ("<span class=\"title\">" in line) and ("Free" in html_list[x+16] or "0,--€" in html_list[x+16]):
            line = str(line).replace("<", ">")
            free_hry.append({"Nazev": (line.split(">"))[2], "Odkaz": findall("(?:https).*/" ,html_list[x-7].strip())[0]})

    return free_hry



free_hry = main()

for i, item in enumerate(free_hry):
    print(i+1, "  " ,item["Nazev"], " "*5, item["Odkaz"])