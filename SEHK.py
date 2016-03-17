# -*- coding: utf-8 -*-
"""
Created on Mon Mar 14 13:22:20 2016

@author: ASUS
"""
import pandas as pd
import urllib
import re
import urllib
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import numpy as np
import statsmodels.formula.api as smf
import sys


 



def get_stock_period(symbol='0001', d=pd.datetime(2015, 9, 15), period=100):
    d0 = d - period*pd.tseries.offsets.BDay()
    url_template = r"http://real-chart.finance.yahoo.com/table.csv?s={0}.HK&a={2}&b={3}&c={1}&d={5}&e={6}&f={4}&ignore=.csv"
                    #http://real-chart.finance.yahoo.com/table.csv?s=0001.HK&d=2&e=14&f=2016&g=d&a=0&b=4&c=2000&ignore=.csv
    #http://real-chart.finance.yahoo.com/table.csv?s=0001.HK&d=5&e=30&f=2000&a=9&b=30&c=2015&ignore=.csv
    url = url_template.format(symbol, d0.year, d0.month-1, d0.day, d.year, d.month-1, d.day)
    stock = pd.read_csv(url)#.sort(columns='Date').set_index('Date')
    ratio = stock['Adj Close']/stock['Close']
    stock['Open'] *= ratio
    stock['High'] *= ratio
    stock['Low'] *= ratio
    stock['Close'] *= ratio
    return stock
    


def prepare_database(db_name="./SEHK.sqlite", date=pd.datetime(2015, 10, 30), period=100):
    #http://real-chart.finance.yahoo.com/table.csv?s=0001.HK&d=2&e=14&f=2016&g=d&a=0&b=4&c=2000&ignore=.csv
    con = sqlite3.connect(db_name)
    listko=[]
    for symbol in listid[0:1000]:
        print(symbol)
        try:
            s = get_stock_period(symbol, d=date, period=period)
            con.execute("DROP TABLE IF EXISTS sid_{0}".format(symbol.replace('-', '_')))
            s.to_sql('sid_{0}'.format(symbol.replace('-', '_')), con)
        except:
            listko.append(symbol)
            next
            
    filee=open("error.txt","w")
    filee.write(listko)
    filee.close
    
        


def test():
    
    company=open("SEHKCOMPANY.txt","r+").read()
    re_id=r"\d{4}"
    re_name=r"\d{4} (.*)"
    ID=re.findall(re_id,company)
    num=1
    for i in ID:
        listid.append(i)
        num+=1
        if num<10:
            print(i)
    num2=1
    name=re.findall(re_name,company)
    for i in name:
        listname.append(i)
        num2+=1
        if num2<10:
            print(i)

   
        
           

if __name__ == '__main__':
    listid=[]
    listname=[]
    test()
    prepare_database()