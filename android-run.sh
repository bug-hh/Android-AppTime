#!/usr/bin/env bash

echo "可测试的 app 如下："
echo "  1. 知乎"
echo "  2. 今日头条"
echo "  3. 百度"
echo "  4. 新浪微博"


read -p "请选择要测试的 app (输入序号即可):  " choice
echo $choice

if [ $choice -eq 1 ]; then
    app_name="知乎"
    package_name="com.zhihu.android"
    activity_name=".app.ui.activity.LauncherActivity"
    echo $app_name
elif [ $choice -eq 2 ]; then
    app_name="今日头条"
    package_name="com.ss.android.article.news"
    activity_name=".activity.SplashActivity"
    echo $app_name
elif [ $choice -eq 3 ]; then
    app_name="百度"
    package_name="com.baidu.searchbox"
    activity_name=".SplashActivity"
    echo $app_name
elif [ $choice -eq 4 ]; then
    app_name="新浪微博"
    package_name="com.sina.weibo"
    activity_name=".SplashActivity"
    echo $app_name
fi

read -p "请输入测试次数: (默认值为 12)" test_count

if [ ! $test_count ]; then
    echo "输入为空，将取默认值 12"
    test_count=12
fi

echo "测试方式如下: （输入序号即可，默认为方式 1）"
echo "  1. 先截图，后测试（适用于初次测试，没有任何截图）"
echo "  2. 只截图"
echo "  3. 直接测试（适用于已存在多组截图，并对这多组截图进行反复测试）"
read -p "请选择测试方式 (输入序号即可): " test_mode
if [ ! $test_mode ]; then
    echo "输入为空，采用「先截图，后测试」的方式"
    test_mode=1
fi

devices_id=""
if [ $test_mode -eq 1 -o $test_mode -eq 2 ]; then
    devices_id=`adb shell getprop ro.serialno`
    if [ "$devices_id" == "" ]; then
        echo "没有检测到连接设备，无法截图，程序退出"
        exit 1
    else
        echo $package_name
        echo $activity_name

        echo "创建本地端口 1313 连接 minicap"
        adb forward tcp:1313 localabstract:minicap

        ABI=$(adb shell getprop ro.product.cpu.abi | tr -d '\r')
        echo "CPU 架构: $ABI"
        adb push libs/$ABI/minicap /data/local/tmp/

        SDK=$(adb shell getprop ro.build.version.sdk | tr -d '\r')
        echo "Android SDK 版本: $SDK"
        adb push jni/android-$SDK/$ABI/minicap.so /data/local/tmp/


        screen_size=$(adb shell dumpsys window | grep -Eo 'init=[0-9]+x[0-9]+' | head -1 | cut -d= -f 2)
        if [ "$screen_size" = "" ]; then
            w=$(adb shell dumpsys window | grep -Eo 'DisplayWidth=[0-9]+' | head -1 | cut -d= -f 2)
            h=$(adb shell dumpsys window | grep -Eo 'DisplayHeight=[0-9]+' | head -1 | cut -d= -f 2)
            screen_size="${w}x${h}"
        fi
        echo $screen_size
        adb shell LD_LIBRARY_PATH=/data/local/tmp /data/local/tmp/minicap -P "$screen_size"@"$screen_size"/0  >/dev/null 2>&1 &
    fi

fi

if [ ! $devices_id ]; then
    devices_id="7b0f49f4"
fi

python3 test.py -d $devices_id -a $activity_name -p $package_name -n $app_name -c $test_count -t $test_mode

process_id=34564
process_id=`ps -Af | grep 'adb shell LD_LIBRARY_PATH=/data/local/tmp /data/local/tmp/minicap' | awk '{print $2}' | head -n 1`
kill $process_id

#
#sh ./android-run.sh --apk_path ./apk/zhihu_v6_4_0.apk
#sh ./android-run.sh

