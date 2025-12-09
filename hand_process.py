import cv2
import mediapipe as mp


class HandDetector:

    def __init__(self):
        # 先定义results和handsjh两个成员变量，先将其定义为空
        self.results = None
        self.handsjh = None
        # 为mp.solutions.hands.Hands()命名为hands，使后续代码比较简短
        self.hands = mp.solutions.hands.Hands()

    def find_hands(self, img, draw=True):
        # 将img图像由BGR转换成RGB
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        # 处理手部检测和追踪的数据，并返回一个mp.solutions.hands.Hands()对象，其中包含了检测到的手部数据
        self.results = self.hands.process(imgRGB)
        if draw:
            # 确定是否有多只手的检测结果
            if self.results.multi_hand_landmarks:
                # 遍历multi_hand_landmarks中的数据
                for handlms in self.results.multi_hand_landmarks:
                    # 画出21个手势地标并其连起来
                    mp.solutions.drawing_utils.draw_landmarks(img, handlms, mp.solutions.hands.HAND_CONNECTIONS)
        return img

    def find_positions(self, img, hand_no=0):
        # 先将handsjh定义为空列表
        self.handsjh = []
        """
        if self.results.multi_hand_landmarks:
            print(len(self.results.multi_hand_landmarks))
        """
        if self.results.multi_hand_landmarks:
            # 选择索引值为hand_no的手部地标数据，并将其赋值给变量hand
            hand = self.results.multi_hand_landmarks[hand_no]
            # 使用enumerate()函数对该手的每一个地标进行遍历，并将地标的索引值赋值给id，，并将每个地标的x、y值赋值给lm
            for id, lm in enumerate(hand.landmark):
                # 计算图像img的长和宽
                h, w, c = img.shape
                # 计算每个地标在img图像对应位置的x、y坐标
                cx, cy = int(lm.x * w), int(lm.y * h)
                # 将计算到的数据存放到handsjh列表中
                self.handsjh.append([id, cx, cy])
        return self.handsjh