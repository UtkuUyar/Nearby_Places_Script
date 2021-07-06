# Nearby_Places_Script
A small python script written with Google Places API to find a certain type of places around a location.
The script gets two inputs: description of a location which will be the "origin" of our search, and keywords to describe the type of places that user is interested in.

## How this code works
1. Description for the origin is taken from user. (i.e a city in a country)
2. Find this origin point's latitude and longitude by sending a find place request.
3. Keywords that describe the type of the places are taken from user. (i.e Gas Station)
4. Send a nearby search request to find most near 20 places.
    * If there are more places to fetch, prompt user to whether they want more places or not. Get another 20 places untill user says otherwise.
    * If there are no more places to fetch, do nothing.
5. For all found places, send a place details request to get name, address, location, contact number and website informations of that place.
6. Form the pandas dataframe and if user wants, save it as an excel file.


# Usage example:

An example run is given under example folder. After running `python main.py` on console like this:

![Sample run of this script](example/spor_salonları_kartal.PNG)

The result gets saved into "spor_salonları_kartal.xlsx". You can also find this file at example folder.
