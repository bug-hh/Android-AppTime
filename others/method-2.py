#!/usr/bin/env python
# coding: utf-8
import os
import datetime
import time
import json

from google_algorithm.label_image import Classifier
from msg_queue.queue_manager import QueueManager

from app_config.config import ZHIHU_STAGE
from app_config.config import WEIBO_STAGE
from app_config.config import TOP_TODAY_STAGE
from app_config.config import BAIDU_STAGE

from app_config.config import TMP_IMG_ZHIHU_DIR
from app_config.config import TMP_IMG_TOP_TODAY_DIR
from app_config.config import TMP_IMG_BAIDU_DIR
from app_config.config import TMP_IMG_WEIBO_DIR

from app_config.config import ZHIHU_PERCENT
from app_config.config import BAIDU_PERCENT
from app_config.config import TOP_TODAY_PERCENT
from app_config.config import WEIBO_PERCENT

from app_config.config import ZHIHU_SORTED_STAGE
from app_config.config import BAIDU_SORTED_STAGE
from app_config.config import TOP_TODAY_SORTED_STAGE
from app_config.config import WEIBO_SORTED_STAGE


class CalTime(object):
    def __init__(self, times_counter, model_code):
        self.model_code = model_code
        self.times_counter = times_counter
        self.cache = {}
        self.progress = 0
        self.classifier = Classifier(model_code)
        self.PID = os.getpid()

        self.loading_exist = True
        self.ad_exist = False

        self._test_app_adapter(model_code)

    def _test_app_adapter(self, test_app_code):
        # 1 知乎 2 微博 3 头条 4 百度
        if test_app_code == 1:
            self.STAGE_PERCENT = ZHIHU_PERCENT
            self.SORTED_STAGE = ZHIHU_SORTED_STAGE
            self.TMP_IMG_DIR = TMP_IMG_ZHIHU_DIR
            self.APP_STAGE = ZHIHU_STAGE

        elif test_app_code == 2:
            self.STAGE_PERCENT = WEIBO_PERCENT
            self.SORTED_STAGE = WEIBO_SORTED_STAGE
            self.TMP_IMG_DIR = TMP_IMG_WEIBO_DIR
            self.APP_STAGE = WEIBO_STAGE

        elif test_app_code == 3:
            self.STAGE_PERCENT = TOP_TODAY_PERCENT
            self.SORTED_STAGE = TOP_TODAY_SORTED_STAGE
            self.TMP_IMG_DIR = TMP_IMG_TOP_TODAY_DIR
            self.APP_STAGE = TOP_TODAY_STAGE

        elif test_app_code == 4:
            self.STAGE_PERCENT = BAIDU_PERCENT
            self.SORTED_STAGE = BAIDU_SORTED_STAGE
            self.TMP_IMG_DIR = TMP_IMG_BAIDU_DIR
            self.APP_STAGE = BAIDU_STAGE

    def upper_bound(self, pic_dir, pic_list, first, last, value, target_stage):
        '''
        求 pic_list 数组中 最后一个大于 value 的值的小标，即 [1,1,2,2,10,10,10,20], value = 10, 那么函数将返回下标 7，即最右边的那个 10 的下标 [first, last), 左闭右开
        如果不存在，则返回 last
        :param pic_dir:
        :param pic_list:
        :param first:
        :param last:
        :param value:
        :return:
        '''
        z = 0
        length = last + 1
        while first < last:
            z += 1
            self.progress += 1
            mid_index = first + (last - first) // 2
            while True:
                if self.cache.get(mid_index):
                    mid = self.cache[mid_index]
                else:
                    pic_path = os.path.join(pic_dir, pic_list[mid_index])
                    mid = self.classifier.identify_pic(pic_path)
                    self.cache[mid_index] = mid
                if mid:
                    break
                else:
                    if mid_index + 1 >= length:
                        return length
                    else:
                        mid_index += 1

            # 防止将 home 界面识别成 ad
            if mid[0] == 'ad' and mid[1] >= 0.9:
                return -1
            if self.SORTED_STAGE[mid[0]] <= value:
                first = mid_index + 1
            else:
                last = mid_index
        print("upper_bound: z = %d" % z)

        return first

    def lower_bound(self, pic_dir, pic_list, first, last, value, target_stage):
        z = 0
        length = last

        while first < last:
            z += 1
            self.progress += 1
            mid_index = first + (last - first) // 2
            while True:
                if self.cache.get(mid_index):
                    mid = self.cache[mid_index]
                else:
                    pic_path = os.path.join(pic_dir, pic_list[mid_index])
                    mid = self.classifier.identify_pic(pic_path)
                    self.cache[mid_index] = mid
                if mid:
                    break
                else:
                    if mid_index + 1 >= length:
                        return length
                    else:
                        mid_index += 1

            # 如果有广告，则直接丢弃该批截图序列
            if mid[0] == 'ad' and mid[1] >= 0.9:
                return -1

            if self.SORTED_STAGE[mid[0]] < value:
                first = mid_index + 1
            else:
                last = mid_index
        print("lower_bound: z = %d" % z)

        return first

    def _check_result(self, is_upper_bound, res, last):
        if res[0] == last or res[0] < 0:
            return False

        if is_upper_bound:
            return res[0] -1 >= 0

        return True

    def _check_precise(self, pic_index, pic_list, pic_dir, target_stage):
        '''
        检查准确度是否符合预期，如果不符合，则返回符合预期的图片的索引值
        :param pic_index:_check_precise
        :param pic_list:
        :param pic_dir:
        :return:
        '''
        y = 0
        target_precise = int(self.STAGE_PERCENT[target_stage] * 10000)
        pic_path = os.path.join(pic_dir, pic_list[pic_index])
        id_ret = self.classifier.identify_pic(pic_path)
        # end 通过 「words」的 upperbound 往后找，loading 通过「newlogo」的upperbound 向后找
        direction = 1
        length = len(pic_list)
        msg = {}
        while id_ret[0] != target_stage and 1 <= pic_index < length - 1:
            if id_ret[0] == 'ad':
                return -2, None
            y += 1
            self.progress += 1
            pic_index += direction
            pic_path = os.path.join(pic_dir, pic_list[pic_index])
            id_ret = self.classifier.identify_pic(pic_path)

        # 先找到logo阶段的 upperbound，再向后找到第一张不是 logo 阶段的图，作为 loading 阶段的开始图
        if target_stage not in ('loading', 'end'):
            return pic_index, id_ret

        prob = round(id_ret[1], 4)
        prob *= 10000
        prob = int(prob)
        last = None
        while prob < target_precise and id_ret[0] == target_stage and 1 <= pic_index < length - 1:
            y += 1
            pic_index += direction
            pic_path = os.path.join(pic_dir, pic_list[pic_index])
            last = id_ret
            id_ret = self.classifier.identify_pic(pic_path)
            prob = round(id_ret[1], 4)
            prob *= 10000
            prob = int(prob)

        print("check_precise: y = %d" % y)

        if id_ret[0] == target_stage:
            return pic_index, id_ret
        else:
            return ((pic_index - 1), last)

    def cal_time(self, pic_dir, exclude_list, start_time):
        cur = time.time()
        ret = {}
        counter = 0
        for st in self.APP_STAGE:
            if st == 'start':
                ret[st] = start_time, None, None
            else:
                ret[st] = None, None, None

        ls = os.listdir(pic_dir)
        pic_list = [pic for pic in ls if not pic.startswith(".")]
        pic_list.sort()

        i = 0
        length = len(pic_list)
        summary = "文件夹 %s 总共包含 %d 张图片" % (os.path.basename(pic_dir), length)
        print(summary)
        msg = {}
        self.cache.clear()
        for stage in self.SORTED_STAGE:
            if stage in exclude_list:
                continue

            search_method = self.upper_bound if stage == 'words' or stage == 'newlogo' else self.lower_bound
            is_upper_bound = True if stage == 'words' or stage == 'newlogo' else False
            self.progress = 0
            bound_index = search_method(pic_dir, pic_list, 0, length, ZHIHU_SORTED_STAGE[stage], stage)
            if bound_index == -1:
                ad_str = "文件夹 %s: 存在广告，丢弃该批数据" % self.times_counter
                print(ad_str)
                return

            if stage == 'words':
                stage = 'end'
            elif stage == 'newlogo':
                stage = 'loading'

            search_result = self._check_precise(bound_index, pic_list, pic_dir, stage)
            if not self._check_result(is_upper_bound, search_result, length):
                error_str = "文件夹 %s: %s 阶段不存在" % (self.times_counter, stage)
                print(error_str)
                ret[stage] = None, None, None
                # return
            else:
                index = search_result[0] - 1 if is_upper_bound else search_result[0]
                pic_path = os.path.join(pic_dir, pic_list[index])
                ret[stage] = (self.get_create_time(pic_list[index]), pic_path, search_result[1])

        print()
        for k in ret:
            print(k, ret[k])

        # 计算启动时长和首页加载时长
        launch_time = 0
        home_page_loading_time = 0
        if ret['loading'][0]:
            launch_time = round((ret['loading'][0] - ret['start'][0]), 4)
        else:
            self.loading_exist = False

        if ret['end'][0]:
            if ret['loading'][0]:
                home_page_loading_time = round((ret['end'][0] - ret['loading'][0]), 4)
            else:
                home_page_loading_time = 0
                launch_time = round(ret['end'][0] - ret['start'][0])

        if self.loading_exist:
            str2 = "文件夹 %s: App 启动时长：%.3fs   App 首页加载时长：%.3fs " % (self.times_counter, launch_time, home_page_loading_time)
            print(str2)
        else:
            print("高端机型不存在「loading」阶段，因此首页加载时长为 0")
            print("文件夹 %s: App 启动时长: %.3fs    App 首页加载时长: 0s" % (self.times_counter, launch_time))

        now = time.time()
        interval = now - cur
        total_time = "文件夹 %s 总共计算耗时: %ds" % (self.times_counter, interval)
        print(total_time)

    def cal_time_linear(self, pic_dir, start_time):
        msg = {}
        cur = time.time()
        ret = {}
        counter = 0
        for st in self.APP_STAGE:
            if st == 'start':
                ret[st] = start_time, None, None
            else:
                ret[st] = None, None, None

        ls = os.listdir(pic_dir)
        pic_list = [pic for pic in ls if not pic.startswith(".")]
        pic_list.sort()

        i = 0
        length = len(pic_list)
        summary = "文件夹 %s 总共包含 %d 张图片" % (os.path.basename(pic_dir), length)
        print(summary)
        index_ls = range(length)
        loading_index, id_ret = self._find_first_loading(pic_dir, pic_list, index_ls)
        self.ad_exist = True if loading_index == -2 else False
        if 0 <= loading_index < length:
            pic_path = os.path.join(pic_dir, pic_list[loading_index])
            ret['loading'] = (self.get_create_time(pic_list[loading_index]), pic_path, id_ret)

            end_index, id_ret = self._find_first_end(loading_index + 1, pic_dir, pic_list, index_ls)
            self.ad_exist = True if end_index == -2 else False
            pic_path = os.path.join(pic_dir, pic_list[end_index])
            if 0 <= end_index < length:
                ret['end'] = (self.get_create_time(pic_list[end_index]), pic_path, id_ret)

        for k in ret:
            print(k, ret[k])

        # 计算启动时长和首页加载时长
        launch_time = 0
        home_page_loading_time = 0
        if ret['loading'][0]:
            launch_time = round((ret['loading'][0] - ret['start'][0]), 4)
        else:
            self.loading_exist = False

        if ret['end'][0]:
            if ret['loading'][0]:
                home_page_loading_time = round((ret['end'][0] - ret['loading'][0]), 4)
            else:
                home_page_loading_time = 0
                launch_time = round(ret['end'][0] - ret['start'][0])

        if self.ad_exist:
            ad_str = "文件夹 %s: 存在广告，丢弃该批数据" % self.times_counter
            info = ad_str
            launch_time = 0
            home_page_loading_time = 0
            print(ad_str)
        elif self.loading_exist:
            str2 = "文件夹 %s: App 启动时长：%.3fs   App 首页加载时长：%.3fs " % (self.times_counter, launch_time, home_page_loading_time)
            info = str2
            print(str2)
        else:
            str3 = "高端机型不存在「loading」阶段，因此首页加载时长为 0"
            str4 = "文件夹 %s: App 启动时长: %.3fs    App 首页加载时长: 0s" % (self.times_counter, launch_time)
            info = str3 + '\n' + str4
            print(str3)
            print(str4)

        result = {
            'launch_time': launch_time,
            'home_page_loading_time': home_page_loading_time
        }

        # self.shared_answer_queue.put((launch_time, home_page_loading_time))
        now = time.time()
        interval = now - cur
        total_time = "文件夹 %s 总共计算耗时: %ds" % (self.times_counter, interval)
        print(total_time)

        msg['dirname'] = os.path.basename(pic_dir)
        msg['summary'] = summary
        msg['info'] = info
        msg['result'] = result
        msg['total_time'] = total_time



    def _find_first_loading(self, pic_dir, pic_list, index_ls):
        flag = False
        for i in index_ls:
            pic_name = pic_list[i]
            pic_path = os.path.join(pic_dir, pic_name)
            id_ret = self.classifier.identify_pic(pic_path)

            if id_ret[0] == 'ad' and id_ret[1] >= 0.8:
                return -2, None

            # 用 logo 找 loading，找到大于或等于给定阈值的 loading
            if flag and id_ret[0] != 'logo':
                # return i, id_ret
                search_result = self._check_precise(i, pic_list, pic_dir, 'loading')
                ret_i, id_ret = search_result[0], search_result[1]
                return ret_i, id_ret
            # 找到 第一张 newlogo
            if not flag and id_ret[0] == 'logo':
                flag = True
            i += 1

        return -1, None

    def _find_first_end(self, start_index, pic_dir, pic_list, index_ls):
        length = len(index_ls)
        while 0 <= start_index < length:
            pic_name = pic_list[start_index]
            pic_path = os.path.join(pic_dir, pic_name)
            id_ret = self.classifier.identify_pic(pic_path)
            if id_ret[0] == 'ad':
                return -2, None

            if id_ret[0] == 'end':
                # return start_index, id_ret
                search_result = self._check_precise(start_index, pic_list, pic_dir, 'end')
                ret_index, id_ret = search_result[0], search_result[1]
                return ret_index, id_ret
            start_index += 1

        return -1, None

    @staticmethod
    def get_create_time(filename):
        fn, ext = os.path.splitext(filename)
        d = datetime.datetime.strptime(fn, "%Y-%m-%d_%H-%M-%S-%f")
        ts = datetime.datetime.timestamp(d)
        return ts

def calculate(pic_dir, times_counter, start_time, model_code):
    ct = CalTime(times_counter, model_code)
    ct.cal_time_linear(pic_dir, start_time)

if __name__ == '__main__':
    # from app_config.config import TMP_IMG_ZHIHU_DIR, EXCLUDED_LIST
    # screenshots_dir = os.path.join(TMP_IMG_ZHIHU_DIR, "Android")
    # pic_dir = os.path.join(screenshots_dir, "1")
    # ct = CalTime(1, 1)
    # ct.cal_time(pic_dir, EXCLUDED_LIST, 1567242814.894939)
    # 1 知乎 2 微博 3 头条 4 百度

    msg = {
        'dirname': '1',
        'summary': '共有 x 张图片',
        'info': '有广告/正常情况/loading 阶段不存在',
        'result': {
            'launch_time': 0,
            'home_page_loading_time': 0
        },
        'total_time': '耗时'
    }
    # from app_config.config import ABOUT_TRAINING
    # screenshots_dir = os.path.join(ABOUT_TRAINING, "zhihu", "test")
    # pic_dir = os.path.join(screenshots_dir, "end")
    # pic_name = "test-end-1.jpg"
    # pic_path = os.path.join(pic_dir, pic_name)
    # classifier = Classifier(1)
    # ret = classifier.identify_pic(pic_path)
    # print(ret)

    capture_path = os.path.abspath(os.path.join(TMP_IMG_ZHIHU_DIR, os.pardir))
    json_file_name = "start_time_zhihu.json"
    fp = open(os.path.join(capture_path, json_file_name))
    start_dt = json.load(fp)
    screenshots_dir = os.path.join(TMP_IMG_ZHIHU_DIR, "Android")
    ls = os.listdir(screenshots_dir)
    times_list = [name for name in ls if not name.startswith(".")]
    times_list.sort()
    length = len(times_list)
    for i in range(length):
        if times_list[i] != '6':
            continue
        pictures_dir_1 = os.path.join(screenshots_dir, times_list[i])
        calculate(pictures_dir_1, times_list[i], start_dt[times_list[i]], 1)