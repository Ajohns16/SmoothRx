import os;
import glob;
from PIL import Image;
import contextlib;
#import imageio;




staticLocation = "C:\\Users\\audre\\OneDrive\\Desktop\\SmoothRx Capstone\\static"
cachelocation = "C:\\Users\\audre\\OneDrive\\Desktop\\SmoothRx Capstone\\static\\cache"
towers = os.listdir(cachelocation)
inbetweens = 60
startTime = "20240110_060000"
endTime =   "20240110_070000"
#TODO
#extract the realtime duration of the request and set a base animation duration, to better sync up animations between towers

for tower in towers:
    print(tower)
    towerlocation = os.path.join(cachelocation, tower)
    firstImage = tower + startTime + "_V06.png"
    lastImageRequest = tower + endTime + "_V06.png"
    files = os.listdir(towerlocation)
    files.sort()
    files = list(filter(lambda f: '.png' in f and f > firstImage and f < lastImageRequest, files))
    #print(files)

    gifname = tower + files[0][4:-8] + "__" + files[-1][4:-8] + "(" + str(inbetweens) + ")" + ".gif"
    #writer = imageio.get_writer(os.path.join(staticLocation, gifname), fps=max(inbetweens, 1) )

    images = []
    for f in files:
        #print(f)
        #images.append(imageio.imopen(os.path.join(towerlocation, f), 'r'))
        #writer.append_data(imageio.imread((os.path.join(towerlocation, f))))
        images.append(Image.open(os.path.join(towerlocation, f)))
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
    frame_one = images[0]
    frameDuration = 1000/(max(inbetweens, 1))
   
    
    
    #imageio.mimwrite(os.path.join(staticLocation, gifname), images, format="FFMPEG", fps=inbetweens)
    
    #print("frameDuration: " + str(frameDuration))
    frame_one.save(os.path.join(staticLocation, gifname), format="GIF", append_images=images,
                save_all=True, disposal=2, duration=frameDuration, loop = 0)

