import os
import sqlite3
import folium
from scipy.spatial import cKDTree
from PySide6.QtCore import QObject, Slot, Signal

class ClickReceiver(QObject):
    # Use 'object' instead of 'int' to allow unlimited-size Python integers
    node_selected_info = Signal(str, float, float, object) 
    node_selected = Signal(object, object)

    def __init__(self, locator):
        super().__init__()
        self.locator = locator
        self.click_count = 0
        self.source_node = None
        self.dest_node = None

    @Slot(float, float)
    def receive_click(self, lat, lon):
        self.click_count += 1
        nearest_osmid = self.locator.get_nearest_node(lat, lon)
        
        if self.click_count == 1:
            self.source_node = nearest_osmid
            self.node_selected_info.emit("source", lat, lon, nearest_osmid)
            self.node_selected.emit(self.source_node, None)
            
        elif self.click_count == 2:
            self.dest_node = nearest_osmid
            self.node_selected_info.emit("destination", lat, lon, nearest_osmid)
            self.node_selected.emit(self.source_node, self.dest_node)
            self.click_count = 0 # Reset for the next routing request


class MapService:
    def __init__(self, db_path="database/indonesia.db"):
        self.db_path = db_path
        self._init_locator()
        self.receiver = ClickReceiver(self)

    def _init_locator(self):
        print("Loading coordinates into KDTree for fast clicking...")
        self.conn = sqlite3.connect(self.db_path)
        self.c = self.conn.cursor()
        
        self.c.execute("SELECT osmid, y, x FROM nodes")
        data = self.c.fetchall()
        
        self.node_ids = [row[0] for row in data]
        self.coords = [(row[2], row[1]) for row in data] 
        self.tree = cKDTree(self.coords)
        print("KDTree ready!")

    def get_nearest_node(self, lat, lon):
        distance, index = self.tree.query((lon, lat), k=1)
        return self.node_ids[index]

    def generate_base_map(self, save_path="src/assets/temp_indonesia_map.html"):
        """Generates the Folium map and returns the absolute path to the HTML file."""
        m = folium.Map(location=[-0.7893, 113.9213], zoom_start=5, tiles="CartoDB positron")

        cursor_style = """
        <style>
            /* 1. Default cursor for the whole map is a crosshair (+) */
            .leaflet-container {
                cursor: crosshair !important;
            }
            
            /* 2. When the user is actively dragging the map, change to the closed grabbing hand */
            .leaflet-dragging .leaflet-container,
            .leaflet-dragging .leaflet-interactive {
                cursor: grabbing !important;
            }
        </style>
        """

        click_js = """
        <script type="text/javascript" src="qrc:///qtwebchannel/qwebchannel.js"></script>
        <script>
            setTimeout(function() {
                var leafletMap = null;
                for (var key in window) {
                    if (key.startsWith("map_") && window[key] && typeof window[key].on === 'function') {
                        leafletMap = window[key];
                        break;
                    }
                }

                if (leafletMap) {
                    // 1. Define custom colored icons
                    var greenIcon = new L.Icon({
                        iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png',
                        shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
                        iconSize: [25, 41],
                        iconAnchor: [12, 41]
                    });

                    var redIcon = new L.Icon({
                        iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png',
                        shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
                        iconSize: [25, 41],
                        iconAnchor: [12, 41]
                    });

                    // 2. Variables to track click state in the browser
                    var clickCount = 0;
                    var activeMarkers = [];

                    new QWebChannel(qt.webChannelTransport, function(channel) {
                        var pyReceiver = channel.objects.pyReceiver;
                        
                        leafletMap.on('click', function(e) {
                            var lat = e.latlng.lat;
                            var lon = e.latlng.lng;
                            
                            // If this is the 3rd click, clear old markers to start a new route
                            if (clickCount >= 2) {
                                activeMarkers.forEach(marker => leafletMap.removeLayer(marker));
                                activeMarkers = [];
                                clickCount = 0;
                            }
                            
                            // Decide icon color based on click order
                            var currentIcon = (clickCount === 0) ? greenIcon : redIcon;
                            
                            // Add the visual marker and save it so we can delete it later
                            var marker = L.marker([lat, lon], {icon: currentIcon}).addTo(leafletMap);
                            activeMarkers.push(marker);
                            
                            clickCount++;
                            
                            // Send to Python
                            pyReceiver.receive_click(lat, lon);
                        });
                    });
                } else {
                    console.error("Could not locate the Leaflet map object.");
                }
            }, 1000);
        </script>
        """
        m.get_root().header.add_child(folium.Element(cursor_style))
        m.get_root().html.add_child(folium.Element(click_js))
        
        abs_path = os.path.abspath(save_path)
        m.save(abs_path)
        return abs_path