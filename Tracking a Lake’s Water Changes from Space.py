import ee
import geemap
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

# Initialize the Earth Engine API
try:
    ee.Initialize()
except Exception as e:
    ee.Authenticate()
    ee.Initialize()

# Define the region of interest (approximate coordinates for Zalzal Lake, Kaghan Valley)
zalzal_lake = ee.Geometry.Point([73.63, 34.58])  # Adjust coordinates if more precise data is available
region = zalzal_lake.buffer(1000)  # 1km buffer around the lake

# Load the USGS SRTM elevation dataset
elevation = ee.Image('USGS/SRTMGL1_003')

# Function to get elevation at the lake's centroid
def get_elevation():
    elev = elevation.sample(zalzal_lake, scale=30).first().get('elevation').getInfo()
    return elev

# Load Sentinel-2 imagery for water detection (2020-2025)
sentinel2 = ee.ImageCollection('COPERNICUS/S2_SR') \
    .filterBounds(region) \
    .filterDate('2020-01-01', '2025-07-03') \
    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20))  # Filter low cloud cover

# Function to calculate water extent using NDWI (Normalized Difference Water Index)
def calculate_ndwi(image):
    ndwi = image.normalizedDifference(['B3', 'B8']).rename('NDWI')
    water = ndwi.gt(0.3)  # Threshold for water detection
    return image.addBands(ndwi).addBands(water.rename('water_mask'))

# Apply NDWI calculation to the image collection
ndwi_collection = sentinel2.map(calculate_ndwi)

# Calculate water area over time
def calculate_water_area(image):
    water_area = ee.Image(image).select('water_mask').reduceRegion(
        reducer=ee.Reducer.sum(),
        geometry=region,
        scale=10
    ).get('water_mask')
    date = ee.Date(image.get('system:time_start')).format('YYYY-MM-dd')
    return ee.Feature(None, {'date': date, 'water_area': water_area})

# Aggregate water area data
water_area_data = ndwi_collection.map(calculate_water_area).getInfo()

# Convert to DataFrame
dates = [item['properties']['date'] for item in water_area_data['features']]
areas = [item['properties']['water_area'] for item in water_area_data['features']]
df = pd.DataFrame({'Date': dates, 'Water Area (pixels)': areas})

# Get mean elevation
mean_elevation = get_elevation()

# Save data to CSV
df.to_csv('zalzal_lake_water_area.csv', index=False)

# Plot water area over time
plt.figure(figsize=(10, 6))
plt.plot(pd.to_datetime(df['Date']), df['Water Area (pixels)'], marker='o')
plt.title('Zalzal Lake Water Area Over Time (2020-2025)')
plt.xlabel('Date')
plt.ylabel('Water Area (pixels)')
plt.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('zalzal_lake_water_area_plot.png')

# Print mean elevation
print(f"Mean elevation at Zalzal Lake: {mean_elevation} meters")
