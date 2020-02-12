import pandas as pd
import json
from progress.bar import Bar, ChargingBar

def show_desc(file_conf):
    headers = []
    data = []
    countDataNotFound =0
    interface = ""
    description = ""

    with open(file_conf) as file:
        lines = file.readlines()
        progress = Bar('Reading INTERFACE DESCRIPTION TABLE', max=len(lines))
        for i in range(len(lines)):
            if i == 0:
                headers.extend(lines[i].split())
            else:
                aux = lines[i].split(maxsplit=3)

                try:
                    interface = aux[0]
                except:
                    countDataNotFound = countDataNotFound + 1
                    interface = None

                try:
                    description = aux[3].replace("\n", "").replace("down", "").strip()
                except:
                    countDataNotFound = countDataNotFound + 1
                    description = None

                data.append({
                    "Interface": interface,
                    "Description": description
                })

            progress.next()
    progress.finish()
    print("Creating CSV File")
    csv_show_desc = pd.DataFrame(data, columns=[headers[0], headers[3]])
    print("Ready!")
    try:
        csv_show_desc.to_csv("output\show_ip_int_desc.csv", index=False)
    except PermissionError:
        print("Close the files")
    return data

def show_mc_tb(file_conf):
    headers = []
    data = []
    interfaces = []
    countDataNotFound = 0

    vlan = ""
    mac_address = ""
    interface = ""

    j = 0

    with open(file_conf) as file:
        lines = file.readlines()
        progress = Bar('Reading MAC TABLE', max=len(lines))
        catchInterface = []
        for i in range(len(lines)):
            if i == 0:
                headers.extend(lines[i].split())
            elif i != 1:
                
                aux = lines[i].split(maxsplit=7)
                if i != len(lines)-1:
                    auxNext = lines[ i+1 ].split(maxsplit=7)
           

                if len(aux) ==  1:
                   

                    #catch data interfaces
                    catchInterface.extend(aux)

                    #Catch data from firts row
                    if j == 0:
                        auxLast = lines[ i-1 ].split(maxsplit=7)
                        #print(auxLast)
                        #input()
                        try:
                            vlan = auxLast[1]
                        except:
                            countDataNotFound = countDataNotFound + 1
                            vlan = None
                        
                        try:
                            mac_address = auxLast[2]
                        except:
                            countDataNotFound = countDataNotFound + 1
                            mac_address = None

                        try:
                            interface = auxLast[6].replace("\n", "")
                        except:
                            countDataNotFound = countDataNotFound + 1
                            interface = None
                    
                    if len(auxNext) == 1:
                        j = j + 1
                        progress.next()
                        continue
                    else:
                        #Create Object
                        data.append({
                            "vlan": vlan,
                            "mac address": mac_address,
                            "interface_mac_table": concat_list(catchInterface),
                            "address": " ",
                            "description": " ",
                            "interface": " "
                        })
                        
                    #Reset data conllection interface
                    catchInterface = []
                    j = 0
                    progress.next()

                else:

                    try:
                        vlan = aux[1]
                    except:
                        countDataNotFound = countDataNotFound + 1
                        vlan = None
                    
                    try:
                        mac_address = aux[2]
                    except:
                        countDataNotFound = countDataNotFound + 1
                        mac_address = None

                    try:
                        interface = aux[6].replace("\n", "")
                    except:
                        countDataNotFound = countDataNotFound + 1
                        interface = None

                    data.append({
                        "vlan": vlan,
                        "mac address": mac_address,
                        "interface_mac_table": interface,
                        "address": " ",
                        "description": " ",
                        "interface": " "
                    })

                
                    progress.next()
    progress.finish()
    print("Creating CSV File")
    csv_show_arp = pd.DataFrame(data, columns=["interface_mac_table", "interface", "vlan", "mac address", "address", "description"])
    print("Ready!")
    try:
        csv_show_arp.to_csv("output\show_mc_add.csv", index=False)
    except PermissionError:
        print("Close the files")
    return data

def show_arp(file_conf):
    headers = []
    data = []
    countDataNotFound = 0
    address = ""
    mac_address = ""
    interface = ""
    with open(file_conf) as file:
        lines = file.readlines()
        progress = Bar('Reading ARP TABLE', max=len(lines))
        for i in range(len(lines)):
            aux = lines[i].split(maxsplit=5)


            if aux[1] != "Address":

                try:
                    address = aux[1]
                except:
                    countDataNotFound = countDataNotFound + 1
                    address =  None

                try:
                    mac_address = aux[3]
                except:
                    countDataNotFound = countDataNotFound + 1
                    mac_address =  None

                try:
                    interface = aux[5].replace("\n", "")
                except:
                    countDataNotFound = countDataNotFound + 1
                    interface =  None

                data.append({
                    "Address": address,
                    "mac address": mac_address,
                    "interface": interface
                })

            progress.next()
    progress.finish()
    print("Creating CSV File")
    csv_show_arp = pd.DataFrame(data, columns=["Address", "mac address", "interface"])
    print("Ready!")
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
    progress = Bar('Searching IP Address', max=(limit))
    for i in range(0, limit):
        show_mc.iloc[i]["address"] = search_ip(show_mc.iloc[i]["mac address"])
        progress.next()
    progress.finish()
    progress = Bar('Searching Description', max=(limit))
    for i in range(0, limit):
        show_mc.iloc[i]["description"] = search_desc(show_mc.iloc[i]["interface_mac_table"])
        progress.next()
    progress.finish()
    progress = Bar('Searching Interface', max=(limit))
    for i in range(0, limit):
        show_mc.iloc[i]["interface"] = search_int(show_mc.iloc[i]["mac address"])
        progress.next()
    progress.finish()
    return show_mc

def search_ip(mac_address):
    show_arp = open_csv("output\show_arp.csv")
    limit = show_arp["Address"].count()
    ip = []
    for i in range(0, limit):
        if mac_address == show_arp.iloc[i]["mac address"]:
            ip.append(show_arp.iloc[i]["Address"])
    return concat_list(ip)

def search_int(mac_address):
    show_arp = open_csv("output\show_arp.csv")
    limit = show_arp["mac address"].count()
    interface = []
    for i in range(0, limit):
        if mac_address == show_arp.iloc[i]["mac address"]:
            interface.append(show_arp.iloc[i]["interface"])
    return concat_list(interface)

def search_desc(interface):
    show_desc = open_csv("output\show_ip_int_desc.csv")
    limit = show_desc["Interface"].count()
    desc = ""
    for i in range(0, limit):

        if str(str(interface).replace("gabitEthernet", "").replace("rt-channel", "")).strip() == str(show_desc.iloc[i]["Interface"]).strip():
            desc = show_desc.iloc[i]["Description"]
            #print(show_desc.iloc[i]["Description"])
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
    csv_show_tb = pd.DataFrame(show_tb, columns=["interface_mac_table", "interface", "vlan", "mac address", "address", "description"])
    csv_show_tb.to_csv("output\show_tb.csv", index=False)