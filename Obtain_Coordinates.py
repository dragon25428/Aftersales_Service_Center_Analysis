import pandas as pd
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from geopy.distance import distance
pd.set_option('display.max_columns', 100, 'display.width', 130, 'display.max_colwidth', 30)

# get location from geocoders
geo_locator = Nominatim(user_agent='my app', timeout=5)

# Create geocode function with rate limiter
geocode = RateLimiter(geo_locator.geocode, min_delay_seconds=1, max_retries=4)

# Import service center data
center = pd.read_csv('dataset/service_center.csv', encoding='utf-8')
center['center_coordinate'] = center[['latitude', 'longitude']].apply(tuple, axis=1)

# Import Customer data
customer = pd.read_excel(r'D:\Haier\01_Project\India Service Center Analysis\customer_request.xlsx')
customer.columns = ['first_name', 'last_name', 'state', 'locality', 'city', 'zip', 'address', 'service_type', 'center', 'SR', 'date']
customer = customer[customer['state'] == 'DELHI']  # filter DELHI only
customer.drop_duplicates(subset=['first_name', 'last_name', 'locality', 'address', 'service_type', 'SR'], inplace=True)
customer = customer[customer.service_type == 'in home service']

# Get location from [address] column
customer['location'] = ''
for i in range(610):
    customer.loc[(i * 20 + 1):(i * 20 + 20), 'location'] = customer.loc[(i * 20 + 1):(i * 20 + 20), 'address'].apply(
        geocode)
    print('part {} done'.format(i))

# Get location from [locality] column
customer['locality'] = customer['locality'].map(lambda x: x + ' ' + 'Delhi')
customer.loc[customer['location'].isna(), 'location'] = customer.loc[customer['location'].isna(), 'locality'].apply(
    geocode)

# Get location from [zip] column
customer['zip'] = customer['zip'].map(lambda x: str(x) + ' ' + 'Delhi')
customer.loc[customer['location'].isna(), 'location'] = customer.loc[customer['location'].isna(), 'zip'].apply(geocode)
customer.loc[customer['location'] == '', 'location'] = customer.loc[customer['location'] == '', 'zip'].apply(geocode)

# Remove the location without values
customer.dropna(subset=['location'], inplace=True)

# Extract longitude and latitude from location data
customer = customer.assign(longitude=customer['location'].map(lambda x: x.longitude))
customer = customer.assign(latitude=customer['location'].map(lambda x: x.latitude))
customer = customer.assign(coordinate=customer['location'].map(lambda x: (x.latitude, x.longitude)))

# Remove wrong coordinates
Long_up_limit = customer.longitude.quantile(q=0.99)
Long_low_limit = customer.longitude.quantile(q=0.01)
Lat_up_limit = customer.latitude.quantile(q=0.99)
Lat_low_limit = customer.latitude.quantile(q=0.01)
customer = customer[(customer.longitude < Long_up_limit) & (customer.longitude > Long_low_limit)
                    & (customer.latitude < Lat_up_limit) & (customer.latitude > Lat_low_limit)]

# Compute distance from customer coordinate to center coordinate
customer['center_coordinate'] = customer[['center']].merge(center[['name', 'center_coordinate']], left_on='center', right_on='name', how='left').center_coordinate
def calculate_distance(data):
    dist = distance(data.coordinate, data.center_coordinate).km
    return dist

customer['distance'] = customer.apply(calculate_distance, axis=1)

# Output customer data with coordinate
customer.to_csv('customer.csv', encoding='utf-8', index=None)


