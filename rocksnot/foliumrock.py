import folium

class Map(folium.Map):
    """A folium map."""
    def __init__(self, location=[45.5236, -122.6750], zoom_start=13, **kwargs):
       
        if "scroll_wheel_zoom" not in kwargs:
            kwargs["scroll_wheel_zoom"] = True
        super().__init__(location=location, zoom_start=zoom_start, **kwargs)

    def add_tile_layer(self, url, name, attribution, **kwargs):
        """Adds a tile layer to the map."""
        tile_layer = folium.TileLayer(tiles=url, name=name, attr=attribution, **kwargs)
        tile_layer.add_to(self)
    
    def add_basemap(self, basemap, **kwargs):
            
        import xyzservices.providers as xyz

        if basemap.lower() == "roadmap":
            url = "http://mt0.google.com/vt/lyrs=m&hl=en&x={x}&y={y}&z={z}"
            self.add_tile_layer(url, name=basemap, attribution="Google")

        elif basemap.lower() == "satellite":
            url = "http://mt0.google.com/vt/lyrs=s&hl=en&x={x}&y={y}&z={z}"
            self.add_tile_layer(url, name=basemap, attribution="Google")

        else:
            try:
                basemap = eval(f"xyz.{basemap}")
                url = basemap.build_url()
                attribution = basemap.attribution
                self.add_tile_layer(url, name=basemap.name, attr=attribution, **kwargs)
            except:
                raise ValueError("Invalid basemap name.")
            
    def add_geojson(self, data, **kwargs):
        """Adds a GeoJSON layer to the map."""
        import json
        with open(data, "r") as f:
            data = json.load(f)
        geojson = folium.GeoJson(data=data, **kwargs)
        geojson.add_to(self)

    def add_shp(self, data, **kwargs):
        """Adds a Shapefile layer to the map."""
        import geopandas as gpd
        import json
        gdf = gpd.read_file(data)
        data = json.loads(gdf.to_json())
        geojson = folium.GeoJson(data=data, **kwargs)
        geojson.add_to(self)