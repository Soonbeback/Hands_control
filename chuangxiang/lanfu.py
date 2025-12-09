from helloFly import fly
from helloAi import init as Ai
from atexit import register
from threading import Thread
import time
import socket
import json
import importlib.util
import sys
pyc_path = '__pycache__/lanfu.cpython-38.pyc'
spec = importlib.util.spec_from_file_location("example", pyc_path)
module = importlib.util.module_from_spec(spec)
sys.modules["example"] = module
spec.loader.exec_module(module)

f = fly()


# 无人机基础类
class Drone:

    def __init__(self, d_id: int = 0) -> None:
        '''
        d_id: 无人机编号
        '''
        self.d_id = d_id
        self.ai = Ai()
        register(self.land)
        self.h_speed = 90
        self.v_speed = 70
        self.wait_status = True
        self.mode_status = '光流定位'
        self.locate_mode(0)
        f.setAutoDelay(d_id, 0)
        self.auto_wait(True)
        f.ledCtrl(d_id, 0, [0, 0, 0])
        self.drone_status = False
        self.start_time = 0.00
        self.end_time = 0.00
        print("\n\033[1;30m{d_id}号无人机初始化完成\033[0m".format(
            d_id=self.d_id))

    # 等待

    def sleep(self, sec) -> None:
        f.sleep(sec)

    # 计时器

    def timer(self) -> None:
        f.getTimer()

    # 计时器清零

    def clear_timer(self) -> None:
        f.getTimer()

    # 语音播报

    def tts(self, string, wait=True) -> None:
        f.tts(string, wait)


# *************************塔台类*************************************

    # 连接塔台

    def connect_ct(self, host: str = '192.168.1.1', port: int = 8000) -> bool:
        '''
        host: 塔台IP地址
        port: 塔台端口
        '''
        tc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        addr = (host, port)
        tc.connect(addr)
        if tc:
            data = {
                "status": True,
                "res": tc
            }
            self.con_res = data
        else:
            print("\n\033[1;30m塔台连接失败，请检查IP地址和端口\033[0m")
            data = {
                "status": False
            }
            self.con_res = data

    # 发送数据
    def send_data(self, content):
        tc = self.con_res.get('res')
        response_data = {
            "msg": content
        }
        response = json.dumps(response_data).encode()
        tc.send(response)

    # 接收数据

    def get_data(self):
        tc = self.con_res.get('res')
        data = tc.recv(1024).decode()
        return json.loads(data)

    # 关闭连接
    def close(self):
        self.tc.close()

    # 塔台连接结果

    def connect_result(self):
        res = self.con_res.get('status')
        if res:
            print("\n\033[1;30m塔台连接成功\033[0m")
        else:
            print("\n\033[1;30m塔台连接失败，请检查IP地址和端口\033[0m")
        return res

    # 请求起飞

    def ask_take_off(self):
        self.send_data('take_off')
        while True:
            msg = self.get_data()
            if msg.get('msg'):
                print("\n\033[1;30m塔台回应：允许起飞，3秒后开始计时！\033[0m")
                time.sleep(1)
                for i in range(0, 3):
                    print("\n\033[1;30m倒计时：" + str(3-i) + "s\033[0m")
                    time.sleep(1)
                self.start_time = time.time()
                return True
            else:
                print("\n\033[1;30m塔台回应：禁止起飞！\033[0m")
                return False

    # 请求降落

    def ask_land(self):
        self.send_data('land')
        while True:
            msg = self.get_data()
            if msg.get('msg'):
                print("\n\033[1;30m塔台回应：允许降落，3秒后结束计时！\033[0m")
                time.sleep(1)
                for i in range(0, 3):
                    print("\n\033[1;30m倒计时：" + str(3-i) + "s\033[0m")
                    time.sleep(1)
                self.end_time = time.time()
                fly_time = self.end_time - self.start_time
                # 飞行时间（保留两位小数）
                fly_time = round(fly_time, 2)
                print("\n\033[1;30m最终飞行时间为：{fly_time}\033[0m".format(
                    fly_time=str(fly_time)))
                return True
            else:
                print("\n\033[1;30m塔台回应：禁止降落！\033[0m")
                return False


# **********************无人机设置类***********************************

    # 设置自动等待

    def auto_wait(self, status: bool = True) -> None:
        '''
        status: 自动等待状态, 打开: True; 关闭: False
        '''
        self.wait_status = status

    # 计算飞行时间

    def fly_sleep(self, distance, speed, add: int = 1.5) -> None:
        if self.wait_status:
            num = 1 / speed
            time1 = round(distance * num + add, 2)
            time.sleep(time1)

    # 设置定位模式

    def locate_mode(self, mode: int = 0) -> None:
        """
        mode: 飞行模式
        光流定位: 0
        标签定位: 1
        巡线模式: 2
        """
        f.flyMode(self.d_id, mode)
        if mode == 0:
            mode = '光流定位'
        elif mode == 1:
            mode = '标签定位'
            time.sleep(1)
        elif mode == 2:
            mode = '巡线模式'
        self.mode_status = mode

    # 设置飞行速度

    def speed(self, h: int = 0, v: int = 0) -> None:
        """
        h: 水平飞行速度
        v: 垂直飞行速度
        """
        if h != 0:
            self.h_speed = h
        f.xySpeed(self.d_id, self.h_speed)

        if v != 0:
            self.v_speed = v
        f.zSpeed(self.d_id, self.v_speed)

    # 锁定无人机机头方向

    def lock_dir(self, status: int = 0) -> None:
        '''
        status: 锁定或者解锁无人机机头方向
        锁定: 0
        解锁: 1
        '''
        f.lockDir(self.d_id, status)

    # 调整无人机重心偏移

    def barycenter(self, value: list = [0, 0]) -> None:
        f.setCenterOffset(self.d_id, value)

    # 设置当前坐标点

    def set_location(self, value: list = [0, 0]) -> None:
        '''
        value: 坐标列表
        '''
        f.setLocation(self.d_id, value)

    # 设置标签间距

    def set_tag_distance(self, value: int = 50) -> None:
        '''
        value: 标签的间距
        '''
        f.setTagDistance(self.d_id, value)


# **********************无人机飞行类***********************************

    # 校准

    def calibrate(self) -> None:
        f.flyCtrl(self.d_id, 4)

    # 起飞

    def take_off(self, height: int = 90) -> None:
        if self.drone_status == False:
            self.drone_status = True
            f.takeOff(self.d_id, height)
            self.fly_sleep(height, self.v_speed, 2)

    # 降落

    def land(self) -> None:
        if self.drone_status:
            f.flyCtrl(self.d_id, 0)
            self.drone_status = False

    # 飞行高度

    def height(self, distance: int = 90) -> None:
        '''
        distance: 无人机的高度
        '''
        f.flyHigh(self.d_id, distance)
        self.fly_sleep(distance, self.v_speed, 1)

    # 光流定位飞行

    def fly(self, direction: int = 1, distance: int = 100) -> None:
        '''
        direction: 方向, 前: 1; 后: 2; 左: 3; 右: 4; ↖: 7; ↗: 8; ↙: 9; ↘: 10
        distance: 距离
        '''
        if self.mode_status == '标签定位':
            self.locate_mode()
        f.moveCtrl(self.d_id, direction, distance)
        self.fly_sleep(distance, self.h_speed)

    # 飞行并扫描标签

    def fly_tag(self, direction: int = 1, distance: int = 100, tag: int = 0) -> None:
        '''
        direction: 方向, 前: 1; 后: 2; 左: 3; 右: 4; ↖: 7; ↗: 8; ↙: 9; ↘: 10
        distance: 距离
        tag: 要扫描的标签号
        '''
        f.moveSearchTag(self.d_id, direction, distance, tag)
        self.fly_sleep(distance, self.h_speed)

    # 飞行并跟随标签

    def follow_tag(self, direction: int = 1, distance: int = 100, tag: int = 0) -> None:
        '''
        direction: 方向, 前: 1; 后: 2; 左: 3; 右: 4; ↖: 7; ↗: 8; ↙: 9; ↘: 10
        distance: 距离
        tag: 要跟随的标签号
        '''
        f.moveFollowTag(self.d_id, direction, distance, tag)

    # 巡线飞行

    def search_line(self, direction: int = 1, distance: int = 100, isCheck: bool = False) -> None:
        '''
        direction: 方向, 前: 1; 后: 2; 左: 3; 右: 4; ↖: 7; ↗: 8; ↙: 9; ↘: 10
        distance: 距离
        isCheck: 是否开启终点标签检测
        '''
        wx = self.wait_status
        self.wait_status = False
        self.locate_mode(2)
        time.sleep(0.1)
        self.fly(direction, distance)
        time.sleep(1)
        if isCheck:
            self.check_tag()
            while True:
                if self.exist_tag():
                    self.fly_tag(1, 0, self.get_tag())
                    time.sleep(2)
                    break
        else:
            self.wait_status = True
            self.fly_sleep(distance, self.h_speed, 2)

        print("\n\033[1;30m{d_id}号无人机, 巡线完成\033[0m".format(d_id=self.d_id))

        self.wait_status = wx
        self.speed(self.h_speed, self.v_speed)

    # 巡色线飞行

    def search_color_line(self, direction: int = 1, distance: int = 100, color: list = [0, 0, 0, 0, 0, 0], isCheck: bool = False) -> None:
        '''
        direction: 方向, 前: 1; 后: 2; 左: 3; 右: 4; ↖: 7; ↗: 8; ↙: 9; ↘: 10
        distance: 距离
        color：颜色阙值
        tag_id: 终点标签号
        '''
        wx = self.wait_status
        self.wait_status = False
        self.locate_mode(2)
        time.sleep(0.1)
        f.mvCheckBlob(self.d_id, 5, color)
        time.sleep(0.1)
        self.fly(direction, distance)
        time.sleep(3)
        if isCheck:
            self.check_tag()
            while True:
                if self.exist_tag():
                    self.fly_tag(1, 0, self.get_tag())
                    time.sleep(2)
                    break
        else:
            self.wait_status = True
            self.fly_sleep(distance, self.h_speed, 2)

        print("\n\033[1;30m{d_id}号无人机, 巡色线完成\033[0m".format(d_id=self.d_id))

        self.wait_status = wx
        self.speed(self.h_speed, self.v_speed)

    # 飞行并扫描色块

    def fly_color(self, direction: int = 1, distance: int = 100, color: list = [0, 0, 0, 0, 0, 0]) -> None:
        '''
        direction: 方向, 前: 1; 后: 2; 左: 3; 右: 4; ↖: 7; ↗: 8; ↙: 9; ↘: 10
        distance: 距离
        color: 6位颜色阙值
        '''
        f.moveSearchBlob(self.d_id, direction, distance, color)
        self.fly_sleep(distance, self.h_speed, 2)

    # 飞行并扫描黑色色块

    def fly_black(self, direction: int = 1, distance: int = 100) -> None:
        '''
        direction: 方向, 前: 1; 后: 2; 左: 3; 右: 4; ↖: 7; ↗: 8; ↙: 9; ↘: 10
        distance: 距离
        '''
        f.moveSearchDot(self.d_id, direction, distance)
        self.fly_sleep(distance, self.h_speed, 2)

    # 以秒数，从当前/目标位置飞往坐标xyz

    def fly_xyz(self, sec: int, l: int = 0, xyz: list = [0, 0, 0]) -> None:
        '''
        xyz: 空间直角坐标点, 列表
        '''
        f.move(0, l, xyz)
        time.sleep(sec)


    # 顺时针向前半正方形
    def f_forword(self, distance):
        wx = self.wait_status
        self.wait_status = True
        self.fly(1, distance)
        self.fly(4, distance)
        self.wait_status = wx


    # 顺时针向后半正方形
    def f_back(self, distance):
        wx = self.wait_status
        self.wait_status = True
        self.fly(2, distance)
        self.fly(3, distance)
        self.wait_status = wx


    # 顺时针向前半圆
    def semicircle_forword(self, distance, sec):
        self.fly(3, distance)
        self.sleep(sec)
        self.fly(1, distance)
        self.sleep(sec)
        self.fly(1, distance)
        self.sleep(sec)
        self.fly(4, distance)
        self.sleep(sec)


    # 顺时针向后半圆
    def semicircle_back(self, distance, sec):
        self.fly(4, distance)
        self.sleep(sec)
        self.fly(2, distance)
        self.sleep(sec)
        self.fly(2, distance)
        self.sleep(sec)
        self.fly(3, distance)
        self.sleep(sec)


    # 直达坐标xyz
    def to_xyz(self, xyz: list = [0, 0, 0]) -> None:
        '''
        xyz: 空间直角坐标点, 列表
        '''
        f.goTo(0, xyz)

    # 直达标签，且调整高度

    def to_tag_height(self, tag: int = 0, height: int = 100) -> None:
        '''
        tag: 标签号
        height: 无人机高度
        '''
        f.goToTag(0, tag, height)

    # 旋转

    def rotate(self, angle: int) -> None:
        '''
        angle: 旋转度数, 正数为顺时针, 负数为逆时针
        '''
        self.locate_mode(0)
        f.rotation(self.d_id, angle)
        time.sleep(angle / 30)

    # 刹车

    def brake(self) -> None:
        f.flyCtrl(self.d_id, 1)

    # 悬停

    def hover(self) -> None:
        f.flyCtrl(self.d_id, 2)

    # 急停

    def scram(self) -> None:
        f.flyCtrl(self.d_id, 3)

    # 翻转

    def flip(self, direction: int = 0, num: int = 1) -> None:
        '''
        direction: 方向, 前: 1; 后: 2; 左: 3; 右: 4; ↖: 7; ↗: 8; ↙: 9; ↘: 10
        num: 圈数
        '''
        f.flipCtrl(self.d_id, direction, num)


# **********************拓展模块控制类***********************************

    # 打开灯光

    def open_led(self, mode: int, color: list = [0, 0, 0]) -> None:
        '''
        mode: 灯光模式
        常亮: 0
        呼吸灯: 1
        七彩变幻: 2
        color: RGB颜色, 列表
        '''
        f.ledCtrl(self.d_id, mode, color)
        time.sleep(0.1)

    # 关闭灯光

    def close_led(self) -> None:
        f.ledCtrl(self.d_id, 0, [0, 0, 0])
        time.sleep(0.1)

    # 射击

    def shoot(self, status: int = 0) -> None:
        '''
        status: 射击状态
        单次射击: 0
        连续射击: 1
        停止射击: 2
        '''
        f.shootCtrl(self.d_id, status)
        time.sleep(1)

    # 磁吸装置

    def magnet(self, status: int = 0) -> None:
        '''
        status: 磁吸装置状态
        关闭: 0
        打开: 1
        '''
        f.magnetCtrl(self.d_id, status)
        time.sleep(0.5)

    # 机械爪

    def servo(self, num=None) -> None:
        '''
        num: 角度
        '''
        f.servoCtrl(self.d_id, num)
        time.sleep(0.5)


# **********************人工智能***********************************

    # 拍照

    def take_photo(self):
        f.isDelay = True
        f.photographMode(self.d_id, 1)
        f.isDelay = False

    # 颜色采集
    def gather_color(self):
        f.isDelay = True
        f.photographMode(self.d_id, 2)
        f.isDelay = False

    # 拍照回传
    def get_photo(self) -> bool:
        return f.photoOk()

    # 识别文字
    def ai_text(self):
        self.ai.runFunction('文字识别')

    # 识别物体
    def ai_body(self):
        self.ai.runFunction('物体识别')

    # 识别人脸
    def ai_face(self):
        self.ai.runFunction('人脸识别')

    # 判断是否识别完成
    def exist_ai(self) -> bool:
        return self.ai.isComplete()

    # 文字识别结果
    def ai_text_result(self):
        return self.ai.result("文字内容")

    # 物体个数识别结果
    def ai_body_result(self):
        return self.ai.result("物体个数")

    # 人脸个数识别结果
    def ai_face_result(self):
        return self.ai.result("人脸张数")

    # 人脸名称
    def ai_face_name(self, num):
        return self.ai.resultFace(num, "名字")

    # 物体名称
    def ai_body_name(self, num):
        return self.ai.resultObject(num, "名称")

    # 物体周长
    def ai_body_per(self, num):
        return self.ai.resultObject(num, "周长")

    # 物体面积
    def ai_body_area(self, num):
        return self.ai.resultObject(num, "面积")

    # 物体长
    def ai_body_length(self, num):
        return self.ai.resultObject(num, "长")

    # 物体宽
    def ai_body_Width(self, num):
        return self.ai.resultObject(num, "宽")


# **********************无人机检测类***********************************

    # 检测色线

    def check_color_line(self, color: list = [0, 0, 0, 0, 0, 0]) -> None:
        f.mvCheckBlob(self.d_id, 5, color)

    # 检测黑线

    def check_black_line(self) -> None:
        f.mvCheckMode(self.d_id, 2)

    # 检测标签

    def check_tag(self) -> None:
        f.mvCheckMode(self.d_id, 3)

    # 检测标签号

    def check_tagId(self, tag: int) -> None:
        '''
        tag: 标签号
        '''
        f.mvCheckTag(self.d_id, tag)

    # 检测二维码

    def check_qr(self) -> None:
        f.mvCheckMode(self.d_id, 7)

    # 检测条形码

    def check_br(self) -> None:
        f.mvCheckMode(self.d_id, 8)

    # 检测颜色

    def check_color(self, color: list = [0, 0, 0, 0, 0, 0]) -> None:
        '''
        color: 6位颜色阙值, 列表
        '''
        f.mvCheckBlob(self.d_id, 4, color)

    # 判断是否检测到黑线

    def exist_black_line(self, direction: int = 0) -> bool:
        '''
        direction: 方向, 前: 0; 后: 1; 左: 2; 右: 3
        '''
        res = f.isMvCheckLine(self.d_id, direction)
        return res

    # 判断是否检测到标签

    def exist_tag(self) -> bool:
        res = f.isMvCheck(self.d_id, 4)
        return res

    # 判断是否检测到二维码

    def exist_qr(self) -> bool:
        res = f.isMvCheck(self.d_id, 6)
        return res

    # 判断是否检测到条形码

    def exist_br(self) -> bool:
        res = f.isMvCheck(self.d_id, 7)
        return res

    # 判断是否检测到颜色

    def exist_color(self) -> bool:
        res = f.isMvCheck(self.d_id, 5)
        print(res)
        return res


# **********************获取无人机参数类***********************************

    # 获取被按下的遥控器按钮

    def get_press(self, key_id) -> None:
        f.getKeyPress(key_id)

    # 获取无人机到障碍物的距离

    def get_distance(self, direction: int = 0) -> int:
        '''
        direction: 方向, 前: 1; 后: 2; 左: 3; 右: 4; ↖: 7; ↗: 8; ↙: 9; ↘: 10
        '''
        res = f.getObsDistance(self.d_id, direction)
        return res

    # 获取检测到的标签号

    def get_tag(self) -> int:
        res = f.getFlySensor(self.d_id, "tagID")
        return res

    # 获取检测到的二维码

    def get_qr(self) -> int:
        res = f.getFlySensor(self.d_id, "qrCode")
        return res

    # 获取检测到的条形码

    def get_br(self) -> int:
        res = f.getFlySensor(self.d_id, "brCode")
        return res

    # 获取横滚角

    def get_rol(self) -> int:
        res = f.getFlySensor(self.d_id, "rol")
        return res

    # 获取俯仰角

    def get_pit(self) -> int:
        res = f.getFlySensor(self.d_id, "pit")
        return res

    # 获取偏航角

    def get_yaw(self) -> int:
        res = f.getFlySensor(self.d_id, "yaw")
        return res

    # 获取横坐标

    def get_x(self) -> int:
        res = f.getFlySensor(self.d_id, "loc_x")
        return res

    # 获取纵坐标

    def get_y(self) -> int:
        res = f.getFlySensor(self.d_id, "loc_y")
        return res

    # 获取无人机高度

    def get_height(self) -> int:
        res = f.getFlySensor(self.d_id, "loc_z")
        return res

    # 获取横坐标误差

    def get_x_err(self) -> int:
        res = f.getFlySensor(self.d_id, "err_x")
        return res

    # 获取纵坐标误差

    def get_y_err(self) -> int:
        res = f.getFlySensor(self.d_id, "err_y")
        return res

    # 获取无人机高度误差

    def get_height_err(self) -> int:
        res = f.getFlySensor(self.d_id, "err_z")
        return res

    # 获取无人机电量

    def get_battery(self) -> int:
        num = round(f.getFlySensor(self.d_id, "vol"), 1)
        if num == 4.2:
            res = 100
        elif num == 4.1:
            res = 85
        elif num == 4.0:
            res = 70
        elif num == 3.9:
            res = 55
        elif num == 3.8:
            res = 40
        elif num == 3.7:
            res = 25
        else:
            res = 10
        print("\n\033[1;30m{d_id}号无人机当前的电量还剩：{res}%\033[0m".format(
            d_id=self.d_id, res=res))
        return res

    # 获取色块的参数

    def get_color_type(self, type: int = 0) -> int:
        '''
        type: 参数类型
        面积: s
        长度: w
        宽度: h
        '''
        if type == 0:
            type = 's'
        elif type == 1:
            type = 'w'
        elif type == 2:
            type = 'h'
        res = f.getBlobResult(self.d_id, type)
        return res


# 开启多线程
def run(obj1, obj2) -> None:
    thread1 = Thread(target=obj1)
    thread2 = Thread(target=obj2)
    thread1.start()
    thread2.start()
