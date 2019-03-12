# YelpAPI-DataParse
Using Python's requests library, I pull data from Yelp using their Fusion REST API, and output it into data that can be read by a custom APP built on AWS.

## Preliminary Notes

This utilizes Python's requests library. The current version of Yelp Fusion API no longer requires the code to pass a client ID and client secret to obtain a bearer token, making the code much simpler. This code still uses the former version of the API. The code will be updated soon to support the current version.

## Running the scripts

Must run `YelpAPI-DataParse.py` with terms -t, -l, and/or -s, standing for term, location, and search limit respectively. 

For example, you can run `YelpAPI-DataParse.py -t 'veterinarian' -l 'Philadelphia, PA' -s 20` to search for term "veterniarian" in location "Philadelphia, PA" and list 20 results. These are actually the default terms as well. 

## Built With

* Python 2.7 or 3.0+
* GeoPy Python library (pip install geopy)

## Authors

* **Henry Luo** 
