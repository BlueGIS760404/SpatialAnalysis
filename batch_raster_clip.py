import os
import rasterio
from rasterio.mask import mask
import geopandas as gpd
from pathlib import Path

def clip_raster_to_shape(input_tif, output_tif, shapefile):
    # Open the raster to get its CRS
    with rasterio.open(input_tif) as src:
        raster_crs = src.crs
        raster_transform = src.transform

        # Read and reproject shapefile
        gdf = gpd.read_file(shapefile)
        if gdf.crs != raster_crs:
            gdf = gdf.to_crs(raster_crs)

        # Mask the raster
        shapes = [feature["geometry"] for feature in gdf.__geo_interface__["features"]]
        out_image, out_transform = mask(src, shapes, crop=True)
        out_meta = src.meta.copy()

    # Update metadata
    out_meta.update({
        "driver": "GTiff",
        "height": out_image.shape[1],
        "width": out_image.shape[2],
        "transform": out_transform,
        "crs": raster_crs
    })

    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_tif), exist_ok=True)

    # Save clipped raster
    with rasterio.open(output_tif, "w", **out_meta) as dest:
        dest.write(out_image)

def process_directory(input_root, output_root, shapefile):
    for dirpath, _, filenames in os.walk(input_root):
        for filename in filenames:
            if filename.lower().endswith(".tif"):
                input_tif = os.path.join(dirpath, filename)
                relative_path = os.path.relpath(dirpath, input_root)
                output_dir = os.path.join(output_root, relative_path)
                output_tif = os.path.join(output_dir, filename)
                print(f"Processing: {input_tif}")
                clip_raster_to_shape(input_tif, output_tif, shapefile)

# === CONFIGURE THESE ===
input_directory = r"D:\Module11\PySEBAL_data\SEBAL_out"
output_directory = r"D:\Module11\PySEBAL_data\SEBAL_out_clipped"
shapefile_path = r"D:\Module11\PySEBAL_data\mississippi.shp"

# === RUN ===
process_directory(input_directory, output_directory, shapefile_path)
