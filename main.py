# udělal RxiPland
# python 3.9.12
# 2022

# Hry zadarmo (steam)

from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication
from grafika import Ui_MainWindow_grafika
from time import sleep
from requests import get, Session
from re import findall
from random import randint, choice
from datetime import datetime
from json import loads
from os.path import exists
from functools import partial
from webbrowser import open_new_tab
from subprocess import call

class grafika(QMainWindow, Ui_MainWindow_grafika):

    def __init__(self, *args, **kwargs):

        QMainWindow.__init__(self, *args, **kwargs)
        self.setupUi(self)

    def load_data_do_tabulky(self):

        if exists("hry_zadarmo.txt"):

            with open("hry_zadarmo.txt", "r") as file:
                hry_zadarmo = file.readlines()

            if len(hry_zadarmo) > 0:

                aktualni_radek = 0

                for row in hry_zadarmo:

                    row = loads(row.strip().replace("\'", "\""))

                    self.tableWidget.setRowCount(aktualni_radek+1)
                    self.tableWidget.setItem(aktualni_radek, 0, QtWidgets.QTableWidgetItem(row["Nazev"]))
                    self.tableWidget.setItem(aktualni_radek, 1, QtWidgets.QTableWidgetItem(row["Datum_konec"] + " " + row["Cas_konec"]))
                    aktualni_radek += 1
        
            else:

                grafika1.label_2.setHidden(False)

    def vyprseni_platnosti(self, id_hry):

        # vrátí datum a čas vypršení akce
        # [datum, čas] např.: ['23. čvn', '19:00']


        headers=[{"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.115 Safari/537.36"}, {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36 OPR/86.0.4363.70"}, {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.124 Safari/537.36 Edg/102.0.1245.41"}]
        mesice = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]

        url_hry = "https://store.steampowered.com/app/" + id_hry
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


    def najit_free_hry(self, reload_tabulky=False):

        # projde celé html získané z proměnné URL, najde pouze hry, které mají cenu 0€, zapíše si jejich název a url,
        # pak zavolá funkci vyprseni_platnosti(), která vrátí datum a čas vypršení nabídky,
        # všechny hry zadarmo na výstupu budou v jsonu a zapíšou se do souboru hry_zadarmo.txt a také se zapíše
        # poslední datum aktualizace do udaje.txt

        grafika1.pushButton.setEnabled(False)

        URL = "https://store.steampowered.com/search/?maxprice=free&specials=1"
        headers=[{"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.115 Safari/537.36"}, {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36 OPR/86.0.4363.70"}, {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.124 Safari/537.36 Edg/102.0.1245.41"}]

        r = get(URL, headers= choice(headers))
        html_list = (r.text).splitlines(True)

        free_hry = []

        for x, line in enumerate(html_list):
            if ("<span class=\"title\">" in line) and ("Free" in html_list[x+16] or "0,--€" in html_list[x+16]):

                line = str(line).replace("<", ">")
                nazev = line.split(">")[2]
                id_hry = str(findall("(?:https).*/" ,html_list[x-7].strip())[0]).split("/")[4]

                datum_cas_platnost = self.vyprseni_platnosti(id_hry)     # funkce vyšle požadavek na steam

                if datum_cas_platnost in ["chyba_vek" ,"chyba_konec"]:
                    datum_cas_platnost = [None, None]

                free_hry.append({"Nazev": nazev, "Id_hry": id_hry, "Datum_konec": datum_cas_platnost[0], "Cas_konec": datum_cas_platnost[1]})

                sleep(PRODLEVA)


        with open("hry_zadarmo.txt", "w") as file:
            for item in free_hry:
                file.writelines(str(item) + "\n")

        now = datetime.now()
        d1 = now.strftime("%H:%M:%S %d.%m.%Y")

        with open("udaje.txt", "w") as file:
            file.write(str({"PosledniCasAktualizace": d1}))
        self.nastavit_label_zelene()

        if reload_tabulky == True:
            self.tableWidget.setRowCount(0)
            self.load_data_do_tabulky()

        grafika1.pushButton.setEnabled(True)

    def posledni_aktualizace(self):

        # zjistí, kdy byly hry v seznamu naposledy aktualizovány a vykoná automatickou aktualizace (více než 12h) / označí text červeně (více než 1h)

        if exists("udaje.txt"):

            with open("udaje.txt", "r") as file:
                obsah = file.readlines()

            PosledniCasAktualizace = str(loads(obsah[0].replace("\'", "\""))["PosledniCasAktualizace"]).split(" ")

            cas = PosledniCasAktualizace[0].split(":")
            datum = PosledniCasAktualizace[1].split(".")

            cas = [int(i) for i in cas]
            datum = [int(i) for i in datum]

            cas_posledni = datetime(datum[2], datum[1], datum[0], cas[0], cas[1], cas[2])
            cas_ted = datetime.now()

            rozdil_mezi_casy = cas_ted - cas_posledni

            rozdil_mezi_casy_sec = rozdil_mezi_casy.total_seconds()

            if rozdil_mezi_casy_sec > 42200:    # dvanáct hodin (v sec)
                # aktualizovat automaticky
                self.najit_free_hry()

            elif rozdil_mezi_casy_sec < 3600:   # jedna hodina (v sec)
                # pouze změnit text a nastavit zelenou barvu
                self.nastavit_label_zelene(int(rozdil_mezi_casy_sec//60))
        else:

            self.najit_free_hry()

    def otevrit_v_prohlizeci(self):

        # otevře vybranou hru v prohlížeči

        vybrany_radek = self.tableWidget.currentRow()

        if vybrany_radek == -1:
            pass
        else:

            if exists("hry_zadarmo.txt"):

                with open("hry_zadarmo.txt", "r") as file:
                    hry_zadarmo = file.readlines()

            id_vybrane_hry = loads(hry_zadarmo[vybrany_radek].replace("\'", "\""))["Id_hry"]
            url_hry = "https://store.steampowered.com/app/" + id_vybrane_hry

            open_new_tab(url_hry)

            grafika1.tableWidget.setCurrentCell(-1, -1) # resetování pozice vybrané buňky

    def otevrit_v_aplikaci(self):

        # otevře vybranou hru v aplikaci steam

        vybrany_radek = self.tableWidget.currentRow()

        if vybrany_radek == -1:
            pass
        else:
            if exists("hry_zadarmo.txt"):

                with open("hry_zadarmo.txt", "r") as file:
                    hry_zadarmo = file.readlines()

            id_vybrane_hry = loads(hry_zadarmo[vybrany_radek].replace("\'", "\""))["Id_hry"]
            url_hry = "steam://store/" + id_vybrane_hry

            open_new_tab(url_hry)

            grafika1.tableWidget.setCurrentCell(-1, -1) # resetování pozice vybrané buňky

    def pridat_hru(self):

        # automaticky přidá vybranou hru na steam účet, který je zrovna přihlášen v aplikaci

        vybrany_radek = self.tableWidget.currentRow()

        if vybrany_radek == -1:
            pass
        else:
            if exists("hry_zadarmo.txt"):

                with open("hry_zadarmo.txt", "r") as file:
                    hry_zadarmo = file.readlines()

            id_vybrane_hry = loads(hry_zadarmo[vybrany_radek].replace("\'", "\""))["Id_hry"]
            install_url = "steam://install/" + id_vybrane_hry

            open_new_tab(install_url)

            grafika1.tableWidget.setCurrentCell(-1, -1) # resetování pozice vybrané buňky

    def spustit(self):

        # zobrazí okno a načte offline data do tabulky (pokud od poslední aktualizace neuběhlo 12h)

        grafika1.show()
        grafika1.posledni_aktualizace()     # kontrola poslední aktualizace seznamu her
        grafika1.load_data_do_tabulky()     # načtení dat do tabulky

    

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    grafika1 = grafika()

    global PRODLEVA
    PRODLEVA = 0.5     # prodleva mezi jednotlivými requesty na steam

    grafika1.spustit()
    grafika1.pushButton.clicked.connect(partial(grafika1.najit_free_hry,True))
    grafika1.pushButton_2.clicked.connect(grafika1.pridat_hru) # přidat na účet
    grafika1.pushButton_3.clicked.connect(grafika1.otevrit_v_prohlizeci) # otevřít v prohlížeči
    grafika1.pushButton_4.clicked.connect(grafika1.otevrit_v_aplikaci) # otevřít v aplikaci


    #app.aboutToQuit.connect(hl_menu.ukoncit)
    sys.exit(app.exec_())