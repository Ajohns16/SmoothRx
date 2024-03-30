import os;
import glob;
from PIL import Image;
import contextlib;



files = os.listdir("C:\\Users\\audre\\OneDrive\\Desktop\\SmoothRx Capstone\\static\\cache")
firstImage = "KGSP20240110_060800_V06.png"
lastImageRequest = "KGSP20240110_063000_V06.png"
# files.sort()
files = filter(lambda f: '.png' in f and f > firstImage and f < lastImageRequest, files)
print(files)
images = []
for f in files:
    images.append(Image.open("C:\\Users\\audre\\OneDrive\\Desktop\\SmoothRx Capstone\\static\\cache\\" +f))
frame_one = images[0]
frame_one.save("C:\\Users\\audre\\OneDrive\\Desktop\\SmoothRx Capstone\\static\\demo.gif", format="GIF", append_images=images,
               save_all=True, disposal=2, duration=100, loop=0)

