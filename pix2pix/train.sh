#!/bin/bash
python3 pix2pix.py --mode train --output_dir model --lr 0.0002 --batch_size 1 --max_epochs 10 --input_dir train/ --which_direction AtoB
