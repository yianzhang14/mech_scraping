
import numpy as np
import pandas as pd
import bs4 as bs
import requests

MAX_PAGES = 10

def get_links(url, query="products"):
    url = url + "?page="

    paths = []
    for i in range(1, MAX_PAGES + 1):
        data = requests.get(url + str(i))
        html = bs.BeautifulSoup(data.text, 'html.parser')
        for link in html.find_all('a'):
            ref = link.get('href')
            if ref != None and query in ref:
                paths.append(ref)
    return list(set(paths))
    
def get_novelkeys_keycaps(base, url):
    url = url + "?page="
    paths = []
    prices = []
    for i in range(1, MAX_PAGES + 1):
        data = requests.get(url + str(i))
        html = bs.BeautifulSoup(data.text, 'html.parser')
        for link in html.find_all('a'):
            ref = link.get('href')
            if "products" in ref:
                paths.append(ref)
        
        for price in html.find_all(class_="product-card-details-grid"):
            prices.append(price.contents[3].text.strip())
    prices = list(map(lambda x: x[-4:].strip("\t"), prices))

    result = pd.DataFrame(index=range(len(paths)))
    for i, path in enumerate(paths):
        link = base + path
        curr = requests.get(link)
        text = bs.BeautifulSoup(curr.text, 'html.parser')
        
        result.loc[i, "vender"] = text.find("meta", {"property": "og:site_name"}).get("content")
        result.loc[i, "url"] = link
        result.loc[i, "product"] = text.find("meta", {"property": "og:title"}).get("content")
        result.loc[i, "description"] = text.find("meta", {"property": "og:description"}).get("content")
        result.loc[i, "image"] = text.find("meta", {"property": "og:image"}).get("content")
        
        result.loc[i, "status"] = text.find(attrs="product-flag").text.strip("\n\\ ")
        
    
    result["prices"] = prices
    
    return result

def get_dang(base, url):
    paths = get_links(url)

    result = pd.DataFrame(index=range(len(paths)))
    for i, path in enumerate(paths):
        link = base + path
        curr = requests.get(link)
        text = bs.BeautifulSoup(curr.text, 'html.parser')
        
        result.loc[i, "vender"] = text.find("meta", {"property": "og:site_name"}).get("content")
        result.loc[i, "url"] = link
        result.loc[i, "product"] = text.find("meta", {"property": "og:title"}).get("content")
        result.loc[i, "description"] = text.find("meta", {"property": "og:description"}).get("content")
        result.loc[i, "image"] = text.find("meta", {"property": "og:image"}).get("content")
        
        result.loc[i, "price"] = text.find(class_="price-item price-item--regular").text.strip("\n\\ ")
        
        # description contains groupbuy/preorder
        for span in text.find_all('span'):
            if "data-add-to-cart-text" in span.attrs:
                result.loc[i, "in_stock"] = str(span.contents).strip("[\n]\\n' ")
                break
        
        for option in text.find_all('option'):
            if "selected" in option.attrs:
                result.loc[i, "kit"] = str(option.contents).strip("[\n]\\n' ")
    
    return result


# def get_cannon_keycaps(base, url, price_query, preorder_type, in_stock_query):
#     paths = get_links(url)

#     result = pd.DataFrame(index=range(len(paths)))
#     for i, path in enumerate(paths):
#         link = base + path
#         curr = requests.get(link)
#         text = bs.BeautifulSoup(curr.text, 'html.parser')
        
#         result.loc[i, "vender"] = text.find("meta", {"property": "og:site_name"}).get("content")
#         result.loc[i, "url"] = link
#         result.loc[i, "product"] = text.find("meta", {"property": "og:title"}).get("content")
#         result.loc[i, "description"] = text.find("meta", {"property": "og:description"}).get("content")
#         result.loc[i, "image"] = text.find("meta", {"property": "og:image"}).get("content")
        
#         if text.find(class_=price_query) != None:
#             result.loc[i, "price"] = text.find(class_=price_query).text.strip("\n\\ ")

#         if preorder_type:
#             pass
#         else:
#             pass
        
#         if i == 1:
#             break
        
#         # result.loc[i, "in_stock"] = text.find(attrs=in_stock_query).text.strip("\n\\ ")
    
#     return result

def get_space_keycaps(base, url):
    url = url + "?page="
    paths = []
    prices = []
    seen = set()
    for i in range(1, MAX_PAGES + 1):
        data = requests.get(url + str(i))
        html = bs.BeautifulSoup(data.text, 'html.parser')
        for link in html.find_all('a'):
            ref = link.get('href')
            if ref != None and "products" in ref and ref not in seen:
                seen.add(ref)
                paths.append(ref)
        for price in html.find_all(class_="price-box"):
            prices.append(price.contents[1].contents[1].text.strip())
            
    actual_price = prices[::2]

    result = pd.DataFrame(index=range(len(paths)))
    for i, path in enumerate(paths):
        link = base + path
        curr = requests.get(link)
        text = bs.BeautifulSoup(curr.text, 'html.parser')
        
        result.loc[i, "vender"] = text.find("meta", {"property": "og:site_name"}).get("content")
        result.loc[i, "url"] = link
        result.loc[i, "product"] = text.find("meta", {"property": "og:title"}).get("content")
        result.loc[i, "description"] = text.find("meta", {"property": "og:description"}).get("content")
        result.loc[i, "image"] = text.find("meta", {"property": "og:image"}).get("content")
        
        result.loc[i, "live"] = text.find("div", id="gb-confirm") == None

    result["price"] = actual_price
    return result

def get_osume_keycaps(base, url):
    paths = get_links(url)

    result = pd.DataFrame(index=range(len(paths)))
    for i, path in enumerate(paths):
        link = base + path
        curr = requests.get(link)
        text = bs.BeautifulSoup(curr.text, 'html.parser')
        
        result.loc[i, "vender"] = text.find("meta", {"property": "og:site_name"}).get("content")
        result.loc[i, "url"] = link
        result.loc[i, "product"] = text.find("meta", {"property": "og:title"}).get("content")
        result.loc[i, "description"] = text.find("meta", {"property": "og:description"}).get("content")
        result.loc[i, "image"] = text.find("meta", {"property": "og:image"}).get("content")
        
        result.loc[i, "in_stock"] = True
        
        if text.find(class_="price-item price-item--regular") == None:
            result.loc[i, "in_stock"] = False
        else:
            result.loc[i, "price"] = text.find(class_="price-item price-item--regular").text.strip("\n\\ ")
    
        
    result["live"] = True
    
    return result

def get_kono_keycaps(base, url, price_query, in_stock_query):
    paths = get_links(url)

    result = pd.DataFrame(index=range(len(paths)))
    for i, path in enumerate(paths):
        link = base + path
        curr = requests.get(link)
        text = bs.BeautifulSoup(curr.text, 'html.parser')
        
        result.loc[i, "vender"] = text.find("meta", {"property": "og:site_name"}).get("content")
        result.loc[i, "url"] = link
        result.loc[i, "product"] = text.find("meta", {"property": "og:title"}).get("content")
        result.loc[i, "description"] = text.find("meta", {"property": "og:description"}).get("content")
        result.loc[i, "image"] = text.find("meta", {"property": "og:image"}).get("content")
        
        result.loc[i, "price"] = text.find(class_="price__current").contents[1].text.strip("\n\\ ")
        
        result[i, "live"] = text.find(class_="product__badge product__badge--status product__badge--custom badge--custom") == None
    
        
    
    
    return result


def get_keys_keycaps():
    base = "https://thekey.company"
    url = "https://thekey.company/collections/in-stock/keycaps"
    paths = get_links(url)

    result = pd.DataFrame(index=range(len(paths)))
    for i, path in enumerate(paths):
        link = base + path
        curr = requests.get(link)
        text = bs.BeautifulSoup(curr.text, 'html.parser')
        
        result.loc[i, "vender"] = text.find("meta", {"property": "og:site_name"}).get("content")
        result.loc[i, "url"] = link
        result.loc[i, "product"] = text.find("meta", {"property": "og:title"}).get("content")
        result.loc[i, "description"] = text.find("meta", {"property": "og:description"}).get("content")
        result.loc[i, "image"] = text.find("meta", {"property": "og:image"}).get("content")
        
        result.loc[i, "price"] = text.find(class_="product-single__price").text.strip("\n\\ ")
        
    result["in_stock"] = True
    
        
    
    
    return result


# get_dang("https://dangkeebs.com", "https://dangkeebs.com/collections/keycaps",).to_csv("dang.csv")
# get_keycaps("https://cannonkeys.com", "https://cannonkeys.com/collections/keycaps", "current-price theme-money", True, "no").to_csv("cannon.csv")
# get_space_keycaps("https://spaceholdings.net", "https://spaceholdings.net/collections/keycaps").to_csv('space.csv')
# get_keycaps("https://kbdfans.com", "https://kbdfans.com/collections/keycaps", "theme-money large-title", True, "badgetitle primebText prime-font-adjust ").to_csv("kbd.csv")

get_keys_keycaps().to_csv("keys.csv")