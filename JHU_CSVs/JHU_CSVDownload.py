########## IMPORTS ##########
import requests
import datetime
import pandas as pd

def downloadJHUCSVS():

    #Create list of 15 most recent days in reverse order
    base = datetime.datetime.today()
    date_list = [base - datetime.timedelta(days=x+1) for x in range(15)]

    #Iterate through each date and download JHU csv from github repo
    for i in date_list:
        day = i.strftime('%d')
        month = i.strftime('%m')
        year = i.strftime('%Y')
        url = f'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/{month}-{day}-{year}.csv'

        try:
            data = requests.get(url, allow_redirects=True)
            #Writes a new file and saves it to the JHU_CSVs folder
            with open(f'{month}-{day}-{year}.csv', 'wb') as f:
                f.write(data.content)
            print(f'{month}-{day}-{year}.csv created')
        except Exception as e:
                print(f'WARNING: Exception when downloading and writing JHU file: {month}-{day}-{year}.csv. \nException: {e}')

downloadJHUCSVS()

        

