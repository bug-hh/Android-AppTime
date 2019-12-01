# -*- coding: utf-8 -*-
import os

ZHIHU_PACKAGE_NAME = 'com.zhihu.android'
ZHIHU_ACTIVITY_PATH = '.app.ui.activity.LauncherActivity'

WEIBO_PACKAGE_NAME = 'com.sina.weibo'
WEIBO_ACTIVITY_PATH = '.SplashActivity'

TOP_TODAY_PACKAGE_NAME = 'com.ss.android.article.news'
TOP_TODAY_ACTIVITY_PATH = '.activity.SplashBadgeActivity'

BAIDU_PACKAGE_NAME = 'com.baidu.searchbox'
BAIDU_ACTIVITY_PATH = '.SplashActivity'


ROOT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))

APK_PATH = os.path.join(ROOT_PATH, 'apk', 'zhihu_v6_4_0.apk')

# 实时截图文件夹
TMP_IMG_ZHIHU_DIR = os.path.join(ROOT_PATH, 'capture', 'tmp_pic_zhihu')
TMP_IMG_WEIBO_DIR = os.path.join(ROOT_PATH, 'capture', 'tmp_pic_weibo')
TMP_IMG_TOP_TODAY_DIR = os.path.join(ROOT_PATH, 'capture', 'tmp_pic_top_today')
TMP_IMG_BAIDU_DIR = os.path.join(ROOT_PATH, 'capture', 'tmp_pic_baidu')

# 将每个阶段映射成一个数字
ZHIHU_SORTED_STAGE = {'start':1, 'logo':2, 'ad': 3, 'loading':4, 'words': 5, 'end':6}
BAIDU_SORTED_STAGE = {'start': 1, 'logo': 2, 'ad': 3, 'loading': 4, 'end': 5}
TOP_TODAY_SORTED_STAGE = {'start': 1, 'logo': 2, 'ad': 3, 'loading': 4, 'end': 5}
WEIBO_SORTED_STAGE = {'start': 1, 'logo': 2, 'ad': 3, 'loading': 4, 'end': 5}

# 通过「words」的 upperbound 算 「end」
# 通过「logo」的 upperbound 找 「loading」
# 现在 启动时长 = (loading || words || end) - start
# 被减数其实可以看成是 logo 的upperbound 后的第一张不是 logo 的画面
# 对于中高端机型来说，「logo」与「loading」可能同时存在于同一张画面中，所以先找到logo阶段的 upperbound，再向后找到第一张不是 logo 阶段的图
EXCLUDED_LIST = ['start', 'loading', 'ad', 'words', 'end']

ABOUT_TRAINING = os.path.join(ROOT_PATH, 'training')

# model
ANDROID_ZHIHU_MODEL_NAME = "android_zhihu_output_graph.pb"
ANDROID_WEIBO_MODEL_NAME = "android_weibo_output_graph.pb"
ANDROID_TOP_TODAY_MODEL_NAME = "android_top_today_output_graph.pb"
ANDROID_BAIDU_MODEL_NAME = "android_baidu_output_graph.pb"

# label
ANDROID_ZHIHU_LABEL_NAME = "android_zhihu_output_labels.txt"
ANDROID_WEIBO_LABEL_NAME = "android_weibo_output_labels.txt"
ANDROID_TOP_TODAY_LABEL_NAME = "android_top_today_output_labels.txt"
ANDROID_BAIDU_LABEL_NAME = "android_baidu_output_labels.txt"

# 每个 app 启动存在的几个阶段
BAIDU_STAGE = ['start', 'logo', 'ad', 'loading', 'end']
TOP_TODAY_STAGE = ['start', 'logo', 'ad', 'loading', 'end']
WEIBO_STAGE = ['start', 'logo', 'ad', 'loading', 'end']
ZHIHU_STAGE = ['start', 'logo', 'ad', 'loading', 'words', 'end']

ZHIHU_PERCENT = {'start': 0.80, 'logo': 0.90, 'ad': 0.90, 'loading': 0.60, 'words': 0.90, 'end': 0.80}
BAIDU_PERCENT = {'start': 0.96, 'logo': 0.95, 'ad': 0.90, 'loading': 0.60, 'end': 0.90}
TOP_TODAY_PERCENT = {'start': 0.96, 'logo': 0.95, 'ad': 0.90, 'loading': 0.70, 'end': 0.9}
WEIBO_PERCENT ={'start': 0.9, 'logo': 0.8, 'ad': 0.9, 'loading': 0.8, 'end': 0.6}

# 二分查找后，有一个调整精度的线性查找，现在给这个线性查找定一个查找次数限制，达到这个限制就不找了
AJUST_LIMIT = 10

# 微博 end 阶段大概率是图片，当碰到都是文字时，end 的识别率只有 0.6 左右，达不到 0.9

# 现在计算「启动时长」 = loading - start，
# 如果没有找到 loading 阶段，那就用 words ，即：启动时长 = words - start

