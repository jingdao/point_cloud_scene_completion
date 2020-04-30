#!/bin/bash
rm results/images/*
DATASETS="mason_east pettit seb_north seb_south seb_west seb_east mason_north vl_south vl_circle vl_east cod"

for D in $DATASETS
#for D in "seb_north"
do
	python3 -u pix2pix_interp.py --mode test \
	--test_id $D \
	--input_dir interpolated_test/ --checkpoint model \
	--output_dir results
done
