import geopandas as gpd
import pandas as pd

# Read shapefiles
gdf1 = gpd.read_file(r"...\reference_2000_bu.shp")
gdf2 = gpd.read_file(r"...\reference_2000_nbu.shp")

# Combine
combined = pd.concat([gdf1, gdf2], ignore_index=True)

# --- FIX GEOMETRY ERRORS ---
# Force valid geometries by buffer(0)
combined["geometry"] = combined["geometry"].buffer(0)

# Add dissolve key
combined["id"] = 1

# Dissolve
dissolved = combined.dissolve(by="id")

# Reproject to UTM Zone 39N (for accurate area calculation)
dissolved_utm = dissolved.to_crs(epsg=32639)

# Calculate area
dissolved_utm["area_sqm"] = dissolved_utm.geometry.area
dissolved_utm["area_sqkm"] = dissolved_utm["area_sqm"] / 1e6

# Keep only geometry + area
fields_to_keep = ["geometry", "area_sqm", "area_sqkm"]
dissolved_cleaned = dissolved_utm[fields_to_keep]

# Save result
out_path = r"...\dissolved_reference.shp"
dissolved_cleaned.to_file(out_path)

print("✅ Dissolved shapefile saved:", out_path)
