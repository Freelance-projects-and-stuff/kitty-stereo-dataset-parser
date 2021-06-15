import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.animation as animation
import numpy as np
from source.parser import DataParser

# Change this to the directory where you store KITTI data
basedir = './data/'

# Specify the dataset to load
date = '2011_09_26'
drive = '0001'

parser = DataParser(basedir, date, drive)

################################################################################
################################################################################

image_idx = 10

depth_map = parser.get_ground_truth(image_idx)
left_RGB = parser.get_left_RGB(image_idx) # left RGB image
right_RGB = parser.get_right_RGB(image_idx) # right RGB image
velocity = parser.get_velocity(image_idx)
stereo_depth_map = parser.get_stereo_map(image_idx)
print(f"velocity:  {velocity}")

f, ax = plt.subplots(2, 2, figsize=(15, 5))
ax[0, 0].imshow(stereo_depth_map, cmap='viridis')
ax[0, 0].set_title('Stereo depth map')

ax[0, 1].imshow(depth_map)
ax[0, 1].set_title('Ground_truth')

ax[1, 0].imshow(left_RGB)
ax[1, 0].set_title('Left RGB Image (cam2)')

ax[1, 1].imshow(right_RGB)
ax[1, 1].set_title('Right RGB Image (cam3)')

plt.show()

################################################################################
################################################################################

def video(images_video, name="movie.mp4"):
    frames = [] # for storing the generated images
    fig = plt.figure()
    for i in range(len(images_video)):
        frames.append([plt.imshow(images_video[i], cmap="viridis", animated=True)])

    ani = animation.ArtistAnimation(fig, frames, interval=50, blit=True,
                                    repeat_delay=1000)
    writervideo = animation.FFMpegWriter(fps=10)
    plt.show()

images_GT = []
images_stereo = []
for image_idx in range(len(parser)):
    # left_RGB = parser.get_left_RGB(image_idx) # left RGB image
    # right_RGB = parser.get_right_RGB(image_idx) # right RGB image
    # velocity = parser.get_velocity(image_idx)
    # print(f"velocity:  {velocity}")
    depth_map = parser.get_ground_truth(image_idx)
    stereo_depth_map = parser.get_stereo_map(image_idx)


    # f, ax = plt.subplots(2, 2, figsize=(15, 5))
    # ax[0, 0].imshow(stereo_depth_map, cmap='viridis')
    # ax[0, 0].set_title('Stereo depth map')

    # ax[0, 1].imshow(depth_map)
    # ax[0, 1].set_title('Ground_truth')

    # ax[1, 0].imshow(left_RGB)
    # ax[1, 0].set_title('Left RGB Image (cam2)')

    # ax[1, 1].imshow(right_RGB)
    # ax[1, 1].set_title('Right RGB Image (cam3)')

    # plt.show()

    images_stereo.append(stereo_depth_map)
    images_GT.append(depth_map)

video(images_stereo, "stereo.avi")
video(images_GT, "GT.avi")

