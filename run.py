import pandas as pd

from scrape_keycaps import *
from scrape_switches import *

if __name__ == "__main__":
    caps = (get_cannon_keycaps, get_dang_keycaps, get_kbd_keycaps, get_keys_keycaps, get_kono_keycaps, get_novelkeys_keycaps, get_space_keycaps, get_osume_keycaps)
    x = []
    for i, func in enumerate(caps):
        curr = func()
        x.append(curr)
        print(i)
        
    df = pd.concat(x, ignore_index=True)
    df.to_csv("keycaps.csv")
    
    # switches = (get_kono_switches, get_novelkeys_switches, get_cannon_switches, get_dang_switches, get_kbd_switches, get_keys_switches)
    # y = []
    # for i, func in enumerate(switches, start=4):
    #     curr = func()
    #     y.append(curr)  
    #     print(i)
        
    # df_switch = pd.concat(y, ignore_index=True)
    # df_switch.to_csv("switches.csv")