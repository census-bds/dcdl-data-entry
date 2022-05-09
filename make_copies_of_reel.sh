#!/usr/bin/bash
set -e

### CREATE COPIES OF SPECIFIED REEL FOR TRAINING

reel_dir=$1

for i in {23..42}
do
    cp -R /data/storage/images/training_images/1980/1980_Texas_3951/ /data/storage/images/training_images/1980/1980_Texas_3951_${i};
done 

