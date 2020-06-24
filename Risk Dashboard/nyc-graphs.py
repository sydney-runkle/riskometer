#Normal imports
import numpy as np
from numpy.random import randn
import pandas as pd

#Import the stats library from numpy
from scipy import stats

#These are the plotting modules and libraries we'll use:
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns

#Importe datetime
import datetime

#Access API data
import requests

#Visualize pd DataFrames
import pandasgui


#Data imports from NYT
covid_data = pd.read_csv('us-counties.csv', sep=',', names=['date', 'county', 'state', 'fips', 'cases', 'deaths'])
state_data = pd.read_csv('us-states.csv', sep=',', names=['date', 'state', 'fips', 'cases', 'deaths'])

#Data imports from JHU
jhu_daily_data = pd.read_csv('06-18-2020.csv', sep=',')

#Remove first line
covid_data = covid_data.drop(covid_data.index[0])
state_data = state_data.drop(state_data.index[0])

#Pull API data for daily US data from COVID Tracking project
response = requests.get('https://covidtracking.com/api/v1/us/daily.json').json()
us_daily_data = pd.DataFrame(response)

#Extract NYT data for nyc and ny
nyc = covid_data[covid_data['county'] == 'New York City']
ny=state_data[state_data['state'] == 'New York']

#Convert Nyc and ny cases count to integer form
nyc['cases'] = nyc['cases'].astype(int)
ny['cases'] = ny['cases'].astype(int)
#Convert date to datetime object (first pandas timestamp)
#nyc['date'] = [i.to_pydatetime() for i in pd.to_datetime(nyc['date'])]

#Create day to day column by subtracting the previous column from the next, and set first day to first case value
nyc['day_data'] = nyc['cases'].sub(nyc['cases'].shift())
nyc['day_data'].iloc[0] = nyc['cases'].iloc[0]


#Calculate the moving average with pandaas built-in rolling mean calculator
ma_day = [3, 7, 14, 31] #Moving average day counts
#Iterate through each of the day counts
for ma in ma_day:
    #New column name based on rolling mean
    column_name = "MA for %s days" %(str(ma))
    #Create a new column in the AAPL dataframe
    #Calculate rolling mean of the adjusted close price for the given number of days
    nyc[column_name] = nyc['day_data'].rolling(ma, center=True).mean()
    
#nyc[['cases', 'MA for 3 days', 'MA for 7 days', 'MA for 14 days', 'MA for 31 days']].plot(subplots=False, figsize=(10, 4))

#fig, ax = plt.subplots()
#NYC and NY total cases plot
ax1 = plt.subplot(211)
ax1.plot(nyc['date'], nyc['cases'], color='red', label='NYC Cases')
ax1.plot(ny['date'], ny['cases'], color='blue', label='NY State Cases')

#Plot customization
plt.xlabel('Date')
plt.title('NYC Total COVID-19 Cases')
plt.ylabel('Cumulative Cases')
plt.xticks(range(0, nyc.shape[0], 10), nyc['date'][::10], rotation = 20)
ax1.legend(fontsize='small', loc='upper left')

#NYC moving average plot
ax2 = plt.subplot(212)
ax2.plot(nyc['date'], nyc['day_data'], marker='o', linewidth=1, markersize=2)
ax2.plot(nyc['date'], nyc[['MA for 3 days', 'MA for 7 days', 'MA for 14 days', 'MA for 31 days']], linewidth=.75)

#Plot customization
plt.xlabel('Date')
plt.title('NYC Daily COVID-19 Cases')
plt.ylabel('Cases')
plt.xticks(range(0, nyc.shape[0], 10), nyc['date'][::10], rotation = 20)
ax2.legend(fontsize='x-small', labels=['NYC cases/day', 'NYC cases/day 3 day rolling average', 'NYC cases/day 7 day rolling average', 'NYC cases/day 14 day rolling average', 'NYC cases/day 31 day rolling average'])
##fig.autofmt_xdate()

#Add space between the plots and show the plot
plt.subplots_adjust(hspace=1)
plt.show()      



