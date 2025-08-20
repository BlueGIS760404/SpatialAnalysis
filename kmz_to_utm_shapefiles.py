import geopandas as gpd
import os
import zipfile
from shapely.geometry import MultiPoint, Point, Polygon
import xml.etree.ElementTree as ET

# ===============================
# 🔧 USER SETTINGS
# ===============================
KMZ_PATH = r"...\2000.kmz"
OUTPUT_DIR = r"shapefiles_output"
REFERENCE_YEAR = 2000
# ===============================

def get_utm_crs(lon, lat):
    """Determine UTM CRS based on longitude and latitude."""
    zone_number = int((lon + 180) // 6) + 1
    hemisphere = "north" if lat >= 0 else "south"
    epsg = 32600 + zone_number if hemisphere == "north" else 32700 + zone_number
    return f"EPSG:{epsg}"

def parse_coordinates(coords_str):
    """Parse coordinates string from KML."""
    coords = []
    for coord in coords_str.strip().split():
        parts = coord.split(',')
        if len(parts) >= 2:
            try:
                lon = float(parts[0])
                lat = float(parts[1])
                coords.append((lon, lat))
            except ValueError:
                continue
    return coords

def extract_features_from_kml(kml_path):
    """Extract all features from KML using direct XML parsing."""
    tree = ET.parse(kml_path)
    root = tree.getroot()
    
    # Define KML namespace
    ns = {'kml': 'http://www.opengis.net/kml/2.2'}
    
    features_by_folder = {}
    current_folder = "Unknown"
    
    # Recursively process elements
    def process_element(element, folder_name):
        if element.tag.endswith('Folder'):
            # New folder
            name_elem = element.find('kml:name', ns)
            new_folder = name_elem.text if name_elem is not None else folder_name
            
            # Process all children
            for child in element:
                process_element(child, new_folder)
                
        elif element.tag.endswith('Placemark'):
            # Placemark found
            name_elem = element.find('kml:name', ns)
            name = name_elem.text if name_elem is not None else "Unnamed"
            
            desc_elem = element.find('kml:description', ns)
            description = desc_elem.text if desc_elem is not None else ""
            
            # Extract geometry
            geometry = None
            point_elem = element.find('.//kml:Point', ns)
            polygon_elem = element.find('.//kml:Polygon', ns)
            
            if point_elem is not None:
                coords_elem = point_elem.find('kml:coordinates', ns)
                if coords_elem is not None and coords_elem.text:
                    coords = parse_coordinates(coords_elem.text)
                    if coords:
                        geometry = Point(coords[0])
            
            elif polygon_elem is not None:
                coords_elem = polygon_elem.find('.//kml:coordinates', ns)
                if coords_elem is not None and coords_elem.text:
                    coords = parse_coordinates(coords_elem.text)
                    if coords:
                        geometry = Polygon(coords)
            
            if geometry is not None:
                if folder_name not in features_by_folder:
                    features_by_folder[folder_name] = []
                
                features_by_folder[folder_name].append({
                    'name': name,
                    'description': description,
                    'geometry': geometry
                })
        
        else:
            # Process children of other elements
            for child in element:
                process_element(child, folder_name)
    
    # Start processing from root
    for child in root:
        process_element(child, current_folder)
    
    return features_by_folder

def kmz_to_category_shapefiles(kmz_path, output_dir, year):
    os.makedirs(output_dir, exist_ok=True)

    # Extract KML from KMZ
    with zipfile.ZipFile(kmz_path, 'r') as kmz:
        kml_files = [f for f in kmz.namelist() if f.endswith('.kml')]
        if not kml_files:
            raise ValueError("No KML found inside KMZ.")
        kml_path = kmz.extract(kml_files[0], path=output_dir)

    try:
        # Parse KML using direct XML parsing to get all features
        features_by_folder = extract_features_from_kml(kml_path)
        print(f"Found folders: {list(features_by_folder.keys())}")
        
        # Process each folder
        for category, features in features_by_folder.items():
            if not features:
                print(f"Skipping empty category: {category}")
                continue
                
            print(f"Category '{category}': Found {len(features)} features")
            
            # Create GeoDataFrame from features
            geometries = []
            names = []
            descriptions = []
            
            for feature in features:
                geometries.append(feature['geometry'])
                names.append(feature['name'])
                descriptions.append(feature['description'])
            
            # Create GeoDataFrame
            category_gdf = gpd.GeoDataFrame({
                'Name': names,
                'Description': descriptions,
                'geometry': geometries
            }, crs="EPSG:4326")  # KML uses WGS84
            
            # Determine UTM zone from centroid
            valid_geoms = [geom.centroid for geom in category_gdf.geometry if geom is not None]
            if not valid_geoms:
                print(f"Skipping category with no valid geometries: {category}")
                continue
                
            centroid = MultiPoint(valid_geoms).centroid
            utm_crs = get_utm_crs(centroid.x, centroid.y)

            # Reproject
            category_gdf_utm = category_gdf.to_crs(utm_crs)
            
            # Clean up column names for Shapefile format (limit to 10 chars)
            new_columns = {}
            for col in category_gdf_utm.columns:
                if len(col) > 10:
                    new_columns[col] = col[:10]
            if new_columns:
                category_gdf_utm = category_gdf_utm.rename(columns=new_columns)

            # Clean category name for filename
            safe_name = str(category).lower().replace(" ", "_").replace("/", "_").replace("\\", "_")
            shp_name = f"reference_{year}_{safe_name}.shp"
            shp_path = os.path.join(output_dir, shp_name)

            # Save to shapefile
            category_gdf_utm.to_file(shp_path, driver="ESRI Shapefile")
            print(f"Saved category '{category}' with {len(category_gdf)} features → {shp_path} (CRS: {utm_crs})")
                
    except Exception as e:
        print(f"Error processing KML file: {e}")
        import traceback
        traceback.print_exc()
        return

# ===============================
# 🚀 RUN SCRIPT
# ===============================
if __name__ == "__main__":
    kmz_to_category_shapefiles(KMZ_PATH, OUTPUT_DIR, REFERENCE_YEAR)
