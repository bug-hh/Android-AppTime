# -*- coding: utf-8 -*-
import os
import shutil

from app_config.config import TMP_IMG_ZHIHU_DIR
from minicap.minicap import MinicapStream


class Record(object):

    def __init__(self, times, port, platform, timeout=10):
        self.times = times
        self.port = port
        self.platform = platform
        self.timeout = timeout

    def record(self):
        img_path = os.path.join(TMP_IMG_ZHIHU_DIR, self.platform, str(self.times))
        if not os.path.exists(img_path):
            print('创建文件夹 %s ' % img_path)
            os.makedirs(img_path)
        else:
            shutil.rmtree(img_path)
            print('删除创建文件夹 %s ' % img_path)
            os.makedirs(img_path)

        print('开始录屏...')
        instance = MinicapStream.get_builder(img_path, self.port)
        instance.run(self.timeout)
