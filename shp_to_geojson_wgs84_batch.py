import geopandas as gpd
import os

# === CONFIGURATION ===
input_folder = r"C:\xampp\htdocs\webmap201\data\shp"   # Folder containing .shp files
output_folder = r"C:\xampp\htdocs\webmap201\data\geojson"  # Folder to save .geojson files

# Create output folder if it doesn't exist
os.makedirs(output_folder, exist_ok=True)

# Loop through all .shp files in the input folder
for filename in os.listdir(input_folder):
    if filename.lower().endswith(".shp"):
        shapefile_path = os.path.join(input_folder, filename)
        geojson_filename = os.path.splitext(filename.lower())[0] + ".geojson"
        geojson_path = os.path.join(output_folder, geojson_filename)

        print(f"Processing: {filename}")

        try:
            # Read shapefile
            gdf = gpd.read_file(shapefile_path)

            # Convert CRS to WGS84 (EPSG:4326)
            gdf = gdf.to_crs(epsg=4326)

            # Export to GeoJSON
            gdf.to_file(geojson_path, driver="GeoJSON")

            print(f"✅ Saved GeoJSON: {geojson_path}")
        except Exception as e:
            print(f"❌ Failed to convert {filename}: {e}")

print("\nAll conversions completed!")
