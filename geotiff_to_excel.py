import rasterio
import pandas as pd

# Open the GeoTIFF
with rasterio.open("D:\Module11\PySEBAL_data\Meteo\geotiff.tif") as src:
    array = src.read(1)  # read first band
    transform = src.transform

# Flatten data with coordinates
rows, cols = array.shape
data = []
for row in range(rows):
    for col in range(cols):
        x, y = transform * (col, row)  # get coordinates
        value = array[row, col]
        data.append((x, y, value))

# Save to Excel
df = pd.DataFrame(data, columns=["X", "Y", "Value"])
df.to_excel("geotiff.xlsx", index=False)
