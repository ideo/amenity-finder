import osmnx as ox
import networkx as nx
import matplotlib.pyplot as plt

import streamlit as st

import bz2
import _pickle as cPickle


@st.cache(allow_output_mutation=True)
def download_dowtown_detroit():
    address = "2001 Woodward Ave, Detroit, MI 48226"
    graph = ox.graph_from_address(address, network_type="walk", dist=2000)
    graph = add_walking_time_to_graph(graph)

    amenities = ox.geometries_from_address(address, tags={"amenity": True})
    return graph, amenities


def add_walking_time_to_graph(graph, travel_speed=4.0):
    # 4.5 km/hr
    meters_per_minute = travel_speed * 1000 / 60
    for u, v, k, data in graph.edges(data=True, keys=True):
        data['time'] = data['length'] / meters_per_minute
    return graph


def walking_isochrone(graph, address, travel_time, amenities, place_name):
    location = ox.geocoder.geocode(address)
    location_node = get_nearest_node(graph, location)
    subgraph = nx.ego_graph(graph, location_node, 
        radius=travel_time, 
        distance="time")

    fig, walkable_amenities = plot_walkable_amenities(subgraph, amenities, travel_time, place_name)
    return fig, walkable_amenities


def plot_walkable_amenities(subgraph, amenities, travel_time, place_name):
    fig, ax = plt.subplots(figsize=(12,12))
    ox.plot_graph(subgraph, ax=ax, node_size=0, show=False, close=False)

    ymax, ymin, xmax, xmin = get_bbox_from_graph(subgraph)
    walkable_amenities = amenities.cx[xmin:xmax, ymin:ymax]

    legend_kwds = {"loc": "lower center", "bbox_to_anchor": (0.5, -0.25), "ncols": 4}
    walkable_amenities.plot(ax=ax, column="amenity", markersize=4, legend=True, legend_kwds=legend_kwds)

    ax.set_title(f"Amenities within a {travel_time} minute walk of\n{place_name}")
    return fig, walkable_amenities



# Utils

def get_bbox_from_graph(graph):
        north = max([node[1]["y"] for node in graph.nodes(data=True)]) 
        south = min([node[1]["y"] for node in graph.nodes(data=True)]) 
        east = max([node[1]["x"] for node in graph.nodes(data=True)]) 
        west = min([node[1]["x"] for node in graph.nodes(data=True)]) 
        bbox = (north, south, east, west)
        # return bbox
        return north, south, east, west


def get_center_node(graph):
    gdf_nodes = ox.graph_to_gdfs(graph, edges=False)
    x, y = gdf_nodes['geometry'].unary_union.centroid.xy
    # center_node = ox.nearest_nodes(graph, (y[0], x[0]))[0]
    center_node = get_nearest_node(graph, (y[0], x[0]))
    return center_node


def get_nearest_node(graph, location):
    """
    Used to find the center node of the graph. If there is no one closest node, 
    osmnx returns a list. Here we simply take the first node from that list. 
    All the nodes will be right on top of each other and there's no point for 
    our purposes in distinguishing between them.
    ---
    Reminder: Longitude is along the X axis. Latitude is along the Y axis. When 
    we speak we tend to say "lat long", implying latitude comes first. But 
    since latitude goes north/south and longidtude goes east/west, in an X-Y 
    coordinate system, longitude comes first. 
    """
    lat = location[0]
    lng = location[1]
    nearest_node = ox.distance.nearest_nodes(graph, lng, lat)
    
    # assert isinstance(nearest_node, int)
    if not isinstance(nearest_node, int):
        nearest_node = nearest_node[0]

    return nearest_node


# Pickle a file and then compress it into a file with extension 
def compressed_pickle(data, filepath_with_extension):
    """
    Loads a .pbz2 files. This will expect that file extension.
    """
    with bz2.BZ2File(filepath_with_extension, "w") as write_file: 
        cPickle.dump(data, write_file)


# Load any compressed pickle file
def decompress_pickle(filepath_with_extension):
    """
    Include the .pbz2 extension in the file arg.
    """
    data = bz2.BZ2File(filepath_with_extension, "rb")
    data = cPickle.load(data)
    return data