#!/usr/bin/env python
# coding: utf-8

# In[106]:


# 2020-03-26:
# 1) Added trip distance corrections
# 2) using operatorcallsign instead of owner
# TODO:
# Explain where does airport come from
# Make sure flights that depart the day before are divided?

import requests
import time
import geopy.distance
import datetime  # To calculate today / yesterday UNIX timestamp
import math  # To see if not a number, NaN
import os
os.environ['OPENBLAS_NUM_THREADS'] = '1'  # required by the server
import pandas as pd
import numpy as np

getwd = os.getcwd()
if 'pedro' in getwd:
    dirpath = "../data/"
    sqlpath = '../website/db/ghgflights.db'
else:
    # This is for when running on the server on public_html
    # dirpath = os.getcwd()+"/public_html/ghgflights/data/"
    # sqlpath = os.getcwd()+"/public_html/ghgflights/db/ghgflights.db"
    # This is for when running on the server on /ghgflights
    # parpath = os.path.dirname(getwd)
    parpath = getwd
    dirpath = parpath+"/ghgflights/data/"
    sqlpath = parpath+"/ghgflights/db/ghgflights.db"

# opensky-network credentials
username = 'pdespouy'
password = '123456Qw'

# In case we want to use a sample of aircrafts in our local machine
ISTEST = False

# number of days with data
# a day is added as buffer
# max number of days is ~30
# 26 days works fine
DAYS = 26
DAYS += 1
if DAYS > 29:
    DAYS = 29

# dates variables
# NOTE: flights api just updates at midnight
end   = int(time.time())
begin = int(end - ((DAYS)*24*3600))  # 1 hour = 60 * 60


# In[107]:


# Opensky aircrafts are labeled as ICAO24 (e.g. c06151), 
# but ICAO fuel-aircraft mapping has aircrafts models in IATA, e.g. B737 is 737 

# We download mapping (aircraftDatabase.csv) from 
# https://opensky-network.org/datasets/metadata/
# And make a lean version of it,
# from only aircrafts with icao codes

aircrafts = pd.read_csv(dirpath+'aircrafts_clean.csv', encoding='latin1')
aircrafts.head()


# In[108]:


aircrafts = aircrafts[['icao24','manufacturername','model','icao','iata','operatorcallsign']]
aircrafts.operatorcallsign.unique()


# In[109]:


# There are duplicates because aircrafts with 
# airline_name 'Air Canada Express' are also under airline_name 'Jazz Air', 
# but with operatorcallsign JAZZ
if (ISTEST):
    aircrafts = aircrafts[aircrafts.operatorcallsign.isin(["AIR CANADA", "JAZZ"])]
print('number of aircrafts:', len(aircrafts))
aircrafts.drop_duplicates(inplace=True)
print('number of aircrafts:', len(aircrafts))
aircrafts.head()


# In[110]:


aircrafts = aircrafts.rename(columns={'operatorcallsign':'owner'}, errors='ignore')


# In[111]:


# For testing purposes, we only take one aircraft
test1 = ['c0172e', 'c02eb9', 'c030fd', 'c030a6', 'c0315c', 'c05f0c', 'c03150', 'c05efa', 'c01b6c']
test2 = ['c03329']
if (ISTEST) :
    aircrafts = aircrafts[aircrafts.icao24.isin(test2)]
aircrafts


# In[112]:


# We pull JSON from API and convert to a pandas dataframe
# Doc: https://opensky-network.org/apidoc/rest.html#departures-by-airport
df_array = []
path = '@opensky-network.org/api/flights/aircraft?icao24='
for index, row in aircrafts.iterrows():
    a = row['icao24'].lower()
    print(a)
    d = 'https://'+username+':'+password+path+a+'&begin='+str(begin)+'&end='+str(end)
    print(d)
    try:
        r = requests.get(d).json()
        # We need to transform the JSON to a pandas dataframe
        df_array.append(pd.json_normalize(r))
    except:
        continue
df_array


# In[76]:


# We merge list of dataframes
ddf = pd.concat(df_array)
ddf.head()


# In[77]:


# We want to select a few columns
ddf = ddf[['icao24','callsign','estDepartureAirport','estArrivalAirport','firstSeen','lastSeen']]
ddf.head()


# In[78]:


# We want to store in db flights with uknown airports
# We want to filter all flights that do not go to 'None'
# ddf = ddf[ddf['estArrivalAirport'].notnull()]
# ddf = ddf[ddf['estDepartureAirport'].notnull()]
# ddf.head()


# In[79]:


# To remove duplicates from merging arrival and departure data frames
df = ddf.drop_duplicates()
print("Flights: ", len(df['icao24']))


# In[80]:


dfi = pd.merge(df, aircrafts, how='inner', on='icao24')
dfi.head()


# In[81]:


fuel = pd.read_csv(dirpath+'fuel_consumption.csv')
# fuel[fuel['Code'] == '767']
fuel.head()


# In[82]:


def getInterval(d):
    if (d < 125):
        return [125, 125]
    elif ((d >= 125) and (d < 250)):
        return [125, 250]
    elif ((d >= 250) and (d < 500)):
        return [250, 500]
    elif ((d >= 500) and (d < 750)):
        return [500, 750]
    elif ((d >= 750) and (d < 1000)):
        return [750, 1000]
    elif ((d >= 1000) and (d < 1500)):
        return [1000, 1500]
    elif ((d >= 1500) and (d < 2000)):
        return [1500, 2000]
    elif ((d >= 2000) and (d < 2500)):
        return [2000, 2500]
    elif ((d >= 2500) and (d < 3000)):
        return [2500, 3000]
    elif ((d >= 3000) and (d < 3500)):
        return [3000, 3500]
    elif ((d >= 3500) and (d < 4000)):
        return [3500, 4000]
    elif ((d >= 4000) and (d < 4500)):
        return [4000, 4500]
    elif ((d >= 4500) and (d < 5000)):
        return [4500, 5000]
    elif ((d >= 5000) and (d < 5500)):
        return [5000, 5500]
    elif ((d >= 5500) and (d < 6000)):
        return [5500, 6000]
    elif ((d >= 6000) and (d < 6500)):
        return [6000, 6500]
    elif ((d >= 6500) and (d < 7000)):
        return [6500, 7000]
    elif ((d >= 7000) and (d < 7500)):
        return [7000, 7500]
    elif ((d >= 7500) and (d < 8000)):
        return [7500, 8000]
    else:
        return [8000, 8500]


# In[83]:


# We want to get distances (in nm, calculated as great circle distance)
airports = pd.read_csv(dirpath+'airports.csv')
# airports = airports[['icao', 'latitude', 'longitude', 'city', 'region_code', 'country_code']]
airports = airports[['gps_code','latitude_deg','longitude_deg',
                     'municipality','iso_region','iso_country']]
airports = airports.rename(columns={
    'gps_code'     :'icao_airport',
    'latitude_deg' :'latitude',
    'longitude_deg':'longitude',
    'municipality' :'city',
    'iso_region'   :'region',
    'iso_country'  :'country'
})
# codeIataAirport;nameAirport;codeIso2Country;codeIcaoAirport;codeIataCity;latitudeAirport;longitudeAirport
# airports.columns.to_series().groupby(airports.dtypes).groups
# We remove rows with empty values in icao_airport
airports = airports[airports['icao_airport'].notnull()]
airports.head()


# In[84]:


# We will merge (outer join) the airport coordinates, and remove the following columns later:
# 'icao_x', 'icao_y', 'latitude_x', 'latitude_y', 'longitude_x', 'longitude_y'
dfi = pd.merge(dfi, airports, how='left', left_on='estDepartureAirport', right_on='icao_airport')
dfi = pd.merge(dfi, airports, how='left', left_on='estArrivalAirport', right_on='icao_airport')
# dfi.to_csv('data/test.csv')
dfi.head()


# In[85]:


def getCO2(model, nm):
    # We get intervals necessary to pull from ICAO table
    intervals = getInterval(nm)
    # print str(columns[0])
    f = fuel[fuel['Code'] == model][[str(intervals[0]), str(intervals[1])]]

    minx = f.iloc[0][0]
    maxx = f.iloc[0][1]
    if (minx == maxx):
        # Some corrections
        minx = 0
        intervals[0] = 0
        
    a = minx
    b = float(maxx - minx)  # on python 2.7, we need to declare variables as float to return us a float
    c = float(nm - intervals[0])
    d = float(intervals[1] - intervals[0])
    # kg_flight = minx + (float(maxx - minx)*float(nm - intervals[0])/float(intervals[1]-intervals[0]))
    kg_flight = a + (b*c/d)

    # constant representing the number of kg of CO2 produced by burning a kg of aviation fuel
    kg_to_c02 = 3.16
    # CO2 emissions in kg:
    co2 = kg_to_c02 * kg_flight
#     print "f", f
#     print "a+(b*c/d)"
#     print a, b, c, d
#     print model, kg_flight, co2
    return co2


# In[86]:


# Test cell
# d = "CYYZ"
# a = "CYYC"
# coords_1 = (dfi[dfi['icao_x'] == d]['latitude_x'].values[0], dfi[dfi['icao_x'] == d]['longitude_x'].values[0])
# coords_2 = (dfi[dfi['icao_y'] == a]['latitude_y'].values[0], dfi[dfi['icao_y'] == a]['longitude_y'].values[0])
# nm = geopy.distance.distance(coords_1, coords_2).nm
# print(int(nm))


# In[88]:


# As to convert timestamps to datetime
# needs to be here so it does not conflict with the previous import
from datetime import datetime

nm_array = []
co_array = []
dt_array = []
for index, row in dfi.iterrows():  # not sure why but we need to use index
    a = row['estArrivalAirport']
    d = row['estDepartureAirport']

    # We calculate the distance with longitude and latitude as input     
    if row['latitude_x'] and row['longitude_x']:
        coords_1 = (row['latitude_x'], row['longitude_x'])
    else:
        pass
    if row['latitude_y'] and row['longitude_y']:
        coords_2 = (row['latitude_y'], row['longitude_y'])
    else:
        pass
    # try/except so if function breaks, it does not stop
    try:
        nm = geopy.distance.distance(coords_1, coords_2).nm
        km = 1.852 * nm
        # We make trip distance corrections, since flights do not follow a straight line, page 8:
        # https://www.icao.int/environmental-protection/CarbonOffset/Documents/Methodology%20ICAO%20Carbon%20Calculator_v10-2017.pdf
        # Less than 550Km: +50 Km
        # Between 550Km and 5500Km: +100 Km
        # Above 5500Km: +125 Km
        if (km==0):
            pass
        elif (km < 550):
            km += 50
        elif (km < 5500):
            km += 100
        else:
            km += 125
        nm = km / 1.852
    except:
        nm = 0
    nm = int(nm)
    a = row['iata']
    if (nm == 0) or (a == 0):
        o = 0
    else:
        try:
            c = getCO2(a, nm)
            o = int(c)
        except:
            o = 0
    print(a,nm,o)
    dt = datetime.utcfromtimestamp(row['firstSeen'])
    dt = dt.strftime('%Y-%m-%d %H:%M:%S')
    nm_array.append(int(nm))
    co_array.append(o)
    dt_array.append(dt)

# We remove extra columns
# manufacturer is already in model column
columns = ['icao_airport_x', 'icao_airport_y', 
           'latitude_x'    , 'latitude_y'    , 
           'longitude_x'   , 'longitude_y'   ,
           'manufacturername']
df = dfi.drop(columns, axis=1)

df['distance']      = nm_array
df['co2']           = co_array
df['firstSeenDate'] = dt_array
df = df.sort_values(by=['distance'])
df.head()


# In[89]:


print('Rows with distance > 0:', len(df[df['distance'] > 0]))
print('Total C02:', sum(df['co2']))
print('Count C02:', len(df['co2']))


# In[90]:


# We remove the whitespaces from callsign column
df['callsign'] = df['callsign'].str.strip()


# In[91]:


# We remove commas from owner
df['owner'] = df['owner'].str.replace(',', '')


# In[92]:


list(df)


# In[93]:


# We want the column names to be the same as the table column names
df.rename(columns={
    'estDepartureAirport':'fromAirport',
    'estArrivalAirport'  :'toAirport',
    
    'city_x'   :'fromCity',
    'region_x' :'fromRegion',
    'country_x':'fromCountry',
    
    'city_y'   :'toCity',
    'region_y' :'toRegion',
    'country_y':'toCountry'
}, inplace=True)

# We replace NaNs with '' in two columns
# NOTE: maybe we should do this in every
# column so conn.execute does not break
df['fromRegion'].fillna('', inplace=True)
df['toRegion'].fillna('', inplace=True)


# In[94]:


list(df)


# In[96]:


df


# In[97]:


# NaNs are replaced with empty string
# so sql query does not break
df = df.replace(np.nan, '', regex=True)


# In[98]:


# ignore so it does not break in case there is a duplicate
import sqlite3
conn = sqlite3.connect(sqlpath)
for index, row in df.iterrows():
    colnames = tuple(list(df))
    values   = tuple(list(row))
    query    = "INSERT OR IGNORE INTO flights {} VALUES {};".format(colnames, values)
    conn.execute(query)
conn.commit()
conn.close()


# In[162]:


# NOTE: we have two columns with unique
# CREATE TABLE flights (id INTEGER PRIMARY KEY, icao24 TEXT, callsign TEXT, fromAirport TEXT, toAirport TEXT, 
#                       firstSeen INTEGER, lastSeen INTEGER, model TEXT, icao TEXT, iata TEXT, owner TEXT, 
#                       fromCity, fromRegion, fromCountry TEXT, toCity TEXT, toRegion TEXT, toCountry TEXT, 
#                       distance INTEGER, co2 INTEGER, firstSeenDate TEXT, UNIQUE(icao24, firstSeen));


# In[163]:


# import subprocess
# subprocess.call("php /home/despfzpe/public_html/carbon/InsertToDB.php")


# In[ ]:




