import numpy as np
import pandas as pd
import bs4 as bs
import requests
import re

headers = {
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36'}

MAX_PAGES = 100

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

def get_novelkeys_switches():
    base = "https://novelkeys.com"
    url = "https://novelkeys.com/collections/switches"
    
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
    
        for price in html.find_all(class_="price-item price price__regular price-item--regular"):
            prices.append(price.text.strip())
        
    prices = prices[::2]

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
        if text.find(attrs="product-flag") == None:
            continue
        result.loc[i, "in_stock"] = text.find(attrs="product-flag").text.strip("\n\\ ")
        
        result.loc[i, "quantity"] = text.find(class_="product-single__subtitle").text.strip("\n\\ ")
    
    result["prices"] = prices
    
    result = result[result["in_stock"].isin(["IN STOCK", "LIMITED STOCK"])]
    result = result.drop(["in_stock"], axis=1)
    result["live"] = True
    
    return result

def get_dang_switches():
    base = "https://dangkeebs.com"
    url = "https://dangkeebs.com/collections/switches"
    paths = get_links(url)

    result = pd.DataFrame(index=range(len(paths)))
    for i, path in enumerate(paths):
        link = base + path
        curr = requests.get(link)
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
                
        if text.find("div", class_="product-single__description rte") != None:
            for x in text.find("div", class_="product-single__description rte").find_all("strong"):
                if "switch" in x.text and "Quantity" in x.text:
                    result.loc[i, "quantity"] = x.text.strip()
        
    result = result[result["in_stock"] == "Add to cart"]
    result["live"] = result["product"].str.contains("\[")
    result = result.drop(["in_stock", "kit"], axis=1)
    
    return result

def get_cannon_switches():
    base = "https://cannonkeys.com"
    search = "https://cannonkeys.com/collections/switches?filter.v.availability=1&page="
    paths = []
    for i in range(1, MAX_PAGES + 1):
        data = requests.get(search + str(i))
        html = bs.BeautifulSoup(data.text, 'html.parser')
        for link in html.find_all('a'):
            ref = link.get('href')
            if ref != None and "products" in ref:
                paths.append(ref)
    paths = list(set(paths))

    result = pd.DataFrame(index=range(len(paths)))
    for i, path in enumerate(paths):
        link = base + path
        if ("https://cannonkeys.com" in path):
            link = base + path[22:]
        curr = requests.get(link, headers=headers)
        text = bs.BeautifulSoup(curr.text, 'html.parser')
        
        result.loc[i, "vender"] = "Cannon Keys"
        result.loc[i, "url"] = link
        result.loc[i, "product"] = text.find("meta", {"property": "og:title"}).get("content")
        result.loc[i, "description"] = text.find("meta", {"property": "og:description"}).get("content")
        result.loc[i, "image"] = text.find("meta", {"property": "og:image"}).get("content")
        
        result.loc[i, "live"] = True
        
        if text.find(class_="current-price theme-money") != None:
            result.loc[i, "price"] = text.find(class_="current-price theme-money").text.strip("\n\\ ")

        if text.find(class_="confirm-checkbox flexrow") != None:
            result.loc[i, "live"] = False
            
        if text.find(class_="option-selector__btns") != None:
            result.loc[i, 'quantity'] = text.find(class_="option-selector__btns").contents[0].get("value")
    
    return result

def get_kono_switches():
    base = "https://kono.store"
    url = "https://kono.store/collections/switches"
    
    paths = get_links(url)

    result = pd.DataFrame(index=range(len(paths)))
    for i, path in enumerate(paths):
        link = base + path
        curr = requests.get(link)
        text = bs.BeautifulSoup(curr.text, 'html.parser')
        
        result.loc[i, "vender"] = "Kono"
        result.loc[i, "url"] = link
        if text.find("meta", {"property": "og:title"}) == None:
            continue
        result.loc[i, "product"] = text.find("meta", {"property": "og:title"}).get("content")
        result.loc[i, "description"] = text.find("meta", {"property": "og:description"}).get("content")
        result.loc[i, "image"] = text.find("meta", {"property": "og:image"}).get("content")
        
        result.loc[i, "price"] = text.find(class_="price__current").contents[1].text.strip("\n\\ ")
        
        result.loc[i, "live"] = text.find(class_="product__badge product__badge--status product__badge--custom badge--custom") == None
        
        if text.find("div", class_="product-description rte") == None:
            continue
        
        temp = ' '.join(x.text.strip() for x in text.find("div", class_="product-description rte").contents)
        regex = re.search("[0-9- ]{2,3}switches|[0-9]{2} count packs", temp, re.IGNORECASE)
        if regex:      
            result.loc[i, "quantity"] = regex.group()
    
    
    return result

def get_keys_switches():
    base = "https://thekey.company"
    url = "https://thekey.company/collections/in-stock/switches"
    
    paths = get_links(url)
    result = pd.DataFrame(index=range(len(paths)))
    for i, path in enumerate(paths):
        link = base + path
        curr = requests.get(link, headers=headers)
        text = bs.BeautifulSoup(curr.text, 'html.parser')
        
        result.loc[i, "vender"] = "The Key Company"
        result.loc[i, "url"] = link
        result.loc[i, "product"] = text.find("meta", {"property": "og:title"}).get("content")
        result.loc[i, "description"] = text.find("meta", {"property": "og:description"}).get("content")
        result.loc[i, "image"] = text.find("meta", {"property": "og:image"}).get("content")
        
        result.loc[i, "price"] = text.find(class_="product-single__price").text.strip("\n\\ ")
        
        if len(text.find_all(attrs={"checked": "checked"})) != 0:
            temp = ""
            for option in text.find_all(attrs={"checked": "checked"}):
                temp += option.get("value")
            result.loc[i, "quantity"] = temp
        elif text.find(attrs={"itemprop": "description"}) != None:
            temp = ' '.join(x.text.strip() for x in text.find(attrs={"itemprop": "description"}).contents)
            regex = re.search("Sold in units of [0-9]{2}", temp, re.IGNORECASE)
            if regex:
                result.loc[i, "quantity"] = regex.group()
    
    result = result[result["product"] != "Gift Card"]
    result["live"] = True
    
    return result

def get_kbd_switches():
    base = "https://kbdfans.com"
    url = "https://kbdfans.com/collections/switches"
    
    search = "https://kbdfans.com/collections/switches?filter.v.availability=1&page="
    
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
            
        regex = re.search("[0-9]{2,3} switches per pack", curr.text, re.IGNORECASE)
        if regex:
            result.loc[i, "quantity"] = regex.group()
            
    pattern = re.compile('[\W_]+')    
    result["live"].apply(lambda x: pattern.sub('', x))
    result = result[result["live"] != "InterestCheckPending"]
    result["live"] = np.where(result["live"] == "PreOrder", False, True)
    
    return result