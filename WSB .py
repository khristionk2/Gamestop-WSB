#!/usr/bin/env python
# coding: utf-8

# In[ ]:


# PUSHSHIFT API get all the comments from 1.1 - 3.13
import pandas as pd
import requests #Pushshift accesses Reddit via an url so this is needed
import json #JSON manipulation
import csv 
import time
import datetime
from pandas import DataFrame
import mysql.connector


# # API using Reddit Wallstreetbets Comments

# In[ ]:


def getPushshiftData(query, after, before, sub):
    #Build URL
    url = 'https://api.pushshift.io/reddit/search/submission/?title='+str(query)+'&size=1000&after='+str(after)+'&before='+str(before)+'&subreddit='+str(sub)
    #Print URL to show user
    print(url)
    #Request URL
    r = requests.get(url)
    #Load JSON data from webpage into data variable
    data = json.loads(r.text)
    #return the data element which contains all the submissions data
    return data['data']


# In[ ]:


#This function will be used to extract the key data points from each JSON result
def collectSubData(subm):
    #subData was created at the start to hold all the data which is then added to our global subStats dictionary.
    subData = list() #list to store data points
    title = subm['title']
    url = subm['url']
    #flairs are not always present so we wrap in try/except
    try:
        flair = subm['link_flair_text']
    except KeyError:
        flair = "NaN"    
    author = subm['author']
    sub_id = subm['id']
    score = subm['score']
    created = datetime.datetime.fromtimestamp(subm['created_utc']) 
    numComms = subm['num_comments']
    permalink = subm['permalink']

    #Put all data points into a tuple and append to subData
    subData.append((sub_id,title,url,author,score,created,numComms,permalink,flair))
    #Create a dictionary entry of current submission data and store all data related to it
    subStats[sub_id] = subData


# In[ ]:


#Create your timestamps and queries for your search URL
#GME
#https://www.unixtimestamp.com/index.php > Use this to create your timestamps
after = "1609459200" #Submissions after this timestamp (1609459200 = Jan 1, 2021)
before = "1615766399" #Submissions before this timestamp (1615766399 = March 13, 2021)
query = "gme" #Keyword(s) to look for in submissions
sub = "wallstreetbets" #Which Subreddit to search in

#subCount tracks the no. of total submissions we collect
subCount = 0
#subStats is the dictionary where we will store our data.
subStats = {}


# In[ ]:


# We need to run this function outside the loop first to get the updated after variable
data = getPushshiftData(query, after, before, sub)
# Will run until all posts have been gathered i.e. When the length of data variable = 0
# from the 'after' date up until before date
while len(data) > 0: #The length of data is the number submissions (data[0], data[1] etc), once it hits zero (after and before vars are the same) end
    for submission in data:
        collectSubData(submission)
        subCount+=1
    # Calls getPushshiftData() with the created date of the last submission
    print(len(data))
    print(str(datetime.datetime.fromtimestamp(data[-1]['created_utc'])))
    #update after variable to last created date of submission
    after = data[-1]['created_utc']
    #data has changed due to the new after variable provided by above code
    data = getPushshiftData(query, after, before, sub)
    
print(len(data))


# In[ ]:


def updateSubs_file():
    filename = 'gme_reddit.csv'
    file = filename
    with open(file, 'w', newline='', encoding='utf-8') as file: 
        a = csv.writer(file, delimiter=',')
        headers = ["Post ID","Title","Url","Author","Score","Create_Date","Total_Comments","Permalink","Flair"]
        a.writerow(headers)
        for sub in subStats:
             a.writerow(subStats[sub][0])
updateSubs_file()


# In[ ]:


df=pd.read_csv('gme_reddit.csv')
df


# In[ ]:


# extract post create date and time into new columns in df
df['Date'] = pd.DatetimeIndex(df['Create_Date']).to_period('D')
df['Time'] = pd.DatetimeIndex(df['Create_Date']).time
df['Total_Comments']= df['Total_Comments']+1
df


# In[ ]:


gme_reddit = df.groupby(by=["Date"]).sum()
gme_reddit= gme_reddit.reset_index()
gme_reddit.columns = ['Date', 'Score', 'Total_Comments']


# # Web scraping on Yahoo Finance 

# In[ ]:


import requests
import pandas as pd
import urllib.parse
import warnings
from bs4 import BeautifulSoup
from requests import get
import datetime
from datetime import datetime, timedelta
import pandas_datareader as wb


# In[ ]:


def convert_time(x):
    date = datetime.strptime(x, '%b %d, %Y')
    return date.date()

def clean(x):
    x = x.replace(',', '')
    x = float(x)
    return x

def data_100row(company):
  headers = {'User-agent': 'Mozilla/5.0'} 
  URL = "https://finance.yahoo.com/quote/" + company + "/history?p=" + company
  page = requests.get(URL, headers=headers)
  soup = BeautifulSoup(page.text, 'lxml')
  soup = soup.find("tbody", attrs={"data-reactid": "50"}) 
  data = soup.find_all("tr", class_="BdT Bdc($seperatorColor) Ta(end) Fz(s) Whs(nw)")
  index = pd.Series(range(0,100))
  columns=['Date', 'Open', 'High', 'Low', 'Close', 'Adjusted_Close', 'Volume']

  df = pd.DataFrame(index=index, columns=columns) 
  for i in range(0, 100):
    df.loc[i, 'Date'] = convert_time(data[i].find_all('span')[0].text)
    df.loc[i, 'Open'] = clean(data[i].find_all('span')[1].text)
    df.loc[i, 'High'] = clean(data[i].find_all('span')[2].text)
    df.loc[i, 'Low'] = clean(data[i].find_all('span')[3].text)
    df.loc[i, 'Close'] = clean(data[i].find_all('span')[4].text)
    df.loc[i, 'Adjusted_Close'] = clean(data[i].find_all('span')[5].text)
    df.loc[i, 'Volume'] = clean(data[i].find_all('span')[6].text)

  return df


# In[ ]:


data = data_100row('GME')
data.to_csv('gme_stock.csv')


# In[ ]:


gme_stock= pd.read_csv('gme_stock.csv')  
gme_stock= gme_stock[['Date','Open', 'High', 'Low', 'Close', 'Adjusted_Close', 'Volume']]
gme_stock


# In[ ]:


gme_stock.dtypes


# In[ ]:


gme_stock['Date'] = gme_stock['Date'].astype('period[D]')


# In[ ]:


gme_reddit.dtypes


# In[ ]:


gme_full= gme_reddit.merge(gme_stock, how='left', on='Date')
gme_full


# In[ ]:


gme_full['Date'] = gme_full['Date'].astype('string')
gme_full= gme_full.dropna()
gme_full


# In[ ]:


gme_full.to_csv('gme_full.csv')

