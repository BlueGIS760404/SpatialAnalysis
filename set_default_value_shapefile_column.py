import geopandas as gpd

# Input shapefile
input_file = r"...\reference_2000_nbu.shp"
output_file = r"...\reference_2000_nbu_new.shp"

# Column name to update
column_name = "class"

# Default value
default_value = 0  # or 0, or any value

# Load shapefile
gdf = gpd.read_file(input_file)

# If column does not exist, create it
if column_name not in gdf.columns:
    gdf[column_name] = None

# Assign default value to all rows
gdf[column_name] = default_value

# Save updated shapefile
gdf.to_file(output_file)

print(f"Updated shapefile saved as {output_file}")
