import geopandas as gpd
import pandas as pd

# Read the shapefiles
gdf1 = gpd.read_file(r'E:\Freelancing\P_05_6.18.2025\data\dataset\tehran_boundary.shp')
gdf2 = gpd.read_file(r'E:\Freelancing\P_05_6.18.2025\data\dataset\alborz_boundary.shp')

# Combine them
combined = pd.concat([gdf1, gdf2], ignore_index=True)

# Dissolve
combined['id'] = 1
dissolved = combined.dissolve(by='id')

# Reproject to UTM Zone 39N (for accurate area calculation)
dissolved_utm = dissolved.to_crs(epsg=32639)

# Calculate area
dissolved_utm['area_sqm'] = dissolved_utm.geometry.area
dissolved_utm['area_sqkm'] = dissolved_utm['area_sqm'] / 1e6

# Clean: Remove unwanted old fields
# Keep only geometry and area fields
fields_to_keep = ['geometry', 'area_sqm', 'area_sqkm']
dissolved_cleaned = dissolved_utm[fields_to_keep]

# Save the result
dissolved_cleaned.to_file(r'E:\Freelancing\P_05_6.18.2025\data\dataset\tehran_alborz_dissolved.shp')
