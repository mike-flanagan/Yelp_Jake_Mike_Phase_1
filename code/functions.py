def yelp_call(headers, url_params):
    """
    This function will use the url_params variable and the headers variable to call the Yelp API,
    and return the data as a JSON 
    This will use the requests module to get from Yelp. 
    What is returned will be modified by our URL parameters.
    This must be called fresh with updated url_params for each call if we want to return more results.
    
    2/14 — defined data variable in this loop.
    """
    response = requests.get(url, headers=headers, params=url_params) # our url, header and params should be consistent, atleast with our Yelp data
    data = response.json()
    return data

def parse_data(list_of_data):
    """
    Input data['businesses'] to return a list of tuples,
    with each tuple containing individual business name, address, rating, review count,
    Categories, and business ID
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
                     biz_price,
                     business['id'],
                     business['categories'])
        businesses.append(biz_tuple)
    return businesses

def call_1000(csv_filepath):
    """
    This function will use the information gathered above to call the Yelp API and construct a data frame
    """
    url_params['offset'] = 0
    results = yelp_call(headers, url_params)
    parsed = parse_data(results['businesses']) # list of businesses in tuples
    num = results['total']
    biz_list = []
    #Loop through the API to reach all of the businesses in the call
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
    
    # Create the data frame from the gathered information
    df = pd.DataFrame(biz_list, columns=['Name', 'Address','City', 'Rating','Review Count','Coordinates','Price','Id','Categories'])
    
    #Save the data frame as a CSV file
    with open(csv_filepath, "a") as f: 
        read_file = csv.writer(f)
        df.to_csv(csv_filepath, mode = "a", index = False)
    print('CSV file written to {csv_filepath}.')
    return df

def call_reviews(biz_id): 
    """
    This function loops through the list of business ID's, and call the API on each one.
    Then, it will save this data to a list, and return the list
    """
    list_of_reviews = []
    for biz in biz_id:
        response = requests.get(f'https://api.yelp.com/v3/businesses/{biz}/reviews',headers = headers)
        review_data = response.json()
        list_of_reviews.append(review_data)
    return list_of_reviews

def call_all_reviews(b_data): 
    """
    This function takes in the data frame, and create a list of the business Id's from it.
    This will then return that list
    """
    biz_id = []
    for j in b_data['Id']: #ID column of business data dataframe
        biz_id.append(j)
    list_of_reviews = call_reviews(biz_id)
    return list_of_reviews

def format_reviews(b_data):
    """
    This function takes in the business data frame, and calls the function 'call_all_reviews' 
    to get the list of business Ids.  It will then loop through and create a new list of dictionaries
    with all of the reviews for that company, and that companies Business Id.
    """
    eg = call_all_reviews(b_data)
    list_of_reviews = []
    x = 0
    for i in eg:
        reviews = {}
        for count in list(range(0, (len(i['reviews'])))):
            reviews[f'Review_{count}'] = i['reviews'][count]['text'] 
        reviews['Id'] = b_data["Id"][x]
        list_of_reviews.append(reviews)
        x+=1
    return list_of_reviews

def reviews_to_csv(b_data): # If you run for all, this will output IndexError: list index out of range
    """
    This function takes in the business data frame, and runs the 'format_reviews' function.
    It then converts the list of dictionaries into the reviews CSV file
    """
    csv_filepath = f'database/{term}_{location}_reviews.csv'
    formatted_reviews = format_reviews(b_data)
    
    df = pd.DataFrame(formatted_reviews)
    with open(csv_filepath, "a") as f:
        read_file = csv.writer(f)
        df.to_csv(csv_filepath, mode = "a", index = False)
    return df