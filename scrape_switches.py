import numpy as np
import pandas as pd
import bs4 as bs
import requests

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

def get_dang_switches(base, url):
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

def get_kono_switches(base, url):
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

def get_keys_switches(base, url):
    paths = get_links(url)

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
        
        print(text.find(attrs={"checked": "checked", "name": "variant"}))
        if text.find(attrs={"checked": "checked", "name": "variant"}) != None:
            result.loc[i, "quantity"] = text.find(attrs={"checked": "checked", "name": "variant"}).get("value")
        elif text.find(class_="product-single__description rte") != None:
            result.loc[i, "quantity"] = ' '.join(x.text.strip() for x in text.find(class_="product-single__description rte").contents)
        
    result["in_stock"] = True
    
        
    
    
    return result

# get_novelkeys_keycaps("https://novelkeys.com", "https://novelkeys.com/collections/switches").to_csv("novel.csv")
# get_dang_switches("https://dangkeebs.com", "https://dangkeebs.com/collections/switches").to_csv("ditches.csv")
# get_kono_switches("https://kono.store", "https://kono.store/collections/switches").to_csv("konoswitch.csv")
get_keys_switches("https://thekey.company", "https://thekey.company/collections/in-stock/switches").to_csv("keyswitch.csv")