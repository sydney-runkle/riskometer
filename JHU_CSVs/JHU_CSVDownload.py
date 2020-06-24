import requests
import datetime
import pandas as pd

base = datetime.datetime.today()
date_list = [base - datetime.timedelta(days=x+1) for x in range(15)]

df = pd.DataFrame()

for i in date_list:
    day = i.strftime('%d')
    month = i.strftime('%m')
    year = i.strftime('%Y')
    url = f'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_daily_reports/{month}-{day}-{year}.csv'
    
    data = requests.get(url, allow_redirects=True)
    with open(f'{month}-{day}-{year}.csv', 'wb') as f:
        f.write(data.content)
        

