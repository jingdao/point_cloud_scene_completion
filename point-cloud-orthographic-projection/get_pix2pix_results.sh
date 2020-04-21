#!/bin/bash

TEST_SET="01_mason_east 02_pettit 03_seb_north 04_seb_south 05_seb_west 06_seb_east 07_mason_north 08_vl_south 09_vl_circle 10_vl_east 11_cod"
S=""
for T in $TEST_SET
do
	S="$S $T"
done
python3 ../fit_image_pix2pix.py 0 $S

for T in $TEST_SET
do
    python point_cloud_ortho_projector.py "$T"
done

for T in $TEST_SET
do
    echo $T
    ../get_accuracy ../input/"$T"_gt.ply "$T"_output.ply
done
