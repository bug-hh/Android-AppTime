#!/usr/bin/env python
# coding:utf-8

import sys

def get_each_task_time(p_am, p_logcat):
    total_time = -1
    tasks_times = {}

    for line in p_am.stdout.readlines():
        if line.startswith('TotalTime:'):
            total_time = int(line.split()[-1])

    if total_time == -1:
        print('🌧 获取启动时间失败')
        sys.exit(-1)

    # 获取每个 Task 的执行时间
    for line in p_logcat.stdout.readlines():
        if '#doRun() end' in line:
            segments = line.split('#doRun() end')
            task_name = segments[0].split()[-1]
            duration = segments[1].split()[-1].strip(';')
            tasks_times[task_name] = int(duration)

    return tasks_times


def caculate_task_time(launch_times, task_time_maps):
    # 计算启动平均时长
    if len(launch_times) <= 0:
        return
    launch_average_time = round(sum(launch_times) / len(launch_times), 3)
    return launch_average_time
