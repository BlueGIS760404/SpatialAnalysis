import geopandas as gpd

# Path to your shapefile
shapefile_path = r"...\county.shp"

# Read shapefile
gdf = gpd.read_file(shapefile_path)

# Get bounds in original CRS
min_x, min_y, max_x, max_y = gdf.total_bounds
print(f"Original CRS: {gdf.crs}")
print(f"Projected bounds:")
print(f"  Min X = {min_x}, Max X = {max_x}")
print(f"  Min Y = {min_y}, Max Y = {max_y}")

# Reproject to WGS84 (EPSG:4326) if not already
if gdf.crs.to_string() != "EPSG:4326":
    gdf_wgs84 = gdf.to_crs(epsg=4326)
else:
    gdf_wgs84 = gdf.copy()

# Get bounds in geographic coordinates (lat/lon)
min_lon, min_lat, max_lon, max_lat = gdf_wgs84.total_bounds
print(f"\nGeographic coordinates (EPSG:4326) bounds:")
print(f"  Longitude: Min = {min_lon}, Max = {max_lon}")
print(f"  Latitude:  Min = {min_lat}, Max = {max_lat}")
