# -*- coding: utf-8 -*-
"""
Created on Mon Mar 14 16:45:46 2016

@author: ASUS
"""

import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import numpy as np
import statsmodels.formula.api as smf
import sys
import re
from pylab import *


def get_stock_period(symbol='0001', d=pd.datetime(2015, 9, 15), period=100):
    d0 = d - period*pd.tseries.offsets.BDay()
    output = sqlite3.connect("./SEHK.sqlite")
    #cmd = "SELECT * from sid_{0} LIMIT 50".format(symbol)
    cmd = "SELECT * from sid_{0}".format(symbol.replace('-','_'))
    s = pd.read_sql(cmd, output).sort(columns='Date').set_index('Date')
    stock = s[d0.strftime('%Y-%m-%d'):d.strftime('%Y-%m-%d')].copy()
    stock['day'] = np.arange(len(stock))
    return stock

def is_bull(date, period):
    def get_stock_period_online( d=pd.datetime(2015, 9, 15), period=30):
        d0 = d - period*pd.tseries.offsets.BDay()
        url_template = r"http://real-chart.finance.yahoo.com/table.csv?s=%5EHSI&d={4}&e={5}&f={3}&g=d&a={1}&b={2}&c={0}&ignore=.csv"
                      #http://real-chart.finance.yahoo.com/table.csv?s=%5EHSI&d=2&e=14&f=2016&g=d&a=11&b=31&c=1986&ignore=.csv
        url = url_template.format(d0.year, d0.month-1, d0.day, d.year, d.month-1, d.day)
        stock = pd.read_csv(url).sort(columns='Date').set_index('Date')
        ratio = stock['Adj Close']/stock['Close']
        stock['Open'] *= ratio
        stock['High'] *= ratio
        stock['Low'] *= ratio
        stock['Close'] *= ratio
        return stock
    
    s = get_stock_period_online(date, period)
    mean = s.Close.mean()
    #print(s.Close[0])
    price = s.Close[len(s)-1]
    return price>mean


class Momentum:
     
    def __init__(self, date=pd.datetime(2015, 9, 15), period=30, period_a=100, nstock=30):
        self.date = date
        self.period = period
        self.period_a = period_a
        self.nstock = nstock
        """
        get_list=open("SEHKCOMPANY.txt","r+").read()
        re_id=r"\d{4}"
        re_name=r"\d{4} (.*)"
        ID=re.findall(re_id,get_list)
        for i in ID:
           listid.append(i)
        name=re.findall(re_name,get_list)
        for i in name:
           listname.append(i)
        """
        self.base = pd.DataFrame({'symbol': listid[:800], 'momentum': False})
        self.is_bull = is_bull(date, period)
        if self.is_bull:
        
            self.qualify()
            print('\n   base.head: {0} '.format(self.base.head(10)))
                    #  Score the momentum stocks and order them
            self.rate()
            print('\n   pool.head: {0} '.format(self.pool.head(10)))
                    #  pick up the first 30 with highest stores
            self.choose(nstock)
            print('\n   choice: {0} '.format(self.choice))
                    #  make the pie-chart
            #from pylab import *
            #figure(0) 
            try:
                self.choice=self.choice.replace([np.inf, -np.inf], np.nan).dropna(subset=["weight"], how="all")
                self.choice=self.choice[self.choice.weight<1]
                weight_list=[]
                symbol_list=[]
                weight_list=self.choice.weight.tolist()
                num=0
                for i in weight_list:
                    weight_list[num]=round(i,4)
                    num+=1
                num=0
                for i in weight_list:
                    weight_list[num]=10000*i
                    num+=1
                num=0
                for i in weight_list:
                    weight_list[num]=int(i)
                    num+=1
                num=0
                for i in weight_list:
                    self.choice.iloc[num]['weight']=i
                    num+=1
                symbol_list=self.choice.symbol.tolist()
                plt.pie(weight_list,labels=symbol_list,autopct='%.2f')
                #self.choice.weight.plot(kind='pie', labels=self.choice.symbol,subplots=True, autopct='%.2f', figsize=(15,15))
                plt.title("HSI most valuable underlying").set_size(30)
                plt.Figure(20,20)
                #//figure(1)        
                plt.show() 
                 
               # self.choice.to_csv("dataframe.csv")
            except:
                return
                  
            return 
        else:
            print(' Bear Here!!  Watch Out! ')
        
    def qualify(self):
        #  check if it is the momentum case
        def is_momentum(symbol):
            #  show status bar
            self.ncall += 1
            #print('   number {0} is: {1}'.format(self.ncall, symbol))
            ninterval = 5
            if self.ncall%ninterval == 0:
                sys.stdout.write('\r')
                #sys.stdout.write("[%-50s] %d%%" % ('='*(self.ncall/10), (100/len(self.base))*self.ncall))
                sys.stdout.write("[%-100s] %d%%" % ('='*(self.ncall/ninterval), 1+int((100./len(self.base))*(self.ncall))))
                sys.stdout.flush()
            #  main part
            s = get_stock_period(symbol, d=self.date, period=self.period_a)
            mean = s.Close.mean()
            price = s.Close[-1]
            price0 = s.Close[0]
            rate = (price-price0)/price0
            #print('   number {0} has finished'.format(self.ncall))            
            return (price>mean) and (rate>0.1)
        
        print('  qualifying all the stocks included in SEHK... ')
        self.ncall = 0
        self.base.momentum = self.base.symbol.apply(is_momentum)
        #  filter out the qualified items
        self.pool = self.base[self.base.momentum].copy()
        
    def rate(self):
        #  calculate the adjusted annualized slope
        pool = self.pool 
        
        #  define the function 
        def cal_slope(symbol):
            #  show status bar
            self.ncall += 1
            sys.stdout.write('\r')
            if self.ncall % 2 == 0:
                sys.stdout.write("[%-100s] %d%%" % ('='*(self.ncall/2), int((100.0/len(pool))*self.ncall)))
            sys.stdout.flush()
            s = get_stock_period(symbol, d=self.date, period=self.period)
            s['ln'] = np.log(s.Close)                        
            lm = smf.ols(formula='ln ~ Open', data=s).fit()
            r2 = lm.rsquared
            rate = (1.0+lm.params['Open'])**250 - 1
            arate = rate*r2
            #print('   Adjusted slope for {0} is: {1}'.format(symbol, arate))
            return arate
        self.ncall = 0
        print('  calculating the annualized slope for each stock... ')
        #  calculate slope for each row
        pool['slope'] = pool.symbol.apply(cal_slope)
        #  order from largest to smallest
        pool.sort('slope', inplace=True, ascending=False)
    
    def choose(self, nstock=30):
        #  pick up the first nstock most promising stocks
        self.choice = self.pool.head(nstock).copy()
        #  define a function to calculate the 20-day average true range (ATR)
        nday = 20
        def cal_atr(symbol):
            s = get_stock_period(symbol, d=self.date, period=nday)
            atr = 0.0
            for i in range(1,nday):
                s0 = s.iloc[i-1,:]
                s1  = s.iloc[i,:]
                #print('  {0} {1} {2}'.format(i,s0,s1))
                r1 = s1.High - s1.Low
                r2 = abs(s0.Close-s1.High)
                r3 = abs(s0.Close-s1.Low)
                r = np.max([r1,r2,r3])
                atr += r/nday
            return atr
        #  add ATR column
        self.choice['ATR'] = self.choice.symbol.apply(cal_atr)
        
        #  add the weight according to ATR and "current" price
        #  here we use Open price for the test
        RiskFactor = 0.001
        def cal_weight(symbol):                       
            s = get_stock_period(symbol, d=self.date, period=1)
            return RiskFactor*s.tail(1).Close
        self.choice['weight'] = self.choice.symbol.apply(cal_weight)
        self.choice.weight /= self.choice['ATR']



def test():
    m = Momentum(date=pd.datetime(2015,10, 25))
    return m.choice
    
     
    #print(m.base.head(10))

if __name__ == '__main__':
    listid=[]
    listname=[]
    con = lite.connect('SEHK.sqlite') 
    with con:
    
     cur = con.cursor()    
     cur.execute('SELECT name from sqlite_master where type="table" ')
     data = cur.fetchall()
     re_id=r"(\d{4})"
     for data in data:
         SID=re.search(re_id,data[0])
         listid.append(str(SID.group()))
         
    listidd=[]
    
    get_list=open("SEHKCOMPANY.txt","r+").read()
    re_id=r"\d{4}"
    re_name=r"\d{4} (.*)"
    ID=re.findall(re_id,get_list)
    for i in ID:
        listidd.append(i)
    name=re.findall(re_name,get_list)
    for i in name:
       listname.append(i)   
    finalresults=test()
         
     
    
    
    listcombo=zip(listidd,listname)
    listnew=[]
    for i in finalresults['symbol']:
        for j in listcombo:
            if i==j[0]:
                listnew.append(j[1])
                next      
                
   
    finalresults.insert(2,"company",listnew)
    finalresults.to_csv("HSI.csv")
    
                
                