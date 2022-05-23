# -*- coding: utf-8 -*-
"""
Created on Thu Feb 17 06:45:15 2022

@author: Owner
"""
import requests as req
from bs4 import BeautifulSoup
import time
import random as ran
import csv

url = 'http://drd.ba.ttu.edu/isqs3358/hw1/'
filepath= 'C:/Users/Owner/Documents/BI/'
filename = 'ISQS3358_HW1_Roach.csv'

highint = 7
lowint = 6

resparent = req.get(url)
parsoup = BeautifulSoup(resparent.text, 'lxml')
moblist = parsoup.find('div', attrs={'id': 'moblist'})
mobs = moblist.find_all('li', attrs={'class':'root'})



with open(filepath + filename,'w') as dataout:
    datawriter = csv.writer(dataout, delimiter=',', quotechar='"', quoting=csv.QUOTE_NONNUMERIC)
    datawriter.writerow(['Name', 'Rarity', 'Level', 'HP','Drop_Mask','Money_Drop','Damage'])
    for i in mobs:
        child_url = i.find('a')
        yourl = child_url.get('href')
        reschild = req.get(url + yourl)
        child_soup = BeautifulSoup(reschild.content, 'lxml')
        mob_info = child_soup.find('div', attrs = {'id': 'mobitem'})
        mob_item = mob_info.find_all('tr')
        print('-----------')
        alist = []
        for j in mob_item:
            label = j.find('span', attrs = {'class':'lbl'})
            value = j.find_all('td')
            print(label.text, value[1].text)
            alist.append(value[1].text)
        alist.insert(0,label.text)
        datawriter.writerow([alist[1],alist[2],alist[3],alist[4],alist[5],alist[6],alist[7]])
        interval = ran.randint(lowint, highint) + ran.random()
        print("sleeping for:  ", interval)
        time.sleep(interval)
            
    
    
    

