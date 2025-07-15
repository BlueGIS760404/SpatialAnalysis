import geopandas as gpd
from shapely.geometry import Polygon

# 1. Load the file
gdf = gpd.read_file("single_polygon.shp")

# 2. Apply aggressive simplification (tolerance in CRS units)
tolerance = 200  # Meters (for UTM) or 0.1 for decimal degrees (WGS84)
gdf.geometry = gdf.geometry.simplify(tolerance)

# 3. Verify
poly = gdf.geometry.iloc[0]
print(f"Final vertex count: {len(poly.exterior.coords)}")  # Should be ≤500

# 4. Export as new file (critical step!)
gdf.to_file("simplified_output.shp")
