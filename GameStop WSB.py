#!/usr/bin/env python
# coding: utf-8

# In[6]:


import re
import mysql.connector
import pandas as pd
import pymysql
import numpy as np
import matplotlib.pyplot as plt
import re
import datetime
import seaborn as sns
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import requests
import urllib.parse
import warnings
from bs4 import BeautifulSoup
from requests import get
import datetime
from datetime import datetime, timedelta
import praw
import copy


# # Exploratory Data Analysis

# In[7]:


gme_full = pd.read_csv('/Users/khristionlambert/Library/Mobile Documents/com~apple~CloudDocs/Grad School/Winter 2021/452_Machine Learning/Final 452/Data/gme_full.csv')
gme_full


# In[3]:


# create dual axises plot

# create figure and axis objects with subplots()

fig,ax = plt.subplots(figsize=(20, 6), )

# make a plot
ax.plot(gme_full.Date,gme_full.Volume, color="red", marker="o")
# set x-axis label
ax.set_xlabel("Date",fontsize=18)
plt.xticks(rotation=90)
# set y-axis label
ax.set_ylabel("Volume",color="red",fontsize=18)

# twin object for two different y-axis on the sample plot
ax2=ax.twinx()
# make a plot with different y-axis using second axis object
ax2.plot(gme_full.Date,gme_full.Close,color="blue",marker="o")
ax2.set_ylabel("Close",color="blue",fontsize=18)
plt.title("GME",fontsize=20)
plt.show()


# In[4]:


# comment vs close price 
# create dual axises plot

# create figure and axis objects with subplots()

fig,ax = plt.subplots(figsize=(20, 6), )

# make a plot
ax.plot(gme_full.Date,gme_full.Total_Comments, color="red", marker="o")
# set x-axis label
ax.set_xlabel("Date",fontsize=18)
plt.xticks(rotation=90)
# set y-axis label
ax.set_ylabel("Total Comments",color="red",fontsize=18)

# twin object for two different y-axis on the sample plot
ax2=ax.twinx()
# make a plot with different y-axis using second axis object
ax2.plot(gme_full.Date,gme_full.Close,color="blue",marker="o")
ax2.set_ylabel("Close",color="blue",fontsize=18)
plt.title("GME",fontsize=20)
plt.show()


# In[5]:


# comments vs volume 
# create dual axises plot
# create figure and axis objects with subplots()

fig,ax = plt.subplots(figsize=(20, 6), )

# make a plot
ax.plot(gme_full['Date'],gme_full['Total_Comments'], color="red", marker="o")
# set x-axis label
ax.set_xlabel("Date",fontsize=18)
plt.xticks(rotation=90)
# set y-axis label
ax.set_ylabel("Total Comments",color="red",fontsize=18)

# twin object for two different y-axis on the sample plot
ax2=ax.twinx()
# make a plot with different y-axis using second axis object
ax2.plot(gme_full['Date'],gme_full['Volume'],color="blue",marker="o")
ax2.set_ylabel("Volume",color="blue",fontsize=18)
plt.title("GME",fontsize=20)
plt.show()


# # Word Cloud

# In[9]:


from PIL import Image
from wordcloud import WordCloud, STOPWORDS, ImageColorGenerator
import nltk
from nltk.corpus import stopwords


# In[10]:


df = pd.read_csv('/Users/khristionlambert/Library/Mobile Documents/com~apple~CloudDocs/Grad School/Winter 2021/452_Machine Learning/Final 452/Data/gme_reddit.csv')
df


# In[11]:


text = " ".join(review for review in df.Title)
stopwords = nltk.corpus.stopwords.words('english')
stopwords.append('GME')
wordcloud = WordCloud(stopwords=stopwords, background_color="white").generate(text)
plt.figure(figsize=(10,10))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis("off")
plt.show()


# # Sentimental Analysis

# In[10]:


title = df[['Title','Publish Date']].copy()
title = title.dropna()
title.Title =title.Title.str.lower()

#Remove handlers
title.Title = title.Title.apply(lambda x:re.sub('@[^\s]+','',x))

# Remove URLS
title.Title = title.Title.apply(lambda x:re.sub(r"http\S+", "", x))

# Remove all the special characters
title.Title = title.Title.apply(lambda x:' '.join(re.findall(r'\w+', x)))

#remove all single characters
title.Title = title.Title.apply(lambda x:re.sub(r'\s+[a-zA-Z]\s+', '', x))

# Substituting multiple spaces with single space
title.Title = title.Title.apply(lambda x:re.sub(r'\s+', ' ', x, flags=re.I))

#Remove Time From Timestamp
title['Publish Date'] = pd.to_datetime(title['Publish Date']).dt.date


# In[11]:


sid = SentimentIntensityAnalyzer()
title2 = copy.deepcopy(title)
title2['sentiments'] = title2['Title'].apply(lambda x: sid.polarity_scores(' '.join(re.findall(r'\w+',x.lower()))))
title2['compound'] = title2['sentiments'].apply(lambda score_dict: score_dict['compound'])

def compound_score(x):
    if x > 0:
        return 'Postive'
    elif x < 0:
        return 'Negative'
    else:
        return 'Neutral'


title2['comp_score'] = title2['compound'].apply(lambda c: compound_score(c))

title2.head()


# In[12]:


# delete neutral
title2 = title2[title2['comp_score'] != 'Neutral']

title3 = title2.groupby(by=["Publish Date"])['comp_score'].value_counts()

title3 = pd.DataFrame(title3)
title3.rename(columns={"comp_score": "frequency"}, inplace = True)
title3.reset_index(inplace = True)
title3 = title3.pivot(index="Publish Date", columns="comp_score", values="frequency")

title3.head()


# In[13]:


normalizedDataFrame = title3.div(title3.sum(axis=1), axis=0)

years  = title3.index

normalizedDataFrame.index = years;

# Draw a percentage based, stacked area plot

normalizedDataFrame.plot.area(stacked=True);

plt.show(block=True);


# In[14]:


#plot trend


# In[15]:


title4 = title2.groupby(by=["Publish Date"])['compound'].sum()
title4 = pd.DataFrame(title4)
title4 = title4.reset_index()
title4.rename(columns={"Publish Date": "Date"}, inplace = True)
title4


# In[16]:


gme_full.drop('Unnamed: 0', axis='columns', inplace=True)


# In[17]:


title4['Date'] = title4['Date'].astype('period[D]')
gme_full['Date'] = gme_full['Date'].astype('period[D]')


# In[18]:


gme = pd.merge(gme_full, title4, on='Date')
gme.Date = gme.Date.astype(str)
gme


# In[19]:



# create dual axises plot

# create figure and axis objects with subplots()

fig,ax = plt.subplots(figsize=(20, 6), )

# make a plot
ax.plot(gme.Date,gme.Volume, color="red", marker="o")
# set x-axis label
ax.set_xlabel("Date",fontsize=18)
plt.xticks(rotation=90)
# set y-axis label
ax.set_ylabel("Volume",color="red",fontsize=18)

# twin object for two different y-axis on the sample plot
ax2=ax.twinx()
# make a plot with different y-axis using second axis object
ax2.plot(gme.Date,gme.compound,color="blue",marker="o")
ax2.set_ylabel("compound",color="blue",fontsize=18)
plt.title("GME",fontsize=20)
plt.show()


# In[20]:


# create dual axises plot

# create figure and axis objects with subplots()

fig,ax = plt.subplots(figsize=(20, 6), )

# make a plot
ax.plot(gme.Date,gme.Close, color="red", marker="o")
# set x-axis label
ax.set_xlabel("Date",fontsize=18)
plt.xticks(rotation=90)
# set y-axis label
ax.set_ylabel("Close",color="red",fontsize=18)

# twin object for two different y-axis on the sample plot
ax2=ax.twinx()
# make a plot with different y-axis using second axis object
ax2.plot(gme.Date,gme.compound,color="blue",marker="o")
ax2.set_ylabel("compound",color="blue",fontsize=18)
plt.title("GME",fontsize=20)
plt.show()

