import nexradaws
import tempfile
from datetime import datetime
import pytz
import numpy as np
import matplotlib.pyplot as plt
import pyart

temp_loc = tempfile.mkdtemp()
conn = nexradaws.NexradAwsInterface()

timezone = pytz.timezone('US/Central')
radar_ids = ['KMRX', 'KFCX', 'KGSP'] #id's for 3 towers with data most relevent to Asheville, NC
start = timezone.localize(datetime(2024, 1, 10, 0, 0, 0)) #corresponds to 6am Jan 10, 2024
end = timezone.localize(datetime(2024, 1, 10, 0, 20, 0))  #corresponds to 6pm Jan 10, 2024

for radar in radar_ids:
    scans = conn.get_avail_scans_in_range(start, end, radar)
    results = conn.download(scans, temp_loc) 
    count = 0
    for scan in results.iter_success():
        if (scan.key[-3:] != "MDM"):
            if count < 1:
                value = scan.open_pyart()
                print(scan.key)
                print(value.longitude['standard_name'] + ": " + str(value.longitude['data'][0]) + " " + value.longitude['units'])
                print(value.latitude['standard_name'] + ": " + str(value.latitude['data'][0]) + " " + value.latitude['units'])
                
                print("_______")
                count += 1