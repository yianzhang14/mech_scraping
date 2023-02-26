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

def get_novelkeys_switches(base, url):
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
    print(prices)

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
        print(path)
        if text.find(attrs="product-flag") == None:
            continue
        result.loc[i, "status"] = text.find(attrs="product-flag").text.strip("\n\\ ")
        
        result.loc[i, "quantity"] = text.find(class_="product-single__subtitle").text.strip("\n\\ ")
        
        
    
    result["prices"] = prices
    
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
                
        result.loc[i, "quantity"] = ' '.join(x.text.strip() for x in text.find("div", class_="product-single__description rte").contents)
    
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
        
        result.loc[i, "vender"] = text.find("meta", {"property": "og:site_name"}).get("content")
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
        
        # result.loc[i, "in_stock"] = text.find(attrs=in_stock_query).text.strip("\n\\ ")
    
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
        
        result.loc[i, "vender"] = text.find("meta", {"property": "og:site_name"}).get("content")
        result.loc[i, "url"] = link
        result.loc[i, "product"] = text.find("meta", {"property": "og:title"}).get("content")
        result.loc[i, "description"] = text.find("meta", {"property": "og:description"}).get("content")
        result.loc[i, "image"] = text.find("meta", {"property": "og:image"}).get("content")
        
        result.loc[i, "price"] = text.find(class_="price__current").contents[1].text.strip("\n\\ ")
        
        result.loc[i, "live"] = text.find(class_="product__badge product__badge--status product__badge--custom badge--custom") == None
        
        if text.find("div", class_="product-description rte") == None:
            continue
    
        result.loc[i, "quantity"] = ' '.join(x.text.strip() for x in text.find("div", class_="product-description rte").contents)
    
    
    return result

def get_keys_switches():
    base = "https://thekey.company"
    url = "https://thekey.company/collections/in-stock/switches"
    
    paths = get_links(url)

    paths = ["/collections/in-stock/products/akko-v3-cream-blue-switches"]
    result = pd.DataFrame(index=range(len(paths)))
    for i, path in enumerate(paths):
        link = base + path
        curr = requests.get(link, headers=headers)
        text = bs.BeautifulSoup(curr.text, 'html.parser')
        
        result.loc[i, "vender"] = text.find("meta", {"property": "og:site_name"}).get("content")
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
            result.loc[i, "quantity"] = ' '.join(x.text.strip() for x in text.find(attrs={"itemprop": "description"}).contents)
        
    result["in_stock"] = True
    
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
    
    print(paths)
    
    result = pd.DataFrame(index=range(len(paths)))
    for i, path in enumerate(paths):
        link = base + path
        if ("https://kbdfans.com" in path):
            link = base + path[19:]
        curr = requests.get(link, headers=headers)
        text = bs.BeautifulSoup(curr.text, 'html.parser')
        try:
            result.loc[i, "vender"] = text.find("meta", {"property": "og:site_name"}).get("content")
            result.loc[i, "url"] = link
            result.loc[i, "product"] = text.find("meta", {"property": "og:title"}).get("content")
            result.loc[i, "description"] = text.find("meta", {"property": "og:description"}).get("content")
            result.loc[i, "image"] = text.find("meta", {"property": "og:image"}).get("content")
            
            if text.find(class_="theme-money large-title") != None:
                result.loc[i, "price"] = text.find(class_="theme-money large-title").text.strip("\n\\ ")
                
            result.loc[i, "live"] = True
            
            if text.find(class_="badgetitle primebText prime-font-adjust") != None:
                result.loc[i, "live"] = text.find(class_="badgetitle primebText prime-font-adjust").text.strip(" \n \\")
                
            regex = re.match("[0-9]{2,3} switches Per Pack", curr.text, re.IGNORECASE)
            if regex:
                result.loc[i, "quantity"] = re.search("[0-9]{2,3} Per Pack", text.text, re.IGNORECASE).group()
        except:
            print(link)
    
    return result

# get_novelkeys_keycaps("https://novelkeys.com", "https://novelkeys.com/collections/switches").to_csv("novel.csv")
# get_dang_switches("https://dangkeebs.com", "https://dangkeebs.com/collections/switches").to_csv("ditches.csv")
# get_kono_switches("https://kono.store", "https://kono.store/collections/switches").to_csv("konoswitch.csv")
get_kbd_switches().to_csv("kbdswitch.csv")