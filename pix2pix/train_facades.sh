#!/bin/bash
python3 pix2pix.py --mode train --output_dir model_facades --adv_loss --lr 0.0002 --batch_size 10 --max_epochs 50 --input_dir facades/train/ --which_direction BtoA 2>/dev/null
