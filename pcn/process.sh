#!/bin/bash

TEST_SET="01_mason_east 02_pettit 03_seb_north 04_seb_south 05_seb_west 06_seb_east 07_mason_north 08_vl_south 09_vl_circle 10_vl_east 11_cod"
for T in $TEST_SET
do
    python3 demo.py --input_path ~/Desktop/point_cloud_scene_completion/input/"$T"_input.ply --output_path tmp/"$T".ply 2>stderr
    python fix_color.py ~/Desktop/point_cloud_scene_completion/input/"$T"_input.ply tmp/"$T".ply tmp_fix/"$T".ply
done
