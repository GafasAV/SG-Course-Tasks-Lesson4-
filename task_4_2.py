import requests
import logging
import concurrent.futures as cf
from lxml import html


__author__ = "Andrew Gafiychuk"


class Scrapper(object):
    """
    class Scrapper - implement methods to get
    some data from page range that user input
    
    """

    def __init__(self, query, p_from, p_to, limit=2):
        self.query = query
        self.p_from = p_from
        self.p_to = p_to
        self.limit = limit
        logging.debug("[-]Scrapper created...")

    def __prepare(self):
        """
        implements Packet Header for HTTP protocol and
        create a client-server session
         
        """
        HEADERS = {
            "Accept": "text/html,application/xhtml+xml,\
                        application/xml;q=0.9,image/web p,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, lzma, sdch",
            "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.6,en;q=0.4",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "Host": "www.olx.ua",
            "Referer": "https://www.olx.ua/",
            "Save-Data": "on",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64)\
                AppleWebKit/537.36 (KHTML, like Gecko) \
                Chrome/54.0.2840.99 Safari/537.36 OPR / 41.0.2353.69",
        }

        self.session = requests.Session()
        self.session.headers.update(HEADERS)

        logging.debug("[-]Header and session are created...")

    def get_link(self, page):
        """
        Create page url to GET data
        
        """
        link = "https://www.olx.ua/chernovtsy/q-{0}/?page={1}" \
            .format(self.query, page)

        return link

    def start(self):
        """
        This method create ThreadPool for multithread GET
        data from server.
        For eache url start new thread.
        
        Return list of data-pair (offer, price)
        
        """
        self.__prepare()

        url_list = []
        items = []

        for pn in range(self.p_from, self.p_to + 1):
            url_list.append(self.get_link(pn))

        with cf.ThreadPoolExecutor(max_workers=self.limit) as tp:
            logging.debug("[-]ThreadPool started...")
            result = tp.map(self.crawl, url_list)

            for el in result:
                for offer, price in el:
                    items.append((offer, price))

        logging.debug("[-]All tasks are done ... result returned...")
        return items

    def crawl(self, url):
        """
        Takes URL, load it, parse and return data-list that contain
        data-pair(offer, price)
        
        if error -> return error code...
        Must be -> (logging.basicConfig(level=logging.DEBUG))
        
        """
        resp = self.session.get(url)

        if resp.status_code == 200:
            logging.debug("[-]Response OK... Data processed...")
            page = resp.text
            root = html.fromstring(page)

            items = []

            offers = root.xpath('//td[@class="offer "]')

            for offer in offers:
                try:
                    title = offer.xpath('.//div[@class="space rel"]'
                                        '/h3/a/strong/text()')[0]
                    price = offer.xpath('.//td[@class="wwnormal '
                                        'tright td-price"]'
                                        '//p/strong/text()')[0]
                    items.append((title, price))
                except ValueError:
                    logging.debug("[-]Response data parse error...")

            logging.debug("[-]Response data parsed... "
                          "Return result list...")

            notify(url)
            return items
        else:
            logging.debug("[-]Bad response... Code {0}..."
                          .format(resp.status_code))


def notify(page_url):
    logging.info("Task done: {0}".format(page_url))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    scrapper = Scrapper("iphone", 1, 9, limit=3)
    results = scrapper.start()

    for res in results:
        offer, price = res
        print(offer, price)

    logging.debug("[-] Program done...")
