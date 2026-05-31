import requests
from decouple import config
import pandas as pd
from pprint import pprint
from urllib.parse import urlencode
from concurrent.futures import ThreadPoolExecutor
from helper import (
    check_all_characters_present
)
from constants import (
    home_airport_hotel_column_names,
    check_routes_columns,
    preprocess_for_final_reviewer_columns,
)
import threading
import concurrent.futures
api_key = config("API_KEY")


def check_home_airport_hotel(df, details_df):

    # Loop through each row in the DataFrame 'df'

    data_list = check_all_characters_present(df,home_airport_hotel_column_names)
    data_list.sort()
    
    for index, row in df.iterrows():
        # Extract latitude and longitude values for origin and destination
        
        origin_addr_lat = row[data_list[6]]
        origin_addr_lng = row[data_list[7]]
        destin_addr_lat = row[data_list[0]]
        destin_addr_lng = row[data_list[1]]

        # Check if origin latitude and longitude are missing
        if not (origin_addr_lat and origin_addr_lng):
            # Get the type of origin place
            origin_place_type = row[data_list[8]]
            lat_col, lng_col = None, None  # Initialize variables for latitude and longitude column names

            # Determine the appropriate columns based on place type
            if 'hotel' in origin_place_type.lower() or 'home' in origin_place_type.lower():
                lat_col, lng_col = data_list[4], data_list[5]
            elif 'airport' in origin_place_type.lower():
                airport_destin_code = row[data_list[2]]
                airport_row = details_df[details_df['LIME_CODE'] == airport_destin_code]
                if not airport_row.empty:
                    lat_col, lng_col = 'lat6', 'lng6'

            # If valid latitude and longitude columns are found, populate the corresponding values
            if lat_col and lng_col:
                df.at[index, data_list[6]] = row[lat_col]
                df.at[index, data_list[7]] = row[lng_col]

        # Check if destination latitude and longitude are missing
        if not (destin_addr_lat and destin_addr_lng):
            # Get the type of destination place
            destin_place_type = row[data_list[3]]
            lat_col, lng_col = None, None  # Initialize variables for latitude and longitude column names

            # Determine the appropriate columns based on place type
            if 'hotel' in destin_place_type.lower() or 'home' in destin_place_type.lower():
                lat_col, lng_col = data_list[4], data_list[5]
            elif 'airport' in destin_place_type.lower():
                airport_destin_code = row[data_list[2]]
                airport_row = details_df[details_df['LIME_CODE'] == airport_destin_code]
                if not airport_row.empty:
                    lat_col, lng_col = 'lat6', 'lng6'

            # If valid latitude and longitude columns are found, populate the corresponding values
            if lat_col and lng_col:
                df.at[index, data_list[0]] = row[lat_col]
                df.at[index, data_list[1]] = row[lng_col]
    # Return the DataFrame 'df' with the populated columns
    return df



# Separate function to make API request
def make_api_request(cord, data_list, base_url, api_key):
    """
    Make a request to the HERE API to check if there's a bus route between two points.
    
    Parameters:
    - cord: A Pandas Series containing latitude and longitude coordinates for various points.
    - data_list: A list of columns from the dataframe indicating which columns to use for the route check.
    - base_url: The base URL for the HERE API endpoint.
    - api_key: The API key for accessing the HERE API.
    
    Returns:
    - "Approved" if a route exists.
    - "Review" otherwise.
    """
    # Check if origin and destination coordinates are different
    if (cord[data_list[0]], cord[data_list[1]]) != (cord[data_list[2]], cord[data_list[3]]):
        waypoint0 = f"{cord[data_list[2]]},{cord[data_list[3]]}"
        waypoint1 = f"{cord[data_list[0]]},{cord[data_list[1]]}"

        # Prepare API parameters
        params = {
            'apiKey': api_key,
            'origin': waypoint0,
            'destination': waypoint1,
            'transportMode': 'bus'
        }
        
        url_with_params = base_url + urlencode(params)
        
        # Check and add via waypoints to the API request if they exist
        for col in cord.index:
            if '_LAT_' in col and col not in [data_list[2], data_list[0]]:
                long_col = col.replace('_LAT_', '_LONG_')
                if not pd.isna(cord.get(col)) and not pd.isna(cord.get(long_col)):
                    via_waypoint = f"{cord[col]},{cord[long_col]}"
                    url_with_params += f"&via={via_waypoint}"

        # Send the API request
        response = requests.get(url_with_params)
        response_json = response.json()
        # Check if a route was found in the response
        if 'routes' in response_json:
            return "Approved"
        else:
            return 'Review'
    else:
        return 'Review'

def check_routes(df):
    """
    Check routes for each row in the dataframe by sending API requests in parallel.
    
    Parameters:
    - df: A Pandas DataFrame containing rows of coordinates.
    
    Returns:
    - DataFrame with an additional 'ROUTE_STATUS' column indicating if a route was found.
    """
    data_list = check_all_characters_present(df, check_routes_columns)
    data_list.sort()
    
    base_url = "https://router.hereapi.com/v8/routes?"
    status_list = []

    # Use ThreadPoolExecutor to send API requests in parallel
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = []
        for _, cord in df.iterrows():
            if 'Test_Status' in df.columns:
                # Only send requests for rows that haven't been tested
                if cord['Test_Status'] != "Tested":
                    futures.append(executor.submit(make_api_request, cord, data_list, base_url, api_key))
                else:
                    status_list.append(cord['ROUTE_STATUS'])
            else:
                futures.append(executor.submit(make_api_request, cord, data_list, base_url, api_key))
        
        # Retrieve the results from the futures
        for future in futures:
            status_list.append(future.result())

    df['ROUTE_STATUS'] = status_list
    return df


# def get_nearest_station_responses(cords):
#     # Make a batched API request for multiple cords
#     url = "https://transit.router.hereapi.com/v8/stations"
#     responses = []

#     for i, cord in cords:
#         params = {
#             "apiKey": api_key,
#             "in": f"{cord[0]},{cord[1]}",  # Coordinates for which you want to find nearby bus stops
#             "radius": 531  # Search radius in meters
#         }
#         response = requests.get(url, params=params, timeout=10)
#         responses.append(response.json())
#         print("================================")
#         print(i, "- Response = ", response.status_code)
#         print("================================")

#     return responses


def get_nearest_station_responses(cords):
    url = "https://transit.router.hereapi.com/v8/stations"
    responses = []
    MAX_RETRIES = 3  # Define a maximum number of retries


    for i, cord in enumerate(cords):
        print(f"Processing cord index {i}: {cord}")
        params = {
            "apiKey": api_key,
            "in": f"{cord[0]},{cord[1]}",
            "radius": 531
        }
        retries = 0
        while retries < MAX_RETRIES:
            try:
                response = requests.get(url, params=params, timeout=10)
                responses.append(response.json())
                break
            except requests.Timeout:
                print(f"Request timed out for cord {cord}. Retrying {retries + 1}/{MAX_RETRIES}...")
                retries += 1
        else:
            # Handle the case when max retries are reached
            print(f"Max retries reached for cord {cord}. Skipping...")
            responses.append(None)

    return responses


# def check_stops(stops_list_data):
#     stops_status = []
#     tested_list = []
#     results = [None] * len(stops_list_data)

#     for i, stop_data in enumerate(stops_list_data):
#         process_stop(stop_data, results, i)

#     for result in results:
#         if result is not None and result[0] is not None:
#             stops_status.append(result[0])
#             tested_list.append(result[1])
    
#     data = {'stops': stops_status, 'tested': tested_list}
#     return data

def check_stops(stops_list_data):
    stops_status = []
    tested_list = []
    results = [None] * len(stops_list_data)
    threads = []

    for i, stop_data in enumerate(stops_list_data):
        thread = threading.Thread(target=process_stop, args=(stop_data, results, i))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    for result in results:
        if result[0] is not None:
            stops_status.append(result[0])
            tested_list.append(result[1])
    
    data = {'stops': stops_status, 'tested': tested_list}
    return data


def process_stop(stops_data, results, index):
    approval_list = []
    for j in range(0, len(stops_data), 2):
        if j + 1 < len(stops_data) and not pd.isna(stops_data[j]) and not pd.isna(stops_data[j + 1]):
            cord = (stops_data[j], stops_data[j + 1])
            response = get_nearest_station_responses([cord])[0]
            # pprint(response)
            if response.get('stations'):
                approval_list.append(True)
            elif response.get('notices'):
                approval_list.append(False)
            else:
                approval_list.append(False)
        else:
            approval_list.append(True)
    # print(f"This Stop having nearest bus stops = {all(approval_list)}")
    if all(approval_list):
        results[index] = ('Approved', 'Tested')
    else:
        results[index] = ('Review', 'Tested')

def preprocess_for_Final_Reviewer(df):
    final_reviewer = []
    first_cleaner = []
    final_usage = []
    final_review=[]
    data_list=check_all_characters_present(df,preprocess_for_final_reviewer_columns)
    route_stop_columns=check_all_characters_present(df,['ROUTE_STATUS','Stops_Status'])
    for index, row in df.iterrows():
        interv_init = row['INTERV_INIT']
        have_5_min = row[data_list[0]]

        if route_stop_columns :
            route_status = row['ROUTE_STATUS']
            stops_status = row['Stops_Status']
        else:
            route_status=None
            stops_status=None

        if interv_init == '999':
            first_cleaner.append('Test')
            final_reviewer.append('Test/No 5 MIN')
            final_usage.append('Remove')
            final_review.append(' ')
        elif have_5_min != 1:
            first_cleaner.append('No 5 MIN')
            final_reviewer.append('Test/No 5 MIN')
            final_usage.append('Remove')
            final_review.append(' ')

        elif have_5_min == 1 and route_status == 'Approved' and stops_status == 'Approved':
            final_reviewer.append('HereAPI Approved')
            final_usage.append('Use')
            final_review.append('Approved')
            first_cleaner.append('HereAPI')
        elif have_5_min == 1  and route_status == 'Approved' and stops_status != 'Approved':
            final_reviewer.append(' ')
            final_usage.append(' ')
            final_review.append(' ')
            first_cleaner.append('HereAPI')
        elif have_5_min == 1 and route_status != 'Approved' and stops_status != 'Approved':
            final_reviewer.append(' ')
            final_usage.append(' ')
            final_review.append(' ')
            first_cleaner.append('HereAPI')
        else:
            final_reviewer.append(' ')
            final_usage.append(' ')
            final_review.append(' ')
            first_cleaner.append('')

    new_dict = {'final_reviewer': final_reviewer, 'first_cleaner': first_cleaner, 'final_usage': final_usage,'final_review':final_review}
    return new_dict