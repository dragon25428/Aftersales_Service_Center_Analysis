import pandas as pd
import folium
from folium.plugins import FastMarkerCluster
from folium.plugins import HeatMap
from folium import Icon

pd.set_option('display.max_columns', 20, 'display.width', 120)

# Import Customer data
customer = pd.read_csv('customer.csv', encoding='utf-8')
customer['coordinate'] = customer[['latitude', 'longitude']].apply(tuple, axis=1)

# Import service center data
center = pd.read_csv('service_center.csv', encoding='utf-8')

# Folium marker map
init_location = [customer.loc[0, 'latitude'], customer.loc[0, 'longitude']]
marker_map = folium.Map(location=init_location,
                        tiles='cartodbpositron',
                        zoom_start=10)
center[center.engineer > 25].apply(
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
                  style="color:red"></i> &nbsp; Engineer > 25 <br>
     &nbsp; <i class="fa fa-wrench fa-2x"
                  style="color:blue"></i> &nbsp; Engineer < 10 <br>
     &nbsp; <i class="fa fa-wrench fa-2x"
                  style="color:darkgreen"></i> &nbsp; Engineer < 5 <br>
      </div>'''
marker_map.get_root().html.add_child(folium.Element(legend_html))
marker_map.save(outfile='marker_map.html')

# Folium heatmap
customer['count'] = 1
heat_map = folium.Map(location=init_location, zoom_start=10)
HeatMap(
    data=customer[['latitude', 'longitude', 'count']].groupby(['latitude', 'longitude'], as_index=False).sum().values,
    radius=11, max_zoom=13).add_to(heat_map)
center[center.engineer > 25].apply(lambda row: folium.Marker(location=[row['latitude'], row['longitude']],
                                                             icon=Icon(color='red', icon='fa-wrench', prefix='fa')).
                                   add_to(heat_map), axis=1)
center[(center.engineer >= 5) & (center.engineer < 10)].apply(
    lambda row: folium.Marker(location=[row['latitude'], row['longitude']],
                              icon=Icon(color='purple', icon='fa-wrench', prefix='fa')).
    add_to(heat_map), axis=1)
center[center.engineer < 5].apply(lambda row: folium.Marker(location=[row['latitude'], row['longitude']],
                                                            icon=Icon(color='darkgreen', icon='fa-wrench', prefix='fa')).
                                  add_to(heat_map), axis=1)
legend_html = '''<div style="position: fixed; 
     top: 100px; left: 50px; width: 200px; height: 150px; 
     border:2px solid grey; z-index:9999; font-size:18px; background-color:white;
     ">&nbsp; Service Center <br>
     &nbsp; <i class="fa fa-wrench fa-2x"
                  style="color:red"></i> &nbsp; Engineer > 25 <br>
     &nbsp; <i class="fa fa-wrench fa-2x"
                  style="color:purple"></i> &nbsp; Engineer < 10 <br>
     &nbsp; <i class="fa fa-wrench fa-2x"
                  style="color:darkgreen"></i> &nbsp; Engineer < 5 <br>
      </div>'''
heat_map.get_root().html.add_child(folium.Element(legend_html))
heat_map.save(outfile='heat_map.html')
