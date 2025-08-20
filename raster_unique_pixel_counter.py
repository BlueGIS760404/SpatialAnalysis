import rasterio
import numpy as np

def get_pixel_value_counts(raster_path):
    """
    Reads a raster and returns a dictionary of unique pixel values and their counts.
    Ignores nodata values if defined.
    """
    with rasterio.open(raster_path) as src:
        data = src.read(1)  # Read first band
        nodata = src.nodata

        # Mask nodata if it exists
        if nodata is not None:
            data = data[data != nodata]

        # Get unique values and their counts
        unique_vals, counts = np.unique(data, return_counts=True)

        # Create dictionary {value: count}
        value_counts = dict(zip(unique_vals, counts))

        print("Pixel value counts:")
        for val, cnt in value_counts.items():
            print(f"Value {val}: {cnt} pixels")

        return value_counts

# Example usage
raster_file = '...\land_cover_2000.tif'
pixel_counts = get_pixel_value_counts(raster_file)
