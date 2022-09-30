#!/usr/bin/bash
set -e

reel_dir=$1
year=$2
state=$3

for i in {1..50}
do
    cp -R /data/storage/images/training_images/${year}/${reel_dir}/ /data/storage/images/training_images/${year}/${reel_dir}_${i}/;
    echo "/data/storage/images/training_images/${year}/${reel_dir}_${i},${year},${state}" >> /apps/django/dcdl_train/train_reel_load_spec.csv
done
