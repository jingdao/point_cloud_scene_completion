# Point Cloud Scene Completion

Supplemental material for the **Sensors** journal paper
*Point Cloud Scene Completion of Obstructed Building Facades with Generative Adversarial Inpainting*.
The paper can be accessed through the following [link](https://www.mdpi.com/1424-8220/20/18/5029/htm).
If you find this code or data useful, please cite our paper as follows:

```
Chen, J., Yi, J., Kahoush, M., Cho, E. and Cho, Y. (2020). “Point Cloud Scene Completion
of Obstructed Building Facades with Generative Adversarial Inpainting.” MDPI Sensors, 20(18), 5029
```

```
@Article{s20185029,
AUTHOR = {Chen, Jingdao and Yi, John Seon Keun and Kahoush, Mark and Cho, Erin S. and Cho, Yong K.},
TITLE = {Point Cloud Scene Completion of Obstructed Building Facades with Generative Adversarial Inpainting},
JOURNAL = {Sensors},
VOLUME = {20},
YEAR = {2020},
NUMBER = {18},
ARTICLE-NUMBER = {5029},
URL = {https://www.mdpi.com/1424-8220/20/18/5029},
ISSN = {1424-8220},
DOI = {10.3390/s20185029}
}
```

## Data preparation

Ground truth and input files:
[input/groundtruth](https://www.dropbox.com/s/kef3ouplemqy0co/input%20and%20ground%20truth.zip?dl=0)

After unzipping the file there will be an input folder containing all the input files, and a ground truth folder containing all the ground truth files. These files are point clouds stored as PLY files. 

## Dependencies
Training is implemented with [TensorFlow](https://www.tensorflow.org/). This code has been tested under TF1.3 on Ubuntu 18.04.

## Baselines
### Hole-filling
To execute the hole filling algorithm:
```
python fill_holes.py input_file.ply
```

### Poisson Reconstruction
To use Poisson Reconstruction download [CloudCompare](https://github.com/cloudcompare/cloudcompare).

Using CloudCompare open the input file and compute its normals.
Use the "poisson recon" plugin to obtain a mesh representation of the input file after poisson reconstruction.
Adjust the SF display parameters range in the properties of the mesh.
Filter the mesh to split the mesh into two, based on the range chosen.
Convert the mesh back into a point cloud by using the sample points tool.

### Plane-fitting
To execute the plane fitting algorithm:
```
python fit_plane_LSE.py input_file.ply
```

### Partial Convolutions

1. Run the Python file `point_cloud_ortho_projector.py` to generate a RGB image and a depth image for the input point cloud file.
2. Use the Python file `fit_image.py` to resize the RGB image to 512x512 pixels.
3. Upload the RGB image at this [site](https://www.nvidia.com/research/inpainting/).
4. Manually draw the mask and perform inpainting.
5. Download the resulting image and resize it back to the original size using the Python file `recover_image.py`.
6. Run the Python file `point_cloud_ortho_projector.py` again to generate a PLY point cloud from the filled RGB image and the previously saved depth image.

### PCN/FoldingNet/TopNet

Refer to [this](https://github.com/jingdao/completion3d) fork of the Completion3D baselines for
instructions on training and testing PCN/FoldingNet/TopNet with our dataset.

## Generative Adversarial Inpainting

Our proposed method for Generative Adversarial Inpainting is built on top of the Pix2Pix network.
Follow the steps below:

1. Create the "train" and "test" subfolders in the "pix2pix" folder by downloading the following image files from Dropbox:
[train](https://www.dropbox.com/s/iv3kgdvihxpz521/train.zip?dl=0) [test](https://www.dropbox.com/s/v07vi2kyu5j1yj9/test.zip?dl=0)
2. Run the training script `pix2pix/train.sh`. Once done, it should save 11 models in total to the "model" folder
3. Run the script `point-cloud-orthographic-projection/prepare_pix2pix_data.sh`. The script will call the Python file `point_cloud_ortho_projector.py` to generate a RGB image and a depth image for each input point cloud file.
Note that the Python file uses Python 2 and the dependencies need to be installed.
4. Run the testing script `pix2pix/test.sh`. This step will apply the trained Pix2Pix models on input RGB images and output filled RGB images.
5. Run the script `point-cloud-orthographic-projection/get_pix2pix_results.sh`. The script will run the Python file `point_cloud_ortho_projector.py` again to generate PLY point clouds from the filled RGB images.

## Evaluation
You can evaluate your results by running:
```
python getAccuracy.py ground_truth.ply input.ply 
```
This will display the evaluation metrics.

## Results

![results](results/inpainting_result.png?raw=true)

## Third-party Code

Wei, J. (2019) "Point Cloud Orthographic Projection with Multiviews" Available [online](https://github.com/jiangwei221/point-cloud-orthographic-projection)

Geodan (2020). "Generate Synthetic Points to Fill Holes in Point Clouds" Available [online](https://github.com/Geodan/fill-holes-pointcloud)

CloudCompare (2020) "CloudCompare" Available [online](https://github.com/CloudCompare/CloudCompare.git)

Isola et al. (2017) "Image-to-Image Translation with Conditional Adveresarial Networks" Available [online](https://github.com/affinelayer/pix2pix-tensorflow.git)

Tchapmi et al. (2019). "Stanford 3D Object Point Cloud Completion Benchmark" Available [online](https://github.com/lynetcha/completion3d)
