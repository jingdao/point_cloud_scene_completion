#!/bin/bash

#for GT in point-cloud-orthographic-projection/input_and_ground_truth/03_seb_north_gt.ply
for GT in point-cloud-orthographic-projection/input_and_ground_truth/*_gt.ply
do
    B=`basename $GT`
    echo $B
    INPUT=point-cloud-orthographic-projection/input_and_ground_truth/`echo $B | sed 's/gt.ply/input.ply/'`
    HOLE_FILLING=baselines/Hole_filling/`echo $B | sed 's/gt.ply/input_hole_filled.ply/'`
    MESHING=baselines/Mesh/`echo $B | sed 's/gt.ply/input_mesh.ply/'`
    ./get_accuracy $GT $INPUT
    ./get_accuracy $GT $HOLE_FILLING
    ./get_accuracy $GT $MESHING
#    python get_accuracy.py $GT $HOLE_FILLING
#    python get_accuracy.py $GT $MESHING
done

