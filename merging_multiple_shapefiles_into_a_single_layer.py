import pandas as pd
import geopandas as gpd
import os
import glob

# Specify the folder containing shapefiles
folder_path = '...path/folder_name'  # Replace with your folder path

# Get list of all .shp files in the folder
shapefiles = glob.glob(os.path.join(folder_path, '*.shp'))

# Initialize an empty list to store GeoDataFrames
gdfs = []

# Read each shapefile and add a source identifier
for shp in shapefiles:
    # Read the shapefile
    gdf = gpd.read_file(shp)
    
    # Add a column to identify the source layer
    source_name = os.path.basename(shp).replace('.shp', '')  # Extract filename without extension
    gdf['source'] = source_name
    
    # Append to the list
    gdfs.append(gdf)

# Check if any shapefiles were found
if not gdfs:
    print("No shapefiles found in the specified folder.")
else:
    # Merge all GeoDataFrames into one
    merged_gdf = gpd.GeoDataFrame(pd.concat(gdfs, ignore_index=True, sort=False))

    # Ensure the CRS is consistent (use the CRS of the first shapefile)
    merged_gdf = merged_gdf.set_crs(gdfs[0].crs, allow_override=True)

    # Save the merged GeoDataFrame to a new shapefile
    output_shapefile = os.path.join(folder_path, 'merged_layer.shp')
    merged_gdf.to_file(output_shapefile)

    print(f"Merged shapefile saved as: {output_shapefile}")
