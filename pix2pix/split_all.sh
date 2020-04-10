#!/bin/bash
rm train/*
rm test/*
rm results/images/*
./split.sh ../point-cloud-orthographic-projection/01_mason_east/ train
./split.sh ../point-cloud-orthographic-projection/02_pettit/ train
./split.sh ../point-cloud-orthographic-projection/03_seb_north/ test
./split.sh ../point-cloud-orthographic-projection/04_seb_south/ test
./split.sh ../point-cloud-orthographic-projection/05_seb_west/ test
./split.sh ../point-cloud-orthographic-projection/06_seb_east/ test
./split.sh ../point-cloud-orthographic-projection/07_mason_north/ train
./split.sh ../point-cloud-orthographic-projection/08_vl_south/ train
./split.sh ../point-cloud-orthographic-projection/09_vl_circle/ train
./split.sh ../point-cloud-orthographic-projection/10_vl_east/ train
./split.sh ../point-cloud-orthographic-projection/11_cod/ train
