#!/bin/bash

TEST_SET="01_mason_east 02_pettit 03_seb_north 04_seb_south 05_seb_west 06_seb_east 07_mason_north 08_vl_south 09_vl_circle 10_vl_east 11_cod"

for T in $TEST_SET
do
    echo $T
    FILLED=$T/"$T"_input_filled.png
    cp ../pix2pix/results/images/"$T"_input_merged-outputs.png $FILLED
    python point_cloud_ortho_projector.py $FILLED
done

#for T in $TEST_SET
#do
#    echo $T
#    GT=$T/"$T"_gt.ply
#    INPUT=$T/"$T"_input.ply
#    OUTPUT=$T/"$T"_input_output.ply
#    ../get_accuracy $GT $INPUT
#    ../get_accuracy $GT $OUTPUT
#done
