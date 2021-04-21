from selenium import webdriver
import requests
import os
import schedule
import time
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
IFTTT_URL = os.environ.get('ifttt_url')
driver_path = os.environ.get('driverpath')


# Scrapes the necessary information from the site
def code():
    url = "https://www.gpw.pl/spolka?isin=PLOPTTC00011"
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome(driver_path)
    driver.get(url)
    Bid = driver.find_element_by_xpath('/html/body/section[3]/div[2]/div/div[1]/table[1]/tbody/tr[1]/td[2]').text
    Ask = driver.find_element_by_xpath('/html/body/section[3]/div[2]/div/div[1]/table[1]/tbody/tr[2]/td[2]').text
    Turnover = driver.find_element_by_xpath('/html/body/section[3]/div[2]/div/div[1]/table[1]/tbody/tr[3]/td[2]').text
    Trading_volume = \
        driver.find_element_by_xpath('/html/body/section[3]/div[2]/div/div[1]/table[2]/tbody/tr[1]/td[2]').text
    Opening_price = \
        driver.find_element_by_xpath('/html/body/section[3]/div[2]/div/div[1]/table[2]/tbody/tr[2]/td[2]').text
    Reference_price = \
        driver.find_element_by_xpath('/html/body/section[3]/div[2]/div/div[1]/table[2]/tbody/tr[3]/td[2]').text
    driver.quit()
# If file doesn't exit or is empty, it creates one and fills it with the sample
    with open('output.txt', 'a') as file1:
        sizecheck = f'{os.path.abspath(os.getcwd())}\\output.txt'
        filesize = os.path.getsize(sizecheck)
        if filesize == 0:
            file1.write('Bid price:223.4000\n'
                        'Ask price:229.5000\n'
                        'Turnover:96 738,78\n'
                        'Trading volume:418557\n'
                        'Opening price:233,00\n'
                        'Reference price:229,90\n')
            file1.close()
            code()
# Reads all lines from file in order to compare value changes
    try:
        with open('output.txt', 'r') as file1:
            all_lines = file1.readlines()
            bid = all_lines[0]
            ask = all_lines[2]
            turnover = all_lines[4]
            trading_volume = all_lines[6]
            opening_price = all_lines[8]
            reference_price = all_lines[10]
    except IndexError:
        with open('output.txt', 'r') as file1:
            all_lines = file1.readlines()
            bid = all_lines[0]
            ask = all_lines[1]
            turnover = all_lines[2]
            trading_volume = all_lines[3]
            opening_price = all_lines[4]
            reference_price = all_lines[5]

# Compares the values (code activates every 1 hour)
    try:
        pd_bid = roz(bid) - roz(Bid)
        pd_ask = roz(ask) - roz(Ask)
        pd_turnover = roz(turnover) - roz(Turnover)
        pd_trading_volume = roz(trading_volume) - roz(Trading_volume)
        pd_opening_price = roz(opening_price) - roz(Opening_price)
        pd_reference_price = roz(reference_price) - roz(Reference_price)
    except (UnboundLocalError, ValueError):
        pass
# Fills the file with new values and compared values
    try:
        with open('output.txt', 'w+') as f:
            f.write(f'Bid price:{Bid}\n'
                    f'Difference in bid:{pd_bid}\n'
                    f'Ask price:{Ask}\n'
                    f'Difference in ask:{pd_ask}\n'
                    f"Turnover:{Turnover}\n"
                    f'Difference in turnover:{pd_turnover}\n'
                    f'Trading volume:{Trading_volume}\n'
                    f'Difference in trading volume:{pd_trading_volume}\n'
                    f'Opening price:{Opening_price}\n'
                    f'Difference in opening price:{pd_opening_price}\n'
                    f'Reference price:{Reference_price}\n'
                    f'Difference in reference price:{pd_reference_price}')
    except UnboundLocalError:
        with open('output.txt', 'w+') as f:
            f.write(f'Bid price:{Bid}\n'
                    f'Ask price:{Ask}\n'
                    f'Turnover:{Trading_volume}\n'
                    f'Trading volume:{Opening_price}\n'
                    f'Opening price:{Opening_price}\n'
                    f'Reference price:{Reference_price}')
# Sends the file content to gmail
    with open('output.txt', 'r') as file:
        info = file.read().rstrip('\n')

    def email_alert(info):
        report = dict()
        report['value1'] = info
        requests.post(IFTTT_URL, data=report)

    email_alert(info)


# Function responsible for splitting and replacing
def roz(data):
    return float(data.replace(',', '.').replace(' ', '').split(':', 1)[-1])


# Activates the code every 1 hour
schedule.every(1).hour.do(code)
while True:
    schedule.run_pending()
    time.sleep(2)
