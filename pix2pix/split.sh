#!/bin/bash

DIR=$1
MODE=$2
IMAGES=`ls -1 $DIR/*_merged.png`
NUM_IMAGES=`ls $DIR/*_merged.png | wc -l`
echo $MODE $NUM_IMAGES images in $DIR
for I in $IMAGES
do
    J=`basename $I`
    if [ "$MODE" = "train"  ]
    then
        ln -s `pwd`/$I train/$J 
    else
        if [ "$MODE" = "test"  ]
        then
            ln -s `pwd`/$I test/$J
        fi
    fi
done
