import pandas as pd

from scrape_keycaps import *
from scrape_switches import *

if __name__ == "__main__":
    # caps = (get_cannon_keycaps, get_dang_keycaps, get_cannon_keycaps, get_kbd_keycaps, get_keys_keycaps, get_kbd_keycaps, get_kono_keycaps, get_novelkeys_keycaps)
    # caps = (get_cannon_keycaps, get_dang_keycaps)
    # x = []
    # for i, func in enumerate(caps[::-1], start=6):
    #     curr = func()
    #     x.append(curr)
    #     curr.to_csv(str(i) + ".csv")
    #     print(i)
        
    # df = pd.concat(x, ignore_index=True)
    # df.to_csv("keycaps.csv")
    
    # get_kono_switches().to_csv("temp.csv")
    # switches = (get_kbd_switches, get_cannon_switches, get_dang_switches, get_keys_switches, get_kono_switches, get_novelkeys_switches)
    # y = []
    # for i, func in enumerate(switches):
    #     curr = func()
    #     y.append(curr)  
    #     curr.to_csv(str(i) + ".csv")
    #     print(i)
        
    # df_switch = pd.concat(y, ignore_index=True)
    # df_switches.to_csv("switches.csv")
    get_dang_switches().to_csv("abcdefg.csv")