from __future__ import print_function
from geopy.geocoders import Nominatim
from random import randint

import json
import pprint
import requests
import sys
import urllib
import argparse

try:
    # For Python 3.0 and later
    from urllib.error import HTTPError
    from urllib.parse import quote
    from urllib.parse import urlencode
except ImportError:
    # Fall back to Python 2's urllib2 and urllib
    from urllib2 import HTTPError
    from urllib import quote
    from urllib import urlencode

CLIENT_ID = 'REDACTED'
CLIENT_SECRET = 'REDACTED'

# API constants, you shouldn't have to change these.
API_HOST = 'https://api.yelp.com'
SEARCH_PATH = '/v3/businesses/search'
BUSINESS_PATH = '/v3/businesses/'  # Business ID will come after slash.
TOKEN_PATH = '/oauth2/token'
GRANT_TYPE = 'client_credentials'

parser = argparse.ArgumentParser()
parser.add_argument('-t', '--term')
parser.add_argument('-l', '--location')
parser.add_argument('-s', '--searchlimit')
args = vars(parser.parse_args())
# Defaults for our simple example.
if not args['term']:
    DEFAULT_TERM = 'veterinarian'
else:
    DEFAULT_TERM = args['term']
if not args['location']:
    DEFAULT_LOCATION = 'Philadelphia, PA'
else:
    DEFAULT_LOCATION = args['location']
if not args['searchlimit']:
    SEARCH_LIMIT = 20
elif not args['searchlimit'].isdigit():
    print('Must use integer, exiting...')
    exit(1)
else:
    SEARCH_LIMIT = args['searchlimit']

def obtain_bearer_token(host, path):
    url = '{0}{1}'.format(host, quote(path.encode('utf8')))
    assert CLIENT_ID, "Please supply your client_id."
    assert CLIENT_SECRET, "Please supply your client_secret."
    data = urlencode({
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': GRANT_TYPE,
    })
    headers = {
        'content-type': 'application/x-www-form-urlencoded',
    }
    response = requests.request('POST', url, data=data, headers=headers)
    bearer_token = response.json()['access_token']
    return bearer_token

def request(host, path, bearer_token, url_params=None):
    url_params = url_params or {}
    url = '{0}{1}'.format(host, quote(path.encode('utf8')))
    headers = {
        'Authorization': 'Bearer %s' % bearer_token,
    }

    print(u'Querying {0} ...'.format(url))

    response = requests.request('GET', url, headers=headers, params=url_params)

    return response.json()

def search(bearer_token, term, location):

    url_params = {
        'term': term.replace(' ', '+'),
        'location': location.replace(' ', '+'),
        'limit': SEARCH_LIMIT
    }
    return request(API_HOST, SEARCH_PATH, bearer_token, url_params=url_params)

def get_business(bearer_token, business_id):
    business_path = BUSINESS_PATH + business_id

    return request(API_HOST, business_path, bearer_token)

def query_api(term, location):
    bearer_token = obtain_bearer_token(API_HOST, TOKEN_PATH)

    response = search(bearer_token, term, location)

    return response


def getNeighborhood( lat, lon, geoObj):
    location = geoObj.reverse([lat, lon])
    for k,y in location.raw.items():
        if k == 'address':
            for kk,yy in y.items():
                if kk == 'neighbourhood':
                    return yy

def anumRand(length):
    try:
        int(length)
    except ValueError:
        print('Not an integer')
        exit(1)
    anumBuffer = 'abcdef0123456789'
    anum = ''
    for i in range(0,length):
        anum = anum + anumBuffer[randint(0,len(anumBuffer)-1)]
    return anum

def main():
    jfile = query_api(DEFAULT_TERM, DEFAULT_LOCATION)
    jdata = jfile['businesses']		#Json Body must be identified based on Yelp API Docs
    count = 0
    newjdata = []
    anumList = []
    geolocator = Nominatim()

    for i in range(0,int(SEARCH_LIMIT)):
        num = anumRand(4)
        while num in anumList:
            num = anumRand(4)
        anumList.append(num)

    for each in jdata:
        newdict = {}                #ALL dictionary
        locationDict = {}           #Location dictionary
        for k,y in each.items():
            newdict['vetHospitalId'] = anumList[count]
            if k == 'name':
                newdict['name'] = y 
            elif k == 'categories':
                cuis = []
                for cats in y:
                    for kk,yy in cats.items():
                        if kk == 'title':
                            cuis.append(yy)
                newdict['specialtyCare'] = cuis
                newdict['service_type'] = cuis[0]
            elif k == 'price':
                newdict['price'] = len(y.encode('ascii','ignore'))
            elif k == 'coordinates':                                         #Coordinates loop
                coordict = {}
                for kk,yy in y.items():
                    if kk == 'latitude':
                        coordict['lat'] = yy
                        lat = str(yy)
                    elif kk == 'longitude':
                        coordict['lon'] = yy
                        lon = str(yy)
                locationDict.update({'geocoordinate': coordict})
                locationDict.update({'neighborhoods': [str(getNeighborhood(lat,lon,geolocator))]})
                print('fetched neighborhood {0}'.format(str(count+1)))
            elif k == 'location':
                for kk,yy in y.items():
                    if kk == 'city':
                        locationDict.update({'city': yy})
                    elif kk == 'state':
                        locationDict.update({'state': yy})
                    elif kk == 'zip_code':
                        locationDict.update({'postal_code': yy})
                    elif kk == 'address1':
                        locationDict.update({'address': [yy]})
        newdict.update({'location': locationDict})
        newdict.update({'insurance': randint(1,4)})
        newjdata.append(newdict)
        count = count + 1
    with open('output.json', 'w') as outfile:
        outfile.write(json.dumps(newjdata, indent=4, sort_keys=True))

if __name__ == '__main__':
    main()
