#!/bin/bash
DATASETS="mason_east pettit seb_north seb_south seb_west seb_east mason_north vl_south vl_circle vl_east cod"

for D in $DATASETS
#for D in "seb_north"
do
	python3 -u pix2pix.py --mode train --output_dir model \
	--test_id $D \
	--adv_loss \
	--lr 0.0002 \
	--batch_size 10 \
	--max_epochs 100 \
	--input_dir train/ \
	--which_direction AtoB 2>/dev/null
done
