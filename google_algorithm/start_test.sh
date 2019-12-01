#!/usr/bin/env bash

python3 label_image.py \
    --graph=../training/top_today/model/android_top_today_output_graph.pb \
    --labels=../training/top_today/labels/android_top_today_output_labels.txt \
    --input_layer=Placeholder \
    --output_layer=final_result \
    --image=../training/top_today/test/ad/test-ad-1.jpg