###### IMPORTS ######
from flask import Flask
from flask_restful import Api, Resource, reqparse
import random

app = Flask(__name__)
api = Api(app)

import datetime
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

import json
import requests

#Create list of 15 most recent days
base = datetime.datetime.today()
date_list = [base - datetime.timedelta(days=x+1) for x in range(15)]

#Initialize pandas dataframe to store COVID-19 info for counties
df = pd.DataFrame()

for i in date_list:
    day = i.strftime('%d')
    month = i.strftime('%m')
    year = i.strftime('%Y')
    print(df.shape)

    link=f'./JHU_CSVs/{month}-{day}-{year}.csv'

    data=pd.read_csv(link, error_bad_lines=False)
    data['Date'] = datetime.datetime(int(year), int(month), int(day))
    df = df.append(data)

def requestFIPS(location):

    fipsRequest = requests.get(f'https://api.opencagedata.com/geocode/v1/json?q={location}&key=679bf5d7a07e424f9cf7d1649ec8037d')

    if fipsRequest.status_code == 200:

        response = json.loads(fipsRequest.text)
        FIPS = int(response['results'][0]['annotations']['FIPS']['county'])
        return FIPS;

def fetchTwoWeekInformation(FIPS):
    two_week_data = pd.DataFrame(df.loc[df['FIPS']==FIPS])[::-1]
    two_week_data['Day_Cases'] = two_week_data['Confirmed'].sub(two_week_data['Confirmed'].shift())
    two_week_data['Day_Cases'].iloc[0] = np.NaN

    county_information = {
        'FIPS': FIPS,
        'two_week_data': two_week_data['Day_Cases'][1:].to_json(orient='values'),
        'location': two_week_data['Combined_Key'].values[0],
        'deaths': int(two_week_data['Deaths'].values[-1]),
        'total cases': int(two_week_data['Confirmed'].values[-1])
    }

    return county_information


class CountyInfo(Resource):

    def get(self, departure, destination):

        if(departure and destination):
            departure_FIPS = requestFIPS(departure)
            departure_info = fetchTwoWeekInformation(departure_FIPS)
            destination_FIPS = requestFIPS(destination)
            destination_info = fetchTwoWeekInformation(destination_FIPS)
            departure_and_destination_info = {
                'departure_chars': departure_info,
                'destination_chars': destination_info
            }
            return departure_and_destination_info, 200
        elif departure:
            departure_FIPS = requestFIPS(departure)
            departure_info = fetchTwoWeekInformation(departure_FIPS)
            return departure_info, 200
        elif destination:
            destination_FIPS = requestFIPS(destination)
            destination_info = fetchTwoWeekInformation(destination_FIPS)
            return destination_info, 200
        else:
            return "County not found", 404

class TestingWindow(Resource):

    def get(self):

        return 'I am working!', 200

class FIPSInfo(Resource):

    def get(self, FIPS):
        info = fetchTwoWeekInformation(FIPS)
        return info, 200



api.add_resource(CountyInfo, "/county-info", "/county-info/", "/county-info/departure=<string:departure>/destination=<string:destination>")
api.add_resource(TestingWindow, '/testing', '/testing/')
api.add_resource(FIPSInfo, '/FIPS/<int:FIPS>')

if __name__ == '__main__':
    app.run(debug=True)


#dictionary_of_dataframes = {}
#for i in df.FIPS.unique():
#    print(i)
#    print(type(i))
#    cases = pd.DataFrame(df.loc[df['FIPS'] == i]['Confirmed'])[::-1]
#    cases['Day_Cases'] = cases['Confirmed'].sub(cases['Confirmed'].shift())
#    cases['Day_Cases'].iloc[0] = np.NaN
#    dictionary_of_dataframes[f'{str(i)}_df'] = cases
