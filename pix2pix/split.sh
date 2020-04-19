#!/bin/bash

rm train/*
rm test/*
rm results/images/*
DATASETS="01_mason_east 02_pettit 03_seb_north 04_seb_south 05_seb_west 06_seb_east 07_mason_north 08_vl_south 09_vl_circle 10_vl_east 11_cod"

for DIR in $DATASETS
do
    IMAGES=`ls -1 ../point-cloud-orthographic-projection/$DIR/*_merged.png`
    NUM_IMAGES=`ls ../point-cloud-orthographic-projection/$DIR/*_merged.png | wc -l`
    echo $MODE $NUM_IMAGES images in $DIR
    for I in $IMAGES
    do
        J=`basename $I`
        if [[ $J = $DIR* ]]
        then
            ln -s `pwd`/$I test/$J
        else
            ln -s `pwd`/$I train/$J
        fi
    done
done
