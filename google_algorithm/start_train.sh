#!/usr/bin/env bash

echo "可训练的 app 如下："
echo "  1. 知乎"
echo "  2. 今日头条"
echo "  3. 百度"
echo "  4. 新浪微博"

read -p "请选择要训练的 app (输入序号即可):  " choice
echo $choice

if [ $choice -eq 1 ]; then
    echo "知乎"
    python3 retrain.py \
    --image_dir ../training/zhihu/Android_1-50 \
     --bottleneck_dir /tmp/zhihu/bottleneck \
    --output_graph ../training/zhihu/model/android_zhihu_output_graph.pb \
    --output_labels ../training/zhihu/labels/android_zhihu_output_labels.txt
elif [ $choice -eq 2 ]; then
    echo "今日头条"
    python3 retrain.py \
    --image_dir ../training/top_today/Android_1-50 \
     --bottleneck_dir /tmp/top_today/bottleneck \
    --output_graph ../training/top_today/model/android_top_today_output_graph.pb \
    --output_labels ../training/top_today/labels/android_top_today_output_labels.txt
elif [ $choice -eq 3 ]; then
    echo "百度"
    python3 retrain.py \
    --image_dir ../training/baidu/Android_1-50 \
    --bottleneck_dir /tmp/baidu/bottleneck \
    --output_graph ../training/baidu/model/android_baidu_output_graph.pb \
    --output_labels ../training/baidu/labels/android_baidu_output_labels.txt
elif [ $choice -eq 4 ]; then
    echo "新浪微博"
    python3 retrain.py \
    --image_dir ../training/weibo/Android_1-50 \
     --bottleneck_dir /tmp/weibo/bottleneck \
    --output_graph ../training/weibo/model/android_weibo_output_graph.pb \
    --output_labels ../training/weibo/labels/android_weibo_output_labels.txt
fi



#2to3 label_image.py -n -w -o python3_7
#2to3 retrain.py -n -w -o python3_7
#pip3 install --ignore-installed --upgrade /Users/bughh/Downloads/tensorflow-1.13.1-cp37-cp37m-macosx_10_9_x86_64.whl

