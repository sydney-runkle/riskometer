########### IMPORTS ###########

from flask import Flask
from flask_restful import Api, Resource, reqparse
import random

#Initialize app and API
app = Flask(__name__)
api = Api(app)

#Additional imports for data manipulation
import datetime
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

#Necessary for accessing other APIs
import json
import requests

########### VARIABLE DECLARATIONS ##########
JHU_df = pd.DataFrame()

#Initialize pandas dataframe to store COVID-19 info for counties

########### FUNCTION DECLARATIONS ##########

#Retrieves last 15 days worth of csv files from the JHU repository
def JHUDataFetch():

    global JHU_df
    #Create list of 15 most recent days in decending order
    base = datetime.datetime.today()
    date_list = [base - datetime.timedelta(days=x+1) for x in range(15)]

    #Iterates through date list and extracts a day, month, and year from each datetime object, then reads the corresponding csv file and attaches the information to the DataFrame
    for i in date_list:
        day = i.strftime('%d')
        month = i.strftime('%m')
        year = i.strftime('%Y')
        print(JHU_df.shape)

        #Using string interpolation
        link=f'./JHU_CSVs/{month}-{day}-{year}.csv'

        try:
            #Reads csv files and appends to the main JHU_df
            data=pd.read_csv(link, error_bad_lines=False)
            #Adds a date column
            data['Date'] = datetime.datetime(int(year), int(month), int(day))
            JHU_df = JHU_df.append(data)
        except Exception as e:
            print(f'WARNING: Exception when uploading JHU file: {link}. \nException: {e}')


#Returns FIPS (county and state) code when given a location in a variety of formats
def requestFIPS(location):

    #Open cage data API call
    fipsRequest = requests.get(f'https://api.opencagedata.com/geocode/v1/json?q={location}&key=679bf5d7a07e424f9cf7d1649ec8037d')


    if fipsRequest.status_code == 200:
        try:
            #Load json from request, then extract the county level FIPS code from the annotations section
            response = json.loads(fipsRequest.text)
            FIPS = int(response['results'][0]['annotations']['FIPS']['county'])
            return FIPS;
        except Exception as e:
            print(f'Failed to find FIPS. Exception: {e}')
    else:
        print(f'Error while processing FIPS request \nStatus Code of request: {fipsRequest.status_code}')


#When given a FIPS code, fetches data from JHU DataFrame
def fetchTwoWeekInformation(FIPS):
    #Fetches two weeks worth of information for a certain county, then reverses it to be in sequential order
    two_week_data = pd.DataFrame(JHU_df.loc[JHU_df['FIPS']==FIPS])[::-1]
    #Adds a Day Cases column that represents the number of new cases reported each day by calculating each row minus the previous
    two_week_data['Day_Cases'] = two_week_data['Confirmed'].sub(two_week_data['Confirmed'].shift())
    two_week_data['Day_Cases'].iloc[0] = np.NaN

    #Dictionary with county information to be returned (later converted to JSON format)
    county_information = {
        'FIPS': FIPS,
        'two_week_data': two_week_data['Day_Cases'][1:].to_json(orient='values'),
        'location': two_week_data['Combined_Key'].values[0],
        'deaths': int(two_week_data['Deaths'].values[-1]),
        'total cases': int(two_week_data['Confirmed'].values[-1])
    }

    return county_information

#Init function for the API
def API_init():
    JHUDataFetch()

########## RESOURCE DECLARATIONS ##########

class InfoByLocation(Resource):

    def get(self, departure="", destination=""):

        #When provided with both departure and destination, return a dictionary with two week characteristics for the departure and destination locations
        if(departure != "" and destination != ""):
            departure_FIPS = requestFIPS(departure)
            departure_info = fetchTwoWeekInformation(departure_FIPS)
            destination_FIPS = requestFIPS(destination)
            destination_info = fetchTwoWeekInformation(destination_FIPS)
            departure_and_destination_info = {
                'departure_chars': departure_info,
                'destination_chars': destination_info
            }
            return departure_and_destination_info, 200
        #When provided with only departure information, return a dictionary with two week information for that location
        elif(departure != "" and destination == ""):
            print('Trying to just analyze departure')
            departure_FIPS = requestFIPS(departure)
            departure_info = fetchTwoWeekInformation(departure_FIPS)
            return departure_info, 200
        #When provided with only destination information, return a dictionary with two week information for that location
        elif(destination != "" and departure == ""):
            destination_FIPS = requestFIPS(destination)
            destination_info = fetchTwoWeekInformation(destination_FIPS)
            return destination_info, 200
        #If none of the above conditions are met, throw an error
        return "County not found by destination or departure", 404

#Fetches two weeks of information about a location based on provided FIPS code
class InfoByFIPS(Resource):

    def get(self, FIPS):

        if FIPS:
            info = fetchTwoWeekInformation(FIPS)
            return info, 200
        return "Failed to fetch two weeks of information by FIPS", 404


#Testing resource
class TestingWindow(Resource):

    def get(self):

        return 'I am working!', 200

########## PROGRAM EXECUTION ##########
API_init()

########## API CONFIGURATION ##########

#Add necessary resources to the API with pertinent endpoints
api.add_resource(InfoByLocation, "/county-info", "/county-info/", "/county-info/departure=<string:departure>/destination=<string:destination>", "/county-info/departure=<string:departure>", "/county-info/destination=<string:destination>")
api.add_resource(TestingWindow, '/testing', '/testing/')
api.add_resource(InfoByFIPS, '/FIPS/<int:FIPS>')

if __name__ == '__main__':
    app.run(debug=True)
