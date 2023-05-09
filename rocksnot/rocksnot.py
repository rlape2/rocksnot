"""Main module."""
import string
import random
import ipyleaflet 
import ipywidgets as widgets
from ipyleaflet import WidgetControl

import fastkml
import simplekml 
import json
import shapefile

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

        if "add_toolbar" not in kwargs:
            kwargs["add_toolbar"] = True
        if kwargs["add_toolbar"]:
            self.add_toolbar()

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
        
    def add_toolbar(self):
        widget_width = "250px"
        padding = "0px 0px 0px 5px"  # upper, right, bottom, left

        toolbar_button = widgets.ToggleButton(
            value=False,
            tooltip="Toolbar",
            icon="wrench",
            layout=widgets.Layout(width="28px", height="28px", padding=padding),
        )

        close_button = widgets.ToggleButton(
            value=False,
            tooltip="Close the tool",
            icon="times",
            button_style="primary",
            layout=widgets.Layout(height="28px", width="28px", padding=padding),
        )

        close_button = widgets.ToggleButton(
            value=False,
            tooltip="Close the tool",
            icon="times",
            button_style="primary",
            layout=widgets.Layout(height="28px", width="28px", padding=padding),
        )
        toolbar = widgets.HBox([toolbar_button])

        def toolbar_click(change):
            if change["new"]:
                toolbar.children = [toolbar_button, close_button]
            else:
                toolbar.children = [toolbar_button]
        
        toolbar_button.observe(toolbar_click, "value")

        def close_click(change):
            if change["new"]:
                toolbar_button.close()
                close_button.close()
                toolbar.close()
                
        close_button.observe(close_click, "value")

        rows = 2
        cols = 2
        grid = widgets.GridspecLayout(rows, cols, grid_gap="0px", layout=widgets.Layout(width="65px"))

        icons = ["folder-open", "map", "info", "question"]

        for i in range(rows):
            for j in range(cols):
                grid[i, j] = widgets.Button(description="", button_style="primary", icon=icons[i*rows+j], 
                                            layout=widgets.Layout(width="28px", padding="0px"))
        grid

        toolbar = widgets.VBox([toolbar_button])

        def toolbar_click(change):
            if change["new"]:
                toolbar.children = [widgets.HBox([close_button, toolbar_button]), grid]
            else:
                toolbar.children = [toolbar_button]
                
        toolbar_button.observe(toolbar_click, "value")

        toolbar_ctrl = WidgetControl(widget=toolbar, position="topright")

        output = widgets.Output()
        output_ctrl = WidgetControl(widget=output, position="bottomright")
        self.add_control(output_ctrl)

        basemap = widgets.Dropdown(
            options=[ "hybrid"],
            value=None,
            description="Basemap:",
            style={"description_width": "initial"},
            layout=widgets.Layout(width="250px")
        )

        def change_basemap(change):
            if change ['new']:
                with output:
                    print(basemap)
                self.add_basemap(basemap.value)


        basemap.observe(change_basemap, 'value')


        basemap_ctrl = WidgetControl(widget = basemap, position="topright")

        def tool_click(b):    
             with output:
                output.clear_output()
                print(f"You clicked the {b.icon} button")

                if b.icon == 'map':
                    self.add(basemap_ctrl)

        for i in range(rows):
            for j in range(cols):
                tool = grid[i, j]
                tool.on_click(tool_click)


        self.add_control(toolbar_ctrl)


def convert_geojson_to_shapefile(geojson_file_path, shapefile_file_path):
    # Load the GeoJSON file into a GeoDataFrame
    import geopandas as gpd
    gdf = gpd.read_file(geojson_file_path)

    # Save the GeoDataFrame as a Shapefile
    gdf.to_file(shapefile_file_path, driver='ESRI Shapefile')

def convert_shapefile_to_geojson(shapefile_file_path, geojson_file_path):
    import geopandas as gpd
    # Load the Shapefile into a GeoDataFrame
    gdf = gpd.read_file(shapefile_file_path)

    # Save the GeoDataFrame as a GeoJSON file
    gdf.to_file(geojson_file_path, driver='GeoJSON')

def convert_geojson_to_kml(geojson_file_path, kml_file_path):
    # Load the GeoJSON file
    with open(geojson_file_path) as f:
        geojson_data = json.load(f)

    # Create a KML object
    kml = simplekml.Kml()

    # Iterate over the features in the GeoJSON file
    for feature in geojson_data['features']:
        # Create a Placemark for each feature
        placemark = kml.newpoint(name=feature['properties']['name'],
                                    coords=[(feature['geometry']['coordinates'][0],
                                            feature['geometry']['coordinates'][1])])

    # Write the KML file
    with open(kml_file_path, 'wb') as f:
        f.write(kml.kml())

def convert_shapefile_to_kml(shapefile_file_path, kml_file_path):
    # Load the Shapefile
    reader = shapefile.Reader(shapefile_file_path)

    # Create a KML object
    kml = simplekml.Kml()

    # Iterate over the shapes in the Shapefile
    for shape in reader.shapes():
        # Create a Placemark for each shape
        placemark = kml.newpoint(name=shape.record[0],
                                    coords=[(pt[1], pt[0]) for pt in shape.points])

    # Write the KML file
    with open(kml_file_path, 'wb') as f:
        f.write(kml.kml())


    def add_image(self, url, width=100, height=100, position="bottomleft"):
        """Adds an image to the map.
        
        Args:
            url (str): The URL of the image.
            width (str): The width of the image.
            height (str): The height of the image.
            position (str): The position of the image.
        """

        widget = widgets.HTML(value=f"<img src={url} width='{width}' height='{height}'>")
        control = WidgetControl(widget=widget, position = position)
        self.add_control(control)

