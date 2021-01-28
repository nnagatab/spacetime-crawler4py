import re
import sys
import os

from urllib.parse import urlparse, urljoin, urldefrag
from urllib import robotparser              # using robotparser to read robot.txt
from utils import get_urlhash
from io import *                            # using io for opening with encoding
from bs4 import BeautifulSoup               # using bs4 to go thru html
from lxml import etree, html                # using lxml to parse thru html/xml data
from simhash import Simhash, SimhashIndex   # using simhash to find similarities between pages


# storage for deliverable information
uniqueSite = set()              # set for unique sites that have been visited
robots = dict()                 # dictionary for unique robots
SimIndex = SimhashIndex([])     # using simhash to find similarities (found implementation on StackOverflow)
longest = {"longest_count": 0, "longest_page": ''}  # store longest page and the count of words (Question #2)






def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

def extract_next_links(url, resp):
    # Implementation requred.
    return list()

def is_valid(url):
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
            return False
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise