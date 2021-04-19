from selenium import webdriver
import requests
import os
import schedule
import time
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
IFTTT_URL = os.environ.get('ifttt_url')
driver_path = os.environ.get('driverpath')

def code():
    url = "https://www.gpw.pl/spolka?isin=PLOPTTC00011"
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome(driver_path)
    driver.get(url)
    Kupno = driver.find_element_by_xpath('/html/body/section[3]/div[2]/div/div[1]/table[1]/tbody/tr[1]/td[2]').text
    Sprzedaz = driver.find_element_by_xpath('/html/body/section[3]/div[2]/div/div[1]/table[1]/tbody/tr[2]/td[2]').text
    Obroty = driver.find_element_by_xpath('/html/body/section[3]/div[2]/div/div[1]/table[1]/tbody/tr[3]/td[2]').text
    Wol_obrotu = driver.find_element_by_xpath('/html/body/section[3]/div[2]/div/div[1]/table[2]/tbody/tr[1]/td[2]').text
    Kurs_otwarcia = \
        driver.find_element_by_xpath('/html/body/section[3]/div[2]/div/div[1]/table[2]/tbody/tr[2]/td[2]').text
    Kurs_odniesienia = \
        driver.find_element_by_xpath('/html/body/section[3]/div[2]/div/div[1]/table[2]/tbody/tr[3]/td[2]').text
    driver.quit()

    with open('output.txt', "a") as file1:
        sizecheck = f'{os.path.abspath(os.getcwd())}\\output.txt'
        filesize = os.path.getsize(sizecheck)
        if filesize == 0:
            file1.write('Kupno:223.4000\n'
                        'Sprzedaz:229.5000\n'
                        'Obroty:96 738,78\n'
                        'Wol_obrotu:418557\n'
                        'Kurs_otwarcia:233,00\n'
                        'Kurs odniesienia:229,90\n')
            file1.close()
            code()

    try:
        with open("output.txt", "r") as file1:
            all_lines = file1.readlines()
            sprzedaz = all_lines[1]
            obroty = all_lines[3]
            wol_obrotu = all_lines[5]
            kurs_otwarcia = all_lines[7]
            kurs_odniesienia = all_lines[9]
    except IndexError:
        with open("output.txt", "r") as file1:
            all_lines = file1.readlines()
            sprzedaz = all_lines[1]
            obroty = all_lines[2]
            wol_obrotu = all_lines[3]
            kurs_otwarcia = all_lines[4]
            kurs_odniesienia = all_lines[5]

    try:
        roz_sprzedaz = roz(sprzedaz) - roz(Sprzedaz)
        roz_obr = roz(obroty) - roz(Obroty)
        roz_wol = roz(wol_obrotu) - roz(Wol_obrotu)
        roz_kursot = roz(kurs_otwarcia) - roz(Kurs_otwarcia)
        roz_kurodn = roz(kurs_odniesienia) - roz(Kurs_odniesienia)
    except UnboundLocalError:
        pass

    try:
        with open('output.txt', 'w+') as f:
            f.write(f'Kupno:{Kupno}\n'
                    f"Sprzedaz:{Sprzedaz}\n"
                    f'Roznica:{roz_sprzedaz}\n'
                    f"Obroty:{Obroty}\n"
                    f'Roznica:{roz_obr}\n'
                    f"Wol_obrotu:{Wol_obrotu}\n"
                    f'Roznica:{roz_wol}\n'
                    f"Kurs_otwarcia:{Kurs_otwarcia}\n"
                    f'Roznica:{roz_kursot}\n'
                    f'Kurs odniesienia:{Kurs_odniesienia}\n'
                    f'Roznica:{roz_kurodn}')
    except UnboundLocalError:
        with open('output.txt', 'w+') as f:
            f.write(f'Kupno:{Kupno}\n'
                    f"Sprzedaz:{Sprzedaz}\n"
                    f"Obroty:{Obroty}\n"
                    f"Wol_obrotu:{Wol_obrotu}\n"
                    f"Kurs_otwarcia:{Kurs_otwarcia}\n"
                    f'Kurs odniesienia:{Kurs_odniesienia}')

    with open('output.txt', 'r') as file:
        info = file.read().rstrip('\n')

    def email_alert(info):
        report = dict()
        report["value1"] = info
        requests.post(IFTTT_URL, data=report)

    email_alert(info)


def roz(data):
    return float(data.replace(',', '.').replace(' ', '').split(":", 1)[-1])


schedule.every(1).hour.do(code)
while True:
    schedule.run_pending()
    time.sleep(2)
