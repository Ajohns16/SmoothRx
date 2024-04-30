from flask import Flask, url_for, request;
import os;
#import imageio;
from PIL import Image;
from datetime import datetime;

#TODO
# replace all '''html''' returns with templates for ease of future modification

app = Flask(__name__)

#constants used in input validation to ensure noone requests data outside of the sample (if sample is expanded would need to be modified)
earliestDatapoint = '20240110_060000'
latestDatapoint = '20240110_090000'

#builds the custum gifs from user requests (very slow, could be optimized)
#TODO
#add a duration parameter to match up animation lengths and better sync data
#alter to always load the 0 inbetween frame animation, load the page and then allow the user to switch to other animations as they become availible
def buildGif(start, end, inbetweens):

    #establish static and cache locations for input and output (output gifs will be loaded into static, input data is stored in "static/cache")
    staticLocation = app.static_folder
    cachelocation = os.path.join(staticLocation, "cache")
    towers = os.listdir(cachelocation)
    startTime =  start #"20240110_060000"
    endTime =    end #"20240110_073000"
    gifNames = []

    for tower in towers:
        towerlocation = os.path.join(cachelocation, tower)
        firstImage = tower + startTime + "_V06.png"
        lastImageRequest = tower + endTime + "_V06.png"
        #find all the files in each tower's cache folder between the endpoints
        files = os.listdir(towerlocation)
        files.sort()
        files = list(filter(lambda f: '.png' in f and f > firstImage and f < lastImageRequest, files))
        #print(files)

        gifname = tower + files[0][4:-8] + "__" + files[-1][4:-8] + "(" + str(inbetweens) + ")" + ".gif"
        #writer = imageio.get_writer(os.path.join(staticLocation, gifname), fps=max(inbetweens, 1) )

        #read each image into the array
        images = []
        for f in files:
            #print(f)
            #images.append(imageio.imopen(os.path.join(towerlocation, f), 'r'))
            #writer.append_data(imageio.imread((os.path.join(towerlocation, f))))
            images.append(Image.open(os.path.join(towerlocation, f)))

            #loads up the desired number of inbetweens into the animation in their proper place
            betweenFolder = f[:-4] + '-i'
            if betweenFolder in os.listdir(towerlocation):
                betweenlocation = os.path.join(towerlocation, betweenFolder)
                betweenfiles = os.listdir(betweenlocation)
                count = inbetweens
                if ((count > 0) & (f != files[-1])):
                    for bf in betweenfiles:
                        if (((count + inbetweens)%(60 / inbetweens)) == 0):
                            #print(bf)
                            #writer.append_data(imageio.imread(os.path.join(betweenlocation, bf)))
                            #images.append(imageio.imopen(os.path.join(betweenlocation, bf), 'r'))
                            images.append(Image.open(os.path.join(betweenlocation, bf)))
                        count += 1

        #writer.close()

        #determine how long each frame should run for
        frame_one = images[0]
        frameDuration = 1000/(max(inbetweens, 1))
    
        #imageio.mimwrite(os.path.join(staticLocation, gifname), images, format="FFMPEG", fps=inbetweens)
        #print("frameDuration: " + str(frameDuration))

        #create the animation (this is the long part)
        frame_one.save(os.path.join(staticLocation, gifname), format="GIF", append_images=images,
                save_all=True, disposal=2, duration=frameDuration, loop = 0)
        #add the gif name to output
        gifNames.append(gifname)
    return gifNames #['KGSP20240110_060022__20240110_065321(0).gif', 'KFCX20240110_060239__20240110_065028(0).gif', 'KMRX20240110_060148__20240110_065349(0).gif'] #sim-link

#webpage meant to redirect a user to the demo pages (should never be used unless the user manually alters thier get requests)
def invalidInput(inbetweens = "0"):
    return '''<html>
    <header>
    </header>
    <body>
        <h1>Uh oh!</h1>
        <h2>You entered invalid bounds on the form (how did you do that?)</h2>
        <h3>You will redirected to the demo page for your selected number of inbetween frames shortly</h3>
        <h3>If you are not redirected automatically, please click <a href = 'http://127.0.0.1:5000/demo'>here</a></h3>  
    </body>
    <script>
        inbetweens =''' + inbetweens + '''
        alert("You manged to enter invalid info. You will redirected to a demo page.")
        window.location.replace("http://127.0.0.1:5000/demo" + inbetweens)
    </script>
    </html>'''

#hmtl, and js for the map page. populates created gifs with the supplied gif urls
def loadMap(imageURLs):
    return '''<html lang="EN">
        <header>
            <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
            integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY="
            crossorigin=""/>
            <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"
            integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo="
            crossorigin=""></script>
            <script src="leaflet-tilelayer-here.js"></script>
        
        </header>
        <body>
            <div id="map" style="height: 100%"></div>
            <script>
                var map = L.map('map').setView([35.585339, -82.537062], 8);
                //L.tileLayer.here({scheme: 'normal.day', resource: 'maptile', mapId: 'newest',appId: 'abcde', appCode: 'fghij'}).addTo(map);
                L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
                maxZoom: 10,
                minZoom: 6,
                subdomain: 'Transport',
                attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                }).addTo(map);
                var kgspLat = 34.883304595947266; //lat lng found pulled from nexrad's volume scans
                var kgspLong = -82.21983337402344;
                
                //Calculate latlng corner points for each tower's radar display. formula pulled from here https://gis.stackexchange.com/questions/15545/calculating-coordinates-of-square-x-miles-from-center-point
                //map coords based on km not miles
                var kgspLatLngBounds = L.latLngBounds([[kgspLat-(300/111), kgspLong - (300/(111*Math.cos((kgspLat * Math.PI)/180)))], 
                                                        [kgspLat + (300/111), kgspLong + (300/111*Math.cos((kgspLat * Math.PI)/180))]]);

                
                console.log("kgspLatLng done");
                var kmrxLat =36.168609619140625;
                var kmrxLong =-83.40194702148438;
                
                var kmrxLatLngBounds = L.latLngBounds([[kmrxLat-(300/111), kmrxLong - (300/(111*Math.cos((kmrxLat * Math.PI)/180)))], 
                                                        [kmrxLat + (300/111), kmrxLong + (300/111*Math.cos((kmrxLat * Math.PI)/180))]]);

                console.log("kmrxLatLng done");
                var kfcxLat =36.168609619140625;
                var kfcxLong =-80.27397155761719;
                
                var kfcxLatLngBounds = L.latLngBounds([[kfcxLat-(300/111), kfcxLong - (300/(111*Math.cos((kfcxLat * Math.PI)/180)))], 
                                                        [kfcxLat + (300/111), kfcxLong + (300/111*Math.cos((kfcxLat * Math.PI)/180))]]);
                
                                                        
                console.log("kfcxLatLng done");
                //var kgspImageUrl = "https://i0.wp.com/dianaurban.com/wp-content/uploads/2017/07/01-cat-stretching-feet.gif?resize=500%2C399&ssl=1";
                var errorOverlayUrl = 'https://cdn-icons-png.flaticon.com/512/110/110686.png';

                //variable structure for template (on image url inclusion)
                //loads each image into the map as imageOverlays
                var kgspImageUrl = "''' + imageURLs[1] + '''"; //value dependent on template input
                var kgspImageOverlay = L.imageOverlay(kgspImageUrl, kgspLatLngBounds, {
                    opacity: 0.8,
                    errorOverlayUrl: errorOverlayUrl,
                    interactive: true
                }).addTo(map);

                var kmrxImageUrl = "''' + imageURLs[2] + '''";
                var kmrxImageOverlay = L.imageOverlay(kmrxImageUrl, kmrxLatLngBounds, {
                    opacity: 0.8,
                    errorOverlayUrl: errorOverlayUrl,
                    interactive: true
                }).addTo(map)

                var kfcxImageUrl = "''' + imageURLs[0] + '''";
                var kfcxImageOverlay = L.imageOverlay(kfcxImageUrl, kfcxLatLngBounds, {
                    opacity: 0.8,
                    errorOverlayUrl: errorOverlayUrl,
                    interactive: true
                }).addTo(map)
                //end template variance
            </script>
        </body>
    </html>'''

#demo pages a user can load (could probably be condensed into a single route with get requests and a switch statement)
@app.route("/demo")
def demo():
    return demo0()

@app.route("/demo0")
def demo0():
    demoURLs = [url_for("static", filename="KFCXDemo(0).gif"), url_for("static", filename="KGSPDemo(0).gif"), url_for("static", filename="KMRXDemo(0).gif")]
    return loadMap(demoURLs)

@app.route("/demo10")
def demo10():
    demoURLs = [url_for("static", filename="KFCXDemo(10).gif"), url_for("static", filename="KGSPDemo(10).gif"), url_for("static", filename="KMRXDemo(10).gif")]
    return loadMap(demoURLs)

@app.route("/demo30")
def demo30():
    demoURLs = [url_for("static", filename="KFCXDemo(30).gif"), url_for("static", filename="KGSPDemo(30).gif"), url_for("static", filename="KMRXDemo(30).gif")]
    return loadMap(demoURLs)

@app.route("/demo60")
def demo60():
    demoURLs = [url_for("static", filename="KFCXDemo(60).gif"), url_for("static", filename="KGSPDemo(60).gif"), url_for("static", filename="KMRXDemo(60).gif")]
    return loadMap(demoURLs)
    # return '''<html lang="EN">
    # <header>
    #     <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
    #     integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY="
    #     crossorigin=""/>
    #     <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"
    #     integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo="
    #     crossorigin=""></script>
    #     <script src="leaflet-tilelayer-here.js"></script>
     
    # </header>
    # <body>
    #     <div id="map" style="height: 100%"></div>
    #     <script>
    #         var map = L.map('map').setView([34.883304595947266, -82.21983337402344], 10);
    #         //L.tileLayer.here({scheme: 'normal.day', resource: 'maptile', mapId: 'newest',appId: 'abcde', appCode: 'fghij'}).addTo(map);
    #         L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    #            maxZoom: 19,
    #            subdomain: 'Transport',
    #            attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
    #         }).addTo(map);
    #         var kgspLat = 34.883304595947266;
    #         var kgspLong = -82.21983337402344;
            
    #         var kgspLatLngBounds = L.latLngBounds([[kgspLat-(300/111), kgspLong - (300/(111*Math.cos((kgspLat * Math.PI)/180)))], 
    #                                                 [kgspLat + (300/111), kgspLong + (300/111*Math.cos((kgspLat * Math.PI)/180))]]);

            
    #         console.log("kgspLatLng done");
    #         var kmrxLat =36.168609619140625;
    #         var kmrxLong =-83.40194702148438;
            
    #         var kmrxLatLngBounds = L.latLngBounds([[kmrxLat-(300/111), kmrxLong - (300/(111*Math.cos((kmrxLat * Math.PI)/180)))], 
    #                                                 [kmrxLat + (300/111), kmrxLong + (300/111*Math.cos((kmrxLat * Math.PI)/180))]]);

    #         console.log("kmrxLatLng done");
    #         var kfcxLat =36.168609619140625;
    #         var kfcxLong =-80.27397155761719;
            
    #         var kfcxLatLngBounds = L.latLngBounds([[kfcxLat-(300/111), kfcxLong - (300/(111*Math.cos((kfcxLat * Math.PI)/180)))], 
    #                                                 [kfcxLat + (300/111), kfcxLong + (300/111*Math.cos((kfcxLat * Math.PI)/180))]]);
            
                                                    
    #         console.log("kfcxLatLng done");
    #         //var kgspImageUrl = "https://i0.wp.com/dianaurban.com/wp-content/uploads/2017/07/01-cat-stretching-feet.gif?resize=500%2C399&ssl=1";
    #         var errorOverlayUrl = 'https://cdn-icons-png.flaticon.com/512/110/110686.png';

    #         //variable structure for template (on image url inclusion)
    #         var kgspImageUrl = "''' + demoURLs[1] + '''"; //value dependent on template input
    #         var kgspImageOverlay = L.imageOverlay(kgspImageUrl, kgspLatLngBounds, {
    #             opacity: 0.8,
    #             errorOverlayUrl: errorOverlayUrl,
    #             interactive: true
    #         }).addTo(map);

    #         var kmrxImageUrl = "''' + demoURLs[2] + '''";
    #         var kmrxImageOverlay = L.imageOverlay(kmrxImageUrl, kmrxLatLngBounds, {
    #             opacity: 0.8,
    #             errorOverlayUrl: errorOverlayUrl,
    #             interactive: true
    #         }).addTo(map)

    #         var kfcxImageUrl = "''' + demoURLs[0] + '''";
    #         var kfcxImageOverlay = L.imageOverlay(kfcxImageUrl, kfcxLatLngBounds, {
    #             opacity: 0.8,
    #             errorOverlayUrl: errorOverlayUrl,
    #             interactive: true
    #         }).addTo(map)
    #         //end template variance
    #     </script>
    # </body>
    # </html>'''

#defualt route out of the form. Extra layer of input validation, failure at this stage redirects to a demo page
@app.route("/map")
def process_form():
    #startDate=&startTime=&endDate=&endTime=&betweenFrames=0
    #?startDate=2024-01-10&startTime=06%3A00&endDate=2024-01-10&endTime=07%3A00&betweenFrames=0

    #retrive the dat from get requests
    start = request.args.get('startDate')
    end = request.args.get('endDate')
    inbetweens = request.args.get('betweenFrames')
    startTime = request.args.get('startTime')
    endTime = request.args.get('endTime')


    #format date and time into the form needed for buildgifs
    startstr = start[0:4] + start[5:7] + start[8:] + "_" + startTime[0:2] + startTime[3:] + '00'
    endstr = end[0:4] + end[5:7] + end[8:] + '_' + endTime[0:2] + endTime[3:] + '00'

    
    #endpoint = datetime(end[0:4], end[5:7], end[8:], endTime[0:2], endTime[3:], '00')
    #startpoint = datetime(start[0:4], start[5:7], start[8:], startTime[0:2], startTime[3:], '00')


    #catches requests for unsupported inbetweens
    if (inbetweens in ["0", "10", "30", "60"]) == False:
        return invalidInput("0")

    #catches requests for edge case requests that can't be processed
    if (startstr < earliestDatapoint) or (startstr >= latestDatapoint) or (endstr > latestDatapoint) or (endstr <= earliestDatapoint):
        return invalidInput(inbetweens) 
    #print(startstr)
    endpoint = datetime.strptime(end + '_' + endTime +':00', '%Y-%m-%d_%H:%M:%S')
    startpoint = datetime.strptime(start + '_' + startTime +':00', '%Y-%m-%d_%H:%M:%S')
    deltaT = endpoint-startpoint

    #catches requests with swapped start and end or with endpoints to far apart
    if (startTime >= endTime) or ((deltaT.total_seconds()/3600) > 1 ):
        return invalidInput(inbetweens)

    #build and save gifs (expand for 3 towers)
    gifNames = buildGif(startstr, endstr, int(inbetweens))
    #print(gifNames)
    #get gifURls
    imageURLs = []
    for vid in gifNames:
        imageURLs.append(url_for('static', filename=vid))
    
    
    #build and return leaflet page (could probably be converted into a template)
    return loadMap(imageURLs)

#Base page. Form that gets user input for creating custom animations. validates user input before submission
@app.route("/")
def inputForm():
    return '''<!DOCTYPE html>
<html>
    <header>

    </header>
    <body>
        <p>This form will let you create a custom visualization using inbetween frames generated with SmoothWx.</p>
        <p>There is a considerable load time for this tool (longer time requests or requests using more inbetween frames could take up to a few minutes to load, please be patient)</p>
        <p>If you would prefer not to wait there are demos for <a href="http://127.0.0.1:5000/demo0">0</a>, <a href = "http://127.0.0.1:5000/demo10">10</a>, <a href="http://127.0.0.1:5000/demo30">30</a>, and <a href="http://127.0.0.1:5000/demo60">60</a> inbetween frames already prepared</p>
        
        <form name="inputForm" action="http://127.0.0.1:5000/map" method = "get" onsubmit="return inputValidation()"> 
            <label for="startTime">Start Time:</label><br>
            <input type="date"  name="startDate" value ="2024-01-10" readonly>
            <input type="time" name="startTime" value = "06:00" required min = "06:00" max = "08:50"><br>

            <label for="endTime">End Time:</label><br>
            <input type="date" name="endDate" value ="2024-01-10" readonly>
            <input type="time" name="endTime" value = "07:00" required min = "06:10" max = "09:00"><br>
            Number of inbetween frames: <br>
            <input type="radio" id="0frames" name="betweenFrames" value="0" checked>
            <label for="0frames">0</label>
            <input type="radio" id="10frames" name="betweenFrames" value="10">
            <label for="10frames">10</label>
            <input type="radio" id="30frames" name="betweenFrames" value="30">
            <label for="30frames">30</label>
            <input type="radio" id="60frames" name="betweenFrames" value="60">
            <label for="60frames">60</label>
            <br><br>
            <input type="submit" value="Submit">

        </form>
    </body>
    <script>
        function inputValidation(){
            console.log("start");
            startTime = document.forms["inputForm"]["startTime"].value;
            endTime = document.forms["inputForm"]["endTime"].value;

            startArr = startTime.split(":")
            startHours = parseFloat(startArr[0]);
            startMinutes = parseFloat(startArr[1]);
            startHours += (startMinutes/60)

            endArr = endTime.split(":")
            endHours = parseFloat(endArr[0]);
            endMinutes = parseFloat(endArr[1]);
            endHours += (endMinutes/60)

            if (endHours < startHours) {
                alert("You seem to have swapped your start and end times, please try again");
                return false;
            }
            if ((endHours-startHours) > 1) {
                alert("Something went wrong with your start and end times. Please note that requested animations must have enpoints within 1 hour of each other")
                return false;
            }
            if (endHours < 6.05 || startHours > 8.9) {
                alert("These bounds could result in no animation being created. Please select a different range.")
                return false;
            }

            return true;
        }
    </script>
</html>'''
