import os
import threading
from tkinter import *
import tkinter as tki
import datetime
import time
import cv2
import numpy as np
import imutils
from djitellopy import tello

cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

class UI:
    def __init__(self, drone, outputPath):
        self.tello = drone
        self.tello.connect() #connect to the drone
        self.tello.streamoff()
        self.tello.streamon()

        print("Finish load")
        print("Current battery: " + self.tello.get_battery())

        outputPath = outputPath
        self.frame = None
        # thread for control our video polling loop
        self.thread = None
        # a thread.Event object used to indicate when the frame pooling thread should be stopped.
        self.stopEvent = None

        self.distance = 50  # default distance for 'move' cmd
        self.degree = 45  # w default degree for 'cw' or 'ccw' cmd

        # initialize the window and image panel
        # root = Tk()
        # panel = None

        #################

        self.root = Tk()
        self.root.title("Tello Drone Panel")
        self.panel = None


        title = tki.Label(text='Drone Control Panel', font='Arial 16 bold')
        title.pack(side='top', padx=10, pady=10)

        # - Instruction Title -
        instruction_title = tki.Label(text='Instruction:', justify="left", font='Arial 12 bold')
        instruction_title.pack(side='top', anchor=tki.W, padx=10, pady=5)

        instruction = tki.Label(text='W - Move Tello Up\t\t\tArrow Up - Move Tello Forward\n'
                                                  'S - Move Tello Down\t\t\tArrow Down - Move Tello Backward\n'
                                                  'A - Rotate Tello Counter-Clockwise\t\tArrow Left - Move Tello Left\n'
                                                  'D - Rotate Tello Clockwise\t\t\tArrow Right - Move Tello Right\n',justify="left")
        instruction.pack(side="top",padx=10, pady=5)

        # create a snapshort button
        btn_snapshot = tki.Button(self.root, text="Snapshot!", command=self.SnapShot)
        btn_snapshot.pack(side="right", fill="both", expand="yes", padx=10, pady=10)

        # - Start -
        btn_start = tki.Button(self.root, text="Start", compound="left", relief="raised",command=self.telloTakeOff)
        btn_start.pack(side="top", fill="both", expand="yes", padx=10, pady=10)
        btn_start.config(background='#32CD32')

        # - Stop -
        btn_stop = tki.Button(self.root, text="Stop", compound="left", relief="raised",command=self.telloLanding)
        btn_stop.pack(side="top", fill="both", expand="yes", padx=10, pady=15)
        btn_stop.config(background='#ED2939')

        # binding arrow keys to drone control
        tmp_f = tki.Frame(self.root, width=100, height=2)
        tmp_f.bind('<KeyPress-w>',self.on_keypress_w)
        tmp_f.bind('<KeyPress-s>',self.on_keypress_s)
        tmp_f.bind('<KeyPress-a>',self.on_keypress_a)
        tmp_f.bind('<KeyPress-d>',self.on_keypress_d)
        tmp_f.bind('<KeyPress-z>',self.SnapShot)
        tmp_f.bind('<KeyPress-g>', self.on_keypress_g)
        # tmp_f.bind('<KeyPress-g>',on_keypress_g)

        tmp_f.bind('<KeyPress-Up>',self.on_keypress_up)
        tmp_f.bind('<KeyPress-Down>',self.on_keypress_down)
        tmp_f.bind('<KeyPress-Left>',self.on_keypress_left)
        tmp_f.bind('<KeyPress-Right>',self.on_keypress_right)
        tmp_f.pack(side="bottom")
        tmp_f.focus_set()

        self.stopEvent = threading.Event()
        self.thread = threading.Thread(target=self.videoLoop, args=())
        self.thread.start()

        # videoLoop();

        self.root.mainloop()

    # Declare Function

    def telloTakeOff(self):
        print("Tello Take Off")
        self.tello.takeoff()

    def telloLanding(self):
        print("Tello Landing")
        self.tello.land()

    def videoLoop(self):
        print("Starting Video Please Wait")

        while True:
            # _, self.frame = cap.read() #comment this line (This is to open laptop cam)

            _, self.frame = self.tello.get_frame_read().frame ##Drone cam
            self.hsv = cv2.cvtColor(self.frame, cv2.COLOR_BGR2HSV)
            lower_green = np.array([40, 70, 80])
            upper_green = np.array([70, 255, 255])

            lower_red = np.array([0, 50, 120])
            upper_red = np.array([10, 255, 255])

            mask2 = cv2.inRange(self.hsv, lower_green, upper_green)
            mask3 = cv2.inRange(self.hsv, lower_red, upper_red)

            cnts2 = cv2.findContours(mask2, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            cnts2 = imutils.grab_contours(cnts2)

            cnts3 = cv2.findContours(mask3, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
            cnts3 = imutils.grab_contours(cnts3)

            for c in cnts2:
                area2 = cv2.contourArea(c)
                if area2 > 5000:
                    cv2.drawContours(self.frame, [c], -1, (0, 255, 0), 3)
                    M = cv2.moments(c)
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    cv2.circle(self.frame, (cx, cy), 7, (255, 255, 255), -1)
                    cv2.putText(self.frame, "Non Criminal", (cx - 20, cy - 20), cv2.FONT_HERSHEY_SIMPLEX, 2.5,
                                (255, 255, 255), 3)

            for c in cnts3:
                area3 = cv2.contourArea(c)
                if area3 > 5000:
                    cv2.drawContours(self.frame, [c], -1, (0, 255, 0), 3)
                    M = cv2.moments(c)
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    cv2.circle(self.frame, (cx, cy), 7, (255, 255, 255), -1)
                    cv2.putText(self.frame, "Criminal", (cx - 20, cy - 20), cv2.FONT_HERSHEY_SIMPLEX, 2.5,
                                (255, 255, 255), 3)

            cv2.imshow("result", self.frame)
            k = cv2.waitKey(5)
            if k == 27:
                break

    def SnapShot(self):
        if self.cap.isOpened():
            ts = datetime.datetime.now()
            filename = "{}.jpg".format(ts.strftime("%Y-%m-%d_%H-%M-%S"))

            # cv2.imwrite('Resources/images/' + filename, self.frame)

            p = os.path.sep.join(('Resources/images/', filename))

            # save the file
            cv2.imwrite(p, self.frame)
            print("You have taken a picture")
            time.sleep(0.3)
        else:
            print("Cap is not open")

    def on_keypress_w(self, event):
        print("up %d m" % self.distance)
        self.tello.move_up(self.distance)

    def on_keypress_s(self, event):
        print("down %d m" % self.distance)
        self.tello.move_down(self.distance)

    def on_keypress_a(self,event): #issue last time
        print("ccw %d degree" % self.degree)
        self.tello.rotate_counter_clockwise(self.degree)

    def on_keypress_d(self,event): #issue last time
        print("cw %d m" % self.degree)
        self.tello.rotate_clockwise(self.degree)

    def on_keypress_g(self,event):
        self.tello.stop()

    def on_keypress_up(self, event):
        print("forward %d m" % self.distance)
        self.tello.move_forward(self.distance)

    def on_keypress_down(self, event): #issue last time
        print("backward %d m" % self.distance)
        self.tello.move_back(self.distance)

    def on_keypress_left(self,event):
        print("left %d m" % self.distance)
        self.tello.move_left(self.distance)

    def on_keypress_right(self,event):
        print("right %d m" % self.distance)
        self.tello.move_right(self.distance)

    def onClose(self):
        print("[INFO] closing...")
        self.stopEvent.set()
        del self.tello
        self.root.quit()