import pandas as pd
import geopandas as gpd

def process_places(path: str) -> gpd.GeoDataFrame:
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
    
    return points_gdf

def process_zones(path: str) -> gpd.GeoDataFrame:
    """_summary_

    Args:
        path (str): the location of the file

    Returns:
        gpd.GeoDataFrame: GeoDataFrame with the right CRS and filtered to only include the neighborhoods of interest
    """
    
    polygons_gdf = gpd.read_file(path)[['lsoa11nmw', 'geometry']].to_crs(epsg=4326).reset_index(drop=True)
    
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
    counts_df = points_in_polygons.groupby(['classname', 'lsoa11nmw']).size().reset_index(drop=False).rename(columns={0:'count'})
    
    # Step 3: Merge with polygons_gdf
    choropleth_gdf = pd.merge(polygons_gdf, counts_df, how='inner', on='lsoa11nmw')
    
    return choropleth_gdf

def filter_datasets(points_gdf: gpd.GeoDataFrame, choropleth_gdf: gpd.GeoDataFrame) -> dict[gpd.GeoDataFrame]:
    """Generates a dictionary with filtered datasets for cafes and bars

    Args:
        points_gdf (gpd.GeoDataFrame): a geopandas dataframe with the points data
        choropleth_gdf (gpd.GeoDataFrame): a geopandas dataframe with the choropleth data

    Returns:
        dict[gpd.GeoDataFrame]: a dictionary with four geopandas dataframes filtered according to classname
    """    
    
    cafe_gdf = points_gdf[points_gdf['classname'] == 'Cafes, Snack Bars and Tea Rooms']
    bar_gdf = points_gdf[points_gdf['classname'] == 'Pubs, Bars and Inns']

    cafe_choropleth_gdf = choropleth_gdf[choropleth_gdf['classname'] == 'Cafes, Snack Bars and Tea Rooms']
    bar_choropleth_gdf = choropleth_gdf[choropleth_gdf['classname'] == 'Pubs, Bars and Inns']
    
    return {'cafe_gdf': cafe_gdf, 'bar_gdf': bar_gdf, 'cafe_choropleth_gdf': cafe_choropleth_gdf, 'bar_choropleth_gdf': bar_choropleth_gdf}


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