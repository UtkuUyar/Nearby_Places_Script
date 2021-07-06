import requests
import time
import pandas as pd
import os

from urllib import parse


# IMPORTANT TO USE ASCII ESCAPE SEQUENCES IN WINDOWS COMMAND BLOCK
os.system("color")


# Custom exception for handling errors from Places API
class CustomException(Exception):
    def __init__(self, reason, extra_info=""):
        self.reason = reason
        self.extra_info = extra_info
        super().__init__(self.reason)


# Error checking
def request_check(r):
    mp = r.json()
    extra_info = ""

    if r.status_code != 200:
        reason = "CONNECTION FAILED"
        raise CustomException(reason)

    # API Errors
    elif mp["status"] != 'OK':
        reason = mp["status"]
        if "error_message" in mp:
            extra_info = mp["error_message"]

        raise CustomException(reason, extra_info=extra_info)


# Function for finding the origin for search of nearby places
def get_midpoint(KEY):
    midpoint_text = "Enter the location that you want to find certain type of places around. (i.e Türkiye Balıkesir):\t"
    midpoint_query = parse.quote(input(midpoint_text), safe='')
    midpoint_baseurl = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json?"

    midpoint_queryurl = midpoint_baseurl + \
        f"input={midpoint_query}&" + f"key={KEY}&" + \
        "inputtype=textquery&" + "fields=geometry"

    r = requests.get(midpoint_queryurl)
    request_check(r)

    midpoint_json = r.json()
    midpoint = midpoint_json["candidates"][0]["geometry"]["location"]

    return midpoint


# Function for getting the id's of nearest n place (n <= 60).
# Place ids are useful for getting the details about that place.
def get_places(KEY, midpoint, keyword):
    results_baseurl = "https://maps.googleapis.com/maps/api/place/nearbysearch/json?"
    results_queryurl = results_baseurl + \
        "&".join([f"key={KEY}",
                  "location={}, {}".format(midpoint["lat"], midpoint["lng"]),
                  "rankby=distance",
                  f"keyword={parse.quote(keyword, safe='')}",
                  ])

    r = requests.get(results_queryurl)
    request_check(r)

    results_json = r.json()
    # Array for holding all of the place ids (Which is an unique id for each place)
    places = []

    cnt = 0

    condition = bool(len(results_json["results"]))

    print()
    # Do while loop
    while condition:
        for place in results_json["results"]:
            places.append(place["place_id"])

        if "next_page_token" not in results_json:
            condition = False
            break

        token = results_json["next_page_token"]

        start_time = time.time()

        choice = input("\033[A" + "\033[K" +
                       f"{(cnt+1) * 20} places ranked by distance to your choice of location has been fetched. Do you want to search for another 20 (y/n)?\t",)

        end_time = time.time()

        if choice != 'y':
            break

        requrl = results_baseurl + f"key={KEY}&" + f"pagetoken={token}"

        # Wait for page token to get registered to google's servers
        inner_delay = end_time - start_time
        sleep_duration = 4.5 - inner_delay if inner_delay < 4.5 else 0

        time.sleep(sleep_duration)

        r = requests.get(requrl)
        request_check(r)
        results_json = r.json()

        cnt += 1

    return places


# Function for getting detailed information corresponding to a place id.
def get_details(KEY, places, fields):
    details_baseurl = "https://maps.googleapis.com/maps/api/place/details/json?" + \
        f"key={KEY}&" + \
        "fields={}&".format(",".join(fields))

    result = dict()

    for index, place_id in enumerate(places):
        details_url = details_baseurl + f"place_id={place_id}"

        r = requests.get(details_url)
        request_check(r)

        details = r.json()["result"]
        details["place_id"] = place_id

        details["geometry"] = ", ".join(
            map(str, details["geometry"]["location"].values()))

        result[index] = details

    return result


# An example program
if __name__ == "__main__":

    # Must be kept secret. Make sure that no one else has access to your key.
    API_KEY = "YOUR KEY HERE"
    try:
        midpoint = get_midpoint(API_KEY)

        keyword = input(
            "What is the place that you are looking for (i.e Pilates Salonu)?\t")
        places = get_places(API_KEY, midpoint, keyword)

        print("Total of {} places found. Constructing the dataframe...".format(
            len(places)), end='\n'*2)

        # For all available field values, check https://developers.google.com/maps/documentation/places/web-service/place-data-fields
        fields = ["name", "formatted_address", "geometry/location",
                  "international_phone_number", "website"]
        dataframe_content = get_details(API_KEY, places, fields)

        df = pd.DataFrame(dataframe_content).astype(str).transpose()

        cols = df.columns.tolist().copy()
        cols.remove("name")
        cols = ["name"] + cols
        df = df[cols]

        print("Constructed dataframe! First five elements:", end='\n'*2)
        print(df.head())

        filename = input(
            "Enter the filename for excel file, enter nothing for quit saving:\t")

        if filename != "":
            writer = pd.ExcelWriter(filename + ".xlsx")
            df.to_excel(writer)
            writer.save()
            print("Excel file has been saved!")

        print("See you later...")
    except CustomException as customerr:
        print("ERROR:")
        print("\tREASON: " + customerr.reason)
        print("\tEXTRA INFORMATION: " + customerr.extra_info)
