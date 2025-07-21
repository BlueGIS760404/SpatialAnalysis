import geopandas as gpd

# Read shapefile
shapefile_path = "...path/shapefile.shp"
gdf = gpd.read_file(shapefile_path)

# Get total bounds (min_x, min_y, max_x, max_y)
min_lon, min_lat, max_lon, max_lat = gdf.total_bounds

print(f"Longitude: Min = {min_lon}, Max = {max_lon}")
print(f"Latitude:  Min = {min_lat}, Max = {max_lat}")
