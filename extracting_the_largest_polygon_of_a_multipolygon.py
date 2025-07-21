wfrom shapely.geometry import Polygon, MultiPolygon
import geopandas as gpd

# Load shapefile (may contain MultiPolygon)
gdf = gpd.read_file("shapefile.shp")

# Extract the largest polygon if it's a MultiPolygon
if gdf.geometry.iloc[0].geom_type == 'MultiPolygon':
    # Get all individual polygons and pick the largest one
    polygons = list(gdf.geometry.iloc[0].geoms)  # Extract polygons from MultiPolygon
    largest_polygon = max(polygons, key=lambda p: p.area)  # Pick largest
    gdf.geometry = gpd.GeoSeries([largest_polygon])  # Replace geometry

# Save as new shapefile (single polygon)
gdf.to_file("single_polygon.shp")
