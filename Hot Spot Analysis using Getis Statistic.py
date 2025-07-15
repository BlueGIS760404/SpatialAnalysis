import geopandas as gpd
import matplotlib.pyplot as plt
from libpysal.weights import Queen
from esda import G_Local

# === Step 1: Load Natural Earth countries shapefile ===
shapefile_path = 'ne_110m_admin_0_countries.shp'
gdf = gpd.read_file(shapefile_path)

# Filter for Africa
gdf = gdf[gdf['CONTINENT'] == 'Africa']

gdf = gdf.to_crs("EPSG:6933")  # Equal-area projection for Africa
gdf['area_m2'] = gdf['geometry'].area
gdf['area_km2'] = gdf['area_m2'] / 1e6

# Create population density column
gdf['pop_density'] = gdf['POP_EST'] / gdf['area_km2']  # people per km²

# === Step 2: Spatial Weights Matrix (Queen contiguity) ===
w = Queen.from_dataframe(gdf)
w.transform = 'r'

# === Step 3: Local G* statistic
g_local = G_Local(gdf['pop_density'], w, transform='r', star=True)

# Add results
gdf['GiZScore'] = g_local.Zs
gdf['p_value'] = g_local.p_sim

# Classification
def classify_gi(z, p, sig_level=0.05):
    if p < sig_level:
        if z > 0:
            return 'Hotspot'
        else:
            return 'Coldspot'
    return 'Not Significant'

gdf['Gi_Classification'] = [classify_gi(z, p) for z, p in zip(gdf['GiZScore'], gdf['p_value'])]

# === Step 4: Plot with Legend
import matplotlib.patches as mpatches

fig, ax = plt.subplots(1, 1, figsize=(12, 8))

# Define classification colors
colors = {'Hotspot': 'red', 'Coldspot': 'blue', 'Not Significant': 'lightgrey'}

# Plot the map
gdf.plot(
    column='Gi_Classification',
    ax=ax,
    color=gdf['Gi_Classification'].map(colors),
    edgecolor='black',
    linewidth=0.5
)

# Manually create legend
legend_patches = [mpatches.Patch(color=clr, label=lbl) for lbl, clr in colors.items()]
ax.legend(handles=legend_patches, title="Gi* Classification", loc='lower left')

# Final formatting
plt.title('Hotspot Analysis (Getis-Ord Gi*) on Population Density in Africa')
plt.axis('off')
plt.tight_layout()
plt.show()
