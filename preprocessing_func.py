import pandas as pd
import geopandas as gpd

def process_places_data(path: str) -> gpd.GeoDataFrame:
    """Reads a vector layer containing places locations and information and 
       processes that into a geojson layer ready to be manipulated by the Geopandas library.

    Args:
        path (str): Path to the file

    Returns:
        gpd.GeoDataFrame: GeoDataFrame with the right CRS and filtered to only include the places of interest
    """
    
    layer_name = 'Points of Interest 2023_06'
    gdf_places = gpd.read_file(path, layer=layer_name)
    gdf_places.crs = 'epsg:27700'
    
    points_gdf = gdf_places[gdf_places['classname'].isin(['Pubs, Bars and Inns', 'Cafes, Snack Bars and Tea Rooms', ])][['name', 'classname', 'street_name', 'postcode', 'url', 'geometry']]\
                     .to_crs(epsg=4326).reset_index(drop=True)

    # Step 3: Convert to GeoJSON (assuming your gdf is not empty)
    places_geojson = points_gdf.to_json()
    
    return places_geojson

def process_neighborhoods(path: str) -> gpd.GeoDataFrame:
    """_summary_

    Args:
        path (str): the location of the file

    Returns:
        gpd.GeoDataFrame: GeoDataFrame with the right CRS and filtered to only include the neighborhoods of interest
    """
    
    polygons_gdf = gpd.read_file(path)[['POSTCODE', 'geometry']].to_crs(epsg=4326).reset_index(drop=True)
    polygons_gdf = polygons_gdf[polygons_gdf['POSTCODE'].str.startswith('CB')]
    
    return polygons_gdf

def create_choropleth_data(points_gdf: gpd.GeoDataFrame, polygons_gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Generates a choropleth layer from a join between the points and polygons layers

    Args:
        points_gdf (gpd.GeoDataFrame): a geopandas dataframe with the points data
        polygons_gdf (gpd.GeoDataFrame): a geopandas dataframe with the polygons data

    Returns:
        gpd.GeoDataFrame: a geopandas dataframe with the choropleth data
    """
    
    # Step 1: Spatial join
    points_in_polygons = gpd.sjoin(points_gdf, polygons_gdf, how='inner', op='within').reset_index(drop=True)
    
    # Step 2: Group by postcode and count
    points_in_polygons = points_in_polygons.groupby(['classname', 'POSTCODE']).size().reset_index(name='counts').sort_values(by='counts', ascending=False).reset_index(drop=True)
    
    # Step 3: Merge with polygons_gdf
    choropleth_gdf = polygons_gdf.merge(points_in_polygons, on='POSTCODE', how='inner')
    
    return choropleth_gdf

def create_popup_html(name: str, address: str, url: str) -> str:
    """Generates HTML code for the popup

    Args:
        name (str): name of the place
        address (str): address of the place
        url (str): url of the place

    Returns:
        str: HTML code for the popup
    """            
    
    return f"""
    <div>
        <h4 style="margin-bottom:0;"><a href="{url}" target="_blank">{name}</a></h4>
        <p style="margin-top:0;"><strong>Address:</strong> {address}</p>
    </div>
    """

def create_tooltip_html(name: str) -> str:
    """Generates HTML code for the tooltip

    Args:
        name (str): name of the place

    Returns:
        str: HTML code for the tooltip
    """    
    
    return f"<div style='font-size: 12px; font-weight: bold;'>{name}</div>"