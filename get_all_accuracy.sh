#!/bin/bash

#for GT in point-cloud-orthographic-projection/input_and_ground_truth/03_seb_north_gt.ply
for GT in point-cloud-orthographic-projection/input_and_ground_truth/*_gt.ply
do
    B=`basename $GT`
	T=`echo $B | sed 's/_gt.ply//'`
    echo $T
    INPUT=point-cloud-orthographic-projection/input_and_ground_truth/`echo $B | sed 's/gt.ply/input.ply/'`
    INPAINT=point-cloud-orthographic-projection/$T/"$T"_input_output.ply
    HOLE_FILLING=baselines/Hole_filling/`echo $B | sed 's/gt.ply/input_hole_filled.ply/'`
    MESHING=baselines/Mesh/`echo $B | sed 's/gt.ply/input_mesh.ply/'`
    PLANE_FITTING=baselines/plane_fitting/`echo $B | sed 's/gt.ply/plane_fitted.ply/'`
    ./get_accuracy $GT $INPUT
    ./get_accuracy $GT $HOLE_FILLING
    ./get_accuracy $GT $MESHING
    ./get_accuracy $GT $PLANE_FITTING
    ./get_accuracy $GT $INPAINT
#    python get_accuracy.py $GT $HOLE_FILLING
#    python get_accuracy.py $GT $MESHING
done

