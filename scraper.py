import re

from urllib.parse import urlparse, urljoin, urldefrag
from urllib import robotparser  # using robotparser to read robot.txt
from io import *  # using io for opening with encoding
from bs4 import BeautifulSoup  # using bs4 to go thru html

# stopwords to ignore
stopwords = {"about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "aren't", "as",
             "at", "be", "because", "been", "before", "being", "below", "between", "both", "but", "by", "can't",
             "cannot", "could", "couldn't", "did", "didn't", "do", "does", "doesn't", "doing", "don't", "down",
             "during", "each", "few", "for", "from", "further", "had", "hadn't", "has", "hasn't", "have", "haven't",
             "having", "he", "he'd", "he'll", "he's", "her", "here", "here's", "hers", "herself", "him", "himself",
             "his", "how", "how's", "i", "i'd", "i'll", "i'm", "i've", "if", "in", "into", "is", "isn't", "it",
             "it's", "its", "itself", "let's""me", "more", "most", "mustn't", "my", "myself", "no", "nor", "not", "of",
             "off", "on", "once", "only", "or", "other", "ought", "our", "ours", "ourselves", "out", "over", "own",
             "same", "shan't", "she", "she'd", "she'll", "she's", "should", "shouldn't", "so", "some", "such", "than",
             "that", "that's", "the", "their", "theirs", "them", "themselves", "then", "there", "there's", "these",
             "they", "they'd", "they'll", "they're", "they've", "this", "those", "through", "to", "too", "under",
             "until", "up", "very", "was", "wasn't", "we", "we'd", "we'll", "we're", "we've", "were", "weren't", "what",
             "what's", "when", "when's", "where", "where's", "which", "while", "who", "who's", "whom", "why",
             "why's", "with", "won't", "would", "wouldn't", "you", "you'd", "you'll", "you're", "you've", "your",
             "yours", "yourself", "yourselves"}

blacklisted = ["https://wics.ics.uci.edu/events/", "https://www.ics.uci.edu/~eppstein/pix/"]
# these websites have little information and a lot of pages


blacklisted_parts = ["/calendar", "share=", "format=xml", "/feed", "/feed/",
                     ".zip", ".sql", "action=login", ".ppt", "version="]
# parts of url that give little information, includes infinite loops like the calendar link


# storage for deliverable information
uniqueDomains = set()  # set for unique sites that have been visited (Question #1)
robots = dict()  # dictionary for unique robots
longest = {"longest_count": 0, "longest_page": ''}  # store longest page and the count of words (Question #2)
pageCount = dict()  # store pages and their word counts (Question #2)
domainCount = dict()  # store domains and subdomain count (Question #4)
wordFrequency = dict()  # Store Common words (Question #3)


# to-do:
# 1. add more trap avoidance and error handling (sortof done)
# 2. implement robot correctly (think i did this right)
# 3. import tokenizer and probably make it taken in html data (taking in soup data)
# 4. finish scrapper and calls to other functions (yes?)
# 5. make scrapper write to files (yes)
# 6. make print statements for visualization in the terminal (yes)
# 7. finsih is_subdomain function to check for subdomains and the counts (yes)
# 8. make write_to function to write to files with information from data storages (yes)


def scraper(url, resp):
    links = extract_next_links(url, resp)
    if resp.raw_response is not None:
        soup = BeautifulSoup(resp.raw_response.text, "html.parser")
        tokenize(url, soup)
    print()
    print("***********************************")
    print("CURRENT URL:", url)
    print("TOTAL SITES VISTED:", len(uniqueDomains))
    print("HTML STATUS:", resp.status)
    print("***********************************")

    found_links = is_subdomain(url, links)
    update_files(url)
    return list(found_links)


def is_subdomain(url, links):
    found_links = set()
    for link in links:
        if is_valid(link):
            found_links.add(link)
            parsed = urlparse(url)
            subdomain = re.match(r"^(www)?(?P<subdomain>.*)\.ics\.uci\.edu.*$", parsed.netloc.lower())
            # used https://regex101.com/ to figure out how to match subdomain
            sub = ""  # initialize variable incase there is no subdomain
            if subdomain is not None:
                sub = subdomain.group("subdomain").strip()  # regex to get subdomain
                if sub is None or sub == "":
                    continue
                elif sub in domainCount:
                    domainCount[sub] += 1
                elif sub not in domainCount:
                    domainCount[sub] = 1
    return found_links


def update_files(url):
    try:
        with open("all_links.txt", "a+") as link_file:  # using a+ to preserve order traversed (question 1)
            link_file.write(url + "\n")

        with open("subdomain_count.txt", "w+") as subdomain_file:  # question 4
            for items in sorted(domainCount.items(), key=lambda x: x[0]):  # sorts by alphabetical order by key
                subdomain_file.write(str(items[0]) + ", " + str(items[1]) + "\n")

        with open("longest_page.txt", "w+") as longest_file:
            longest_file.write(str(longest) + "\n")
            longest_file.write("-------------------------------" + "\n")
            for items in sorted(pageCount.items(), key=lambda x: x[1], reverse=True):  # sorts by longest page
                longest_file.write(str(items[0]) + " -> " + str(items[1]) + "\n")

        with open("word_frequency.txt", "w+") as word_file:
            count = 0
            for item in sorted(wordFrequency.items(), key=lambda x: x[1], reverse=True):
                word_file.write(str(item[0]) + " -> " + str(item[1]) + "\n")
                if count != 50:
                    count += 1
                else:
                    break

    except Exception as e:
        print("Ran into error updating files\n")
        print(str(e) + "\n")


def tokenize(url, soup):    # changed my tokenizer to take soup instead of file name
    try:
        text = soup.get_text()
        pattern = r"\b[a-zA-Z0-9]+\b"  # taken from stack overflow to only find alphanumeric characters
        tokenList = re.findall(pattern, text)  # list that will be returned, I think this is slower
        wordCount = 0   # wordcount for the page so I know how many words were on the page (excluding stopwords)
        for token in tokenList:
            lower = token.lower()
            if lower not in stopwords:
                if len(lower) <= 1:  # ignore single letters
                    continue
                wordCount += 1
                if lower in wordFrequency:  # just combined my wordfrequency from partA into my tokenizer
                    print("adding 1 to wordFrequency")
                    wordFrequency[lower] += 1
                else:
                    print("setting word to 1 wordFrequency")
                    wordFrequency[lower] = 1
        pageCount[url] = wordCount
        if longest["longest_count"] < wordCount:
            longest["longest_count"] = wordCount
            longest["longest_page"] = url
    except Exception as error:
        print("ran into problem tokenizing\n")
        print(str(error) + "\n")


def extract_next_links(url, resp):  # specifications number 3.2, 3.3
    next_links = set()
    base_url = urlparse(url)
    valid = [200, 201, 203]  # list of valid html status codes https://www.w3.org/Protocols/HTTP/HTRESP.html
    if resp.status in valid:
        if url in uniqueDomains:
            return list()

        resp_content = resp.raw_response.headers['Content-Type'].split(';')[0]
        if resp_content != "text/html":
            return list()  # found on stackoverflow on how to read headers

        # uniqueDomains.add(url)
        soup = BeautifulSoup(resp.raw_response.content, "lxml")  # using lxml to read content
        if resp.status == 200 and str(soup) == "":  # making sure website is not empty
            return list()

        for link in soup.find_all("a"):  # uses beautifulsoup to find urls
            link = link.get("href")
            if link is None or link == "":
                continue
            else:
                link = link.lower()  # making link lowercase in order to defragment

            defragmented_url = urldefrag(link)[0]
            fixed_link = fix_url(defragmented_url, base_url)  # need to fix relative links
            if fixed_link not in uniqueDomains:  # makes sure only unique domains are being crawled
                uniqueDomains.add(fixed_link)
                next_links.add(fixed_link)
            else:
                continue
    return list(next_links)  # returns list of set of links (makes sure links are unique)


def fix_url(url, base):
    # need this function in order to deal with relative urls talked about on piazza
    # https://piazza.com/class/kj05cieqyrj620?cid=130

    if url.startswith("//"):  # if starts with '//' just add 'https://'
        returnlink = urljoin("https://", url)
        return returnlink

    elif url.startswith("/"):  # if starts with '/' need to add 'https://' and base url first
        returnlink = urljoin("https://" + base.netloc, url)
        return returnlink

    return url


def is_valid(url):  # implement more trap avoidance
    parsed = urlparse(url)
    try:
        if parsed.scheme not in set(["http", "https"]):
            return False
        for trap in blacklisted:
            if trap in url:
                return False
        for trap in blacklisted_parts:
            if trap in url:
                return False
        valids = set([".ics.uci.edu"
                         , ".cs.uci.edu"
                         , ".informatics.uci.edu"
                         , ".stat.uci.edu"
                         , "today.uci.edu"
                      ])
        for link in valids:
            if link in parsed.netloc:
                break
            else:
                return False

        if re.match(  # changed return to if statement because want to reach is_robot
                r".*\.(css|js|bmp|gif|jpe?g|ico"
                + r"|png|tiff?|mid|mp2|mp3|mp4"
                + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
                + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
                + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
                + r"|epub|dll|cnf|tgz|sha1"
                + r"|thmx|mso|arff|rtf|jar|csv"
                + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower()):
            return False

        is_robot(url, parsed)  # call to check for robots.txt
        return True  # since changed return call to if need to return True

    except TypeError:
        print("TypeError for ", parsed)
        raise


def is_robot(url, parsed):
    # documentation: https://docs.python.org/3/library/urllib.robotparser.html
    # found most of this code on stackoverflow on how to use robots
    # not sure if this works fully but i think it does
    try:
        robots_url = parsed.scheme + "://" + parsed.netloc.lower() + "/robots.txt"  # checking if there is robots.txt
        if parsed.netloc.lower() not in robots:
            robot = robotparser.RobotFileParser()  # starting the robot
            robot.set_url(robots_url)  # setting robot to the url
            if robot:
                robot.read()  # sends the robot to read robots.txt #belive this runs the robots.txt
                robots[parsed.netloc.lower()] = robot  # adds robot to our robots dictionary
        if parsed.netloc.lower() in robots:  # check if robot in dictionary
            return robots[parsed.netloc.lower()].can_fetch("*", url)
        return True
    except Exception as e:  # exception handling
        print("There was no robots.txt")
        print(e)
        return True


if __name__ == "__main__":
    # testing and understanding function calls
    '''
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
    '''
