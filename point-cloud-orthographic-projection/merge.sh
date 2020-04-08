#!/bin/sh

DIRNAME=$1
GT=`ls $DIRNAME | grep gt_rgb256.png`
#echo $DIRNAME
#echo $GT

for IMG in $DIRNAME/*_rgb256.png
do
    if [ "$IMG" != "$DIRNAME/$GT" ]
    then
        OUT=`echo $IMG | sed 's/rgb256/merged/'`
        echo convert +append $IMG $DIRNAME/$GT $OUT
        convert +append $IMG $DIRNAME/$GT $OUT
    fi
done
