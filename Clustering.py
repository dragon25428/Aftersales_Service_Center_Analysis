from sklearn.cluster.k_means_ import KMeans
from sklearn.preprocessing import StandardScaler
import pandas as pd
import folium
from folium import Icon

pd.set_option('display.max_columns', 30, 'display.max_colwidth', 20, 'display.width', 130)

# Import service center data
center = pd.read_csv('service_center.csv', encoding='utf-8')

# Import Customer data
customer = pd.read_csv('customer.csv', encoding='utf-8')
customer['coordinate'] = customer[['latitude', 'longitude']].apply(tuple, axis=1)

# Standardize Longitude and Latitude
scaler = StandardScaler()
customer['longitude_std'] = scaler.fit_transform(customer[['longitude', 'latitude']])[:, 0]
customer['latitude_std'] = scaler.fit_transform(customer[['longitude', 'latitude']])[:, 1]

# K-means Clustering
kmeans = KMeans(n_clusters=9, init='k-means++', n_init=10, max_iter=300, verbose=1, random_state=123)
kmeans.fit_transform(customer[['longitude_std', 'latitude_std']])
centers = scaler.inverse_transform(kmeans.cluster_centers_)
groups = kmeans.predict(customer[['longitude_std', 'latitude_std']])
customer['groups'] = groups

# Coordinate of each cluster
cluster_center = kmeans.cluster_centers_
cluster_center = scaler.inverse_transform(cluster_center)
cluster_center = pd.DataFrame(cluster_center, columns=['longitude', 'latitude'])
cluster_center['group'] = range(0, 9)

# Plot Map
init_location = [customer.loc[0, 'latitude'], customer.loc[0, 'longitude']]
cluster_map = folium.Map(location=init_location,
                         zoom_start=10)
customer[customer.groups == 6].apply(
    lambda row: folium.CircleMarker(location=tuple([row['latitude'], row['longitude']]),
                                    radius=6, fill=True, color='blue').add_to(cluster_map), axis=1)
customer[customer.groups == 1].apply(
    lambda row: folium.CircleMarker(location=tuple([row['latitude'], row['longitude']]),
                                    radius=6, fill=True, color='purple').add_to(cluster_map), axis=1)
customer[customer.groups == 3].apply(
    lambda row: folium.CircleMarker(location=tuple([row['latitude'], row['longitude']]),
                                    radius=6, fill=True, color='green').add_to(cluster_map), axis=1)
customer[customer.groups == 4].apply(
    lambda row: folium.CircleMarker(location=tuple([row['latitude'], row['longitude']]),
                                    radius=6, fill=True, color='red').add_to(cluster_map), axis=1)
customer[customer.groups == 2].apply(
    lambda row: folium.CircleMarker(location=tuple([row['latitude'], row['longitude']]),
                                    radius=6, fill=True, color='darkcyan').add_to(cluster_map), axis=1)
customer[customer.groups == 5].apply(
    lambda row: folium.CircleMarker(location=tuple([row['latitude'], row['longitude']]),
                                    radius=6, fill=True, color='sienna').add_to(cluster_map), axis=1)
customer[customer.groups == 8].apply(
    lambda row: folium.CircleMarker(location=tuple([row['latitude'], row['longitude']]),
                                    radius=6, fill=True, color='gold').add_to(cluster_map), axis=1)
customer[customer.groups == 0].apply(
    lambda row: folium.CircleMarker(location=tuple([row['latitude'], row['longitude']]),
                                    radius=6, fill=True, color='orange').add_to(cluster_map), axis=1)
customer[customer.groups == 7].apply(
    lambda row: folium.CircleMarker(location=tuple([row['latitude'], row['longitude']]),
                                    radius=6, fill=True, color='gray').add_to(cluster_map), axis=1)
center[center.engineer > 25].apply(lambda row: folium.Marker(location=[row['latitude'], row['longitude']],
                                                             icon=Icon(color='red', icon='fa-wrench', prefix='fa')).
                                   add_to(cluster_map), axis=1)
center[(center.engineer >= 5) & (center.engineer < 10)].apply(
    lambda row: folium.Marker(location=[row['latitude'], row['longitude']],
                              icon=Icon(color='blue', icon='fa-wrench', prefix='fa')).add_to(cluster_map), axis=1)
center[center.engineer < 5].apply(lambda row: folium.Marker(location=[row['latitude'], row['longitude']],
                                                            icon=Icon(color='darkgreen', icon='fa-wrench',
                                                                      prefix='fa')).add_to(cluster_map), axis=1)
cluster_center.apply(lambda row: folium.Marker(location=[row['latitude'], row['longitude']],
                                                                          icon=Icon(color='black', icon='fa-angellist',
                                                                                    prefix='fa')).add_to(cluster_map), axis=1)
legend_html = '''<div style="position: fixed; 
     top: 100px; left: 50px; width: 240px; height: 180px; 
     border:2px solid grey; z-index:9999; font-size:18px; background-color:white;
     ">&nbsp; Service Center <br>
     &nbsp; <i class="fa fa-wrench fa-2x"
                  style="color:red"></i> &nbsp; Engineer > 25 <br>
     &nbsp; <i class="fa fa-wrench fa-2x"
                  style="color:blue"></i> &nbsp; Engineer < 10 <br>
     &nbsp; <i class="fa fa-wrench fa-2x"
                  style="color:darkgreen"></i> &nbsp; Engineer < 5 <br>
     &nbsp; <i class="fa fa-angellist fa-2x"
                  style="color:black"></i> &nbsp; Optimum Location <br>
      </div>'''
cluster_map.get_root().html.add_child(folium.Element(legend_html))
legend_html_1 = '''<div style="position: fixed; 
     top: 300px; left: 50px; width: 240px; height: 230px; 
     border:2px solid grey; z-index:9999; font-size:15px; background-color:white;
     ">&nbsp; Customer Requests Number <br>&nbsp; in each cluster <br>
     &nbsp; <i class="fa fa-circle"
                  style="color:blue"></i> &nbsp; 1094 requests <br>
     &nbsp; <i class="fa fa-circle"
                  style="color:purple"></i> &nbsp; 713 requests <br>
     &nbsp; <i class="fa fa-circle"
                  style="color:green"></i> &nbsp; 675 requests <br>
     &nbsp; <i class="fa fa-circle"
                  style="color:red"></i> &nbsp; 614 requests <br>
     &nbsp; <i class="fa fa-circle"
                  style="color:darkcyan"></i> &nbsp; 491 requests <br>
     &nbsp; <i class="fa fa-circle"
                  style="color:sienna"></i> &nbsp; 406 requests <br>
     &nbsp; <i class="fa fa-circle"
                  style="color:gold"></i> &nbsp; 224 requests <br>
     &nbsp; <i class="fa fa-circle"
                  style="color:orange"></i> &nbsp; 221 requests <br>
     &nbsp; <i class="fa fa-circle"
                  style="color:grey"></i> &nbsp; 99 requests <br>
      </div>'''
cluster_map.get_root().html.add_child(folium.Element(legend_html_1))
cluster_map.save(outfile='cluster_map.html')
