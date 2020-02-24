import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
from geopy.distance import distance
import datetime as dt
plt.rc('font', family='SimHei', size='15')

# get location from geocoders
geo_locator = Nominatim(user_agent='my app', timeout=5)

# Create geocode function with rate limiter
geocode = RateLimiter(geo_locator.geocode, min_delay_seconds=1, max_retries=4)

# ------------------------------------------------- Load customer data ---------------------------------------------
customer = pd.read_excel('dataset/201801-05德里工单明细.xlsx')
customer.drop_duplicates(subset=['SR_NUM'], inplace=True)
customer = customer[customer.SERVICETYPE == 'in home service']
customer = customer[
    ['SR_NUM', 'CREATED_TIME', 'Zip Code', 'SRLOCALITY', 'BRANCHNAME', 'Service Start Time', 'Service End Time']]
customer.columns = ['SR', 'date', 'zip', 'locality', 'center', 'start_time', 'end_time']

# ---------------------------------  Obtain Coordinate -------------------------------------------------------------
customer_old = pd.read_csv('dataset/customer.csv')
center = pd.read_csv('dataset/service_center.csv')

# Get location from [locality] column
customer['locality'] = customer['locality'].map(lambda x: x + ' ' + 'Delhi')
customer['location'] = customer['locality'].apply(geocode)

# Get location from [zip] column
customer['zip'] = customer['zip'].map(lambda x: str(x) + ' ' + 'Delhi')
customer.loc[customer['location'].isna(), 'location'] = customer.loc[customer['location'].isna(), 'zip'].apply(geocode)

# Extract Latitude and Longitude
customer = customer[customer.location.notna()]
customer = customer.assign(longitude=customer['location'].map(lambda x: x.longitude))
customer = customer.assign(latitude=customer['location'].map(lambda x: x.latitude))
customer.drop(columns='location', inplace=True)

# Remove Outliers Coordinates
Long_up_limit = customer.longitude.quantile(q=0.998)
Long_low_limit = customer.longitude.quantile(q=0.002)
Lat_up_limit = customer.latitude.quantile(q=0.996)
Lat_low_limit = customer.latitude.quantile(q=0.001)
customer = customer[(customer.longitude <= Long_up_limit) & (customer.longitude >= Long_low_limit)
                    & (customer.latitude <= Lat_up_limit) & (customer.latitude >= Lat_low_limit)]
customer.to_excel('dataset/201801-05德里工单明细_with_coordinates.xlsx', index=None)

# Merge with Center Coordinate
customer = customer[customer.center.map(lambda x: x in center.name.unique())]
center = center[['name', 'longitude', 'latitude']]
customer = pd.merge(customer, center, how='inner', left_on='center', right_on='name').drop(columns='name')
customer['user_coordinate'] = customer[['latitude_x', 'longitude_x']].apply(tuple, axis=1)
customer['center_coordinate'] = customer[['latitude_y', 'longitude_y']].apply(tuple, axis=1)
customer.rename(columns={'longitude_x': 'longitude', 'latitude_x': 'latitude'}, inplace=True)


# calculate distance
def calculate_distance(data):
    dist = distance(data.user_coordinate, data.center_coordinate).km
    return dist

customer = customer.assign(distance=customer.apply(calculate_distance, axis=1))
customer['distance'] = customer['distance'].map(lambda x: round(x, 2))
customer.drop(columns=['longitude_y', 'latitude_y', 'center_coordinate'], inplace=True)
customer.to_excel('dataset/201801-05德里工单明细_with_coordinates.xlsx', index=None)

# Distance Distribution
fig, ax = plt.subplots(figsize=(8, 5))
sns.distplot(customer[customer.center == 'DSC Delhi'].distance, kde=False, norm_hist=False, bins=20, label='DSC Delhi')
sns.distplot(customer[customer.center == 'DSC Delhi 2'].distance, kde=False, norm_hist=False, bins=20, label='DSC Delhi 2')
plt.legend()
plt.xlabel('服务距离(km)')
plt.ylabel('工单数量')
plt.tight_layout()
fig.savefig('figures/服务距离分布')

customer[customer.center == 'DSC Delhi'].label.value_counts()
customer[customer.center == 'DSC Delhi 2'].label.value_counts()



