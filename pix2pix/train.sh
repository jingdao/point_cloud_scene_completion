#!/bin/bash
python3 pix2pix.py --mode train --output_dir model --adv_loss --lr 0.0002 --batch_size 10 --max_epochs 100 --input_dir train/ --which_direction AtoB 2>/dev/null
