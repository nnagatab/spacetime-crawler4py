import re
import sys
import os

from urllib.parse import urlparse, urljoin, urldefrag
from urllib import robotparser              # using robotparser to read robot.txt
from utils import get_urlhash
from io import *                            # using io for opening with encoding
from bs4 import BeautifulSoup               # using bs4 to go thru html
from lxml import etree, html                # using lxml to parse thru html/xml data


# storage for deliverable information
uniqueDomains = set()                      # set for unique sites that have been visited
robots = dict()                         # dictionary for unique robots
longest = {"longest_count": 0, "longest_page": ''}  # store longest page and the count of words (Question #2)
pageCount = dict()                      # store pages and their word counts
domainCount = dict()                    # store domains and subdomain count (question 4)
wordFrequency = dict()


def scraper(url, resp):
    #global longest,pageCount, domainCount, wordFrequency
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]


def extract_next_links(url, resp):      # specifications number 3.2, 3.3
    next_links = set()
    base_url = urlparse(url)
    valid = [200, 201, 203]     # list of valid html status codes https://www.w3.org/Protocols/HTTP/HTRESP.html
    if resp.status in valid:
        if url in uniqueDomains:
            return list()

        resp_content = resp.raw_response.headers['Content-Type'].split(';')[0]
        if resp_content != "text/html":
            return list()   # found on stackoverflow on how to read headers

        # uniqueDomains.add(url)
        soup = BeautifulSoup(resp.raw_response.content, "lxml")     # using lxml to read content
        if resp.status == 200 and str(soup) == "":      # making sure website is not empty
            return list()

        for link in soup.findall("a"):      # uses beautifulsoup to find urls
            link = link.get("href")
            if link is None or link is "":
                continue
            else:
                link = link.lower()     # making link lowercase in order to defragment

            defragmented_url = urldefrag(link)[0]
            fixed_link = fix_url(defragmented_url, base_url)    # need to fix relative links
            if fixed_link not in uniqueDomains:   # makes sure only unique domains are being crawled
                uniqueDomains.add(fixed_link)
                next_links.add(fixed_link)
            else:
                continue
    return list(next_links)     # returns list of set of links (makes sure links are unique)


def fix_url(url,base):
    # need this function in order to deal with relative urls talked about on piazza

    if url.startswith("//"):    # if starts with '//' just add 'https://'
        returnlink = urljoin("https://", url)
        return returnlink

    elif url.startswith("/"):   # if starts with '/' need to add 'https://' and base url first
        returnlink = urljoin("https://" + base.netloc, url)
        return returnlink

    return url


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


def add_domain(extractedLinks):
    global domainCount


if __name__ == "__main__":
    # testing and understanding function calls

    url = "http://www.ics.uci.edu#bbb"
    x = urlparse(url)
    print(url)
    print(x)
    pure, frag = urldefrag(url)
    print(pure)
    print(frag)
    print("//")
    base = urlparse("https://swiki.ics.uci.edu")
    url2 = "//uci.edu/coronavirus/"
    url3 = "/doku.php/start"
    pure = urldefrag(url2)[0]
    pure2 = urldefrag(url3)[0]
    print(fix_url(pure, base))
    print(fix_url(pure2, base))

