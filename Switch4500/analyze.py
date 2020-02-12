import pandas as pd
import json

def show_desc(file_conf):
    headers = []
    data = []
    with open(file_conf) as file:
        lines = file.readlines()
        for i in range(len(lines)):
            if i == 0:
                headers.extend(lines[i].split())
            else:
                aux = lines[i].split(maxsplit=3)
                try:
                    data.append({
                        "Interface": aux[0],
                        "Description": aux[3].replace("\n", "").replace("down", "")
                    })
                except:
                    print("No hay Datos")
    print(json.dumps(data, indent=4))
    csv_show_desc = pd.DataFrame(data, columns=[headers[0], headers[3]])
    try:
        csv_show_desc.to_csv("output\show_ip_int_desc.csv", index=False)
    except PermissionError:
        print("Close the files")
    return data

def show_mc_tb(file_conf):
    headers = []
    data = []
    with open(file_conf) as file:
        lines = file.readlines()
        for i in range(len(lines)):
            if i == 0:
                headers.extend(lines[i].split())
            else:
                aux = lines[i].split(maxsplit=4)
                try:
                    data.append({
                        "vlan": aux[0],
                        "mac address": aux[1],
                        "port": aux[4].replace("\n", ""),
                        "address": " ",
                        "description": " "
                    })
                except:
                    print("No hay Datos")
    print(json.dumps(data, indent=4))
    csv_show_arp = pd.DataFrame(data, columns=["port", "vlan", "mac address", "address", "description"])
    try:
        csv_show_arp.to_csv("output\show_mc_add.csv", index=False)
    except PermissionError:
        print("Close the files")
    return data

def show_arp(file_conf):
    headers = []
    data = []
    with open(file_conf) as file:
        lines = file.readlines()
        for i in range(len(lines)):
            aux = lines[i].split(maxsplit=5)
            try:
                data.append({
                    "Address": aux[1],
                    "mac address": aux[3],
                    "port": aux[5].replace("\n", "")
                })
            except Exception as err:
                print("No hay Datos", err)
    print(json.dumps(data, indent=4))
    csv_show_arp = pd.DataFrame(data, columns=["Address", "mac address", "port"])
    try:
        csv_show_arp.to_csv("output\show_arp.csv", index=False)
    except PermissionError:
        print("Close the files")
    return data

def removeDup(objects_list):
    seen=set()
    new_l=[]
    for d in objects_list:
        t=tuple(d.items())
        if t not in seen:
            seen.add(t)
            new_l.append(d)
    return new_l

def build_table():
    show_mc = open_csv("output\show_mc_add.csv")
    limit = show_mc["mac address"].count()
    for i in range(0, limit):
        show_mc.iloc[i]["address"] = search_ip(show_mc.iloc[i]["mac address"])
    print(show_mc)
    for i in range(0, limit):
        show_mc.iloc[i]["description"] = search_desc(show_mc.iloc[i]["port"])
    print(show_mc)
    return show_mc

def search_ip(mac_address):
    show_arp = open_csv("output\show_arp.csv")
    limit = show_arp["Address"].count()
    ip = []
    for i in range(0, limit):
        if mac_address == show_arp.iloc[i]["mac address"]:
            ip.append(show_arp.iloc[i]["Address"])
    return concat_list(ip)

def search_desc(interface):
    show_desc = open_csv("output\show_ip_int_desc.csv")
    limit = show_desc["Interface"].count()
    desc = ""
    for i in range(0, limit):
        print(str(interface.replace("gabitEthernet", "").replace("rt-channel", "").strip())==str(show_desc.iloc[i]["Interface"]).strip())
        if str(interface.replace("gabitEthernet", "").replace("rt-channel", "")).strip() == str(show_desc.iloc[i]["Interface"]).strip():
            desc = show_desc.iloc[i]["Description"]
            print(show_desc.iloc[i]["Description"])
            #input()
    return desc
    

def open_csv(file_csv):
    return pd.read_csv(file_csv)

def concat_list(list_ip):
    ip = ""
    for obj in list_ip:
        ip = ip + " " + obj 
    return ip

if __name__ == "__main__":

    show_desc = show_desc("input\show_ip_int_desc.txt")
    show_mc_add = show_mc_tb("input\show_mac_add.txt")
    show_arp = show_arp("input\show_arp.txt")

    show_tb = build_table()
    csv_show_tb = pd.DataFrame(show_tb, columns=["port", "vlan", "mac address", "address", "description"])
    csv_show_tb.to_csv("output\show_tb.csv", index=False)