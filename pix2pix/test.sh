#!/bin/bash
rm results/images/*
python3 -u pix2pix.py --mode test \
--input_dir test/ --checkpoint model \
--output_dir results 2>/dev/null
