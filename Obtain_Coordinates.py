import pandas as pd
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter

pd.set_option('display.max_columns', 20, 'display.width', 120)

# get location from geocoders
geo_locator = Nominatim(user_agent='my app', timeout=5)

# Import Customer data
customer = pd.read_excel(r'D:\Haier\01_Project\Service Center Analysis\customer_request.xlsx')
customer.columns = ['first_name', 'last_name', 'state', 'locality', 'city', 'zip', 'address', 'service_type']
customer = customer[customer['state'] == 'DELHI']  # filter DELHI only

# Create geocode function with rate limiter
geocode = RateLimiter(geo_locator.geocode, min_delay_seconds=1, max_retries=4)

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

# Output customer data with coordinate
customer.to_csv('customer.csv', encoding='utf-8')
