# -*- coding: utf-8 -*-

import os


class Banner(object):

    def __init__(self):
        self.version = 0  # 版本信息
        self.length = 0  # banner长度
        self.pid = 0  # 进程ID
        self.real_width = 0  # 设备的真实宽度
        self.real_height = 0  # 设备的真实高度
        self.virtual_width = 0  # 设备的虚拟宽度
        self.virtual_height = 0  # 设备的虚拟高度
        self.orientation = 0  # 设备方向
        self.quirks = 0  # 设备信息获取策略

    def __str__(self):
        message = "Banner [Version=" + str(self.version) + ", length=" + str(self.length) + ", Pid=" + str(
            self.pid) + ", realWidth=" + str(self.real_width) + ", realHeight=" + str(
            self.real_height) + ", virtualWidth=" + str(self.virtual_width) + ", virtualHeight=" + str(
            self.virtual_height) + ", orientation=" + str(self.orientation) + ", quirks=" + str(self.quirks) + "]"
        return message
