# -*- coding: utf-8 -*-
import subprocess
import sys
import os
import time
import sched
import datetime
import random
import smtplib
from datetime import date
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
import configparser
import ocr_util
#日志同时输出到屏幕和文件
import logging
logger = logging.getLogger(__name__)
logger.setLevel(level = logging.INFO)
handler = logging.FileHandler("log/ding.txt")
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

console = logging.StreamHandler()
console.setLevel(logging.INFO)

logger.addHandler(handler)
logger.addHandler(console)


config = configparser.ConfigParser(allow_no_value=False)
config.read("dingding.cfg")
scheduler = sched.scheduler(time.time,time.sleep)
go_hour = int(config.get("time","go_hour"))
back_hour = int(config.get("time","back_hour"))
min_am = int(config.get("time","min_am"))
max_am = int(config.get("time","max_am"))
min_pm = int(config.get("time","min_pm"))
max_pm = int(config.get("time","max_pm"))

weekwork = config.get("file","weekwork")
holiday = config.get("file","holiday")

directory = config.get("ADB","directory")
sender = config.get("email","sender")
psw = config.get("email","psw")
receive = config.get("email","receive")
screen_dir = config.get("screen","screen_dir")
today = date.today().strftime("%Y-%m-%d")

# 打开钉钉，关闭钉钉封装为一个妆饰器函数
def with_open_close_dingding(func):
    def wrapper(self, *args, **kwargs):
        logger.info("点亮屏幕， 滑屏解锁")
        operation_list = [self.adbpower, self.adbclear]
        for operation in operation_list:
            process = subprocess.Popen(operation, shell=False,stdout=subprocess.PIPE)
            process.wait()
            time.sleep(2)
        logger.info("输入解锁密码")
        operation_list0 = [self.adbinput_p1, self.adbinput_p2, self.adbinput_p3, self.adbinput_p4, self.adbinput_p5, self.adbinput_p6]
        for operation in operation_list0:
            process = subprocess.Popen(operation, shell=False,stdout=subprocess.PIPE)
            process.wait()
            time.sleep(2)
        # 确保完全启动，并且加载上相应按键
        time.sleep(3)
        logger.info("打开钉钉")
        operation_list1 = [self.adbopen_dingding]
        for operation in operation_list1:
            process = subprocess.Popen(operation, shell=False,stdout=subprocess.PIPE)
            process.wait()
            time.sleep(3)
        time.sleep(5)
        # 包装函数
        func(self, *args, **kwargs)
        logger.info("关闭钉钉")
        operation_list2 = [self.adbback_index, self.adbkill_dingding, self.adbkill_wechat, self.adbpower]
        for operation in operation_list2:
            process = subprocess.Popen(operation, shell=False,stdout=subprocess.PIPE)
            process.wait()
        logger.info("kill dingding success")
    return wrapper


class dingding:

    # 初始化，设置adb目录
    def __init__(self,directory):

        self.filetime = "%s%s" % (date.today().strftime("%Y%m%d"), time.strftime("%H%M%S"))


        self.directory = directory
        # 点亮屏幕
        self.adbpower = '"%s\\adb" shell input keyevent 26' % directory
        # 滑屏解锁
        self.adbclear = '"%s\\adb" shell input swipe %s' % (directory,config.get("position","light_position"))
        # 输入密码(点击6次)
        self.adbinput_p1 = '"%s\\adb" shell input tap %s' % (directory,config.get("position","pwd_position"))
        self.adbinput_p2 = '"%s\\adb" shell input tap %s' % (directory,config.get("position","pwd_position"))
        self.adbinput_p3 = '"%s\\adb" shell input tap %s' % (directory,config.get("position","pwd_position"))
        self.adbinput_p4 = '"%s\\adb" shell input tap %s' % (directory,config.get("position","pwd_position"))
        self.adbinput_p5 = '"%s\\adb" shell input tap %s' % (directory,config.get("position","pwd_position"))
        self.adbinput_p6 = '"%s\\adb" shell input tap %s' % (directory,config.get("position","pwd_position"))
        # 启动钉钉应用
        self.adbopen_dingding = '"%s\\adb" shell monkey -p com.alibaba.android.rimet -c android.intent.category.LAUNCHER 1' %directory
        self.adbquickbutton_dingding = '"%s\\adb" shell input tap %s' % (directory,config.get("position","quickbutton"))
        self.adbquickopenbutton_dingding = '"%s\\adb" shell input tap %s' % (directory,config.get("position","openquick"))
        self.adbnormalbutton_dingding = '"%s\\adb" shell input tap %s' % (directory,config.get("position","normalbutton"))
        # 点击上班打卡
        self.adbclick_playgocard = '"%s\\adb" shell input tap %s' % (directory,config.get("position","playgo_position"))
        # 关闭钉钉
        self.adbkill_dingding = '"%s\\adb" shell am force-stop com.alibaba.android.rimet'% directory
        # 返回桌面
        self.adbback_index = '"%s\\adb" shell input keyevent 3' % directory
        # 点击工作
        self.adbselect_work = '"%s\\adb" shell input tap %s' % (directory,config.get("position","work_position"))
        # 滑屏到底
        self.adbscrbottom = '"%s\\adb" shell input swipe %s' % (directory,config.get("position","scrbottom_position"))
        # 点击考勤打卡
        self.adbselect_playcard = '"%s\\adb" shell input tap %s' % (directory,config.get("position","check_position"))
        # 点击下班打卡
        self.adbclick_playcard = '"%s\\adb" shell input tap %s' % (directory,config.get("position","play_position"))
        # 点击打卡备注
        self.adbclick_submit = '"%s\\adb" shell input tap %s' % (directory,config.get("position","submit_position"))



        # 启动WeChat 
        self.adbopen_wechat = '"%s\\adb" shell monkey -p com.tencent.mm -c android.intent.category.LAUNCHER 1' % directory
        # 点击选择聊天对象
        self.adbselect_chat = '"%s\\adb" shell input tap %s' % (directory,config.get("wechat","select_chat"))
        # 点击选择焦点输入
        self.adbfocus_text = '"%s\\adb" shell input tap %s' % (directory,config.get("wechat","focus_text"))
        # 回车
        self.adbenter = '"%s\\adb" shell input keyevent 66' % directory
        # 点击发送
        self.adbsend_msg = '"%s\\adb" shell input tap %s' % (directory,config.get("wechat","send_msg"))
        # 点击发送2
        self.adbsend_msg2 = '"%s\\adb" shell input tap %s' % (directory,config.get("wechat","send_msg2"))
        # 关闭WeChat
        self.adbkill_wechat = '"%s\\adb" shell am force-stop com.tencent.mm'% directory



        # 设备截屏保存到sdcard
        self.adbscreencap = '"%s\\adb" shell screencap -p sdcard/screen.png' % (directory)
        # 传送到计算机
        self.adbpull = '"%s\\adb" pull sdcard/screen.png %s%s/screen-%s.png' % (directory, screen_dir, today, self.filetime)
        # 删除设备截屏
        self.adbrm_screencap = '"%s\\adb" shell rm -r sdcard/screen.png' % (directory)

    # 点亮屏幕 》》解锁 》》打开钉钉
    def open_dingding(self):
        operation_list = [self.adbpower,self.adbclear,self.adbopen_dingding]
        for operation in operation_list:
            process = subprocess.Popen(operation, shell=False,stdout=subprocess.PIPE)
            process.wait()
            time.sleep(3)
        # 确保完全启动，并且加载上相应按键
        time.sleep(10)
        self.screencap("open_dingding")
        logger.info("open dingding success")


    # 返回桌面 》》 退出钉钉 》》 手机黑屏
    def close_dingding(self):
        operation_list = [self.adbback_index,self.adbkill_dingding,self.adbpower]
        for operation in operation_list:
            process = subprocess.Popen(operation, shell=False,stdout=subprocess.PIPE)
            process.wait()
            time.sleep(0.5)
        logger.info("kill dingding success")

    def close_open(self):
        logger.info("关闭钉钉重新打开")
        operation_list = [self.adbkill_dingding, self.adbopen_dingding]
        for operation in operation_list:
           process = subprocess.Popen(operation, shell=False,stdout=subprocess.PIPE)
           process.wait()
           time.sleep(5)        

    # 上班(极速打卡)
    @with_open_close_dingding
    def goto_work(self,minute):
        self.screencap("quickding")
        self.sendEmail(minute)
        # 识别图片
        _file = "%s%s/screen-%s.png" % (screen_dir, today, "quickding")
        for dirlist in os.walk("%s%s" % (screen_dir, today)):
            filelist = dirlist[2]
            filelist.reverse()
            _file = "%s%s/%s" % (screen_dir, today, filelist[0])
        if self.get_ocr_content(_file):
            logger.info("极速打卡成功")
        else:
            logger.info("极速打卡失败, 重新打卡")
            self.close_open()
            self.goto_work2(minute)

    # 上班(极速打卡失败?)
    @with_open_close_dingding
    def goto_work2(self, minute):
        self.openplaycard_interface()
        operation_list = [self.adbclick_playgocard]
        for operation in operation_list:
            process = subprocess.Popen(operation, shell=False,stdout=subprocess.PIPE)
            process.wait()
            time.sleep(3)
        self.screencap("normalding")
        self.sendEmail(minute)
        _file = "%s%s/screen-%s.png" % (screen_dir, today, "normalding")
        for dirlist in os.walk("%s%s" % (screen_dir, today)):
            filelist = dirlist[2]
            filelist.reverse()
            _file = "%s%s/%s" % (screen_dir, today, filelist[0])
        if self.get_ocr_content(_file):
            logger.info("正常上班打卡成功")
            self.wechatmsg("normal go work dingding ok!")
        else:
            logger.info("正常上班打卡失败, 重新打卡")
            self.wechatmsg("normal go work dingding fail! try again.")
            self.close_open()
            self.goto_work2(minute)

    # 打开打卡界面
    def openplaycard_interface(self):
        logger.info("打开打卡界面")
        operation_list = [self.adbselect_work, self.adbscrbottom, self.adbselect_playcard]
        for operation in operation_list:
            process = subprocess.Popen(operation, shell=False,stdout=subprocess.PIPE)
            process.wait()
            time.sleep(2)
        time.sleep(5)

    # 下班
    @with_open_close_dingding
    def after_work(self,minute):
        self.openplaycard_interface()
        operation_list = [self.adbclick_playcard]
        for operation in operation_list:
            process = subprocess.Popen(operation, shell=False,stdout=subprocess.PIPE)
            process.wait()
            time.sleep(3)
        self.screencap("afterding")
        self.sendEmail(minute)
        _file = "%s%s/screen-%s.png" % (screen_dir, today, "afterding")
        for dirlist in os.walk("%s%s" % (screen_dir, today)):
            filelist = dirlist[2]
            filelist.reverse()
            _file = "%s%s/%s" % (screen_dir, today, filelist[0])
        logger.info(_file)
        if self.get_ocr_content(_file):
            logger.info("下班打卡成功")
            self.wechatmsg("after dingding ok!")
        else:
            logger.info("下班打卡失败, 重新打卡")
            self.wechatmsg("after dingding fail! try again.")
            self.close_open()
            self.after_work(minute)

    # 只能发送单字节字符串(英文和符号)
    def wechatmsg(self, msg):

        operation_list1 = [self.adbopen_wechat]
        for operation in operation_list1:
            process = subprocess.Popen(operation, shell=False,stdout=subprocess.PIPE)
            process.wait()
            time.sleep(10)
            self.screencap2()
        # 确保完全启动，并且加载上相应按键
        time.sleep(3)
        logger.info("启动WeChat完成")
        operation_list2 = [self.adbselect_chat, self.adbfocus_text]
        for operation in operation_list2:
            process = subprocess.Popen(operation, shell=False,stdout=subprocess.PIPE)
            process.wait()
            time.sleep(5)
            self.screencap2()

        # adb shell am broadcast -a ADB_INPUT_TEXT --es msg
        adbmsg = '"%s\\adb" shell am broadcast -a ADB_INPUT_TEXT --es msg "%s"' % (directory, msg)
        operation_list = [adbmsg, self.adbsend_msg2]
        for operation in operation_list:
            process = subprocess.Popen(operation, shell=False,stdout=subprocess.PIPE)
            process.wait()
            time.sleep(5)
            self.screencap2()
        logger.info("发送wechat msg: {}, 关闭WeChat".format(msg))

    # 只能发送单字节字符串(英文和符号) 要先解锁
    def wechatmsg2(self, msg):

        logger.info("点亮屏幕， 滑屏解锁")
        operation_list = [self.adbpower, self.adbclear]
        for operation in operation_list:
            process = subprocess.Popen(operation, shell=False,stdout=subprocess.PIPE)
            process.wait()
            time.sleep(2)
        logger.info("输入解锁密码")
        operation_list0 = [self.adbinput_p1, self.adbinput_p2, self.adbinput_p3, self.adbinput_p4, self.adbinput_p5, self.adbinput_p6]
        for operation in operation_list0:
            process = subprocess.Popen(operation, shell=False,stdout=subprocess.PIPE)
            process.wait()
            time.sleep(2)

        operation_list1 = [self.adbopen_wechat]
        for operation in operation_list1:
            process = subprocess.Popen(operation, shell=False,stdout=subprocess.PIPE)
            process.wait()
            time.sleep(10)
            self.screencap2()
        # 确保完全启动，并且加载上相应按键
        time.sleep(3)
        logger.info("启动WeChat完成")
        operation_list2 = [self.adbselect_chat, self.adbfocus_text]
        for operation in operation_list2:
            process = subprocess.Popen(operation, shell=False,stdout=subprocess.PIPE)
            process.wait()
            time.sleep(5)
            self.screencap2()

        # adb shell am broadcast -a ADB_INPUT_TEXT --es msg
        adbmsg = '"%s\\adb" shell am broadcast -a ADB_INPUT_TEXT --es msg "%s"' % (directory, msg)
        operation_list3 = [adbmsg, self.adbsend_msg2]
        for operation in operation_list3:
            process = subprocess.Popen(operation, shell=False,stdout=subprocess.PIPE)
            process.wait()
            time.sleep(5)
        self.screencap2()
        logger.info("发送wechat msg: {}, 关闭WeChat".format(msg))

    # 截屏>> 发送到电脑 >> 删除手机中保存的截屏
    def screencap(self, capname):
        dt_rnd = "%s%s" % (date.today().strftime("%Y%m%d"), time.strftime("%H%M%S"))
        logger.info("today: {}".format(dt_rnd))
        if os.path.exists("%s%s" % (screen_dir, today)) == False:
            os.mkdir("%s%s" % (screen_dir, today))
        _capname = dt_rnd
        #if capname:
        #    _capname = capname
        self.adbpull = '"%s\\adb" pull sdcard/screen.png %s%s/screen-%s.png' % (directory, screen_dir, today, _capname)
        operation_list = [self.adbscreencap,self.adbpull,self.adbrm_screencap]
        for operation in operation_list:
            process = subprocess.Popen(operation, shell=False,stdout=subprocess.PIPE)
            process.wait()
            time.sleep(5)
        logger.info("screencap to computer success")

    def screencap2(self):
        logger.info("today: {}".format(today))
        if os.path.exists("%s%s" % (screen_dir, today)) == False:
            os.mkdir("%s%s" % (screen_dir, today))
        operation_list = [self.adbscreencap,self.adbpull,self.adbrm_screencap]
        for operation in operation_list:
            process = subprocess.Popen(operation, shell=False,stdout=subprocess.PIPE)
            process.wait()
            time.sleep(5)
        logger.info("screencap to computer success")

    # 识别图片
    def get_ocr_content(self, _file):
        str = ocr_util.get_ocr_str(_file)
        str = str.replace("\n", "")
        logger.info(str)
        idx = str.find("打卡成功")
        idx2 = str.find("极速打卡")
        if idx >=0 or idx2 >= 0:
            return True
        else:
            return False

    # 发送邮件（QQ邮箱）
    def sendEmail(self,minute):
        global today
        """
        qq邮箱 需要先登录网页版，开启SMTP服务。获取授权码，
        :return:
        """
        now_time = datetime.datetime.now().strftime("%H:%M:%S")
        today = date.today().strftime("%Y-%m-%d")
        message = MIMEMultipart('related')
        subject = '%s [%s]打卡 下次打卡随机分钟： %s' % (now_time, is_weekend(today, False), str(minute))
        message['Subject'] = subject
        message['From'] = "日常打卡"
        message['To'] = receive
        html = '<html><body>{}</body></html>'

        try:
            for finfo in os.walk("%s%s" % (screen_dir, today)):
                logger.info(finfo)
                img_html = ''
                for fname in finfo[2]:
                    filepath = "{}/{}".format(finfo[0], fname)
                    if os.path.exists(filepath):
                        file = open(filepath, "rb")
                        img_data = file.read()
                        file.close()
                        img = MIMEImage(img_data)
                        img.add_header('Content-ID', fname)
                        message.attach(img)
                        img_html = '%s<img width="300px" src="cid:%s" alt="%s">' % (img_html, fname, fname)
                content = MIMEText(html.format(img_html), 'html', 'utf-8')
                message.attach(content)
        except FileNotFoundError:
            logger.info("File is not found.")
        except PersmissionError:
            logger.info("You don't have permission to access this file.")

        try:
            server = smtplib.SMTP_SSL("smtp.163.com", 465)
            server.login(sender, psw)
            server.sendmail(sender, receive, message.as_string())
            server.quit()
            del message
            logger.info("邮件发送成功")
        except smtplib.SMTPException as e:
            logger.info(e)

# 发送邮件（QQ邮箱）
    def sendEmailTips(self,minute):
        global today
        """
        qq邮箱 需要先登录网页版，开启SMTP服务。获取授权码，
        :return:
        """
        now_time = datetime.datetime.now().strftime("%H:%M:%S")
        today = date.today().strftime("%Y-%m-%d")
        message = MIMEMultipart('related')
        subject = '即将在%s分钟后开始打卡' % (minute)
        message['Subject'] = subject
        message['From'] = "打卡前提醒"
        message['To'] = receive
        content = ""

        try:
            server = smtplib.SMTP_SSL("smtp.163.com", 465)
            server.login(sender, psw)
            server.sendmail(sender, receive, message.as_string())
            server.quit()
            logger.info("{}分钟前的邮件提醒".format(minute))
        except smtplib.SMTPException as e:
            logger.info(e)

# 随机打卡时间段
def random_minute():
    nowhour = datetime.datetime.now().hour
    if nowhour >= go_hour and nowhour < back_hour:
        return random.randint(min_pm, max_pm)
    else:
        return random.randint(min_am, max_am)

# 包装循环函数，传入随机打卡时间点
def incode_loop(func,minute):
    """
    包装start_loop任务调度函数，主要是为了传入随机分钟数。保证在不打卡的情况下能保持分钟数不变。
    :param func: star_loop
    :param minute: 随机分钟数
    :return: None
    """
    dingding(directory).filetime = "%s%s" % (date.today().strftime("%Y%m%d"), time.strftime("%H%M%S"))
    logger.info("邮件接收地址{} {}".format(receive, dingding(directory).filetime))
    nowhour = datetime.datetime.now().hour

    # 判断时间当超过上班时间则打下班卡。否则则打上班卡。
    msg = wemsg = ""
    if  nowhour >= go_hour and nowhour < back_hour:
        # 用来分类上班和下班。作为参数传入任务调度
        hourtype = 1
        msg = "下次将在{}:{}打卡".format(str(back_hour), str(minute))
        wemsg = "Next time will dingding on %s:%s" % (str(back_hour), str(minute))
    else:
        hourtype = 2
        msg = "下次将在{}:{}打卡".format(str(go_hour), str(minute))
        wemsg = "Next time will dingding on %s:%s" % (str(go_hour), str(minute))
    logger.info(msg)
    #dingding(directory).wechatmsg2(wemsg)
    #执行任务调度函数
    func(hourtype,minute)


# 任务调度
def start_loop(hourtype,minute):
    global today
    """
    每次循环完成，携带生成的随机分钟数来再次进行循环，当打卡后，再重新生成随机数
    :param hourtype: 设置的上班时间点
    :param minute: 随机生成的分钟数（30-55）
    :return: None
    """
    now_time = datetime.datetime.now()

    today = date.today().strftime("%Y-%m-%d")

    #random_time = random_minute()
    #dingding(directory).after_work(now_time.minute)
    #scheduler.enter(0, 0, incode_loop,(start_loop,random_time,))

    now_hour = now_time.hour
    now_minute = now_time.minute

    current_time = int(time.time())

    # 上班，不是周末（双休），小时对应，随机分钟对应
    if hourtype == 2 and now_hour == go_hour and now_minute == minute and is_weekend(today):
        random_time = random_minute()
        dingding(directory).goto_work2(random_time)
        scheduler.enter(0,0,incode_loop,(start_loop,random_time,))
    if hourtype == 1 and now_hour == back_hour and now_minute == minute and is_weekend(today):
        random_time = random_minute()
        dingding(directory).after_work(random_time)
        scheduler.enter(0, 0, incode_loop,(start_loop,random_time,))
    else:
        # if now_hour - 2 >= go_hour or now_hour -2 >= back_hour:
        #     try:
        #         sys.exit(0)
        #     finally:
        #         print("时间还没到, 退出程序")
        next_dktime_str = "{} {}".format(date.today().strftime("%Y-%m-%d"), time.strftime("%H:%M:%S"))
        next_dktime = 0
        #  0 - 9
        if now_hour <= go_hour and hourtype == 2:
                next_dktime_str = "{} {}:{}:{}".format(datetime.date.today().strftime("%Y-%m-%d"), go_hour, minute, 0)
        elif go_hour < now_hour <= back_hour and hourtype == 1:
                next_dktime_str = "{} {}:{}:{}".format(datetime.date.today().strftime("%Y-%m-%d"), back_hour, minute, 0)
        else:
            # 早上, 明天 +1
            next_dktime_str = "{} {}:{}:{}".format((datetime.date.today() + datetime.timedelta(days=1)).strftime("%Y-%m-%d"), go_hour, minute, 0)
        next_dktime = int(time.mktime(time.strptime(next_dktime_str, "%Y-%m-%d %H:%M:%S")))

        only_minute = int((next_dktime - current_time) / 60)

        tip_msg = "now: {}:{} -- next_minute: {} -- only_minute: {} -- {} {}".format(now_hour, now_minute, minute, only_minute, is_weekend(today, False, False), next_dktime_str)
        
        logger.info(tip_msg)
        #dingding(directory).wechatmsg2(tip_msg)
        if only_minute in [5, 10, 15, 30, 60, 500, 900, 1200, 1500]:
            dingding(directory).sendEmailTips(only_minute)
            dingding(directory).wechatmsg2(tip_msg)
        scheduler.enter(60,0,start_loop,(hourtype,minute,))

# 即时执行
def need_now():
    global today

    now_time = datetime.datetime.now()
    today = date.today().strftime("%Y-%m-%d")
    now_hour = now_time.hour
    now_minute = now_time.minute

    #dingding(directory).goto_work(now_minute)

    if now_hour >= go_hour and now_hour <= 12:
        dingding(directory).goto_work2(now_minute)
    elif now_hour == back_hour:
        dingding(directory).after_work(now_minute)
    else:
        dingding(directory).after_work(now_minute)
        #logger.info("不是上下班时间~")

# 是否是周末
def is_weekend(today, b = True, zh = True):
    """
    :return: if weekend return False else return True
    """
    now_time = datetime.datetime.now().strftime("%w")
    if is_weekendwork_holiday(today, weekwork):
        s = "{} 周末补班".format(today)
        logger.info(s)
        if b:
            return True
        else:
            if zh:
                return s
            else:
                return "%s weekend work" % today
    elif is_weekendwork_holiday(today, holiday):
        s = "{} 节假日哦".format(today)
        logger.info(s)
        if b:
            return False
        else:
            if zh:
                return s
            else:
                return "%s holidays not work" % today
    elif now_time == "6" or now_time == "0":
        s = "{} 周末休息".format(today)
        logger.info(s)
        if b:
            return False
        else:
            if zh:
                return s
            else:
                return "%s weekend not work" % today
    else:
        s = "{} 正常工作日".format(today)
        logger.info(s)
        if b:
            return True
        else:
            if zh:
                return s
            else:
                return "%s normal is work" % today

# 是否是周末且工作日1 或 节假日2
def is_weekendwork_holiday(today, filename):
    fo = open(filename, 'r')
    lines = fo.readlines()
    fo.close()

    for line in lines:
        line = line.strip()
        if line == today:
            return True
    return False


if __name__ == "__main__":

    # ======formal
    if len(sys.argv) > 1:
        #dingding.sendEmail('', 1)
        need_now()
    else:

        scheduler.enter(0,0,incode_loop,(start_loop,random_minute(),))
        scheduler.run()

    #dingding.sendEmail('', 1)
    # ====test
    # dingding  = dingding(directory)
    # dingding.goto_work(12)
    # ==== weekend
    # print(is_weekend())
