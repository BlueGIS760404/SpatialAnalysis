import geopandas as gpd

# Read shapefile
gdf = gpd.read_file(r"C:\Users\Reza\329.shp")

# Create area field
gdf["AREA_SORT"] = gdf.geometry.area

# Sort so large polygons first, small polygons last
gdf_sorted = gdf.sort_values(by="AREA_SORT", ascending=False)

# Save new shapefile
gdf_sorted.to_file(r"C:\Users\Reza\329_sorted.shp")

print("Saved sorted shapefile.")
