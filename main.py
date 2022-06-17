# udělal RxiPland
# python 3.9.12
# 2022

# Hry zadarmo (steam)

from time import sleep
from requests import get, Session
from re import findall
from random import randint, choice

def vyprseni_platnosti(url_hry):

    headers=[{"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.115 Safari/537.36"}, {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36 OPR/86.0.4363.70"}, {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.124 Safari/537.36 Edg/102.0.1245.41"}]
    mesice = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

    id_hry = url_hry.split("/")[4]
    url_AgeSetCheck = "https://store.steampowered.com/agecheckset/app/" + id_hry

    session1 = Session()
    session1.cookies.set("Steam_Language", "czech")
    session1.cookies.set("timezoneOffset", "7200,0")
    r = session1.get(url= url_hry, headers= choice(headers))

    
    session_id = (session1.cookies.get_dict())['sessionid']    
    udaje = {"sessionid": session_id, "ageDay": randint(1, 30), "ageMonth": choice(mesice), "ageYear": randint(1970,2002)}

    r2 = session1.post(url=url_AgeSetCheck, data=udaje, cookies=(r.cookies.get_dict()), headers= choice(headers))

    if str(r2.text) == '{"success":1}':
        pass
    else:
        return "chyba_vek"

    r = session1.get(url=url_hry ,headers= choice(headers))

    html_list = (r.text).splitlines(True)

    for line in html_list:
        if "game_purchase_discount_quantity" in line:
            line.replace("<", ">")
            konec = line.strip().split(">")[1].split("\t")[0].split("do ")[1].split(". v ")

            return konec

    return "chyba_konec"

def main():

    URL = "https://store.steampowered.com/search/?maxprice=free&specials=1"
    headers=[{"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.115 Safari/537.36"}, {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36 OPR/86.0.4363.70"}, {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.124 Safari/537.36 Edg/102.0.1245.41"}]

    r = get(URL, headers= choice(headers))

    html_list = (r.text).splitlines(True)

    free_hry = []

    for x, line in enumerate(html_list):
        if ("<span class=\"title\">" in line) and ("Free" in html_list[x+16] or "0,--€" in html_list[x+16]):

            line = str(line).replace("<", ">")
            nazev = line.split(">")[2]
            odkaz = findall("(?:https).*/" ,html_list[x-7].strip())[0]

            datum_cas_platnost = vyprseni_platnosti(odkaz)

            if datum_cas_platnost in ["chyba_vek" ,"chyba_konec"]:
                datum_cas_platnost = [None, None]

            free_hry.append({"Nazev": nazev, "Odkaz": odkaz, "Datum": datum_cas_platnost[0], "Cas": datum_cas_platnost[1]})

            sleep(0.5)

    return free_hry

free_hry = main()