import nexradaws
import tempfile
from datetime import datetime
import pytz
import numpy as np
import matplotlib.pyplot as plt
import pyart


temp_loc = tempfile.mkdtemp()

conn = nexradaws.NexradAwsInterface()
print("start")

timezone = pytz.timezone('US/Central')
radar_id = 'KGSP'
start = timezone.localize(datetime(2024, 1, 10, 0, 0, 0))
end = timezone.localize(datetime(2024, 1, 10, 1, 0, 0))
scans = conn.get_avail_scans_in_range(start, end, radar_id)

results = conn.download(scans, temp_loc)

prevRadar = 0
fig = plt.figure(figsize=(16,12))

for scan in sorted(results.iter_success(), key=lambda scan: scan.filename, reverse=True):
    if (scan.key[-3:] != "MDM"):
        print(scan.radar_id + " " + str(scan.scan_time))
        
        radar = scan.open_pyart()

        ax = fig.add_subplot()
        ax.set_axis_off()
        display = pyart.graph.RadarDisplay(radar)
        display.plot('reflectivity',0,ax=ax, title_flag = False, colorbar_flag = False, axislabels_flag = False)
        display.set_limits((-300, 300), (-300, 300), ax=ax) ##probably fine with bounds around 300km
        filename = scan.filename + ".png"
        fig.savefig("C:\\Users\\audre\\OneDrive\\Desktop\\SmoothRx Capstone\\static\\cache\\" + filename, transparent=True)
        fig.clear()

        if (prevRadar != 0) :
            ##do things
            #print("prevRadar:")
            #print(prevRadar.fields["reflectivity"]['data'])
            #rint("curRadar:")
            #print(radar.fields["reflectivity"]['data'])
            dataSteps =  (prevRadar.fields["reflectivity"]['data'] - radar.fields["reflectivity"]['data']) / 10
            #print("dataSteps:")
            #print(dataSteps)
            print("_____")

            for i in range(10):
                print(i)
                prevRadar.fields["reflectivity"]['data'] = radar.fields["reflectivity"]['data'] + dataSteps

                ax = fig.add_subplot()
                ax.set_axis_off()
                display = pyart.graph.RadarDisplay(prevRadar)
                display.plot('reflectivity',0,ax=ax, title_flag = False, colorbar_flag = False, axislabels_flag = False)
                display.set_limits((-300, 300), (-300, 300), ax=ax) ##probably fine with bounds around 300km
                filename = scan.filename + "-a" + str(i) + ".png"
                fig.savefig("C:\\Users\\audre\\OneDrive\\Desktop\\SmoothRx Capstone\\static\\cache\\" + filename, transparent=True)
                fig.clear()


            
            #print(prevRadar.longitude['standard_name'] + ": " + str(prevRadar.longitude['data'][0]) + " " + prevRadar.longitude['units'])
            #print(prevRadar.latitude['standard_name'] + ": " + str(prevRadar.latitude['data'][0]) + " " + prevRadar.latitude['units'])
            # prevRadar.info()

        prevRadar = radar
    else :
        print("not used")
print("out of loop")


print("done")


