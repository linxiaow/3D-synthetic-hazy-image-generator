# 3D Hazy Image Generator

haze_generator.py is a Blender script for creating large number of 3D hazy scenes with random correlated air transmittance. The 3D scenes also have associated depth information that can be used to extract depth maps. The outputs of this script are sets of 2D images taken from multiple views of the 3D images, and also include the position of cameras and labels for air transmittance that can be used for image depth neural network training, dehazing algorithm and 3D haze reconstruction.

For how the depth infomation is added, refer to this github repo: https://github.com/LouisFoucard/DepthMap_dataset

Blender is a open source 3D graphics and animation software, downloadable at "https://www.blender.org/".

## Example images

Here is some example images:

![hazy images](example_images/img_preserve/0.08/image_set_0/Camera.png =60)
