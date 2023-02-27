# cat /home/pi/DOGZILLA/app_dogzilla/oled_dogzilla.py
str_Name = "DOG"

#!/usr/bin/env python3
# coding=utf-8
from curses.ascii import isdigit
import time
import os
import sys
import Adafruit_SSD1306 as SSD

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import subprocess

from DOGZILLALib import DOGZILLA


# V1.0.8
class Dogzilla_OLED:
    def __init__(self, dogzilla, i2c_bus=1, clear=False, debug=False):
        self.__debug = debug
        self.__i2c_bus = i2c_bus
        self.__clear = clear
        self.__top = -2
        self.__x = 0

        self.__total_last = 0
        self.__idle_last = 0
        self.__str_CPU = "CPU:0%"

        self.__battery = 0
        self.__battery_index = 0
        self.__str_battery = ""
        self.__offset_battery = 104
        self.__dog = dogzilla

        self.__WIDTH = 128
        self.__HEIGHT = 32
        self.__image = Image.new('1', (self.__WIDTH, self.__HEIGHT))
        self.__draw = ImageDraw.Draw(self.__image)
        self.__font = ImageFont.load_default()

    def __del__(self):
        self.clear(True)
        if self.__debug:
            print("---OLED-DEL---")

    # 初始化OLED，成功返回:True，失败返回:False
    # Initialize OLED, return True on success, False on failure
    def begin(self):
        try:
            self.__oled = SSD.SSD1306_128_32(
                rst=None, i2c_bus=self.__i2c_bus, gpio=1)
            self.__oled.begin()
            self.__oled.clear()
            self.__oled.display()
            if self.__debug:
                print("---OLED begin ok!---")
            return True
        except:
            if self.__debug:
                print("---OLED no found!---")
            return False

    # 清除显示。refresh=True立即刷新，refresh=False不刷新。
    # Clear the display.  Refresh =True Refresh immediately, refresh=False refresh not
    def clear(self, refresh=False):
        self.__draw.rectangle(
            (0, 0, self.__WIDTH, self.__HEIGHT), outline=0, fill=0)
        if refresh:
            try:
                self.refresh()
                return True
            except:
                return False

    # 增加字符。start_x start_y表示开始的点。text是要增加的字符。
    # refresh=True立即刷新，refresh=False不刷新。
    # Add characters.  Start_x Start_y indicates the starting point.  Text is the character to be added
    # Refresh =True Refresh immediately, refresh=False refresh not
    def add_text(self, start_x, start_y, text, refresh=False):
        if start_x > self.__WIDTH or start_x < 0 or start_y < 0 or start_y > self.__HEIGHT:
            if self.__debug:
                print("oled text: x, y input error!")
            return
        x = int(start_x + self.__x)
        y = int(start_y + self.__top)
        self.__draw.text((x, y), str(text), font=self.__font, fill=255)
        if refresh:
            self.refresh()

    # 写入一行字符text。refresh=True立即刷新，refresh=False不刷新。
    # line=[1, 4]
    # Write a line of character text.  Refresh =True Refresh immediately, refresh=False refresh not.
    def add_line(self, text, line=1, refresh=False):
        if line < 1 or line > 4:
            if self.__debug:
                print("oled line input error!")
            return
        y = int(8 * (line - 1))
        self.add_text(0, y, text, refresh)

    # 刷新OLED，显示内容
    # Refresh the OLED to display the content
    def refresh(self):
        self.__oled.image(self.__image)
        self.__oled.display()


    # 读取CPU占用率
    # Read the CPU usage rate
    def getCPULoadRate(self, index):
        count = 10
        if index == 0:
            f1 = os.popen("cat /proc/stat", 'r')
            stat1 = f1.readline()
            data_1 = []
            for i in range(count):
                data_1.append(int(stat1.split(' ')[i+2]))
            self.__total_last = data_1[0]+data_1[1]+data_1[2]+data_1[3] + \
                data_1[4]+data_1[5]+data_1[6]+data_1[7]+data_1[8]+data_1[9]
            self.__idle_last = data_1[3]
        elif index == 4:
            f2 = os.popen("cat /proc/stat", 'r')
            stat2 = f2.readline()
            data_2 = []
            for i in range(count):
                data_2.append(int(stat2.split(' ')[i+2]))
            total_now = data_2[0]+data_2[1]+data_2[2]+data_2[3] + \
                data_2[4]+data_2[5]+data_2[6]+data_2[7]+data_2[8]+data_2[9]
            idle_now = data_2[3]
            total = int(total_now - self.__total_last)
            idle = int(idle_now - self.__idle_last)
            usage = int(total - idle)
            usageRate = int(float(usage / total) * 100)
            self.__str_CPU = "CPU:" + str(usageRate) + "%"
            self.__total_last = 0
            self.__idle_last = 0
            # if self.__debug:
            #     print(self.__str_CPU)
        return self.__str_CPU

    # 读取系统时间
    # Read system time
    def getSystemTime(self):
        cmd = "date +%H:%M:%S"
        date_time = subprocess.check_output(cmd, shell=True)
        str_Time = str(date_time).lstrip('b\'')
        str_Time = str_Time.rstrip('\\n\'')
        # print(date_time)
        return str_Time

    # 读取内存占用率 和 总内存
    # Read the memory usage and total memory
    def getUsagedRAM(self):
        cmd = "free | awk 'NR==2{printf \"RAM:%2d%% -> %.1fGB \", 100*($2-$7)/$2, ($2/1048576.0)}'"
        FreeRam = subprocess.check_output(cmd, shell=True)
        str_FreeRam = str(FreeRam).lstrip('b\'')
        str_FreeRam = str_FreeRam.rstrip('\'')
        return str_FreeRam

    # 读取空闲的内存 / 总内存
    # Read free memory/total memory
    def getFreeRAM(self):
        cmd = "free -h | awk 'NR==2{printf \"RAM: %.1f/%.1fGB \", $7,$2}'"
        FreeRam = subprocess.check_output(cmd, shell=True)
        str_FreeRam = str(FreeRam).lstrip('b\'')
        str_FreeRam = str_FreeRam.rstrip('\'')
        return str_FreeRam

    # 读取TF卡空间占用率 / TF卡总空间
    # Read the TF card space usage/TOTAL TF card space
    def getUsagedDisk(self):
        cmd = "df -h | awk '$NF==\"/\"{printf \"SDC:%s -> %.1fGB\", $5, $2}'"
        Disk = subprocess.check_output(cmd, shell=True)
        str_Disk = str(Disk).lstrip('b\'')
        str_Disk = str_Disk.rstrip('\'')
        return str_Disk

    # 读取空闲的TF卡空间 / TF卡总空间
    # Read the free TF card space/total TF card space
    def getFreeDisk(self):
        cmd = "df -h | awk '$NF==\"/\"{printf \"Disk:%.1f/%.1fGB\", $4,$2}'"
        Disk = subprocess.check_output(cmd, shell=True)
        str_Disk = str(Disk).lstrip('b\'')
        str_Disk = str_Disk.rstrip('\'')
        return str_Disk

    # 获取本机IP
    # Read the local IP address
    def getLocalIP(self):
        ip = os.popen(
            "/sbin/ifconfig eth0 | grep 'inet' | awk '{print $2}'").read()
        ip = ip[0: ip.find('\n')]
        if(ip == '' or len(ip) > 15):
            ip = os.popen(
                "/sbin/ifconfig wlan0 | grep 'inet' | awk '{print $2}'").read()
            ip = ip[0: ip.find('\n')]
            if(ip == ''):
                ip = 'x.x.x.x'
        if len(ip) > 15:
            ip = 'x.x.x.x'
        return ip

    # 设置要显示的电池电量百分比
    def setBatteryShow(self):
        if self.__dog == None:
            return
        if self.__battery_index == 1:
            self.__battery = self.__dog.read_battery()
            # if self.__debug:
            #     print("Read Battery:", self.__battery)
            self.__str_battery = "%d%%" % self.__battery
            if self.__battery <= 0:
                self.__str_battery = ""
            elif self.__battery < 10:
                self.__offset_battery = 116
            elif self.__battery < 100:
                self.__offset_battery = 110
            else:
                self.__offset_battery = 104
        self.add_text(self.__offset_battery, 0, self.__str_battery)
        self.__battery_index = self.__battery_index + 1
        if self.__battery_index >= 30:
            self.__battery_index = 0

    # oled主要运行函数，在while循环里调用，可实现热插拔功能。
    # Oled mainly runs functions that are called in a while loop and can be hot-pluggable
    def main_program(self):
        global str_Name
        try:
            cpu_index = 0
            state = self.begin()
            while state:
                self.clear()
                if self.__clear:
                    self.refresh()
                    return True
                #str_CPU = self.getCPULoadRate(cpu_index)
                #str_Time = self.getSystemTime()
                if cpu_index == 0:
                    #str_FreeRAM = self.getUsagedRAM()
                    #str_Disk = self.getUsagedDisk()
                    str_IP = "IP: " + self.getLocalIP()
                #self.add_text(0, 0, str_CPU)
                self.add_text(0, 0, str_Name)
                #self.add_text(50, 0, str_Time)
                self.setBatteryShow()
                #self.add_line(str_FreeRAM, 2)
                #self.add_line(str_Disk, 3)
                self.add_line(str_IP, 4)
                # Display image.
                self.refresh()
                cpu_index = cpu_index + 1
                if cpu_index >= 5:
                    cpu_index = 0
                time.sleep(.1)
            return False
        except:
            if self.__debug:
                print("!!!---OLED refresh error---!!!")
            return False


if __name__ == "__main__":
    try:
        g_dog = DOGZILLA()
        # g_dog = None
        oled_clear = False
        oled_debug = False
        state = False
        if len(sys.argv) > 1:
            if str(sys.argv[1]) == "clear":
                oled_clear = True
            elif str(sys.argv[1]) == "debug":
                oled_debug = True
        oled = Dogzilla_OLED(g_dog, clear=oled_clear, debug=oled_debug)

        while True:
            state = oled.main_program()
            oled.clear(True)
            if state:
                del oled
                print("---OLED CLEARED!---")
                break
            time.sleep(1)
    except KeyboardInterrupt:
        del oled
        print("---Program closed!---")
