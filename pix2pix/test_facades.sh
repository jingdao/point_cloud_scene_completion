#!/bin/bash
rm results/images/*
python3 pix2pix.py --mode test --output_dir results --input_dir facades/test/ --checkpoint model_facades 2>/dev/null
