
import numpy as np
import pandas as pd
import bs4 as bs
import requests
import re

headers = {
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36'}

MAX_PAGES = 10

def get_links(url, query="products"):
    url = url + "?page="

    paths = []
    for i in range(1, MAX_PAGES + 1):
        data = requests.get(url + str(i), headers=headers)
        html = bs.BeautifulSoup(data.text, 'html.parser')
        for link in html.find_all('a'):
            ref = link.get('href')
            if ref != None and query in ref:
                paths.append(ref)
    return list(set(paths))
    
def get_novelkeys_keycaps():
    base = "https://novelkeys.com"
    url = "https://novelkeys.com/collections/keycaps"
    
    url = url + "?page="
    paths = []
    prices = []
    for i in range(1, MAX_PAGES + 1):
        data = requests.get(url + str(i), headers=headers)
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
        
        result.loc[i, "vender"] = "NovelKeys"
        result.loc[i, "url"] = link
        result.loc[i, "product"] = text.find("meta", {"property": "og:title"}).get("content")
        result.loc[i, "description"] = text.find("meta", {"property": "og:description"}).get("content")
        result.loc[i, "image"] = text.find("meta", {"property": "og:image"}).get("content")
        
        result.loc[i, "live"] = text.find(attrs="product-flag").text.strip("\n\\ ")
        
    result["price"] = prices
    
    result = result[~result["price"].str.contains("Sold out")]
    result["live"] = np.where(result["live"].isin(["LIMITED STOCK", "IN STOCK", "CLEARANCE"]), True, False)
    
    return result

def get_dang_keycaps():
    base = "https://dangkeebs.com"
    url = "https://dangkeebs.com/collections/keycaps"
    
    paths = get_links(url)

    result = pd.DataFrame(index=range(len(paths)))
    for i, path in enumerate(paths):
        link = base + path
        curr = requests.get(link, headers=headers)
        text = bs.BeautifulSoup(curr.text, 'html.parser')
        
        result.loc[i, "vender"] = "DangKeebs"
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
                
    result = result[result["in_stock"] == "Add to cart"]
    result["live"] = result["product"].str.contains("\[")
    result = result.drop(["in_stock", "kit"], axis=1)
    
    return result


def get_cannon_keycaps():
    base = "https://cannonkeys.com"
    url = "https://cannonkeys.com/collections/keycaps"
    
    paths = get_links(url)

    result = pd.DataFrame(index=range(len(paths)))
    for i, path in enumerate(paths):
        link = base + path
        if ("https://cannonkeys.com" in path):
            link = base + path[22:]
        curr = requests.get(link, headers=headers)
        text = bs.BeautifulSoup(curr.text, 'html.parser')
        
        result.loc[i, "vender"] = "CannonKeys"
        result.loc[i, "url"] = link
        result.loc[i, "product"] = text.find("meta", {"property": "og:title"}).get("content")
        result.loc[i, "description"] = text.find("meta", {"property": "og:description"}).get("content")
        result.loc[i, "image"] = text.find("meta", {"property": "og:image"}).get("content")
        
        result.loc[i, "live"] = True
        result.loc[i, "in_stock"] = True
        
        if text.find(class_="current-price theme-money") != None:
            result.loc[i, "price"] = text.find(class_="current-price theme-money").text.strip("\n\\ ")

        if text.find(class_="confirm-checkbox flexrow") != None:
            result.loc[i, "live"] = False
            
        if text.find(class_="product-unavailable") != None:
            result.loc[i, "in_stock"] = False
        
        # result.loc[i, "in_stock"] = text.find(attrs=in_stock_query).text.strip("\n\\ ")
        
    result = result[result["in_stock"]]
    result = result.drop(["in_stock"], axis=1)
    
    return result

def get_space_keycaps():
    base = "https://spaceholdings.net"
    url = "https://spaceholdings.net/collections/keycaps"
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
        
        result.loc[i, "vender"] = "Space Holdings"
        result.loc[i, "url"] = link
        result.loc[i, "product"] = text.find("meta", {"property": "og:title"}).get("content")
        result.loc[i, "description"] = text.find("meta", {"property": "og:description"}).get("content")
        result.loc[i, "image"] = text.find("meta", {"property": "og:image"}).get("content")
        
        result.loc[i, "live"] = text.find("div", id="gb-confirm") == None

    result["price"] = actual_price
    return result

def get_osume_keycaps():
    base = "https://osumekeys.com"
    url = "https://osumekeys.com/collections/keycaps"
    paths = get_links(url)

    result = pd.DataFrame(index=range(len(paths)))
    for i, path in enumerate(paths):
        link = base + path
        curr = requests.get(link)
        text = bs.BeautifulSoup(curr.text, 'html.parser')
        
        result.loc[i, "vender"] = "Osume"
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
    result = result[result["in_stock"]]
    result = result.drop(["in_stock"], axis=1)
    
    return result

def get_kono_keycaps():
    base = "https://kono.store"
    url = "https://kono.store/collections/keycap-sets"
    
    paths = get_links(url)

    result = pd.DataFrame(index=range(len(paths)))
    for i, path in enumerate(paths):
        link = base + path
        curr = requests.get(link)
        text = bs.BeautifulSoup(curr.text, 'html.parser')
        
        result.loc[i, "vender"] = "Kono"
        result.loc[i, "url"] = link
        result.loc[i, "product"] = text.find("meta", {"property": "og:title"}).get("content")
        result.loc[i, "description"] = text.find("meta", {"property": "og:description"}).get("content")
        result.loc[i, "image"] = text.find("meta", {"property": "og:image"}).get("content")
        
        result.loc[i, "price"] = text.find(class_="price__current").contents[1].text.strip("\n\\ ")
        
        result.loc[i, "live"] = text.find(class_="product__badge product__badge--status product__badge--custom badge--custom") == None
    
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
        
        result.loc[i, "vender"] = "The Key Company"
        result.loc[i, "url"] = link
        result.loc[i, "product"] = text.find("meta", {"property": "og:title"}).get("content")
        result.loc[i, "description"] = text.find("meta", {"property": "og:description"}).get("content")
        result.loc[i, "image"] = text.find("meta", {"property": "og:image"}).get("content")
        
        result.loc[i, "price"] = text.find(class_="product-single__price").text.strip("\n\\ ")
        
    result = result[result["product"] != "Gift Card"]
    result["live"] = True
    
    return result

def get_kbd_keycaps():
    base = "https://kbdfans.com"
    url = "https://kbdfans.com/collections/keycaps"
    
    search = "https://kbdfans.com/collections/keycaps?filter.v.availability=1&page="
    
    paths = []
    for i in range(1, MAX_PAGES + 1):
        data = requests.get(search + str(i), headers=headers)
        html = bs.BeautifulSoup(data.text, 'html.parser')
        for link in html.find_all('a'):
            ref = link.get('href')
            if ref != None and "products" in ref:
                paths.append(ref)
    paths = list(set(paths))
    
    result = pd.DataFrame(index=range(len(paths)))
    for i, path in enumerate(paths):
        link = base + path
        if ("https://kbdfans.com" in path):
            link = base + path[19:]
        curr = requests.get(link, headers=headers)
        text = bs.BeautifulSoup(curr.text, 'html.parser')
        
        result.loc[i, "vender"] = "KBDFans"
        result.loc[i, "url"] = link
        result.loc[i, "product"] = text.find("meta", {"property": "og:title"}).get("content")
        result.loc[i, "description"] = text.find("meta", {"property": "og:description"}).get("content")
        result.loc[i, "image"] = text.find("meta", {"property": "og:image"}).get("content")
        
        if text.find(class_="theme-money large-title") != None:
            result.loc[i, "price"] = text.find(class_="theme-money large-title").text.strip("\n\\ ")
            
        result.loc[i, "live"] = True
        
        if text.find(class_="badgetitle primebText prime-font-adjust") != None:
            result.loc[i, "live"] = text.find(class_="badgetitle primebText prime-font-adjust").text.strip(" \n \\")
        
    pattern = re.compile('[\W_]+')    
    result["live"].apply(lambda x: pattern.sub('', x))
    
    result["live"] = np.where(result["live"] == "PreOrder", False, True)
    
    return result