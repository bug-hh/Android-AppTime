#!/usr/bin/env python
# coding:utf-8
import json
import os
import time

from optparse import OptionParser
from android_tester import AndroidTester
from app_config.config import ZHIHU_PACKAGE_NAME
from app_config.config import ZHIHU_ACTIVITY_PATH

def main(package_name, activity_name, device_id, app_name, test_count, test_mode):
    apk_url = ""
    # 开始录屏和启动 app
    # TODO download app -- test -- report

    cur = time.time()
    tester = AndroidTester(test_count, "Android", device_id, package_name, activity_name, app_name, test_mode)
    # launch, page_loading = tester.test()
    tester.test()
    # print ("APP 启动时长 %f" % launch)
    # print ("APP 首页加载时长 %f" % page_loading)
    now = time.time()
    print("总共耗时： %ds" % (now - cur))

if __name__ == '__main__':
    parser = OptionParser()
    cwd = os.getcwd()
    apk_dir = os.path.join(cwd, 'apk')
    ls = os.listdir(apk_dir)
    apk_name = ""
    for fn in ls:
        if fn.endswith(".apk"):
            apk_name = fn
            break

    apk_default_path = os.path.join(cwd, 'apk', apk_name)

    parser.add_option("-a", "--activity_name", dest="activity_name", default=ZHIHU_ACTIVITY_PATH, help="activity name")
    parser.add_option("-p", "--package_name", dest="package_name", default="Android", help="platform,Android or iOS")
    parser.add_option("-d", "--device_id", dest="device_id", default="f955925d4043f9d8fbb014da293dcf6ecc58b8aa", help="lock device id")
    parser.add_option("-n", "--app_name", dest="app_name", default="知乎", help="app name")
    parser.add_option("-c", "--test_count", dest="test_count", default="12", help="test count")
    parser.add_option("-t", "--test_mode", dest="test_mode", default="1", help="test mode")

    (options, args) = parser.parse_args()

    test_count = 12
    if options.activity_name:
        activity_name = options.activity_name
    if options.package_name:
        package_name = options.package_name
    if options.device_id:
        device_id = options.device_id
    if options.app_name:
        app_name = options.app_name
    if options.test_count:
        test_count = int(options.test_count)
    if options.test_mode:
        test_mode = int(options.test_mode)

    main(package_name, activity_name, device_id, app_name, test_count, test_mode)
