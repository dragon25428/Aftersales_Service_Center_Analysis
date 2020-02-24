import pandas as pd
import numpy as np
from folium.plugins import TimestampedGeoJson
import folium
from folium import Icon
import matplotlib.pyplot as plt
import seaborn as sns
from Delhi_GeoJSON import DSC_Coverage, DSC2_Coverage
plt.rc('font', family='SimHei', size='15')

# Import service center data
center = pd.read_csv('dataset/service_center.csv', encoding='utf-8')
center['center_coordinate'] = center[['latitude', 'longitude']].apply(tuple, axis=1)

# Import Customer data
customer = pd.read_excel('dataset/201801-05德里工单明细_with_coordinates.xlsx', encoding='utf-8')
customer.drop(columns=['SR', 'zip', 'locality', 'start_time', 'end_time'], inplace=True)

# Label Color
cond = [customer.distance <= 5, (customer.distance > 5) & (customer.distance <= 10),
        (customer.distance > 10) & (customer.distance <= 15),
        (customer.distance > 15) & (customer.distance <= 20), customer.distance > 20]
choice = ['blue', 'red', 'green', 'purple', 'orange']
customer['label'] = np.select(cond, choice)

# Label Size
grp = customer.groupby(['date', 'longitude', 'latitude', 'center'], as_index=False)
customer['count'] = grp['distance'].transform('count')

# ------------------------------------------------ Define Function --------------------------------------------
def create_geojson_features(df):
    print('> Creating GeoJSON features...')
    features = []
    for loc, row in df.iterrows():
        feature = {
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': [row['longitude'], row['latitude']]
            },
            'properties': {
                'time': row['date'].date().__str__(),
                'style': {'color': row['label']},
                'icon': 'circle',
                'iconstyle': {
                    'fillColor': row['label'],
                    'fillOpacity': 0.8,
                    'stroke': 'true',
                    'radius': row['count']
                }
            }
        }
        features.append(feature)
    return features


def make_map(features, center_name, coverage):
    print('> Making map...')
    init_location = [customer.loc[0, 'latitude'], customer.loc[0, 'longitude']]
    time_map = folium.Map(location=init_location, control_scale=True, zoom_start=11)
    center[center.name == center_name].apply(lambda row: folium.Marker(location=[row['latitude'], row['longitude']],
                                                                       icon=Icon(color='black', icon='fa-wrench',
                                                                                 prefix='fa')).add_to(time_map), axis=1)
    time_map.choropleth(
        geo_data=coverage,
        fill_color='yellow',
        fill_opacity=0.1
    )
    TimestampedGeoJson(
        data={'type': 'Feature',
              'features': features},
        period='P1D',
        duration='P1D',
        auto_play=False,
        loop=False,
        max_speed=10,
        loop_button=True,
        date_options='YYYY/MM/DD',
        time_slider_drag_update=True).add_to(time_map)
    print('> Done.')
    return time_map
# ------------------------------------------ Function End ------------------------------------------------------------

# Plot time maps
features_DSC = create_geojson_features(customer[customer.center == 'DSC Delhi'])
time_map_DSC = make_map(features=features_DSC, center_name='DSC Delhi', coverage=DSC_Coverage)
time_map_DSC.save('HTML/time_map_DSC.html')

features_DSC2 = create_geojson_features(customer[customer.center == 'DSC Delhi 2'])
time_map_DSC2 = make_map(features=features_DSC2, center_name='DSC Delhi 2', coverage=DSC2_Coverage)
time_map_DSC2.save('HTML/time_map_DSC2.html')

# Plot service amount with time for DSC 1 and DSC 2
customer.date = customer.date.map(lambda x: x.date())
fig, ax = plt.subplots(figsize=(8, 5.5))
customer[customer.center == 'DSC Delhi'].groupby('date').center.count().plot(kind='bar')
xticklabels = ax.get_xticklabels()
plt.xticks(ticks=[i for i in np.arange(0, 151, 15)], labels=[xticklabels[i] for i in np.arange(0, 151, 15)])
fig.autofmt_xdate()
ax.set(xlabel='', ylabel='工单数量', title='DSC Delhi 日服务量')
plt.tight_layout()
fig.savefig('figures/DSC Delhi 日服务量.png', dpi=500)

fig, ax = plt.subplots(figsize=(8, 5.5))
customer[customer.center == 'DSC Delhi 2'].groupby('date').center.count().plot(kind='bar')
xticklabels = ax.get_xticklabels()
plt.xticks(ticks=[i for i in np.arange(5, 81, 9)], labels=[xticklabels[i] for i in np.arange(5, 81, 9)])
fig.autofmt_xdate()
ax.set(xlabel='', ylabel='工单数量', title='DSC Delhi 2 日服务量')
plt.tight_layout()
fig.savefig('figures/DSC Delhi2 日服务量.png', dpi=500)

# Distance Analysis
customer.set_index('date', inplace=True)
distance_mean = customer.groupby(['center', pd.Grouper(freq='M')]).distance.mean()
customer_DSC = customer[customer.center == 'DSC Delhi']
customer_DSC2 = customer[customer.center == 'DSC Delhi 2']

fig, ax = plt.subplots(2, 1, figsize=(8, 7))
sns.distplot(customer_DSC[customer_DSC.index < '2018-04'].distance, bins=10, label='1-3月', ax=ax[0])
sns.distplot(customer_DSC[customer_DSC.index > '2018-04'].distance, bins=10, label='4-5月', ax=ax[0])
sns.distplot(customer_DSC2.distance, bins=10, ax=ax[1])
ax[0].set(title='DSC Delhi', xlabel='服务距离(km)', ylabel='频率')
ax[1].set(title='DSC Delhi 2', xlabel='服务距离(km)', ylabel='频率')
ax[0].legend()
plt.tight_layout()
fig.savefig('figures/服务距离分布.png', dpi=500)

