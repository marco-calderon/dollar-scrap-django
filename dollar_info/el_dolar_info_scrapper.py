from bs4 import BeautifulSoup
from datetime import datetime
from selenium import webdriver
import logging

class ElDolarInfoScrapper():
    def __init__(self):
        options = webdriver.ChromeOptions()

        options.add_argument('headless')
        browser = webdriver.Chrome(options=options)
        self.browser = browser

        print('Succesfully initialized scraper.')
        logging.info('Succesfully initialized scraper.')

    def scrap_today(self):
        history_url = 'https://www.eldolar.info/en/mexico/dia/'
        print('Scraping today {0}...'.format(history_url))
        logging.info('Scraping today {0}...'.format(history_url))

        try:
            self.browser.get(history_url)
            print('Finished getting url.')
            logging.info('Finished getting url.')
            parsed = BeautifulSoup(self.browser.page_source, 'html.parser')
            print('Parsed website.')
            logging.info('Parsed website.')
            table = parsed.find('tbody')
            if table is not None:
                print('Found table!')
                logging.debug('Found table!')
                trs = table.find_all('tr')
                print('{0} rows found.'.format(len(trs)))
                logging.debug('{0} rows found.'.format(len(trs)))
                tds = trs[1].find_all('td')
                if len(tds) == 4:
                    date_str = tds[0].find('a')['href'].replace('/en/mexico/dia/', '');
                    date = datetime.strptime(date_str, '%Y%m%d')
                    print('Found record, {0}'.format(date_str))
                    logging.info('Found record, {0}'.format(date_str))
                    return {
                        'date': date,
                        'buy_price': float(tds[1].text),
                        'sell_price': float(tds[2].text)
                    }
                else:
                    print('Format is not valid. Please verify website format.')
                    logging.warning('Format is not valid. Please verify website format.')
                    self.close()
                    return None
            else:
                print('Table not found on page.')
                logging.warning('Table not found on page.')
                self.close()
                return None
        except Exception as e: 
            print(e)
            logging.error(e)
            self.close()
            return None

    def scrap_history(self):
        history_url = 'https://www.eldolar.info/en/mexico/dia/'
        print('Scraping history {0}...'.format(history_url))
        logging.info('Scraping history {0}...'.format(history_url))

        try:
            self.browser.get(history_url)
            print('Finished getting url.')
            logging.info('Finished getting url.')
            parsed = BeautifulSoup(self.browser.page_source, 'html.parser')
            print('Parsed website.')
            logging.info('Parsed website.')
            table = parsed.find('tbody')
            if table is not None:
                print('Found table!')
                logging.debug('Found table!')
                trs = table.find_all('tr')
                print('{0} rows found.'.format(len(trs)))
                logging.debug('{0} rows found.'.format(len(trs)))
                for tr in trs:
                    tds = tr.find_all('td')
                    if len(tds) == 4:
                        date_str = tds[0].find('a')['href'].replace('/en/mexico/dia/', '');
                        date = datetime.strptime(date_str, '%Y%m%d')
                        print('Found record for day {0}'.format(date_str))
                        logging.info('Found record for day {0}'.format(date_str))
                        yield {
                            'date': date,
                            'buy_price': float(tds[1].text),
                            'sell_price': float(tds[2].text)
                        }
            else:
                print('Table not found on page.')
                logging.warning('Table not found on page.')
                self.close()
        except Exception as e: 
            print(e)
            logging.error(e)
            self.close()

    def close(self):
        self.browser.close()
        self.browser.quit()