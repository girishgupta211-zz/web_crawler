import urllib.request as urlrq
from collections import Counter
from collections import defaultdict
from urllib import error
from urllib.parse import urlparse

import certifi
from bs4 import BeautifulSoup
from bs4.element import Comment

in_memory_store = {}

stopwords = set(
    ['ourselves', 'hers', 'between', 'yourself', 'but', 'again', 'there', 'about', 'once', 'during', 'out', 'very',
     'having', 'with', 'they', 'own', 'an', 'be', 'some', ' for ', 'do', 'its', 'yours', 'such', 'into', 'of',
     'most', 'itself', 'other', 'off', ' is ', 's', 'am', ' or ', 'who', 'as', 'from ', 'him', 'each', 'the',
     'themselves',
     'until', 'below', 'are', 'we', 'these', 'your', 'his', 'through', 'don', 'nor', 'me', 'were', 'her', 'more',
     'himself', 'this', 'down', 'should', 'our', 'their', 'while ', 'above', 'both', 'up', 'to', 'ours', 'had',
     'she', 'all', 'no', 'when', 'at', 'any', 'before', 'them', 'same', ' and ', 'been', 'have', ' in ', 'will', 'on',
     'does', 'yourselves', 'then', 'that', 'because', 'what', 'over', 'why', 'so', 'can', 'did', ' not ', 'now',
     'under',
     'he', 'you', 'herself', 'has', 'just', 'where', 'too', 'only', 'myself', 'which', 'those', 'i', 'after', 'few',
     'whom', 't', 'being', ' if ', 'theirs', 'my', 'against', 'a', 'by', 'doing', 'it', 'how', 'further', 'was',
     'here',
     'than', '&', '-', 'and', 'from', 'is', 'for', '=', ',', 'the', 'in'])


def crawl_urls(url_list, crawled_urls, url, domain):
    """ get a set of urls and crawl each url recursively"""
    print("parsing {}".format(url))
    # Once the url is parsed, add it to crawled url list
    crawled_urls.append(url)
    try:
        html = urlrq.urlopen(url, cafile=certifi.where()).read()
    except error.URLError as ex:
        print(ex.args)

    soup = BeautifulSoup(html, features="lxml")
    urls = soup.findAll("a")

    # Even if the url is not part of the same domain, it is still collected
    # But those urls not in the same domain are not parsed
    for a in urls:
        if (a.get("href")) and (a.get("href") not in url_list):
            url_list.append(a.get("href"))

    # Recursively parse each url within same domain
    for page in set(url_list):  # set to remove duplicates
        # Check if the url belong to the same domain And if this url is already parsed ignore it
        if (urlparse(page).netloc == domain) and (page not in crawled_urls):
            crawl_urls(url_list, crawled_urls, page, domain)

    # Once all urls are crawled return the list to calling function
    else:
        return crawled_urls, url_list


def fetch_valid_urls(urls, parent_url):
    result = []
    for url in urls:
        if url[0] == '/':
            result.append(parent_url + url)

    print(result)
    return result


def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, Comment):
        return False
    return True


def get_top_10_words(list_words):
    wordcount = {}
    # To eliminate duplicates, remember to split by punctuation, and use case demiliters.
    for words in list_words:
        for word in words.split(' '):
            if word.lower() not in stopwords:
                if word not in wordcount:
                    wordcount[word] = 1
                else:
                    wordcount[word] += 1
    if '' in wordcount:
        del wordcount['']

    word_counter = Counter(wordcount)
    top_10 = word_counter.most_common(10)
    print(top_10)
    return top_10


def extract_words(valid_urls):
    urls_dict = defaultdict(lambda: ('title', list))
    for i, link in enumerate(valid_urls):
        html = urlrq.urlopen(link, cafile=certifi.where()).read()
        soup = BeautifulSoup(html, features="lxml")
        title = soup.title.string
        print(title)
        texts = soup.findAll(text=True)
        visible_texts = filter(tag_visible, texts)
        list_words = [t.strip() for t in visible_texts if t.strip() is not ""]
        top_10_words = get_top_10_words(list_words)
        urls_dict[link] = (title, top_10_words)
    return urls_dict


def crawl_page(parent_url, unique_id):
    url_list = list()
    crawled_urls = list()
    url_list.append(parent_url)
    domain = urlparse(parent_url).netloc
    crawled_urls, url_list = crawl_urls(url_list, crawled_urls, parent_url, domain)
    print(crawled_urls)
    print(url_list)
    valid_urls = fetch_valid_urls(url_list, parent_url)
    # store these results against unique_id in db
    result = extract_words(valid_urls)
    in_memory_store[unique_id] = result
    return result
