import rasterio
import numpy as np

input_path = r"...\L8_composite_2020.tif"
output_path = r"...\L8_composite_2020_n.tif"
nodata_value = -3.4028235e+38

with rasterio.open(input_path) as src:
    profile = src.profile
    data = src.read()  # shape: (bands, rows, cols)

    # Create a mask where pixels == nodata_value
    mask = (data == nodata_value)

    # Replace nodata pixels with np.nan (or any nodata)
    # You can also pick a nodata value for output; here we use -9999
    output_nodata = -9999
    data = data.astype('float32')  # promote to float for NaN support
    data[mask] = output_nodata

    # Update profile to set nodata value
    profile.update(
        dtype=rasterio.float32,
        nodata=output_nodata,
        compress='lzw'  # optional compression
    )

    # Write masked data to new raster
    with rasterio.open(output_path, 'w', **profile) as dst:
        dst.write(data)

print(f"Saved masked raster: {output_path}")
