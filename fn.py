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

""" 
# Note: The 2 variables below are useful for the review functions below
# Can be used to open database by referring to the last term and location the user has set
# These may be good to put in a function

term_loc = f'database/{term}_{location}_database.csv'
biz_data = pd.read_csv(term_loc)
"""

def call_reviews(biz_id): 
    list_of_reviews = []
    for biz in biz_id:
        response = requests.get(f'https://api.yelp.com/v3/businesses/{biz}/reviews',headers = headers)
        review_data = response.json()
        list_of_reviews.append(review_data)
    return list_of_reviews

def call_all_reviews(b_data): 
    biz_id = []
    for j in b_data['Id']: #ID column of business data dataframe
        biz_id.append(j)
    list_of_reviews = call_reviews(biz_id)
    return list_of_reviews

def format_reviews(b_data):
    eg = call_all_reviews(b_data)
    list_of_reviews = []
    x = 0
    for i in eg:
        reviews = {}
#         if len(i['reviews']))
        for count in list(range(0, (len(i['reviews'])))):
            reviews[f'Review_{count}'] = i['reviews'][count]['text'] 
        reviews['Id'] = b_data["Id"][x]
        list_of_reviews.append(reviews)
        x+=1
    return list_of_reviews

# format_reviews(biz_data[:20])

def reviews_to_csv(b_data): # If you run for all, this will output IndexError: list index out of range
    csv_filepath = f'database/{term}_{location}_reviews.csv'
    formatted_reviews = format_reviews(b_data)
#     for i in formatted_reviews:
#         if 'reviews' not in i:
#             break
    df = pd.DataFrame(formatted_reviews)
    with open(csv_filepath, "a") as f: #'x' creates and writes to csv
        read_file = csv.writer(f)
        df.to_csv(csv_filepath, mode = "a", index = False)
    return df.head()

# reviews_to_csv(biz_data[:50])
'''
#-------------------------------------------------------------
#Make me a function later
biz_data = pd.read_csv('database/spa_NYC_database.csv')
#biz_id = [biz_data[i] for i in biz_data['Id']] 
#biz_data['Id'][0]
biz_id2 = []
for i in biz_data['Id']:
    biz_id2.append(i)
biz_id[0]

#-------------------------------------------------------------


def call_reviews(biz_id_list): 
    data = []
    for biz in biz_id2:
        response = requests.get(f'https://api.yelp.com/v3/businesses/{biz}/reviews',headers = headers)
        review_data = response.json()
        reviews = {}
        count = 1
        for i in list_of_reviews[0]['reviews']:
            reviews[f'Review_{count}'] = i['text']
            count += 1   
            reviews['Id'] = biz
        data.append(reviews)
    return data

'''