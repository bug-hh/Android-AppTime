#!/usr/bin/env bash

devices_id=""
read -p "请输入测试次数: " test_count
if [ ! $devices_id ]; then
    echo "devices_id 为空，将取默认值 10"
    test_count=10
fi

echo $test_count
#
#zhihu=`adb shell "cmd package resolve-activity --brief com.zhihu.android"`
#weibo=`adb shell "cmd package resolve-activity --brief com.sina.weibo"`
#top_today=`adb shell "cmd package resolve-activity --brief com.ss.android.article.news"`

#devices_id=`adb shell getprop ro.serialno`
#
#if [ "$devices_id" == "" ]; then
#    echo "没有检测到连接设备，程序退出"
#    exit 1
#fi
#
#echo "可测试的 app 如下："
#echo "  1. 知乎"
#echo "  2. 今日头条"
#echo "  3. 百度"
#echo "  4. 新浪微博"
#echo "  5. 其他"
#
#read -p "请选择要测试的 app (输入序号即可):  " choice
#echo $choice
#
#if [ $choice -eq 1 ]; then
#    echo "知乎"
#    package_name="com.zhihu.android"
#    activity_name=".app.ui.activity.LauncherActivity"
#elif [ $choice -eq 2 ]; then
#    echo "今日头条"
#    package_name="com.ss.android.article.news"
#    activity_name=".activity.SplashActivity"
#elif [ $choice -eq 3 ]; then
#    echo "百度"
#    package_name="com.baidu.searchbox"
#    activity_name=".SplashActivity"
#elif [ $choice -eq 4 ]; then
#    echo "新浪微博"
#    package_name="com.sinal.weibo"
#    activity_name=".SplashActivity"
#elif [ $choice -eq 5 ]; then
#    read -p "请输入其他 app 包名 (eg: com.zhihu.android): "  package_name
#    read -p "请输入其他 app launch acitvity 名称 (eg: .app.ui.activity.LauncherActivity): "  activity_name
#fi
#
#echo $package_name
#echo $activity_name
#






