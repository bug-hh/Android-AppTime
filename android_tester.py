# -*- coding: utf-8 -*-
import os
import threading
import time
import datetime
import json
import shutil

import queue

from queue import Queue
from multiprocessing import Process

from subprocess import PIPE

from app import Android

from app_config.config import ZHIHU_PACKAGE_NAME
from app_config.config import ZHIHU_ACTIVITY_PATH
from app_config.config import TMP_IMG_ZHIHU_DIR

from app_config.config import WEIBO_PACKAGE_NAME
from app_config.config import WEIBO_ACTIVITY_PATH
from app_config.config import TMP_IMG_WEIBO_DIR

from app_config.config import TOP_TODAY_PACKAGE_NAME
from app_config.config import TOP_TODAY_ACTIVITY_PATH
from app_config.config import TMP_IMG_TOP_TODAY_DIR

from app_config.config import BAIDU_PACKAGE_NAME
from app_config.config import BAIDU_ACTIVITY_PATH
from app_config.config import TMP_IMG_BAIDU_DIR

from app_config.config import ZHIHU_SORTED_STAGE
from app_config.config import EXCLUDED_LIST

from app_config.config import ZHIHU_PERCENT
from app_config.config import BAIDU_PERCENT
from app_config.config import TOP_TODAY_PERCENT
from app_config.config import WEIBO_PERCENT


from msg_queue.queue_manager import QueueManager
from minicap.minicap import MinicapStream

from cal_time import CalTime

from record import Record

class AndroidTester(object):
    def __init__(self, test_count, platform, device_id, package_name, activity_name, app_name, test_mode):
        self.test_count = test_count
        self.total_time = {}  # 存储样式：total_time = {totaltime:tasks_times}
        self.total_time_lock = threading.Lock()
        self.platform = platform
        self.device_id = device_id
        self.android = Android(device_id)
        self.apk_info = {}
        self.result = []
        self.package_name = package_name
        self.activity_name = activity_name
        self.app_name = app_name
        self.model_code = 1
        self.answer_queue = Queue()
        self.msg_queue = Queue()

        self.need_screenshot = 1
        self.need_test = 1

        self.task_pid_status = {}
        self.start_dt = {}

        if test_mode == 1:
            self.need_screenshot = 1
            self.need_test = 1
        elif test_mode == 2:
            self.need_screenshot = 1
            self.need_test = 0
        elif test_mode == 3:
            self.need_screenshot = 0
            self.need_test = 1

        if self.package_name == ZHIHU_PACKAGE_NAME:
            self.STAGE_PERCENT = ZHIHU_PERCENT
            self.json_file_name = "start_time_zhihu.json"
            self.model_code = 1
            self.tmp_pic_dir = TMP_IMG_ZHIHU_DIR
        elif self.package_name == WEIBO_PACKAGE_NAME:
            self.STAGE_PERCENT = WEIBO_PERCENT
            self.json_file_name = "start_time_weibo.json"
            self.model_code = 2
            self.tmp_pic_dir = TMP_IMG_WEIBO_DIR
        elif self.package_name == TOP_TODAY_PACKAGE_NAME:
            self.STAGE_PERCENT = TOP_TODAY_PERCENT
            self.json_file_name = "start_time_top_today.json"
            self.model_code = 3
            self.tmp_pic_dir = TMP_IMG_TOP_TODAY_DIR
        elif self.package_name == BAIDU_PACKAGE_NAME:
            self.STAGE_PERCENT = BAIDU_PERCENT
            self.json_file_name = "start_time_baidu.json"
            self.model_code = 4
            self.tmp_pic_dir = TMP_IMG_BAIDU_DIR

        # if os.path.exists(self.tmp_pic_dir):
        #     shutil.rmtree(self.tmp_pic_dir)

        QueueManager.register('get_task_status', callable=lambda : self.task_pid_status)
        QueueManager.register('get_answer_queue', callable=lambda: self.answer_queue)
        QueueManager.register('get_msg_queue', callable=lambda : self.msg_queue)

        self.manager = QueueManager(address=('localhost', QueueManager.SHARED_PORT), authkey=b'1234')
        self.manager.start()

        self.shared_task_status_dt = self.manager.get_task_status()
        self.shared_answer_queue = self.manager.get_answer_queue()
        self.shared_msg_queue = self.manager.get_msg_queue()

    def _get_apk_info(self):
        data = self.android.get_aapt_data()
        print('data : ' + data)
        for line in data.split("\n"):
            if line.startswith("package:"):
                for word in line.split(" "):
                    if "=" in word:
                        word = word.replace("'", "")
                        self.apk_info[word.split("=")[0]] = word.split("=")[1]

    def _get_time_stamp(self, filename):
        fn, ext = os.path.splitext(filename)
        d = datetime.datetime.strptime(fn, "%Y-%m-%d_%H-%M-%S-%f")
        ts = datetime.datetime.timestamp(d)
        return ts

    def _dispatch_cal_task(self):
        capture_path = os.path.abspath(os.path.join(self.tmp_pic_dir, os.pardir))
        fp = open(os.path.join(capture_path, self.json_file_name))
        self.start_dt = json.load(fp)
        screenshots_dir = os.path.join(self.tmp_pic_dir, self.platform)
        ls = os.listdir(screenshots_dir)
        times_list = [int(name) for name in ls if not name.startswith(".")]
        times_list.sort()
        i = 0
        flag_1 = False
        flag_2 = False
        # length = len(times_list)
        length = self.test_count

        finished_list = []

        while i < length:
            if not flag_1:
                str_time_list_i = str(times_list[i])
                pictures_dir_1 = os.path.join(screenshots_dir, str_time_list_i)
                task_process_1 = Process(target=self._cal_time, args=(pictures_dir_1, str_time_list_i, self.start_dt[str_time_list_i], self.model_code))
                task_process_1.start()
                self.shared_task_status_dt.setdefault(task_process_1.pid, False)
                flag_1 = True
                i += 1

            if not flag_2 and i < length:
                str_time_list_i = str(times_list[i])
                pictures_dir_2 = os.path.join(screenshots_dir, str_time_list_i)
                task_process_2 = Process(target=self._cal_time, args=(pictures_dir_2, str_time_list_i, self.start_dt[str_time_list_i], self.model_code))
                task_process_2.start()
                self.shared_task_status_dt.setdefault(task_process_2.pid, False)
                flag_2 = True
                i += 1

            status1 = self.shared_task_status_dt.get(task_process_1.pid)
            if status1 and task_process_1.pid not in finished_list:
                finished_list.append(task_process_1.pid)
                flag_1 = False

            status2 = self.shared_task_status_dt.get(task_process_2.pid)
            if status2 and task_process_2.pid not in finished_list:
                finished_list.append(task_process_2.pid)
                flag_2 = False

        while True:
            is_all_finished = True
            for status in self.shared_task_status_dt.values():
                is_all_finished = is_all_finished and status
            if is_all_finished:
                break

        print()
        print('#######################')
        print()
        # 取 12 组数据，最终结果去掉一个最小值和一个最大值，再计算平均值
        launch_time_ls = []
        loading_time_ls = []
        while True:
            try:
                data = self.shared_answer_queue.get_nowait()
                msg = json.loads(data)
                dirname = msg['dirname']
                summary = msg['summary']
                info = msg['info']
                total_time = msg['total_time']
                launch_time = msg['result']['launch_time']
                loading_time = msg['result']['home_page_loading_time']
                print("文件夹：%s"  % dirname)
                print("\t%s" % summary)
                print("\t%s" % info)
                print("\t%s" % (total_time))
                print("\tApp 启动时长：%.3fs" % (launch_time))
                # print("\tApp 启动时长：%.3fs   App 首页加载时长：%.3fs" % (launch_time, loading_time))
                print('#######################')
                print()
                if launch_time > 0:
                    launch_time_ls.append(int(launch_time * 1000))
                if loading_time > 0:
                    loading_time_ls.append(int(loading_time * 1000))
            except queue.Empty:
                break
        launch_time_ls.sort()
        loading_time_ls.sort()
        len1 = len(launch_time_ls)
        len2 = len(loading_time_ls)
        if len1 > 2:
            aver_launch_time = 1.0 * sum(launch_time_ls[1:-1]) / (len1 - 2)
        else:
            aver_launch_time = 0

        if len2 > 2:
            aver_home_page_loading_time = 1.0 * sum(loading_time_ls[1:-1]) / (len2 - 2)
        else:
            aver_home_page_loading_time = 0

        aver_launch_time /= 1000
        aver_home_page_loading_time /= 1000
        str_aver = "%s App 的平均启动时长：%.3fs" % (self.app_name, aver_launch_time)
        # str_aver = "平均启动时长：%.3fs  平均加载时长: %.3fs" % (aver_launch_time, aver_home_page_loading_time)
        print(str_aver)

    def parse_data(self, msg_data):
        msg = json.loads(msg_data)

    def _cal_time(self, pic_dir, times_counter, start_time, model_code):
        ct = CalTime(times_counter, model_code)
        ct.cal_time(pic_dir, EXCLUDED_LIST, start_time)

    def capture_pic(self):
        # 前 4 次不计入启动，出现广告概率较高
        for times in range(4):
            self.android.start_app(self.package_name, self.activity_name)
            time.sleep(12)
            self.android.kill_app(self.package_name)
            time.sleep(5)

        self.minicap = MinicapStream(port=QueueManager.MINICAP_PORT, model_code=self.model_code)
        self.minicap.run()

        for times in range(self.test_count):
            self.shared_msg_queue.put(times + 1)

            # 启动 LauncherActivity
            print('正在启动 MainActivity 进行测试...')
            p_am = self.android.adb([
                'shell', 'am', 'start', '-W', '-n', '%s/%s' % (self.package_name, self.activity_name)
            ], stdout=PIPE)
            self.start_time = time.time()
            self.start_dt[times + 1] = self.start_time
            # 等待 MainActivity 启动完毕
            while p_am.poll() is None:
                time.sleep(0.1)

            time.sleep(15)
            self.android.kill_app(self.package_name)

            time.sleep(5)
            #准备开始下一次截图
            self.shared_msg_queue.put(-1)

        # 关闭连接 minicap 的套接字
        self.shared_msg_queue.put(-2)
        # 保存 每次的 start time

        fp = os.path.join(os.path.join(self.tmp_pic_dir, os.pardir), self.json_file_name)
        with open(fp, "w") as fobj:
            json.dump(self.start_dt, fobj)

    def test(self):
        # 先捕获图片
        if self.need_screenshot == 1:
            self.capture_pic()
        # 不管有几个文件夹，每次都只跑两个进程
        if self.need_test == 1:
            self._dispatch_cal_task()

def query_service(port):
    fobj = os.popen("lsof -i tcp:%d" % port)
    state = fobj.read().strip()
    if len(state) == 0:
        return False, -1
    ls = state.split("\n")

    status_list = ls[-1].split()
    status = status_list[-1]
    pid = status_list[1]
    return status == "(LISTEN)", pid

def close_shared_server():
    state, pid = query_service(QueueManager.SHARED_PORT)
    if pid != -1:
        os.system("kill %s" % pid)

if __name__ == '__main__':
    try:
        test_counter = 10
        device_id = os.popen("adb shell getprop ro.serialno").read().strip()
        package_name = "com.zhihu.android"
        activity_name = ".app.ui.activity.LauncherActivity"
        # print(device_id)
        at = AndroidTester(10, "Android", device_id, package_name, activity_name, cal_mode="2")
        # at.capture_pic()
        at._dispatch_cal_task()
    finally:
        close_shared_server()
