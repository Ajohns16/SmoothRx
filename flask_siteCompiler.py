from flask import Flask, url_for, Request;

app = Flask(__name__)

def buildGif(start, end):
    return 'cache/KGSP20240110_060022_V06.png' #sim-link

@app.route("/")
def hello_world():
    #build and save gifs (expand for 3 towers)
    gifName = buildGif("start", "end")
    #get gifURls 9expand for 3 towers)
    imageURL = url_for('static', filename=gifName)
    
    #build and return leaflet page (could probably be converted into a template)
    return '''<html lang="EN">
    <header>
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
        integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY="
        crossorigin=""/>
        <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"
        integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo="
        crossorigin=""></script>
     
    </header>
    <body>
        <div id="map" style="height: 100%"></div>
        <script>
            var map = L.map('map').setView([34.883304595947266, -82.21983337402344], 10);
            L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
                maxZoom: 19,
                attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
            }).addTo(map);
            var kgspLat = 34.883304595947266;
            var kgspLong = -82.21983337402344;
            var imageUrl = "''' + imageURL + '''"
            //var imageUrl ="https://i0.wp.com/dianaurban.com/wp-content/uploads/2017/07/01-cat-stretching-feet.gif?resize=500%2C399&ssl=1";
            var latLngBounds = L.latLngBounds([[kgspLat-(300/111), kgspLong - (300/(111*Math.cos((kgspLat * Math.PI)/180)))], [kgspLat + (300/111), kgspLong + (300/111*Math.cos((kgspLat * Math.PI)/180))]]);
            var errorOverlayUrl = 'https://cdn-icons-png.flaticon.com/512/110/110686.png';

            var imageOverlay = L.imageOverlay(imageUrl, latLngBounds, {
                opacity: 0.8,
                errorOverlayUrl: errorOverlayUrl,
                interactive: true
            }).addTo(map);
        </script>
    </body>
</html>'''

