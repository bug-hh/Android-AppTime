# Copyright 2017 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

import argparse

import numpy as np
import tensorflow as tf
import os

from app_config.config import ABOUT_TRAINING
from app_config.config import ANDROID_ZHIHU_MODEL_NAME
from app_config.config import ANDROID_WEIBO_MODEL_NAME
from app_config.config import ANDROID_TOP_TODAY_MODEL_NAME
from app_config.config import ANDROID_BAIDU_MODEL_NAME

class Classifier(object):
    def __init__(self, model_code):
        if model_code == 1:
            self.model_dir = "zhihu"
            self.model_name = ANDROID_ZHIHU_MODEL_NAME
            self.labels = ['ad', 'end', 'loading', 'logo', 'start', 'words']
        elif model_code == 2:
            self.model_dir = "weibo"
            self.model_name = ANDROID_WEIBO_MODEL_NAME
            self.labels = ['ad', 'end', 'loading', 'logo', 'start']
        elif model_code == 3:
            self.model_dir = "top_today"
            self.model_name = ANDROID_TOP_TODAY_MODEL_NAME
            self.labels = ['ad', 'end', 'loading', 'logo', 'start']
        elif model_code == 4:
            self.model_dir = "baidu"
            self.model_name = ANDROID_BAIDU_MODEL_NAME
            self.labels = ['ad', 'end', 'loading', 'logo', 'start']

        model_file = os.path.join(ABOUT_TRAINING, self.model_dir, 'model', self.model_name)
        self.graph = load_graph(model_file)

    def identify_pic(self, file_name):
        # TODO 放到一个单独的 config 文件中
        input_height = 299
        input_width = 299
        input_mean = 0
        input_std = 255
        input_layer = "Placeholder"
        output_layer = "final_result"

        # graph = load_graph(model_file)
        t = read_tensor_from_image_file(
            file_name,
            input_height=input_height,
            input_width=input_width,
            input_mean=input_mean,
            input_std=input_std)

        input_name = "import/" + input_layer
        output_name = "import/" + output_layer
        input_operation = self.graph.get_operation_by_name(input_name)
        output_operation = self.graph.get_operation_by_name(output_name)

        with tf.Session(graph=self.graph) as sess:
            results = sess.run(output_operation.outputs[0], {
                input_operation.outputs[0]: t
            })
        results = np.squeeze(results)

        top_k = results.argsort()[-5:][::-1]
        # labels 顺序要与 output_labels.txt 文件一致，不然识别结果会不准确
        # todo 分 app 写 labels
        # labels = ['ad', 'end', 'loading', 'newlogo', 'oldlogo', 'start', 'words']
        # labels = ['end', 'loading', 'logo', 'start']
        check_dic = {}
        for i in top_k:
            # print(labels[i], results[i])
            check_dic[self.labels[i]] = results[i]
        sorted_dic = sorted(check_dic.items(), key=lambda kv: kv[1], reverse=True)

        return sorted_dic[0]

def load_graph(model_file):
    graph = tf.Graph()
    graph_def = tf.GraphDef()

    with open(model_file, "rb") as f:
        graph_def.ParseFromString(f.read())
    with graph.as_default():
        tf.import_graph_def(graph_def)

    return graph


def read_tensor_from_image_file(file_name,
                                input_height=299,
                                input_width=299,
                                input_mean=0,
                                input_std=255):
    input_name = "file_reader"
    output_name = "normalized"
    file_reader = tf.read_file(file_name, input_name)
    if file_name.endswith(".png"):
        image_reader = tf.image.decode_png(
            file_reader, channels=3, name="png_reader")
    elif file_name.endswith(".gif"):
        image_reader = tf.squeeze(
            tf.image.decode_gif(file_reader, name="gif_reader"))
    elif file_name.endswith(".bmp"):
        image_reader = tf.image.decode_bmp(file_reader, name="bmp_reader")
    else:
        image_reader = tf.image.decode_jpeg(
            file_reader, channels=3, name="jpeg_reader")
    float_caster = tf.cast(image_reader, tf.float32)
    dims_expander = tf.expand_dims(float_caster, 0)
    resized = tf.image.resize_bilinear(dims_expander, [input_height, input_width])
    normalized = tf.divide(tf.subtract(resized, [input_mean]), [input_std])
    sess = tf.compat.v1.Session()
    result = sess.run(normalized)

    return result


def load_labels(label_file):
    label = []
    proto_as_ascii_lines = tf.gfile.GFile(label_file).readlines()
    for l in proto_as_ascii_lines:
        label.append(l.rstrip())
    return label


if __name__ == "__main__":
    file_name = "tensorflow/examples/label_image/data/grace_hopper.jpg"
    model_file = \
        "tensorflow/examples/label_image/data/inception_v3_2016_08_28_frozen.pb"
    label_file = "tensorflow/examples/label_image/data/imagenet_slim_labels.txt"
    input_height = 299
    input_width = 299
    input_mean = 0
    input_std = 255
    input_layer = "input"
    output_layer = "InceptionV3/Predictions/Reshape_1"

    parser = argparse.ArgumentParser()
    parser.add_argument("--image", help="image to be processed")
    parser.add_argument("--graph", help="graph/model to be executed")
    parser.add_argument("--labels", help="name of file containing labels")
    parser.add_argument("--input_height", type=int, help="input height")
    parser.add_argument("--input_width", type=int, help="input width")
    parser.add_argument("--input_mean", type=int, help="input mean")
    parser.add_argument("--input_std", type=int, help="input std")
    parser.add_argument("--input_layer", help="name of input layer")
    parser.add_argument("--output_layer", help="name of output layer")
    args = parser.parse_args()

    if args.graph:
        model_file = args.graph
    if args.image:
        file_name = args.image
    if args.labels:
        label_file = args.labels
    if args.input_height:
        input_height = args.input_height
    if args.input_width:
        input_width = args.input_width
    if args.input_mean:
        input_mean = args.input_mean
    if args.input_std:
        input_std = args.input_std
    if args.input_layer:
        input_layer = args.input_layer
    if args.output_layer:
        output_layer = args.output_layer

    graph = load_graph(model_file)
    t = read_tensor_from_image_file(
        file_name,
        input_height=input_height,
        input_width=input_width,
        input_mean=input_mean,
        input_std=input_std)

    input_name = "import/" + input_layer
    output_name = "import/" + output_layer
    input_operation = graph.get_operation_by_name(input_name)
    output_operation = graph.get_operation_by_name(output_name)

    with tf.compat.v1.Session(graph=graph) as sess:
        results = sess.run(output_operation.outputs[0], {
            input_operation.outputs[0]: t
        })
    results = np.squeeze(results)

    top_k = results.argsort()[-5:][::-1]
    labels = load_labels(label_file)
    for i in top_k:
        print(labels[i], results[i])


