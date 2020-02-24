import pandas as pd
import folium
from folium.plugins import FastMarkerCluster
from folium.plugins import HeatMap
from folium import Icon
from Delhi_GeoJSON import DSC_Coverage, DSC2_Coverage

pd.set_option('display.max_columns', 30, 'display.max_colwidth', 20, 'display.width', 130)

# Import service center data
center = pd.read_csv('dataset/service_center.csv', encoding='utf-8')
center['center_coordinate'] = center[['latitude', 'longitude']].apply(tuple, axis=1)

# Import Customer data
customer = pd.read_excel('dataset/201801-05德里工单明细_with_coordinates.xlsx', encoding='utf-8')
customer['coordinate'] = customer[['latitude', 'longitude']].apply(tuple, axis=1)

# Folium marker map
init_location = [customer.loc[0, 'latitude'], customer.loc[0, 'longitude']]
marker_map = folium.Map(location=init_location,
                        zoom_start=10)
center[center.engineer >= 20].apply(
    lambda row: folium.Marker(location=tuple([row['latitude'], row['longitude']]),
                              icon=Icon(color='red', icon='fa-wrench', prefix='fa')).add_to(marker_map), axis=1)
center[(center.engineer >= 5) & (center.engineer < 10)].apply(
    lambda row: folium.Marker(location=tuple([row['latitude'], row['longitude']]),
                              icon=Icon(color='blue', icon='fa-wrench', prefix='fa')).add_to(marker_map), axis=1)
center[center.engineer < 5].apply(
    lambda row: folium.Marker(location=tuple([row['latitude'], row['longitude']]),
                              icon=Icon(color='darkgreen', icon='fa-wrench', prefix='fa')).add_to(marker_map), axis=1)
FastMarkerCluster(data=customer['coordinate'].tolist()).add_to(marker_map)
legend_html = '''<div style="position: fixed; 
     top: 100px; left: 50px; width: 200px; height: 150px; 
     border:2px solid grey; z-index:9999; font-size:18px; background-color:white;
     ">&nbsp; Service Center <br>
     &nbsp; <i class="fa fa-wrench fa-2x"
                  style="color:red"></i> &nbsp; Engineer > 20 <br>
     &nbsp; <i class="fa fa-wrench fa-2x"
                  style="color:blue"></i> &nbsp; Engineer < 10 <br>
     &nbsp; <i class="fa fa-wrench fa-2x"
                  style="color:darkgreen"></i> &nbsp; Engineer < 5 <br>
      </div>'''
marker_map.get_root().html.add_child(folium.Element(legend_html))
marker_map.save(outfile='HTML/marker_map.html')

# Folium heatmap
customer['count'] = 10
customer_DSC = customer[customer.center == 'DSC Delhi']
heat_map = folium.Map(location=init_location, zoom_start=10)
HeatMap(
    data=customer_DSC[['latitude', 'longitude', 'count']].groupby(['latitude', 'longitude'],
                                                                  as_index=False).sum().values,
    radius=11, max_zoom=13).add_to(heat_map)
center[center.name == 'DSC Delhi'].apply(lambda row: folium.Marker(location=[row['latitude'], row['longitude']],
                                                                   icon=Icon(color='red', icon='fa-wrench',
                                                                             prefix='fa')).add_to(heat_map), axis=1)
center[center.name == 'DSC Delhi 2'].apply(lambda row: folium.Marker(location=[row['latitude'], row['longitude']],
                                                                   icon=Icon(color='green', icon='fa-wrench',
                                                                             prefix='fa')).add_to(heat_map), axis=1)
legend_html = '''<div style="position: fixed; 
     top: 100px; left: 50px; width: 200px; height: 150px; 
     border:2px solid grey; z-index:9999; font-size:18px; background-color:white;
     ">&nbsp; Service Center <br>
     &nbsp; <i class="fa fa-wrench fa-2x"
                  style="color:red"></i> &nbsp; DSC Delhi <br>
     &nbsp; <i class="fa fa-wrench fa-2x"
                  style="color:green"></i> &nbsp; DSC Delhi 2 <br>
      </div>'''
heat_map.get_root().html.add_child(folium.Element(legend_html))
heat_map.save(outfile='HTML/heat_map_DSC Delhi.html')

# DSC Delhi task map group by distance
init_location = [customer.loc[0, 'latitude'], customer.loc[0, 'longitude']]
distance_map = folium.Map(location=init_location,
                          zoom_start=10)
distance_map.choropleth(
    geo_data=DSC_Coverage,
    fill_color='yellow',
    fill_opacity=0.2
)
center[center.name == 'DSC Delhi'].apply(lambda row: folium.Marker(location=[row['latitude'], row['longitude']],
                                                                   icon=Icon(color='black', icon='fa-wrench',
                                                                             prefix='fa')).add_to(distance_map), axis=1)
customer[(customer.center == 'DSC Delhi') & (customer.distance < 5)].apply(
    lambda row: folium.CircleMarker(location=tuple([row['latitude'], row['longitude']]),
                                    radius=6, fill=True, color='blue').add_to(distance_map), axis=1)
customer[(customer.center == 'DSC Delhi') & (customer.distance >= 5) & (customer.distance < 10)].apply(
    lambda row: folium.CircleMarker(location=tuple([row['latitude'], row['longitude']]),
                                    radius=6, fill=True, color='red').add_to(distance_map), axis=1)
customer[(customer.center == 'DSC Delhi') & (customer.distance >= 10) & (customer.distance < 15)].apply(
    lambda row: folium.CircleMarker(location=tuple([row['latitude'], row['longitude']]),
                                    radius=6, fill=True, color='green').add_to(distance_map), axis=1)
customer[(customer.center == 'DSC Delhi') & (customer.distance >= 15) & (customer.distance < 20)].apply(
    lambda row: folium.CircleMarker(location=tuple([row['latitude'], row['longitude']]),
                                    radius=6, fill=True, color='purple').add_to(distance_map), axis=1)
customer[(customer.center == 'DSC Delhi') & (customer.distance >= 20)].apply(
    lambda row: folium.CircleMarker(location=tuple([row['latitude'], row['longitude']]),
                                    radius=6, fill=True, color='orange').add_to(distance_map), axis=1)
legend_html = '''<div style="position: fixed; 
     top: 300px; left: 50px; width: 240px; height: 180px; 
     border:2px solid grey; z-index:9999; font-size:15px; background-color:white;
     ">&nbsp; Customer Requests Number <br>&nbsp; in each cluster <br>
     &nbsp; <i class="fa fa-wrench"
                  style="color:black"></i> &nbsp; DSC Delhi <br>
     &nbsp; <i class="fa fa-circle"
                  style="color:blue"></i> &nbsp; < 5km <br>
     &nbsp; <i class="fa fa-circle"
                  style="color:red"></i> &nbsp; < 10km <br>
     &nbsp; <i class="fa fa-circle"
                  style="color:green"></i> &nbsp; < 15km  <br>
     &nbsp; <i class="fa fa-circle"
                  style="color:purple"></i> &nbsp; < 20km <br>
     &nbsp; <i class="fa fa-circle"
                  style="color:orange"></i> &nbsp; > 20km <br>
      </div>'''
distance_map.get_root().html.add_child(folium.Element(legend_html))
distance_map.save(outfile='HTML/distance_map_DSC.html')

# DSC Delhi 2 task map group by distance
init_location = [customer.loc[0, 'latitude'], customer.loc[0, 'longitude']]
distance_map = folium.Map(location=init_location,
                          zoom_start=10)
distance_map.choropleth(
    geo_data=DSC2_Coverage,
    fill_color='yellow',
    fill_opacity=0.2
)
center[center.name == 'DSC Delhi 2'].apply(lambda row: folium.Marker(location=[row['latitude'], row['longitude']],
                                                                     icon=Icon(color='red', icon='fa-wrench',
                                                                               prefix='fa')).add_to(distance_map),
                                           axis=1)
customer[(customer.center == 'DSC Delhi 2') & (customer.distance < 5)].apply(
    lambda row: folium.CircleMarker(location=tuple([row['latitude'], row['longitude']]),
                                    radius=6, fill=True, color='blue').add_to(distance_map), axis=1)
customer[(customer.center == 'DSC Delhi 2') & (customer.distance >= 5) & (customer.distance < 10)].apply(
    lambda row: folium.CircleMarker(location=tuple([row['latitude'], row['longitude']]),
                                    radius=6, fill=True, color='red').add_to(distance_map), axis=1)
customer[(customer.center == 'DSC Delhi 2') & (customer.distance >= 10) & (customer.distance < 15)].apply(
    lambda row: folium.CircleMarker(location=tuple([row['latitude'], row['longitude']]),
                                    radius=6, fill=True, color='green').add_to(distance_map), axis=1)
customer[(customer.center == 'DSC Delhi 2') & (customer.distance >= 15) & (customer.distance < 20)].apply(
    lambda row: folium.CircleMarker(location=tuple([row['latitude'], row['longitude']]),
                                    radius=6, fill=True, color='purple').add_to(distance_map), axis=1)
customer[(customer.center == 'DSC Delhi 2') & (customer.distance >= 20)].apply(
    lambda row: folium.CircleMarker(location=tuple([row['latitude'], row['longitude']]),
                                    radius=6, fill=True, color='orange').add_to(distance_map), axis=1)
legend_html = '''<div style="position: fixed; 
     top: 300px; left: 50px; width: 240px; height: 180px; 
     border:2px solid grey; z-index:9999; font-size:15px; background-color:white;
     ">&nbsp; Customer Requests Number <br>&nbsp; in each cluster <br>
     &nbsp; <i class="fa fa-wrench"
                  style="color:red"></i> &nbsp; DSC Delhi 2 <br>
     &nbsp; <i class="fa fa-circle"
                  style="color:blue"></i> &nbsp; < 5km <br>
     &nbsp; <i class="fa fa-circle"
                  style="color:red"></i> &nbsp; < 10km <br>
     &nbsp; <i class="fa fa-circle"
                  style="color:green"></i> &nbsp; < 15km  <br>
     &nbsp; <i class="fa fa-circle"
                  style="color:purple"></i> &nbsp; < 20km <br>
     &nbsp; <i class="fa fa-circle"
                  style="color:orange"></i> &nbsp; > 20km <br>
      </div>'''
distance_map.get_root().html.add_child(folium.Element(legend_html))
distance_map.save(outfile='HTML/distance_map_DSC2.html')

# DSC Delhi and DSC Delhi 2 Coverage Map
init_location = [customer.loc[0, 'latitude'], customer.loc[0, 'longitude']]
coverage_map = folium.Map(location=init_location,
                          zoom_start=10)
coverage_map.choropleth(
    geo_data=DSC_Coverage,
    fill_color='yellow',
    fill_opacity=0.2
)
coverage_map.choropleth(
    geo_data=DSC2_Coverage,
    fill_color='green',
    fill_opacity=0.2
)
center[center.name == 'DSC Delhi'].apply(lambda row: folium.Marker(location=[row['latitude'], row['longitude']],
                                                                   icon=Icon(color='yellow', icon='fa-wrench',
                                                                             prefix='fa')).add_to(coverage_map), axis=1)
center[center.name == 'DSC Delhi 2'].apply(lambda row: folium.Marker(location=[row['latitude'], row['longitude']],
                                                                     icon=Icon(color='green', icon='fa-wrench',
                                                                               prefix='fa')).add_to(coverage_map), axis=1)
legend_html = '''<div style="position: fixed; 
     top: 300px; left: 50px; width: 240px; height: 80px; 
     border:2px solid grey; z-index:9999; font-size:15px; background-color:white;
     ">&nbsp; Service Centers <br>
     &nbsp; <i class="fa fa-wrench"
                  style="color:red"></i> &nbsp; DSC Delhi <br>
     &nbsp; <i class="fa fa-wrench"
                  style="color:green"></i> &nbsp; DSC Delhi 2 <br>
      </div>'''
coverage_map.get_root().html.add_child(folium.Element(legend_html))
coverage_map.save(outfile='HTML/coverage_map.html')
