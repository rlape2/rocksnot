"""Main module."""
import string
import random
import ipyleaflet 

class Map(ipyleaflet.Map):
    
    def __init__(self, center=(20, 0), zoom=2, **kwargs) -> None:

        if "scroll_wheel_zoom" not in kwargs:
            kwargs["scroll_wheel_zoom"] = True

        super().__init__(center=center, zoom=zoom, **kwargs)

        if "height" not in kwargs:
            self.layout.height = "500px"
        else:
            self.layout.height = kwargs["height"]

        if "fullscreen_control" not in kwargs:
            kwargs["fullscreen_control"] = True
        if kwargs["fullscreen_control"]:
            self.add_fullscreen_control()
        
        if "layers_control" not in kwargs:
            kwargs["layers_control"] = True
        if kwargs["layers_control"]:
            self.add_layers_control()

    def add_search_control(self, position="topleft", **kwargs):
        """Adds a search control to the map."""
        if "url" not in kwargs:
            kwargs["url"] = 'https://nominatim.openstreetmap.org/search?format=json&q={s}'
    

        search_control = ipyleaflet.SearchControl(position=position, **kwargs)
        self.add_control(search_control)

    def add_draw_control(self, **kwargs):
        """Adds a draw control to the map."""
        draw_control = ipyleaflet.DrawControl(**kwargs)

        draw_control.polyline =  {
            "shapeOptions": {
                "color": "#6bc2e5",
                "weight": 8,
                "opacity": 1.0
            }
        }
        draw_control.polygon = {
            "shapeOptions": {
                "fillColor": "#6be5c3",
                "color": "#6be5c3",
                "fillOpacity": 1.0
            },
            "drawError": {
                "color": "#dd253b",
                "message": "Oups!"
            },
            "allowIntersection": False
        }
        draw_control.circle = {
            "shapeOptions": {
                "fillColor": "#efed69",
                "color": "#efed69",
                "fillOpacity": 1.0
            }
        }
        draw_control.rectangle = {
            "shapeOptions": {
                "fillColor": "#fca45d",
                "color": "#fca45d",
                "fillOpacity": 1.0
            }
        }

        self.add_control(draw_control)

    def add_layers_control(self, position="topright"):
        """Adds a layers control to the map."""
        layers_control = ipyleaflet.LayersControl(position=position)
        self.add_control(layers_control)

    def add_fullscreen_control(self, position="topleft"):
        """Adds a fullscreen control to the map."""
        fullscreen_control = ipyleaflet.FullScreenControl(position=position)
        self.add_control(fullscreen_control)

    def add_tile_layer(self, url, name, attribution="", **kwargs):
        """Adds a tile layer to the map."""
        tile_layer = ipyleaflet.TileLayer(url=url, attribution=attribution, name=name, **kwargs)
        self.add_layer(tile_layer)

    def add_basemap(self, basemap):
        """Adds a basemap to the map."""
        import xyzservices.providers as xyz

        if basemap.lower() == "hybrid":
            url = "https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}"
            self.add_tile_layer(url, name=basemap)

        else:
            try:
                layer = eval(f"xyz.{basemap}")
                url = layer.build_url()
                attribution = layer.attribution
                self.add_tile_layer(url=url, attribution=attribution, name=basemap)

            except:
                raise ValueError(f"Invalid basemap name: {basemap}")
    

    def add_geojson(self, data, **kwargs):
        """Adds a GeoJSON layer to the map."""
        import json

        if isinstance(data, str):
            with open(data, "r") as f:
                data = json.load(f)

        geojson = ipyleaflet.GeoJSON(data=data, **kwargs)
        self.add_layer(geojson)

    def add_shp(self, data, **kwargs):
        """Adds a Shapefile layer to the map."""
        import geopandas as gpd
        import json
        gdf = gpd.read_file(data)
        data = json.loads(gdf.to_json())
        geojson = ipyleaflet.GeoJSON(data=data, **kwargs)
        self.add_layer(geojson)
        #return geojson
    
    def add_vector(self, data, **kwargs):
        """Adds a Vector layer to the map."""
        import geopandas as gpd
        import json
        gdf = gpd.read_file(data)
        data = json.loads(gdf.to_json())
        vector = ipyleaflet.VectorLayer(data=data, **kwargs)
        self.add_layer(vector)
        #return vector

    def add_raster(self, url, name='Raster', fit_bounds=True, **kwargs):
        import httpx
        titiler_endpoint = "https://titiler.xyz" 
     
        r = httpx.get(
            f"{titiler_endpoint}/cog/info",
            params = {
                "url": url,
            }
        ).json()

        bounds = r["bounds"]

        r = httpx.get(
            f"{titiler_endpoint}/cog/tilejson.json",
            params = {
             "url": url,
            }
        ).json()

        tile = r['tiles'][0]

        self.add_tile_layer(url=tile, name=name, **kwargs)

        if fit_bounds:
            bbox = [[bounds[1], bounds[0]], [bounds[3], bounds[2]]]
            self.fit_bounds(bbox)

    def add_local_raster(self, filename, name='Local Raster', **kwargs):
        try:
            import localtilesserver
        except ImportError:
            raise ImportError("Please install localtilesserver: pip install localtilesserver")