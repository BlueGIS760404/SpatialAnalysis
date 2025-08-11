import rasterio
import numpy as np
import matplotlib.pyplot as plt
import os

def detect_sensor(filename, dataset):
    """
    Detect sensor type based on filename or metadata.
    Returns sensor name string and band mapping dictionary.
    """
    fname = os.path.basename(filename).lower()

    if "lc08" in fname or "landsat8" in fname or "l8" in fname:
        sensor = "Landsat8"
        bands = {
            "B2": 2,  # Blue
            "B3": 3,  # Green
            "B4": 4,  # Red
            "B5": 5,  # NIR
            "B8": 8   # Panchromatic (optional)
        }
    elif "lt05" in fname or "landsat5" in fname or "l5" in fname:
        sensor = "Landsat5"
        bands = {
            "B1": 1,  # Blue
            "B2": 2,  # Green
            "B3": 3,  # Red
            "B4": 4,  # NIR
            "B8": 8   # Panchromatic band may or may not exist
        }
    elif "le07" in fname or "landsat7" in fname or "l7" in fname:
        sensor = "Landsat7"
        bands = {
            "B1": 1,  # Blue
            "B2": 2,  # Green
            "B3": 3,  # Red
            "B4": 4,  # NIR
            "B8": 8   # Panchromatic
        }
    elif "sentinel" in fname or "s2" in fname or "sentinel-2" in fname:
        sensor = "Sentinel2"
        bands = {
            "B2": 2,   # Blue
            "B3": 3,   # Green
            "B4": 4,   # Red
            "B8": 8    # NIR
        }
    elif "modis" in fname:
        sensor = "MODIS"
        bands = {
            "B1": 1,  # Red
            "B2": 2,  # NIR
        }
    else:
        sensor = "Unknown"
        bands = {}
    
    return sensor, bands

# --- Main code ---
image_path = r"E:\Freelancing\P_05_6.18.2025\data\dataset\imagery\landsat\L5_composite_2000.tif"
dataset = rasterio.open(image_path)

sensor, bands = detect_sensor(image_path, dataset)
print(f"Detected sensor: {sensor}")
print(f"Using bands: {bands}")

if not bands:
    raise ValueError("Could not detect sensor or bands automatically. Please specify bands manually.")

nodata_val = dataset.nodata
print(f"\nNodata value detected: {nodata_val}")

out_image = dataset.read().astype(float)
num_bands = out_image.shape[0]

# NDVI bands selection per sensor
required_bands_for_ndvi = []
if sensor == "Landsat5" or sensor == "Landsat7":
    required_bands_for_ndvi = ["B4", "B3"]  # NIR=4, Red=3
elif sensor == "Landsat8":
    required_bands_for_ndvi = ["B5", "B4"]  # NIR=5, Red=4
elif sensor == "Sentinel2":
    required_bands_for_ndvi = ["B8", "B4"]  # NIR=8, Red=4

# Validate NDVI bands presence
missing_band = False
indices = []
if required_bands_for_ndvi:
    for b in required_bands_for_ndvi:
        if b not in bands:
            print(f"Required band {b} for NDVI not found.")
            missing_band = True
            break
        idx = bands[b] - 1
        if idx >= num_bands:
            print(f"Band index {idx} for {b} out of range.")
            missing_band = True
            break
        indices.append(idx)
else:
    missing_band = True

# Prepare figure for combined output
fig, axes = plt.subplots(2, 3, figsize=(18, 10))
axes = axes.flatten()

# Plot histograms for up to 4 bands
plot_count = 0
for band_name, band_idx in bands.items():
    if plot_count >= 4:
        break
    if band_idx - 1 >= num_bands:
        print(f"Skipping {band_name}, index {band_idx} out of range.")
        continue
    data = out_image[band_idx - 1]

    if nodata_val is not None:
        data = data[data != nodata_val]
    data = data[np.isfinite(data)]

    axes[plot_count].hist(data, bins=50, color='gray', edgecolor='black')
    axes[plot_count].set_title(f"{band_name} Histogram")
    plot_count += 1

# Calculate NDVI if possible and plot histogram + map
if not missing_band:
    nir = out_image[indices[0]]
    red = out_image[indices[1]]

    valid_mask = np.ones(nir.shape, dtype=bool)
    if nodata_val is not None:
        valid_mask = (nir != nodata_val) & (red != nodata_val)

    nir = np.where(valid_mask, nir, np.nan)
    red = np.where(valid_mask, red, np.nan)

    ndvi = (nir - red) / (nir + red)
    ndvi[np.isinf(ndvi)] = np.nan

    # NDVI histogram
    axes[4].hist(ndvi[np.isfinite(ndvi)], bins=50, color='green', edgecolor='black')
    axes[4].set_title("NDVI Histogram")

    # NDVI spatial map
    ndvi_img = axes[5].imshow(ndvi, cmap='RdYlGn', vmin=-1, vmax=1)
    axes[5].set_title("NDVI Map")
    axes[5].axis('off')
    fig.colorbar(ndvi_img, ax=axes[5], fraction=0.046, pad=0.04)
else:
    axes[4].axis('off')
    axes[5].axis('off')
    print("Skipping NDVI due to missing bands.")

plt.tight_layout()

output_file = "output_histograms_ndvi.png"
plt.savefig(output_file, dpi=300)
print(f"Saved combined figure as {output_file}")

plt.show()
