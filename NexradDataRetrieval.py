import nexradaws
import tempfile
from datetime import datetime
import pytz
import numpy as np
import matplotlib.pyplot as plt
import pyart
import os
import copy


temp_loc = tempfile.mkdtemp()
#must start the with the current working directory already in the desired output location
#static and cache are used by the flask controller, and must be in the same folder 
#(either set the cwd to the same directory as the flask controller or move the static directory later)
baseLocation = os.getcwd()
if ("static" in os.listdir(baseLocation) == False) :
    os.mkdir(os.path.join(baseLocation, "static"))
    os.mkdir(os.path.join(baseLocation, "static", "cache"))

cacheLocation = os.path.join(baseLocation, "static", "cache")#"C:\\Users\\audre\\OneDrive\\Desktop\\SmoothRx Capstone\\static\\cache\\"
print("cache located at " + str(cacheLocation))
#Establish a connection to nexrad's aws server
conn = nexradaws.NexradAwsInterface()
print("start")
#
timezone = pytz.timezone('US/Central')
radar_ids = ['KMRX', 'KFCX', 'KGSP'] #id's for 3 towers with data most relevent to Asheville, NC
start = timezone.localize(datetime(2024, 1, 10, 1, 50, 0)) #corresponds to 7:50am Jan 10, 2024
end = timezone.localize(datetime(2024, 1, 10, 3, 0, 0))  #corresponds to 9pm Jan 10, 2024 

#loops through each radar tower id
for radar_id in radar_ids:
    storageLoc = os.path.join(cacheLocation, radar_id)
    if ((radar_id in os.listdir(cacheLocation)) == False):
        os.mkdir(storageLoc)    #creates a directory to store each radar's data (it would be a nightmare to sort through otherwise)

    #searches for a downloads all relevent level 2 volume scans in the given time frame
    scans = conn.get_avail_scans_in_range(start, end, radar_id)
    results = conn.download(scans, temp_loc) 

    prevRadar = 0
    fig = plt.figure(figsize=(16,12))
    #loop though each scan build the radar image, and create inbetweens
    for scan in sorted(results.iter_success(), key=lambda scan: scan.filename, reverse=False):
        if (scan.key[-3:] != "MDM"):
            print(scan.radar_id + " " + str(scan.scan_time))
            
            radar = scan.open_pyart()
            #hide junk data points to create a clearer radar image
            gatefilter = pyart.filters.GateFilter(radar)
            gatefilter.exclude_below('reflectivity', 0)

            #create the actual radar figure (maps the radial data to a xy cartesian plane through pyART)
            ax = fig.add_subplot()
            ax.set_axis_off()
            display = pyart.graph.RadarDisplay(radar)
            display.plot('reflectivity',0,ax=ax, title_flag = False, colorbar_flag = False, axislabels_flag = False, gatefilter=gatefilter)
            display.set_limits((-300, 300), (-300, 300), ax=ax) ##probably fine with bounds around 300km
            filename = scan.filename + ".png"
            fig.savefig(os.path.join(storageLoc, filename), transparent=True)
            fig.clear()

            #prep's the data for creating inbetweens
            radar.fields["reflectivity"]['data'].mask = np.ma.nomask

            # for i in range(0, len(radar.fields["reflectivity"]['data'])):
            #         for j in range(0, len(radar.fields["reflectivity"]["data"][i])):
            #              radar.fields["reflectivity"]["data"].mask[i][j] = False
            #              if (radar.fields["reflectivity"]["data"].data[i][j] < -10):
            #                 radar.fields["reflectivity"]["data"].data[i][j] = -10           
                    # radar.fields["reflectivity"]['mask'][i] = np.nan_to_num(radar.fields["reflectivity"]['data'][i], False, nan=-10.0)
            #        print(radar.fields["reflectivity"]['data'][i])
            
            #begins's creating inbetweens once at least 2 data points are processed and ready
            if (prevRadar != 0) :
                #inbetween images are stored in a seperate location from real scan images 
                betweenStorage = os.path.join(storageLoc, (prevScan.filename + "-i"))
                #print(os.listdir(storageLoc))
                if (((prevScan.filename + "-i") in os.listdir(storageLoc)) == False):
                    #print("condition met")
                    os.mkdir(betweenStorage)
                
                inbetweens = 60 #maximum number of inbetween frames a user can later request. 

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
                dataSteps = prevRadar.fields["reflectivity"]['data'].data

                #print(radar.fields["reflectivity"]['data'].data.shape)
                #print(prevRadar.fields["reflectivity"]['data'].data.shape)

                #print(radar.fields["reflectivity"]['data'].data.size)
                #print(prevRadar.fields["reflectivity"]['data'].data.size)


                #reflectivity is stored in numpy arrays
                #if they are not compatbile shapes (the same number of total entries) they must be modified to perform calculations (this might cause additional inconsistencies in output)
                curRadar = copy.deepcopy(radar) #the current radar must be copied, so the changes made here will not interfere with future loop iterations
                if curRadar.fields["reflectivity"]['data'].data.shape[0] > prevRadar.fields["reflectivity"]['data'].data.shape[0]:
                    #determine the invalid dimension and buff it up
                    filler = [[0] * prevRadar.fields["reflectivity"]['data'].data.shape[1]] * (curRadar.fields["reflectivity"]['data'].data.shape[0] - prevRadar.fields["reflectivity"]['data'].data.shape[0])
                    filler = np.array(filler)
                    #filler.reshape(1, prevRadar.fields["reflectivity"]['data'].data.shape[1])
                    prevRadar.fields["reflectivity"]['data'] = np.concatenate((prevRadar.fields["reflectivity"]['data'], filler), axis=0)
                    #print(prevRadar.fields["reflectivity"]['data'].data.shape)
                elif curRadar.fields["reflectivity"]['data'].data.shape[0] < prevRadar.fields["reflectivity"]['data'].data.shape[0]:
                    #determine the invalid dimension and buff it up
                    filler = [[0] * prevRadar.fields["reflectivity"]['data'].data.shape[1]] * (prevRadar.fields["reflectivity"]['data'].data.shape[0] - curRadar.fields["reflectivity"]['data'].data.shape[0])
                    filler = np.array(filler)
                    #filler.reshape(1, prevRadar.fields["reflectivity"]['data'].data.shape[1])
                    #print(filler.shape)
                    curRadar.fields["reflectivity"]['data'] = np.concatenate((curRadar.fields["reflectivity"]['data'], filler), axis=0)
                    #print(curRadar.fields["reflectivity"]['data'].data.shape)

                #curRadar.fields["reflectivity"]['data'].data = np.concatenate(
                #    ([[0]] * abs(radar.fields["reflectivity"]['data'].data.size - prevRadar.fields["reflectivity"]['data'].data.size)),
                #    curRadar.fields["reflectivity"]['data'].data)
                #if radar.fields["reflectivity"]['data'].data.size == prevRadar.fields["reflectivity"]['data'].data.size:
                #    print(scan.filename + " used")

                #once data has been fully preped, let numpy calculate the change per frame for each value (this is why data masks had to be removed earlier)
                dataSteps =  (curRadar.fields["reflectivity"]['data'].data - prevRadar.fields["reflectivity"]['data'].data) / inbetweens
                #else:
                #    flag = False
                #print("dataSteps:")
                #print(dataSteps)
                #print("_____")

                #actually begin creating inbetweens
                for i in range(inbetweens):
                #     print(i)
                    
                    prevRadar.fields["reflectivity"]['data'].mask = np.ma.nomask #reset the numpy mask
                    prevRadar.fields["reflectivity"]['data'] = prevRadar.fields["reflectivity"]['data'] + (dataSteps) #perform calc
                    
                    #rebuild the mask filtering out any extraneous data points that should not be displayed in radar (reflectivity < 0)
                    mask = [[False]] * len(prevRadar.fields["reflectivity"]['data'])
                    for k in range(0, len(prevRadar.fields["reflectivity"]['data'])):
                        mask[k] = [False] * len(prevRadar.fields["reflectivity"]['data'][k])
                        for j in range(0, len(prevRadar.fields["reflectivity"]['data'][k])):
                            if (prevRadar.fields["reflectivity"]['data'].data[k][j] < 0) :
                                mask[k][j] = True
                            else :
                                mask[k][j] = False
                            
                    prevRadar.fields["reflectivity"]['data'].mask = mask
                    #gatefilter = pyart.filters.GateFilter(prevRadar)
                    #gatefilter.exclude_below('reflectivity', 0)

                    #create and save the actual image
                    ax = fig.add_subplot()
                    ax.set_axis_off()
                    display = pyart.graph.RadarDisplay(prevRadar)
                    display.plot('reflectivity',0,ax=ax, title_flag = False, colorbar_flag = False, axislabels_flag = False)
                    display.set_limits((-300, 300), (-300, 300), ax=ax) ##probably fine with bounds around 300km
                    filename = prevScan.filename + "-a" + str((inbetweens - i)).zfill(2) + ".png"
                    fig.savefig(os.path.join(betweenStorage, filename), transparent=True)
                    fig.clear()


                
                #print(prevRadar.longitude['standard_name'] + ": " + str(prevRadar.longitude['data'][0]) + " " + prevRadar.longitude['units'])
                #print(prevRadar.latitude['standard_name'] + ": " + str(prevRadar.latitude['data'][0]) + " " + prevRadar.latitude['units'])
                # prevRadar.info()

            #save the current radar and scan for used in the next round of inbetween calculations
            prevRadar = radar
            prevScan = scan
        else :
            print("not used")
    print(radar_id +" done")
print("done")


