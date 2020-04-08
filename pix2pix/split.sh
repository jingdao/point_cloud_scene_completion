#!/bin/bash

DIRNAME=$1
NUM_IMAGES=`ls $DIRNAME/*_merged.png | wc -l`
let NUM_TRAIN=NUM_IMAGES/4*3
echo $NUM_TRAIN train from $NUM_IMAGES images in $DIRNAME
IMAGES=`ls $DIRNAME/*_merged.png | shuf`
n=0
for I in $IMAGES
do
    J=`basename $I`
    if (( n < $NUM_TRAIN))
    then
        ln -s `pwd`/$I train/$J 
    else
        ln -s `pwd`/$I test/$J
    fi
    ((n++))
done
