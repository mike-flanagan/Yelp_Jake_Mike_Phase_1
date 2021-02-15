# def import_module()
#     import requests
#     import json
#     import sys
#     import pandas as pd
#     import csv
#     from  keys  import  client_id, api_key
    
# something_nice = import_module()
# """awww
# from fn import something_nice 
# ^ doesn't work :(
# """

url =  'https://api.yelp.com/v3/businesses/search' #points to url of user's yelp developer page

headers = {
        'Authorization': 'Bearer {}'.format(api_key),
    }

### 
# Dynamic: change term, location, and categories to pull different results from call
# * Required for defining url_params
term = 'Film Production'
location = 'Brooklyn'
categories = 'Video/Film'
spec = f'{term}_{location}_{categories}_data'

url_params = {
                "term": term.replace(' ', '+'),
                "location": location.replace(' ', '+'),
                "categories" : categories,
                "limit": 50,
                "offset": 0
            }

csv_filepath = f'database/{term}_{location}_database.csv'

def yelp_call(headers, url_params):
    """
    This will use the requests module to get from Yelp. 
    What is returned will be modified by our URL parameters.
    This must be called fresh with updated url_params for each call if we want to return more results.
    
    our url, header and params should be consistent, atleast with our Yelp data
    
    2/14 — defined data variable in to this function.
    """
    response = requests.get(url, headers=headers, params=url_params) 
    data = response.json()
    return data

def parse_data(list_of_data):
    """
    Input data['businesses'] to return a list of tuples,
    with each tuple containing individual business name, address, and other items
    """
    businesses = []
    for business in list_of_data:
        biz_price = None
        if 'price' not in business.keys():
            biz_price = None
        else:
            biz_price = len(business['price'])
        biz_tuple = (business['name'],
                     business['location']['display_address'],
                     business['location']['city'],
                     business['rating'],
                     business['review_count'],
                     business['coordinates'],
                     biz_price)
        businesses.append(biz_tuple)
    return businesses

def call_1000(csv_filepath):
    """
    JAKE I FUCKING DID IT

    WE DON'T EVEN GET AN ERROR MESSAGE ANYMORE
    """
    url_params['offset'] = 0
    results = yelp_call(headers, url_params)
    parsed = parse_data(results['businesses']) # list of businesses in tuples
    num = results['total']
    biz_list = []
    while url_params['offset'] < 1000 and len(biz_list) < num:
        for biz in parsed:
            biz_list.append(biz)
        url_params['offset'] += 50
        results = yelp_call(headers, url_params)
        if num >= len(biz_list):
            if 'businesses' not in results:
                break
            else:
                parsed = parse_data(results['businesses']) # list of businesses in tuples
        elif len(biz_list) <= 950:
            continue
        else:
            break
    df = pd.DataFrame(biz_list, columns=['Name', 'Address','City', 'Rating','Review Count','Coordinates','Price'])
    with open(csv_filepath, "a") as f: #'x' creates and writes to csv
        read_file = csv.writer(f)
        df.to_csv(csv_filepath, mode = "a", index = False)
    print('CSV file written to {csv_filepath}.')
    return df
