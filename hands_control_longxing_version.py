import cv2
from hand_process import HandDetector
import threading
import time
# from helloFly import fly
from TuXingKeJi.TuXingSDK import TuXingSDK
from TuXingKeJi.enumHelper import Color, State, Land, SPED, Dir, Rotate, OFFON
from TuXingKeJi.peripheral import Peripheral
from TuXingKeJi.serialHelper import find_serial_port
from numpy.random import permutation
from scipy.signal import periodogram

#fh=fly()
#fh.setAutoDelay(0,0)

port_name = find_serial_port()
print(port_name)
if len(port_name)>0:
    peripheral = Peripheral(port_name[0])
    FLY = TuXingSDK(peripheral)
    FLY.start()
    time.sleep(0.5)
    FLY.init_uav()
else:
    print("串口调用错误")
    exit()

left_hand_top_x = 110
left_hand_top_y = 190
left_hand_bottom_x = 210
left_hand_bottom_y = 290

right_hand_top_x = 430
right_hand_top_y = 190
right_hand_bottom_x = 530
right_hand_bottom_y = 290

interval = 15

take_off = False

cap = cv2.VideoCapture(0)
detector = HandDetector()

tip_ids = [4,8,12,16,20]


def draw_rect(img):
    for i in range(6):
        cv2.rectangle(img, (left_hand_top_x - interval*i, left_hand_top_y - interval*i),
                      (left_hand_bottom_x + interval*i, left_hand_bottom_y + interval*i),
                      (0, 255, 0), 1, 4)
        cv2.rectangle(img, (right_hand_top_x - interval * i, right_hand_top_y - interval * i),
                      (right_hand_bottom_x + interval * i, right_hand_bottom_y + interval * i),
                      (0, 255, 0), 1, 4)

def took_off(sun):
    global take_off
    if len(sun) > 0:
        # 先定义一个空列表，用户存放0和1,0表示手指闭合，1表示手指张开
        fingers = []
        # 遍历5根手指的指尖
        for tid in tip_ids:
            # 取出指尖的x坐标和y坐标
            x, y = sun[tid][1], sun[tid][2]
            # 在指尖上画一个圆
            # cv2.circle(img, (x, y), 10, (0, 255, 0), cv2.FILLED)
            # 如果是大拇指
            if tid == 4:
                # 如果大拇指指尖的x位置大于第二个关节的第二个位置，则认为大拇指打开
                if sun[tid][1] > sun[tid - 1][1]:
                    # 给fingers列表添加一个1元素，表示一个手指张开，识别到的数字就加一
                    fingers.append(1)
                else:
                    # 给fingers列表添加一个0元素，表示一个手指闭合，识别到的数字就不变
                    fingers.append(0)
            # 如果是其他手指
            else:
                # 如果这些手指的指尖的y位置大于第二关节的位置，则认为这个手指打开，否则认为这个手指关闭
                if sun[tid][2] < sun[tid - 2][2]:
                    fingers.append(1)
                else:
                    fingers.append(0)

        # 判断有几个手指打开
        cnt = fingers.count(1)
        print("起飞测试手指数：", cnt)
        x, y= sun[8][1],sun[8][2]
        if cnt == 5:
            if 190 < y < 290 and 110 < x < 210:
                #fh.takeOff(0,100)
                FLY.take_off(100)
                time.sleep(3)
                print("起飞")
                #time.sleep(2)
                take_off = True

def set_z_speed(sun):
    speed = 20
    if len(sun)>0:
        y=sun[8][2]
        if 190 > y > 115:
            speed = ((190-y)//15+1)*20

        elif 290 < y < 365:
            speed = ((y-290)//15+1)*20
        #fh.zSpeed(0, speed)
        print("飞行速度：",speed)

def vertical_movement(sun):
    if len(sun) > 0:
        y = sun[8][2]
        if 190 > y > 115:
            set_z_speed(sun)
            #fh.moveCtrl(0, 5, 20)
            #fh.sleep(0.3)
            FLY.move_Ctrl_cm(Dir.UP, 20)
            time.sleep(0.3)
            print("向上飞20cm")
        elif 290 < y < 365:
            set_z_speed(sun)
            #fh.moveCtrl(0, 6, 20)
            #fh.sleep(0.3)
            FLY.move_Ctrl_cm(Dir.DOWN, 20)
            time.sleep(0.3)
            print("向下飞20cm")

def horizontal_movement(sun):
    if len(sun)>0:
        x, y=sun[8][1], sun[8][2]
        if 430<x<530:
            if 115<y<190:
                #fh.moveCtrl(0, 1, 40)
                #fh.sleep(0.3)
                FLY.move_Ctrl_cm(Dir.FRONT, 40)
                time.sleep(0.3)
                print("向前飞40cm")
            elif 290 < y < 365:
                #fh.moveCtrl(0, 2, 40)
                #fh.sleep(0.3)
                FLY.move_Ctrl_cm(Dir.BACK, 40)
                time.sleep(0.3)
                print("向后飞40cm")
        if 190<y<290:
            if 355<x<430:
                #fh.moveCtrl(0, 3, 40)
                #fh.sleep(0.3)
                FLY.move_Ctrl_cm(Dir.LEFT, 40)
                time.sleep(0.3)
                print("向左飞40cm")
            elif 530<x<605:
                #fh.moveCtrl(0, 4, 40)
                #fh.sleep(0.3)
                FLY.move_Ctrl_cm(Dir.RIGHT, 20)
                time.sleep(0.3)
                print("向右飞40cm")


def show_pic():
    """
    线程函数显示摄像头画面
    Returns
    -------

    """
    while True:
        success, img = cap.read()

        draw_rect(img)

        if success:
            img = cv2.flip(img, 1)
            img = detector.find_hands(img, draw=True)
            sun = detector.find_positions(img)
            if len(sun) > 0:
                cv2.circle(img, (sun[8][1], sun[8][2]), 10, (0, 255, 0), cv2.FILLED)

            if detector.results.multi_hand_landmarks:
                if len(detector.results.multi_hand_landmarks) == 2:
                    sun2 = detector.find_positions(img, 1)
                    cv2.circle(img, (sun2[8][1], sun2[8][2]), 10, (0, 255, 0), cv2.FILLED)
        cv2.imshow("pic", img)

        k=cv2.waitKey(1)
        if k == ord('q'):
            cap.release()
            cv2.destroyAllWindows()
            break

#多线程显示摄像头画面
show = threading.Thread(target=show_pic)
show.start()

#fh.xySpeed(0,100)
#fh.zSpeed(0,20)

while True:
    success, img = cap.read()

    draw_rect(img)

    if success:
        img = cv2.flip(img, 1)
        img = detector.find_hands(img, draw=True)


        if detector.results.multi_hand_landmarks:
            if len(detector.results.multi_hand_landmarks)==2:
                left_hand = detector.find_positions(img, 0)
                right_hand = detector.find_positions(img, 1)
                #print("左手：", left_hand)
                #print("右手：", right_hand)

                #起飞检查
                if not take_off:
                    took_off(left_hand)
                else:
                    #设置垂直速度
                    set_z_speed(left_hand)
                    #垂直飞行
                    vertical_movement(left_hand)
                    horizontal_movement(right_hand)
                    print(left_hand, right_hand)
                    if not left_hand and not right_hand:
                        #fh.flyCtrl(0, 0)
                        FLY.landing(Land.ORD, 50)
        if take_off:
            if not detector.results.multi_hand_landmarks:
                #fh.flyCtrl(0, 0)
                FLY.landing(Land.ORD, 50)
                take_off = False




    #cv2.resizeWindow("hands", 640, 480)

    k=cv2.waitKey(1)
    if k == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
