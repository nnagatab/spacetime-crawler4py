from threading import Thread

from utils.download import download
from utils import get_logger
from scraper import scraper
from urllib.parse import urlparse
from urllib import robotparser
import time




class Worker(Thread):
    def __init__(self, worker_id, config, frontier):
        self.logger = get_logger(f"Worker-{worker_id}", "Worker")
        self.config = config
        self.frontier = frontier
        self.robots = dict()
        super().__init__(daemon=True)
        
    def run(self):
        while True:
            try: #added try statement for error handling
                tbd_url = self.frontier.get_tbd_url()
                if not tbd_url:
                    self.logger.info("Frontier is empty. Stopping Crawler.")
                    break
                resp = download(tbd_url, self.config, self.logger)
                self.logger.info(
                    f"Downloaded {tbd_url}, status <{resp.status}>, "
                    f"using cache {self.config.cache_server}.")
                scraped_urls = scraper(tbd_url, resp)
                for scraped_url in scraped_urls:
                    self.frontier.add_url(scraped_url)
                self.frontier.mark_url_complete(tbd_url)
                time.sleep(self.config.time_delay)
            except Exception as error: #catch exceptions and print them to an error report
                print("Error: ", error)
                with open("errorReport.txt", "a+") as error_report:
                    error_report.write("url: " + tbd_url + "\n")
                    error_report.write("Error: " + str(error) + "\n\n")
                continue
