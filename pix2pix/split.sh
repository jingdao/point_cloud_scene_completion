#!/bin/bash

rm train/*.png
rm test/*.png
NUM_IMAGES=0
IMAGES=""
#for D in "$@"
for D in ../point-cloud-orthographic-projection/0* ../point-cloud-orthographic-projection/1*
do
    MERGED=`ls -1 $D/*_merged.png`
    for M in $MERGED
    do
        IMAGES="$IMAGES"$M"\n"
        ((NUM_IMAGES++))
    done
done

let NUM_TRAIN=NUM_IMAGES/4*3
echo $NUM_TRAIN train from $NUM_IMAGES images in $# dirs...
IMAGES=`echo -e $IMAGES | shuf`
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
