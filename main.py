# udělal RxiPland
# python 3.9.12
# 2022

# Hry zadarmo (steam)

from PyQt5.QtWidgets import QMainWindow, QApplication
from grafika import Ui_MainWindow_grafika
from time import sleep
from requests import get, Session
from re import findall
from random import randint, choice
from threading import Thread
from datetime import datetime
from json import loads


class grafika(QMainWindow, Ui_MainWindow_grafika):

    def __init__(self, *args, **kwargs):

        QMainWindow.__init__(self, *args, **kwargs)
        self.setupUi(self)

    def vyprseni_platnosti(self, url_hry):

        # vrátí datum a čas vypršení akce
        # [datum, čas] např.: ['23. čvn', '19:00']

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
                konec[1] = konec[1][0:-1:].replace(".", ":")    # přeměna tečky mezi časy na dvojtečku

                return konec

        return "chyba_konec"


    def najit_free_hry(self):

        # projde celé html, najde pouze hry, které mají cenu 0€, zapíše si jejich název a url v obchodě,
        # pak zavolá funkci vyprseni_platnosti(), která vrátí datum a čas vypršení nabídky,
        # všechny hry zadarmo na výstupu budou v jsonu

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

                datum_cas_platnost = self.vyprseni_platnosti(odkaz)     # funkce vyšle požadavek na steam

                if datum_cas_platnost in ["chyba_vek" ,"chyba_konec"]:
                    datum_cas_platnost = [None, None]

                free_hry.append({"Nazev": nazev, "Odkaz": odkaz, "Datum_konec": datum_cas_platnost[0], "Cas_konec": datum_cas_platnost[1]})

                sleep(PRODLEVA)


        with open("hry_zadarmo.txt", "w") as file:
            for item in free_hry:
                file.writelines(str(item) + "\n")

        now = datetime.now()
        d1 = now.strftime("%H:%M:%S;%d.%m.%Y")

        with open("udaje.txt", "w") as file:
            file.write(str({"PosledniCasAktualizace": d1}))


    def spustit(self):

        # zobrazí okno a načte offline data do tabulky (pokud od poslední aktualizace neuběhlo 12h)

        grafika1.show()

        with open("udaje.txt", "r") as file:
            obsah = file.readlines()

        PosledniCasAktualizace = str(loads(obsah[0].replace("\'", "\""))["PosledniCasAktualizace"]).split(";")

        cas = PosledniCasAktualizace[0].split(":")
        datum = PosledniCasAktualizace[1].split(".")

        cas = [int(i) for i in cas]
        datum = [int(i) for i in datum]

        cas_posledni = datetime(datum[2], datum[1], datum[0], cas[0], cas[1], cas[2])
        cas_ted = datetime.now()

        print(cas_ted - cas_posledni)   # vrací milisekundy!
        

        #t = Thread(target=self.najit_free_hry)
        #t.start()



if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    grafika1 = grafika()

    global PRODLEVA
    PRODLEVA = 0.5     # prodleva mezi jednotlivými requesty na steam

    grafika1.spustit()

    #app.aboutToQuit.connect(hl_menu.ukoncit)
    sys.exit(app.exec_())