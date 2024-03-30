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

for scan in sorted(results.iter_success(), key=lambda scan: scan.filename, reverse=False):
    if (scan.key[-3:] != "MDM"):
        print(scan.radar_id + " " + str(scan.scan_time))
        
        radar = scan.open_pyart()
        gatefilter = pyart.filters.GateFilter(radar)
        gatefilter.exclude_below('reflectivity', 0)

        ax = fig.add_subplot()
        ax.set_axis_off()
        display = pyart.graph.RadarDisplay(radar)
        display.plot('reflectivity',0,ax=ax, title_flag = False, colorbar_flag = False, axislabels_flag = False, gatefilter=gatefilter)
        display.set_limits((-300, 300), (-300, 300), ax=ax) ##probably fine with bounds around 300km
        filename = scan.filename + ".png"
        fig.savefig("C:\\Users\\audre\\OneDrive\\Desktop\\SmoothRx Capstone\\static\\cache\\" + filename, transparent=True)
        fig.clear()

        #radar.fields["reflectivity"]['data'].mask = np.ma.nomask
        for i in range(0, len(radar.fields["reflectivity"]['data'])):
                for j in range(0, len(radar.fields["reflectivity"]["data"][i])):
                     radar.fields["reflectivity"]["data"].mask[i][j] = False
                     if (radar.fields["reflectivity"]["data"].data[i][j] < -10):
                        radar.fields["reflectivity"]["data"].data[i][j] = -10
                     
                # radar.fields["reflectivity"]['mask'][i] = np.nan_to_num(radar.fields["reflectivity"]['data'][i], False, nan=-10.0)
        #        print(radar.fields["reflectivity"]['data'][i])
        
        if (prevRadar != 0) :
            
            inbetweens = 10
            ##do things
            #print("prevRadar:")
            #print(prevRadar.fields["reflectivity"]['data'])
            #rint("curRadar:")
            #np.nan_to_num(radar.fields["reflectivity"]['data'], False, nan=-10.0, posinf = 999, neginf = -999)
            #for i in range(0, len(radar.fields["reflectivity"]['data'])):
            #    radar.fields["reflectivity"]['data'][i] = np.nan_to_num(radar.fields["reflectivity"]['data'][i], False, nan=-10.0, posinf = 999, neginf = -999)
            #     for j in range(0, len(radar.fields["reflectivity"]['data'][i])):
            #         if (radar.fields["reflectivity"]['data'][i][j] == np.nan):
            #             print("found value")
            #             radar.fields["reflectivity"]['data'][i][j] = -999
            # #print(radar.fields["reflectivity"]['data'])
            dataSteps =  (radar.fields["reflectivity"]['data'] - prevRadar.fields["reflectivity"]['data'].data) / inbetweens
            #print("dataSteps:")
            print(dataSteps)
            print("_____")

            for i in range(inbetweens):
            #     print(i)
                prevRadar.fields["reflectivity"]['data'] = radar.fields["reflectivity"]['data'] - (dataSteps * i)
                for k in range(0, len(prevRadar.fields["reflectivity"]['data'])):
                    for j in range(0, len(prevRadar.fields["reflectivity"]['data'][k])):
                        if (prevRadar.fields["reflectivity"]['data'].data[k][j] < 0) :
                            prevRadar.fields["reflectivity"]['data'].mask[k][j] = True
                        else :
                             prevRadar.fields["reflectivity"]["data"].mask[k][j] = False
                        
                #gatefilter = pyart.filters.GateFilter(prevRadar)
                #gatefilter.exclude_below('reflectivity', 0)

                ax = fig.add_subplot()
                ax.set_axis_off()
                display = pyart.graph.RadarDisplay(prevRadar)
                display.plot('reflectivity',0,ax=ax, title_flag = False, colorbar_flag = False, axislabels_flag = False)
                display.set_limits((-300, 300), (-300, 300), ax=ax) ##probably fine with bounds around 300km
                filename = prevScan.filename + "-a" + str((inbetweens - i)).zfill(2) + ".png"
                fig.savefig("C:\\Users\\audre\\OneDrive\\Desktop\\SmoothRx Capstone\\static\\cache\\" + filename, transparent=True)
                fig.clear()


            
            #print(prevRadar.longitude['standard_name'] + ": " + str(prevRadar.longitude['data'][0]) + " " + prevRadar.longitude['units'])
            #print(prevRadar.latitude['standard_name'] + ": " + str(prevRadar.latitude['data'][0]) + " " + prevRadar.latitude['units'])
            # prevRadar.info()

        prevRadar = radar
        prevScan = scan
    else :
        print("not used")
print("out of loop")


print("done")


