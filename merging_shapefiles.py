import pandas as pd
import geopandas as gpd

# Input shapefiles
shp1 = r"...\reference_2000_bu.shp"
shp2 = r"...\reference_2000_nbu.shp"

# Read both
gdf1 = gpd.read_file(shp1)
gdf2 = gpd.read_file(shp2)

# Make sure both have same CRS
if gdf1.crs != gdf2.crs:
    gdf2 = gdf2.to_crs(gdf1.crs)

# Merge (stack them on top of each other)
merged = gpd.GeoDataFrame(pd.concat([gdf1, gdf2], ignore_index=True), crs=gdf1.crs)

# Save merged shapefile
merged.to_file(r"...\merged_reference.shp")

print("✅ Merged shapefile saved as merged_reference.shp")
