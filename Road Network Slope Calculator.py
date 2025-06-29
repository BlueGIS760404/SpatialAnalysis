import geopandas as gpd
import rasterio
from rasterio.sample import sample_gen
import numpy as np
import matplotlib.pyplot as plt
from shapely.ops import segmentize

# 1. Load road network (shapefile) and DEM (GeoTIFF)
roads_gdf = gpd.read_file("roads.shp")
with rasterio.open("dem.tif") as src:
    dem_data = src.read(1)  # Read first band (elevation)
    transform = src.transform
    nodata = src.nodata
    dem_crs = src.crs

# 2. Ensure roads match DEM's CRS
roads_gdf = roads_gdf.to_crs(dem_crs)

# 3. Segmentize roads for finer elevation sampling (e.g., every 10 meters)
roads_gdf['geometry'] = roads_gdf.geometry.apply(lambda geom: segmentize(geom, max_segment_length=10))

# 4. Function to calculate slope for a road segment
def calculate_slope(geom, raster_data, transform, nodata):
    coords = list(geom.coords)  # Get start and end points
    start, end = coords[0], coords[-1]
    
    # Sample elevation at start and end points
    elevations = list(sample_gen(raster_data, [(start[0], start[1]), (end[0], end[1])], 1))
    elev_start, elev_end = elevations[0][0], elevations[1][0]
    
    # Check for NoData or invalid values
    if elev_start == nodata or elev_end == nodata or np.isnan(elev_start) or np.isnan(elev_end):
        return np.nan
    
    # Calculate rise (elevation difference) and run (horizontal distance)
    rise = abs(elev_end - elev_start)  # In meters
    run = geom.length  # In CRS units (meters if UTM)
    
    # Calculate percent slope: (rise/run) * 100
    if run == 0:  # Avoid division by zero
        return np.nan
    slope_percent = (rise / run) * 100
    
    return slope_percent

# 5. Apply slope calculation to each road segment
roads_gdf['slope_percent'] = roads_gdf.geometry.apply(
    lambda geom: calculate_slope(geom, dem_data, transform, nodata)
)

# 6. Visualize roads colored by slope
fig, ax = plt.subplots(figsize=(10, 6))
roads_gdf.plot(column='slope_percent', ax=ax, legend=True, cmap='RdYlGn_r',
               legend_kwds={'label': "Slope (%)", 'orientation': "horizontal"},
               missing_kwds={'color': 'lightgrey', 'label': 'No Data'})
plt.title("Road Network Slope Analysis")
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.show()

# 7. Save results to a new shapefile (optional)
roads_gdf.to_file("roads_with_slope.shp")
