#!/bin/bash
rm results/images/*
python3 pix2pix.py --mode test --output_dir results --input_dir test/ --checkpoint model 2>/dev/null
