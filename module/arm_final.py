#!/usr/bin/env python3
# Software License Agreement (BSD License)
#
# Copyright (c) 2022, UFACTORY, Inc.
# All rights reserved.
#
# Author: Vinman <vinman.wen@ufactory.cc> <vinman.cub@gmail.com>

"""
# Notice
#   1. Changes to this file on Studio will not be preserved
#   2. The next conversion will overwrite the file with the same name
#
# xArm-Python-SDK: https://github.com/xArm-Developer/xArm-Python-SDK
#   1. git clone git@github.com:xArm-Developer/xArm-Python-SDK.git
#   2. cd xArm-Python-SDK
#   3. python setup.py install
"""
import sys
import math
import time
import queue
import datetime
import random
import traceback
import threading
from xarm import version
from xarm.wrapper import XArmAPI

from threading import Thread, Event
import socket
import json
import os
import cv2
import numpy as np
from ultralytics import YOLO
import argparse
sys.path.append("/home/addinedu/aris/aris-repo-5_통신")
try:
    from caricature import caricature
    print("✅ Caricature Import 성공!")
except ImportError as e:
    print("❌ Caricature Import 실패:", e)

class RobotMain(object):
    """Robot Main Class"""

    def __init__(self, robot, topping, **kwargs):
        self.alive = True
        self._arm = robot
        self._tcp_speed = 50/2
        self._tcp_acc = 1000/2
        self._angle_speed = 10/2
        self._angle_acc = 250/2
        self.order_msg = 'A'
        self.order_msg_topping_pos = topping if topping is not None else "N"
        self._vars = {}
        self._funcs = {}
        self._robot_init()
        self.state = 'stopped'
        self.end_flag = False
        #==============================추가 좌표=========================
        self.pick_angle = [193.7, 6.6, 26.7, 64.7, 95.5, 17.6]
        self.pick_position = [-74.3, -139.1, 224.6, -138.1, 88.3, 162.2]
        self.additional_position2 = [-68.7, -135.3, 286.6, -0.6, 75, -62.7]
        self.additional_position3 = [-136.7, 11.2, 264, -113.3, 85.3, 116.2]
        self.additional_position4 = [-100, -88.8, 223, -116, 84.9, -176.5]
        self.additional_position5 = [-134.6, -29.7, 227.9, 119.6, 85.7, 33.9]
        # -------------------- 처음 좌표설정(4개) --------------------
        self.position_start_1 = [-307,  -74.9, 152.3,  96.1,  88.5, -83.9]
        self.position_start_2 = [-190.5, -75.6, 151.6, -106.3, 86.3, 20.3]
        self.position_start_3 = [-310.6, 101.5, 162.9, -142.4, 86.7, 38.5]
        self.position_start_4 = [-188.8,  99.8, 173.7, -161.9, 85.6, 16.9]

        # 장애물 감지 관련 이벤트 추가
        self.stop_event = threading.Event()

        # YOLO 모델 로드 및 카메라 활성화
        self.model = YOLO("/home/addinedu/dev_ws/stable_diff/arm/aris-repo-5/module/model/best_default.pt")
        self.model_cap = YOLO("/home/addinedu/dev_ws/stable_diff/arm/aris-repo-5/module/model/best_cap_pen.pt")
        self.cap = cv2.VideoCapture(2)
        if not self.cap.isOpened():
            print("❌ 웹캠을 열 수 없습니다.")

    def _robot_init(self):
        self._arm.clean_warn()
        self._arm.clean_error()
        self._arm.motion_enable(True)
        self._arm.set_mode(0)
        self._arm.set_state(0)
        time.sleep(1)
        self._arm.register_error_warn_changed_callback(self._error_warn_changed_callback)
        self._arm.register_state_changed_callback(self._state_changed_callback)
        if hasattr(self._arm, 'register_count_changed_callback'):
            self._arm.register_count_changed_callback(self._count_changed_callback)

    def _error_warn_changed_callback(self, data):
        if data and data['error_code'] != 0:
            self.alive = False
            self.pprint('err={}, quit'.format(data['error_code']))
            self._arm.release_error_warn_changed_callback(self._error_warn_changed_callback)

    def _state_changed_callback(self, data):
        if data and data['state'] == 4:
            self.alive = False
            self.pprint('state=4, quit')
            self._arm.release_state_changed_callback(self._state_changed_callback)

    def _count_changed_callback(self, data):
        if self.is_alive:
            self.pprint('counter val: {}'.format(data['count']))

    def _check_code(self, code, label):
        """
        장애물 감지 시 로봇 명령을 보내지 않고, 장애물이 사라질 때까지 대기
        """
        while self.stop_event.is_set():
            print("⏸️ 장애물 감지됨. 대기 중...")
            time.sleep(0.1)
        if code != 0:
            self.alive = False
            print(f'❌ 오류 발생: {label}, 코드: {code}')
            return False
        return True

    @staticmethod
    def pprint(*args, **kwargs):
        try:
            stack_tuple = traceback.extract_stack(limit=2)[0]
            print('[{}][{}] {}'.format(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())),
                                       stack_tuple[1], ' '.join(map(str, args))))
        except Exception:
            print(*args, **kwargs)

    @property
    def arm(self):
        return self._arm

    @property
    def VARS(self):
        return self._vars

    @property
    def FUNCS(self):
        return self._funcs

    @property
    def is_alive(self):
        if self.alive and self._arm.connected and self._arm.error_code == 0:
            if self._arm.state == 5:
                cnt = 0
                while self._arm.state == 5 and cnt < 5:
                    cnt += 1
                    time.sleep(0.1)
            return self._arm.state < 4
        else:
            return False

    # ────────── Motion 함수들 (motion_home, motion_grab_capsule, 등) ──────────
    # (이전 코드와 동일하므로 여기서는 생략합니다.)

    def motion_home(self):
        if not self._check_code(self._arm.set_cgpio_analog(0, 0), 'set_cgpio_analog'):
            return
        if not self._check_code(self._arm.set_cgpio_analog(1, 0), 'set_cgpio_analog'):
            return
        if not self._check_code(self._arm.set_cgpio_digital(3, 0, delay_sec=0), 'set_cgpio_digital'):
            return
        if not self._check_code(self._arm.set_cgpio_digital(0, 0, delay_sec=0), 'set_cgpio_digital'):
            return
        self._angle_speed = 80/2
        self._angle_acc = 200/2
        if not self._check_code(
            self._arm.set_servo_angle(angle=[179.2, -42.1, 7.4, 186.7, 41.5, -1.6],
                                      speed=self._angle_speed,
                                      mvacc=self._angle_acc,
                                      wait=True,
                                      radius=0.0),
            'set_servo_angle'):
            return
        print('motion_home finish')
    #==============================펜 잡고 놓기===================================
    def motion_pick_sequence(self, label=''):
        """
        (1) self.pick_angle으로 이동 -> 그리퍼 열기
        (2) self.pick_position으로 이동 -> 그리퍼 닫기
        (3) 추가 좌표2로 이동
        (4) 추가 좌표3로 이동
        (5) 다시 pick_angle으로 복귀
        """
        self.pprint(f'=== motion_pick_sequence({label}) start ===')
        # 1) 관절 각도 pick_angle 이동
        code = self._arm.set_servo_angle(
            angle=self.pick_angle,
            speed=self._angle_speed,
            mvacc=self._angle_acc,
            wait=True,
            radius=0.0
        )
        if not self._check_code(code, f'{label}_go_angle'):
            return
        # 그리퍼 열기
        code = self._arm.open_lite6_gripper()
        if not self._check_code(code, f'{label}_gripper_open'):
            return
        time.sleep(1)
        # 2) 선형 좌표 pick_position 이동
        code = self._arm.set_position(
            *self.pick_position,
            speed=self._tcp_speed,
            mvacc=self._tcp_acc,
            radius=0.0,
            wait=True
        )
        if not self._check_code(code, f'{label}_go_position'):
            return
        # 그리퍼 닫기
        code = self._arm.close_lite6_gripper()
        if not self._check_code(code, f'{label}_gripper_close'):
            return
        time.sleep(1)
        # 3) 추가 좌표2로 이동
        code = self._arm.set_position(
            *self.additional_position2,
            speed=self._tcp_speed,
            mvacc=self._tcp_acc,
            radius=0.0,
            wait=True
        )
        if not self._check_code(code, f'{label}_go_additional_position2'):
            return
        # 4) 추가 좌표3로 이동
        code = self._arm.set_position(
            *self.additional_position3,
            speed=self._tcp_speed,
            mvacc=self._tcp_acc,
            radius=0.0,
            wait=True
        )
        if not self._check_code(code, f'{label}_go_additional_position3'):
            return
        self.pprint(f'=== motion_pick_sequence({label}) finish ===')

    def motion_pick_sequence_again(self, label=''):
        """
        (1) pick_angle으로 이동
        (2) pick_position으로 이동
        (3) pick_position에 도착한 후 그리퍼 열기 (그리퍼 열린 상태 유지)
        (4) 추가 좌표2로 이동
        (5) 추가 좌표3로 이동
        (6) 다시 pick_angle으로 복귀
        """
        self.pprint(f'=== motion_pick_sequence_again({label}) start ===')
        # (1) 추가 좌표3로 이동
        code = self._arm.set_position(
            *self.additional_position3,
            speed=self._tcp_speed,
            mvacc=self._tcp_acc,
            radius=0.0,
            wait=True
        )
        if not self._check_code(code, f'{label}_go_additional_position3'):
            return
        # (2) pick_angle으로 이동
        code = self._arm.set_servo_angle(
            angle=self.pick_angle,
            speed=self._angle_speed,
            mvacc=self._angle_acc,
            wait=True,
            radius=0.0
        )
        if not self._check_code(code, f'{label}_go_angle'):
            return
        # (3) 추가 좌표2로 이동
        code = self._arm.set_position(
            *self.additional_position2,
            speed=self._tcp_speed,
            mvacc=self._tcp_acc,
            radius=0.0,
            wait=True
        )
        if not self._check_code(code, f'{label}_go_additional_position2'):
            return
        # (4) pick_position으로 이동
        code = self._arm.set_position(
            *self.pick_position,
            speed=self._tcp_speed,
            mvacc=self._tcp_acc,
            radius=0.0,
            wait=True
        )
        if not self._check_code(code, f'{label}_go_position'):
            return
        # (5) pick_position에 도착한 후 그리퍼 열기 (그리퍼 열린 상태 유지)
        code = self._arm.open_lite6_gripper()
        if not self._check_code(code, f'{label}_gripper_open'):
            return
        time.sleep(1)  # 그리퍼가 완전히 열릴 때까지 대기
        # 추가 좌표4로 이동
        code = self._arm.set_position(
            *self.additional_position4,
            speed=self._tcp_speed,
            mvacc=self._tcp_acc,
            radius=0.0,
            wait=True
        )
        if not self._check_code(code, f'{label}_go_additional_position4'):
            return
        self.pprint(f'=== motion_pick_sequence_again({label}) finish ===')
        # 추가: 동작 완료 후, additional_position5 좌표로 이동
        code = self._arm.set_position(
            *self.additional_position5,
            speed=self._tcp_speed,
            mvacc=self._tcp_acc,
            radius=0.0,
            wait=True
        )
        if not self._check_code(code, f'{label}_go_additional_position5'):
            return
        time.sleep(1)  # 그리퍼가 완전히 열릴 때까지 대기

        

        self.pprint(f'=== motion_pick_sequence_again({label}) finish ===')
    # ===================================================================
    def motion_grab_capsule(self, location):
        # (이전 코드와 동일)
        if not self.alive:
            print("⏸️ 로봇 동작 중단됨 (장애물 감지)")
            return
        self.order_msg = location
        if not self._check_code(self._arm.set_cgpio_analog(0, 5), 'set_cgpio_analog'):
            return
        if not self._check_code(self._arm.set_cgpio_analog(1, 5), 'set_cgpio_analog'):
            return
        self._angle_speed = 100/2
        self._angle_acc = 350/2
        if not self._check_code(self._arm.close_lite6_gripper(), 'close_lite6_gripper'):
            return
        time.sleep(1)
        if not self._check_code(self._arm.open_lite6_gripper(), 'open_lite6_gripper'):
            return
        time.sleep(1)
        if not self._check_code(self._arm.stop_lite6_gripper(), 'stop_lite6_gripper'):
            return
        time.sleep(1)
        if not self._check_code(
            self._arm.set_servo_angle(angle=[166.1, 30.2, 25.3, 75.3, 93.9, -5.4],
                                      speed=self._angle_speed,
                                      mvacc=self._angle_acc,
                                      wait=True,
                                      radius=0.0),
            'set_servo_angle'):
            return
        if not self._check_code(self._arm.open_lite6_gripper(), 'open_lite6_gripper'):
            return
        time.sleep(1)
        if self.order_msg == 'A':
            if not self._check_code(
                self._arm.set_servo_angle(angle=[179.5, 33.5, 32.7, 113.0, 93.1, -2.3],
                                          speed=self._angle_speed,
                                          mvacc=self._angle_acc,
                                          wait=True,
                                          radius=0.0),
                'set_servo_angle'):
                return
            if not self._check_code(
                self._arm.set_position(*[-257.3, -138.3, 192.1, 68.3, 86.1, -47.0],
                                       speed=self._tcp_speed,
                                       mvacc=self._tcp_acc,
                                       radius=0.0,
                                       wait=True),
                'set_position'):
                return
        elif self.order_msg == 'B':
            if not self._check_code(
                self._arm.set_position(*[-152.3, -129.0, 192.8, 4.8, 89.0, -90.7],
                                       speed=self._tcp_speed,
                                       mvacc=self._tcp_acc,
                                       radius=0.0,
                                       wait=True),
                'set_position'):
                return
        if not self._check_code(self._arm.close_lite6_gripper(), 'close_lite6_gripper'):
            return
        time.sleep(1)
        if not self._check_code(
            self._arm.set_position(z=100,
                                   radius=0,
                                   speed=self._tcp_speed,
                                   mvacc=self._tcp_acc,
                                   relative=True,
                                   wait=True),
            'set_position'):
            return
        self._angle_speed = 200/2
        self._angle_acc = 1000/2
        if not self._check_code(
            self._arm.set_servo_angle(angle=[146.1, -10.7, 10.9, 102.7, 92.4, 24.9],
                                      speed=self._angle_speed,
                                      mvacc=self._angle_acc,
                                      wait=True,
                                      radius=20.0),
            'set_servo_angle'):
            return

    def motion_place_capsule(self):
        # (이전 코드와 동일)
        if not self.alive:
            print("⏸️ 로봇 동작 중단됨 (장애물 감지)")
            return
        if not self._check_code(
            self._arm.set_servo_angle(angle=[81.0, -10.8, 6.9, 103.6, 88.6, 9.6],
                                      speed=self._angle_speed,
                                      mvacc=self._angle_acc,
                                      wait=False,
                                      radius=20.0),
            'set_servo_angle'):
            return
        if not self._check_code(
            self._arm.set_servo_angle(angle=[27.0, -24.9, 7.2, 108.0, 76.4, 32.7],
                                      speed=self._angle_speed,
                                      mvacc=self._angle_acc,
                                      wait=False,
                                      radius=20.0),
            'set_servo_angle'):
            return
        if not self._check_code(
            self._arm.set_servo_angle(angle=[-0.9, -24.9, 10.4, 138.3, 66.0, 19.1],
                                      speed=self._angle_speed,
                                      mvacc=self._angle_acc,
                                      wait=False,
                                      radius=20.0),
            'set_servo_angle'):
            return
        if not self._check_code(
            self._arm.set_servo_angle(angle=[8.4, -42.7, 23.7, 177.4, 31.6, 3.6],
                                      speed=self._angle_speed,
                                      mvacc=self._angle_acc,
                                      wait=True,
                                      radius=20.0),
            'set_servo_angle'):
            return
        if not self._check_code(
            self._arm.set_servo_angle(angle=[8.4, -32.1, 55.1, 96.6, 29.5, 81.9],
                                      speed=self._angle_speed,
                                      mvacc=self._angle_acc,
                                      wait=True,
                                      radius=0.0),
            'set_servo_angle'):
            return
        if not self._check_code(
            self._arm.set_position(*[231.7, 129.3, 486.7, 133.6, 87.2, -142.1],
                                   speed=self._tcp_speed,
                                   mvacc=self._tcp_acc,
                                   radius=0.0,
                                   wait=True),
            'set_position'):
            return
        if not self._check_code(
            self._arm.set_position(*[231.7, 129.3, 466.7, 133.6, 87.2, -142.1],
                                   speed=self._tcp_speed,
                                   mvacc=self._tcp_acc,
                                   radius=0.0,
                                   wait=True),
            'set_position'):
            return
        if not self._check_code(self._arm.set_cgpio_analog(0, 0), 'set_cgpio_analog'):
            return
        if not self._check_code(self._arm.set_cgpio_analog(1, 5), 'set_cgpio_analog'):
            return
        if not self._check_code(self._arm.open_lite6_gripper(), 'open_lite6_gripper'):
            return
        time.sleep(2)
        if not self._check_code(self._arm.stop_lite6_gripper(), 'stop_lite6_gripper'):
            return
        time.sleep(0.5)

    def motion_grab_cup(self):
        # (이전 코드와 동일)
        if not self.alive:
            print("⏸️ 로봇 동작 중단됨 (장애물 감지)")
            return
        if not self._check_code(
            self._arm.set_position(*[233.4, 10.3, 471.1, -172.2, 87.3, -84.5],
                                   speed=self._tcp_speed,
                                   mvacc=self._tcp_acc,
                                   radius=0.0,
                                   wait=True),
            'set_position'):
            return
        if not self._check_code(self._arm.open_lite6_gripper(), 'open_lite6_gripper'):
            return
        time.sleep(1)
        if not self._check_code(
            self._arm.set_servo_angle(angle=[-2.8, -2.5, 45.3, 119.8, -79.2, -18.8],
                                      speed=self._angle_speed,
                                      mvacc=self._angle_acc,
                                      wait=True,
                                      radius=0.0),
            'set_servo_angle'):
            return
        if not self._check_code(
            self._arm.set_position(*[195.0, -96.5, 200.8, -168.0, -87.1, -110.5],
                                   speed=self._tcp_speed,
                                   mvacc=self._tcp_acc,
                                   radius=10.0,
                                   wait=True),
            'set_position'):
            return
        if not self._check_code(
            self._arm.set_position(*[213.9, -98.0, 144.1, -127.1, -89.2, -162.1],
                                   speed=self._tcp_speed,
                                   mvacc=self._tcp_acc,
                                   radius=0.0,
                                   wait=False),
            'set_position'):
            return
        if not self._check_code(self._arm.close_lite6_gripper(), 'close_lite6_gripper'):
            return
        time.sleep(2)
        if not self._check_code(
            self._arm.set_position(z=120,
                                   radius=0,
                                   speed=self._tcp_speed,
                                   mvacc=self._tcp_acc,
                                   relative=True,
                                   wait=True),
            'set_position'):
            return
        if not self._check_code(
            self._arm.set_servo_angle(angle=[2.9, -31.0, 33.2, 125.4, -30.4, -47.2],
                                      speed=self._angle_speed,
                                      mvacc=self._angle_acc,
                                      wait=True,
                                      radius=0.0),
            'set_servo_angle'):
            return
        if not self._check_code(self._arm.set_cgpio_analog(0, 5), 'set_cgpio_analog'):
            return
        if not self._check_code(self._arm.set_cgpio_analog(1, 5), 'set_cgpio_analog'):
            return
        time.sleep(0.5)

        

    def motion_topping(self):
        if not self.alive:
            print("⏸️ 로봇 동작 중단됨 (장애물 감지)")
            return
        print('send')
        if self.order_msg_topping_pos != 'N':
            if not self._check_code(
                self._arm.set_servo_angle(
                    angle=[36.6, -36.7, 21.1, 85.6, 59.4, 44.5],
                    speed=self._angle_speed,
                    mvacc=self._angle_acc,
                    wait=True,
                    radius=0.0
                ),
                'set_servo_angle'
            ):
                return

            if self.order_msg_topping_pos == 'C':
                if not self._check_code(
                    self._arm.set_position(
                        *[43.6, 137.9, 350.1, -92.8, 87.5, 5.3],
                        speed=self._tcp_speed,
                        mvacc=self._tcp_acc,
                        radius=0.0,
                        wait=False
                    ),
                    'set_position'
                ):
                    return
                if not self._check_code(
                    self._arm.set_cgpio_digital(2, 1, delay_sec=0),
                    'set_cgpio_digital'
                ):
                    return
                if not self._check_code(
                    self._arm.set_position(
                        z=20, radius=0,
                        speed=self._tcp_speed,
                        mvacc=self._tcp_acc,
                        relative=True,
                        wait=False
                    ),
                    'set_position'
                ):
                    return
                if not self._check_code(
                    self._arm.set_pause_time(8),
                    'set_pause_time'
                ):
                    return
                if not self._check_code(
                    self._arm.set_cgpio_digital(2, 0, delay_sec=0),
                    'set_cgpio_digital'
                ):
                    return
                if not self._check_code(
                    self._arm.set_position(
                        z=-20, radius=0,
                        speed=self._tcp_speed,
                        mvacc=self._tcp_acc,
                        relative=True,
                        wait=False
                    ),
                    'set_position'
                ):
                    return

            elif self.order_msg_topping_pos == 'B':
                if not self._check_code(
                    self._arm.set_servo_angle(
                        angle=[55.8, -48.2, 14.8, 86.1, 60.2, 58.7],
                        speed=self._angle_speed,
                        mvacc=self._angle_acc,
                        wait=True,
                        radius=0.0
                    ),
                    'set_servo_angle'
                ):
                    return
                # Previously commented out code remains unchanged.
                if not self._check_code(
                    self._arm.set_servo_angle(
                        angle=[106.5, -39.7, 15.0, 158.7, 40.4, 16.9],
                        speed=self._angle_speed,
                        mvacc=self._angle_acc,
                        wait=True,
                        radius=0.0
                    ),
                    'set_servo_angle'
                ):
                    return
                if not self._check_code(
                    self._arm.set_cgpio_digital(1, 1, delay_sec=0),
                    'set_cgpio_digital'
                ):
                    return
                if not self._check_code(
                    self._arm.set_position(
                        z=20, radius=0,
                        speed=self._tcp_speed,
                        mvacc=self._tcp_acc,
                        relative=True,
                        wait=False
                    ),
                    'set_position'
                ):
                    return
                if not self._check_code(
                    self._arm.set_pause_time(8),
                    'set_pause_time'
                ):
                    return
                if not self._check_code(
                    self._arm.set_cgpio_digital(1, 0, delay_sec=0),
                    'set_cgpio_digital'
                ):
                    return
                if not self._check_code(
                    self._arm.set_position(
                        z=-20, radius=0,
                        speed=self._tcp_speed,
                        mvacc=self._tcp_acc,
                        relative=True,
                        wait=True
                    ),
                    'set_position'
                ):
                    return
                if not self._check_code(
                    self._arm.set_servo_angle(
                        angle=[87.5, -48.2, 13.5, 125.1, 44.5, 46.2],
                        speed=self._angle_speed,
                        mvacc=self._angle_acc,
                        wait=True,
                        radius=0.0
                    ),
                    'set_servo_angle'
                ):
                    return
                if not self._check_code(
                    self._arm.set_position(
                        *[43.6, 137.9, 350.1, -92.8, 87.5, 5.3],
                        speed=self._tcp_speed,
                        mvacc=self._tcp_acc,
                        radius=0.0,
                        wait=True
                    ),
                    'set_position'
                ):
                    return

            elif self.order_msg_topping_pos == 'A':
                if not self._check_code(
                    self._arm.set_position(
                        *[-200.3, 162.8, 359.9, -31.7, 87.8, 96.1],
                        speed=self._tcp_speed,
                        mvacc=self._tcp_acc,
                        radius=0.0,
                        wait=True
                    ),
                    'set_position'
                ):
                    return
                if not self._check_code(
                    self._arm.set_cgpio_digital(0, 1, delay_sec=0),
                    'set_cgpio_digital'
                ):
                    return
                if not self._check_code(
                    self._arm.set_pause_time(8),
                    'set_pause_time'
                ):
                    return
                if not self._check_code(
                    self._arm.set_cgpio_digital(0, 0, delay_sec=0),
                    'set_cgpio_digital'
                ):
                    return
                if not self._check_code(
                    self._arm.set_servo_angle(
                        angle=[130.0, -33.1, 12.5, 194.3, 51.0, 0.0],
                        speed=self._angle_speed,
                        mvacc=self._angle_acc,
                        wait=True,
                        radius=0.0
                    ),
                    'set_servo_angle'
                ):
                    return
                if not self._check_code(
                    self._arm.set_position(
                        *[-38.2, 132.2, 333.9, -112.9, 86.3, -6.6],
                        speed=self._tcp_speed,
                        mvacc=self._tcp_acc,
                        radius=0.0,
                        wait=True
                    ),
                    'set_position'
                ):
                    return
                if not self._check_code(
                    self._arm.set_position(
                        *[43.6, 137.9, 350.1, -92.8, 87.5, 5.3],
                        speed=self._tcp_speed,
                        mvacc=self._tcp_acc,
                        radius=0.0,
                        wait=True
                    ),
                    'set_position'
                ):
                    return

            elif self.order_msg_topping_pos == 'AB':
                # 토핑 A 이동 -> 토핑 받기
                if not self._check_code(
                    self._arm.set_position(
                        *[-200.3, 162.8, 359.9, -31.7, 87.8, 96.1],
                        speed=self._tcp_speed,
                        mvacc=self._tcp_acc,
                        radius=0.0,
                        wait=True
                    ),
                    'set_position'
                ):
                    return
                if not self._check_code(
                    self._arm.set_cgpio_digital(0, 1, delay_sec=0),
                    'set_cgpio_digital'
                ):
                    return
                if not self._check_code(
                    self._arm.set_pause_time(8),
                    'set_pause_time'
                ):
                    return
                if not self._check_code(
                    self._arm.set_cgpio_digital(0, 0, delay_sec=0),
                    'set_cgpio_digital'
                ):
                    return
                # Topping_A_to_icecream1
                if not self._check_code(
                    self._arm.set_servo_angle(
                        angle=[130.0, -33.1, 12.5, 194.3, 51.0, 0.0],
                        speed=self._angle_speed,
                        mvacc=self._angle_acc,
                        wait=True,
                        radius=0.0
                    ),
                    'set_servo_angle'
                ):
                    return
                # Topping_B_Position
                if not self._check_code(
                    self._arm.set_servo_angle(
                        angle=[106.5, -39.7, 15.0, 158.7, 40.4, 16.9],
                        speed=self._angle_speed,
                        mvacc=self._angle_acc,
                        wait=True,
                        radius=0.0
                    ),
                    'set_servo_angle'
                ):
                    return
                if not self._check_code(
                    self._arm.set_cgpio_digital(1, 1, delay_sec=0),
                    'set_cgpio_digital'
                ):
                    return
                if not self._check_code(
                    self._arm.set_position(
                        z=20, radius=0,
                        speed=self._tcp_speed,
                        mvacc=self._tcp_acc,
                        relative=True,
                        wait=False
                    ),
                    'set_position'
                ):
                    return
                if not self._check_code(
                    self._arm.set_pause_time(8),
                    'set_pause_time'
                ):
                    return
                if not self._check_code(
                    self._arm.set_cgpio_digital(1, 0, delay_sec=0),
                    'set_cgpio_digital'
                ):
                    return
                if not self._check_code(
                    self._arm.set_position(
                        z=-20, radius=0,
                        speed=self._tcp_speed,
                        mvacc=self._tcp_acc,
                        relative=True,
                        wait=True
                    ),
                    'set_position'
                ):
                    return
                # Topping_B_Icecream
                if not self._check_code(
                    self._arm.set_servo_angle(
                        angle=[87.5, -48.2, 13.5, 125.1, 44.5, 46.2],
                        speed=self._angle_speed,
                        mvacc=self._angle_acc,
                        wait=True,
                        radius=0.0
                    ),
                    'set_servo_angle'
                ):
                    return
                # Topping_to_Icecream
                if not self._check_code(
                    self._arm.set_position(
                        *[43.6, 137.9, 350.1, -92.8, 87.5, 5.3],
                        speed=self._tcp_speed,
                        mvacc=self._tcp_acc,
                        radius=0.0,
                        wait=True
                    ),
                    'set_position'
                ):
                    return

            elif self.order_msg_topping_pos == 'AC':
                # 토핑 A 이동 -> 토핑 받기
                if not self._check_code(
                    self._arm.set_position(
                        *[-200.3, 162.8, 359.9, -31.7, 87.8, 96.1],
                        speed=self._tcp_speed,
                        mvacc=self._tcp_acc,
                        radius=0.0,
                        wait=True
                    ),
                    'set_position'
                ):
                    return
                if not self._check_code(
                    self._arm.set_cgpio_digital(0, 1, delay_sec=0),
                    'set_cgpio_digital'
                ):
                    return
                if not self._check_code(
                    self._arm.set_pause_time(8),
                    'set_pause_time'
                ):
                    return
                if not self._check_code(
                    self._arm.set_cgpio_digital(0, 0, delay_sec=0),
                    'set_cgpio_digital'
                ):
                    return
                # Topping_A_to_icecream1
                if not self._check_code(
                    self._arm.set_servo_angle(
                        angle=[130.0, -33.1, 12.5, 194.3, 51.0, 0.0],
                        speed=self._angle_speed,
                        mvacc=self._angle_acc,
                        wait=True,
                        radius=0.0
                    ),
                    'set_servo_angle'
                ):
                    return
                # Topping_A_to_icecream2
                if not self._check_code(
                    self._arm.set_position(
                        *[-38.2, 132.2, 333.9, -112.9, 86.3, -6.6],
                        speed=self._tcp_speed,
                        mvacc=self._tcp_acc,
                        radius=0.0,
                        wait=True
                    ),
                    'set_position'
                ):
                    return
                # Topping_C_Position
                if not self._check_code(
                    self._arm.set_position(
                        *[43.6, 137.9, 350.1, -92.8, 87.5, 5.3],
                        speed=self._tcp_speed,
                        mvacc=self._tcp_acc,
                        radius=0.0,
                        wait=False
                    ),
                    'set_position'
                ):
                    return
                if not self._check_code(
                    self._arm.set_cgpio_digital(2, 1, delay_sec=0),
                    'set_cgpio_digital'
                ):
                    return
                if not self._check_code(
                    self._arm.set_position(
                        z=20, radius=0,
                        speed=self._tcp_speed,
                        mvacc=self._tcp_acc,
                        relative=True,
                        wait=False
                    ),
                    'set_position'
                ):
                    return
                if not self._check_code(
                    self._arm.set_pause_time(8),
                    'set_pause_time'
                ):
                    return
                if not self._check_code(
                    self._arm.set_cgpio_digital(2, 0, delay_sec=0),
                    'set_cgpio_digital'
                ):
                    return
                if not self._check_code(
                    self._arm.set_position(
                        z=-20, radius=0,
                        speed=self._tcp_speed,
                        mvacc=self._tcp_acc,
                        relative=True,
                        wait=False
                    ),
                    'set_position'
                ):
                    return
                # C_to_the_Icecream_Position
                if not self._check_code(
                    self._arm.set_position(
                        *[166.3, 171.3, 359.5, 43.9, 88.3, 83.3],
                        speed=self._tcp_speed,
                        mvacc=self._tcp_acc,
                        radius=0.0,
                        wait=True
                    ),
                    'set_position'
                ):
                    return

            elif self.order_msg_topping_pos == 'BC':
                if not self._check_code(
                    self._arm.set_servo_angle(
                        angle=[55.8, -48.2, 14.8, 86.1, 60.2, 58.7],
                        speed=self._angle_speed,
                        mvacc=self._angle_acc,
                        wait=True,
                        radius=0.0
                    ),
                    'set_servo_angle'
                ):
                    return
                # Topping_B_Position
                if not self._check_code(
                    self._arm.set_servo_angle(
                        angle=[106.5, -39.7, 15.0, 158.7, 40.4, 16.9],
                        speed=self._angle_speed,
                        mvacc=self._angle_acc,
                        wait=True,
                        radius=0.0
                    ),
                    'set_servo_angle'
                ):
                    return
                if not self._check_code(
                    self._arm.set_cgpio_digital(1, 1, delay_sec=0),
                    'set_cgpio_digital'
                ):
                    return
                if not self._check_code(
                    self._arm.set_position(
                        z=20, radius=0,
                        speed=self._tcp_speed,
                        mvacc=self._tcp_acc,
                        relative=True,
                        wait=False
                    ),
                    'set_position'
                ):
                    return
                if not self._check_code(
                    self._arm.set_pause_time(8),
                    'set_pause_time'
                ):
                    return
                if not self._check_code(
                    self._arm.set_cgpio_digital(1, 0, delay_sec=0),
                    'set_cgpio_digital'
                ):
                    return
                # Topping_B_Icecream
                if not self._check_code(
                    self._arm.set_position(
                        z=-20, radius=0,
                        speed=self._tcp_speed,
                        mvacc=self._tcp_acc,
                        relative=True,
                        wait=True
                    ),
                    'set_position'
                ):
                    return
                # Topping_to_Icecream
                if not self._check_code(
                    self._arm.set_servo_angle(
                        angle=[87.5, -48.2, 13.5, 125.1, 44.5, 46.2],
                        speed=self._angle_speed,
                        mvacc=self._angle_acc,
                        wait=True,
                        radius=0.0
                    ),
                    'set_servo_angle'
                ):
                    return
                # Topping_C_Position
                if not self._check_code(
                    self._arm.set_position(
                        *[43.6, 137.9, 350.1, -92.8, 87.5, 5.3],
                        speed=self._tcp_speed,
                        mvacc=self._tcp_acc,
                        radius=0.0,
                        wait=False
                    ),
                    'set_position'
                ):
                    return
                if not self._check_code(
                    self._arm.set_cgpio_digital(2, 1, delay_sec=0),
                    'set_cgpio_digital'
                ):
                    return
                if not self._check_code(
                    self._arm.set_position(
                        z=20, radius=0,
                        speed=self._tcp_speed,
                        mvacc=self._tcp_acc,
                        relative=True,
                        wait=False
                    ),
                    'set_position'
                ):
                    return
                if not self._check_code(
                    self._arm.set_pause_time(8),
                    'set_pause_time'
                ):
                    return
                if not self._check_code(
                    self._arm.set_cgpio_digital(2, 0, delay_sec=0),
                    'set_cgpio_digital'
                ):
                    return
                if not self._check_code(
                    self._arm.set_position(
                        z=-20, radius=0,
                        speed=self._tcp_speed,
                        mvacc=self._tcp_acc,
                        relative=True,
                        wait=False
                    ),
                    'set_position'
                ):
                    return
                # C_to_the_Icecream_Position
                if not self._check_code(
                    self._arm.set_position(
                        *[166.3, 171.3, 359.5, 43.9, 88.3, 83.3],
                        speed=self._tcp_speed,
                        mvacc=self._tcp_acc,
                        radius=0.0,
                        wait=True
                    ),
                    'set_position'
                ):
                    return

            if not self._check_code(
                self._arm.set_position(
                    *[166.3, 171.3, 359.5, 43.9, 88.3, 83.3],
                    speed=self._tcp_speed,
                    mvacc=self._tcp_acc,
                    radius=0.0,
                    wait=True
                ),
                'set_position'
            ):
                return
            if not self._check_code(
                self._arm.set_cgpio_digital(3, 1, delay_sec=0),
                'set_cgpio_digital'
            ):
                return
        else:
            # Previously commented-out default code remains unchanged.
            if not self._check_code(
                self._arm.set_servo_angle(
                    angle=[48.1, -15.4, 35.0, 193.2, 41.6, -8.9],
                    speed=self._angle_speed,
                    mvacc=self._angle_acc,
                    wait=True,
                    radius=0.0
                ),
                'set_servo_angle'
            ):
                return
            if not self._check_code(
                self._arm.set_cgpio_digital(3, 1, delay_sec=0),
                'set_cgpio_digital'
            ):
                return
            if not self._check_code(
                self._arm.set_position(
                    z=3, radius=0,
                    speed=self._tcp_speed,
                    mvacc=self._tcp_acc,
                    relative=True,
                    wait=True
                ),
                'set_position'
            ):
                return

        time.sleep(0.5)


    def motion_make_icecream(self):
        if not self.alive:
            print("⏸️ 로봇 동작 중단됨 (장애물 감지)")
            return
        if self.order_msg_topping_pos != 'N':
            time.sleep(5)
        else:
            time.sleep(8)
        if not self._check_code(
            self._arm.set_position(z=-20,
                                   radius=0,
                                   speed=self._tcp_speed,
                                   mvacc=self._tcp_acc,
                                   relative=True,
                                   wait=True),
            'set_position'):
            return
        time.sleep(2)
        if not self._check_code(
            self._arm.set_position(z=-10,
                                   radius=0,
                                   speed=self._tcp_speed,
                                   mvacc=self._tcp_acc,
                                   relative=True,
                                   wait=True),
            'set_position'):
            return
        time.sleep(1)
        if not self._check_code(self._arm.set_pause_time(0), 'set_pause_time'):
            return
        if not self._check_code(
            self._arm.set_position(z=-50,
                                   radius=0,
                                   speed=self._tcp_speed,
                                   mvacc=self._tcp_acc,
                                   relative=True,
                                   wait=True),
            'set_position'):
            return
        time.sleep(1)
        if not self._check_code(self._arm.set_cgpio_digital(3, 0, delay_sec=0), 'set_cgpio_digital'):
            return
        time.sleep(0.5)

    def motion_serve(self):
        if not self.alive:
            print("⏸️ 로봇 동작 중단됨 (장애물 감지)")
            return
        if not self._check_code(
            self._arm.set_servo_angle(angle=[18.2, -12.7, 8.3, 90.3, 88.1, 23.6],
                                      speed=self._angle_speed,
                                      mvacc=self._angle_acc,
                                      wait=True,
                                      radius=0.0),
            'set_servo_angle'):
            return
        if not self._check_code(
            self._arm.set_servo_angle(angle=[146.9, -12.7, 8.3, 91.0, 89.3, 22.1],
                                      speed=self._angle_speed,
                                      mvacc=self._angle_acc,
                                      wait=True,
                                      radius=0.0),
            'set_servo_angle'):
            return
        if self.order_msg == 'A':
            if not self._check_code(
                self._arm.set_position(*[-259.8, -144.2, 210.7, 68.3, 86.1, -47.0],
                                       speed=self._tcp_speed,
                                       mvacc=self._tcp_acc,
                                       radius=0.0,
                                       wait=True),
                'set_position'):
                return
            if not self._check_code(
                self._arm.set_position(z=-21,
                                       radius=0,
                                       speed=self._tcp_speed,
                                       mvacc=self._tcp_acc,
                                       relative=True,
                                       wait=False),
                'set_position'):
                return
            if not self._check_code(self._arm.open_lite6_gripper(), 'open_lite6_gripper'):
                return
            time.sleep(1)
            if not self._check_code(self._arm.stop_lite6_gripper(), 'stop_lite6_gripper'):
                return
            time.sleep(1)
            if not self._check_code(
                self._arm.set_tool_position(*[0.0, 0.0, -30, 0.0, 0.0, 0.0],
                                           speed=self._tcp_speed,
                                           mvacc=self._tcp_acc,
                                           wait=True),
                'set_position'):
                return
            if not self._check_code(
                self._arm.set_position(*[-189.7, -26.0, 193.3, -28.1, 88.8, -146.0],
                                       speed=self._tcp_speed,
                                       mvacc=self._tcp_acc,
                                       radius=0.0,
                                       wait=True),
                'set_position'):
                return
        elif self.order_msg == 'B':
            if not self._check_code(
                self._arm.set_servo_angle(angle=[200.1, 22.0, 26.0, 106.5, 88.7, 0.6],
                                          speed=self._angle_speed,
                                          mvacc=self._angle_acc,
                                          wait=True,
                                          radius=0.0),
                'set_servo_angle'):
                return
            if not self._check_code(
                self._arm.set_position(z=-15,
                                       radius=0,
                                       speed=self._tcp_speed,
                                       mvacc=self._tcp_acc,
                                       relative=True,
                                       wait=False),
                'set_position'):
                return
            if not self._check_code(self._arm.open_lite6_gripper(), 'open_lite6_gripper'):
                return
            time.sleep(1)
            if not self._check_code(self._arm.stop_lite6_gripper(), 'stop_lite6_gripper'):
                return
            time.sleep(1)
            if not self._check_code(
                self._arm.set_tool_position(*[0.0, 0.0, -30, 0.0, 0.0, 0.0],
                                           speed=self._tcp_speed,
                                           mvacc=self._tcp_acc,
                                           wait=True),
                'set_position'):
                return
            if not self._check_code(
                self._arm.set_position(*[-168.5, -33.2, 192.8, -92.9, 86.8, -179.3],
                                       speed=self._tcp_speed,
                                       mvacc=self._tcp_acc,
                                       radius=0.0,
                                       wait=True),
                'set_position'):
                return
        elif self.order_msg == 'C':
            if not self._check_code(
                self._arm.set_servo_angle(angle=[171.0, 13.7, 13.5, 73.9, 92.3, -2.9],
                                          speed=self._angle_speed,
                                          mvacc=self._angle_acc,
                                          wait=True,
                                          radius=0.0),
                'set_servo_angle'):
                return
            if not self._check_code(
                self._arm.set_position(*[-62.1, -140.2, 205.5, -68.4, 86.4, -135.0],
                                       speed=self._tcp_speed,
                                       mvacc=self._tcp_acc,
                                       radius=0.0,
                                       wait=True),
                'set_position'):
                return
            if not self._check_code(
                self._arm.set_position(z=-17,
                                       radius=0,
                                       speed=self._tcp_speed,
                                       mvacc=self._tcp_acc,
                                       relative=True,
                                       wait=False),
                'set_position'):
                return
            if not self._check_code(self._arm.open_lite6_gripper(), 'open_lite6_gripper'):
                return
            time.sleep(1)
            if not self._check_code(self._arm.stop_lite6_gripper(), 'stop_lite6_gripper'):
                return
            time.sleep(1)
            if not self._check_code:
                self._arm.set_position(z=-10,
                                    radius=0,
                                    speed=self._tcp_speed,
                                    mvacc=self._tcp_acc,
                                    relative=True,
                                    wait=True)
            if not self._check_code(
                self._arm.set_tool_position(*[0.0, 0.0, -30, 0.0, 0.0, 0.0],
                                           speed=self._tcp_speed,
                                           mvacc=self._tcp_acc,
                                           wait=True),
                'set_position'):
                return
            if not self._check_code(
                self._arm.set_position(*[-98.1, -52.1, 191.4, -68.4, 86.4, -135.0],
                                       speed=self._tcp_speed,
                                       mvacc=self._tcp_acc,
                                       radius=0.0,
                                       wait=True),
                'set_position'):
                return
        if not self._check_code(
            self._arm.set_servo_angle(angle=[169.6, -8.7, 13.8, 85.8, 93.7, 19.0],
                                      speed=self._angle_speed,
                                      mvacc=self._angle_acc,
                                      wait=True,
                                      radius=10.0),
            'set_servo_angle'):
            return

    def motion_trash_capsule(self):
        if not self.alive:
            print("⏸️ 로봇 동작 중단됨 (장애물 감지)")
            return
        self._angle_speed = 150
        self._angle_acc = 300
        if not self._check_code(
            self._arm.set_servo_angle(angle=[51.2, -8.7, 13.8, 95.0, 86.0, 17.0],
                                      speed=self._angle_speed,
                                      mvacc=self._angle_acc,
                                      wait=True,
                                      radius=30.0),
            'set_servo_angle'):
            return
        if not self._check_code(
            self._arm.set_servo_angle(angle=[-16.2, -19.3, 42.7, 82.0, 89.1, 55.0],
                                      speed=self._angle_speed,
                                      mvacc=self._angle_acc,
                                      wait=True,
                                      radius=0.0),
            'set_servo_angle'):
            return
        if not self._check_code(self._arm.open_lite6_gripper(), 'open_lite6_gripper'):
            return
        if not self._check_code(
            self._arm.set_servo_angle(angle=[-19.9, -19.1, 48.7, 87.2, 98.7, 60.0],
                                      speed=self._angle_speed,
                                      mvacc=self._angle_acc,
                                      wait=True,
                                      radius=0.0),
            'set_servo_angle'):
            return
        if not self._check_code(
            self._arm.set_position(*[222.8, 0.9, 470.0, -153.7, 87.3, -68.7],
                                   speed=self._tcp_speed,
                                   mvacc=self._tcp_acc,
                                   radius=0.0,
                                   wait=True),
            'set_position'):
            return
        if not self._check_code(
            self._arm.set_position(*[234.2, 129.8, 464.5, -153.7, 87.3, -68.7],
                                   speed=self._tcp_speed,
                                   mvacc=self._tcp_acc,
                                   radius=0.0,
                                   wait=True),
            'set_position'):
            return
        if not self._check_code(self._arm.close_lite6_gripper(), 'close_lite6_gripper'):
            return
        time.sleep(1)
        if not self._check_code(
            self._arm.set_position(z=30,
                                   radius=-1,
                                   speed=self._tcp_speed,
                                   mvacc=self._tcp_acc,
                                   relative=True,
                                   wait=True),
            'set_position'):
            return
        self._tcp_speed = 100
        self._tcp_acc = 1000
        if not self._check_code(
            self._arm.set_position(*[221.9, 0, 500.4, -153.7, 87.3, -68.7],
                                   speed=self._tcp_speed,
                                   mvacc=self._tcp_acc,
                                   radius=0.0,
                                   wait=True),
            'set_position'):
            return
        self._angle_speed = 60
        self._angle_acc = 100
        if not self._check_code(
            self._arm.set_servo_angle(angle=[-10.7, -2.4, 53.5, 50.4, 78.1, 63.0],
                                      speed=self._angle_speed,
                                      mvacc=self._angle_acc,
                                      wait=True,
                                      radius=10.0),
            'set_servo_angle'):
            return
        self._angle_speed = 160
        self._angle_acc = 1000
        if not self._check_code(
            self._arm.set_servo_angle(angle=[18.0, 11.2, 40.4, 90.4, 58.7, -148.8],
                                      speed=self._angle_speed,
                                      mvacc=self._angle_acc,
                                      wait=True,
                                      radius=0.0),
            'set_servo_angle'):
            return
        if not self._check_code(self._arm.open_lite6_gripper(), 'open_lite6_gripper'):
            return
        if not self._check_code(
            self._arm.set_servo_angle(angle=[25.2, 15.2, 42.7, 83.2, 35.0, -139.8],
                                      speed=self._angle_speed,
                                      mvacc=self._angle_acc,
                                      wait=False,
                                      radius=0.0),
            'set_servo_angle'):
            return
        if not self._check_code(
            self._arm.set_servo_angle(angle=[18.0, 11.2, 40.4, 90.4, 58.7, -148.8],
                                      speed=self._angle_speed,
                                      mvacc=self._angle_acc,
                                      wait=False,
                                      radius=0.0),
            'set_servo_angle'):
            return
        if not self._check_code(
            self._arm.set_servo_angle(angle=[25.2, 15.2, 42.7, 83.2, 35.0, -139.8],
                                      speed=self._angle_speed,
                                      mvacc=self._angle_acc,
                                      wait=True,
                                      radius=0.0),
            'set_servo_angle'):
            return
        if not self._check_code(self._arm.stop_lite6_gripper(), 'stop_lite6_gripper'):
            return
        if not self._check_code(
            self._arm.set_servo_angle(angle=[28.3, -9.0, 12.6, 85.9, 78.5, 20.0],
                                      speed=self._angle_speed,
                                      mvacc=self._angle_acc,
                                      wait=True,
                                      radius=10.0),
            'set_servo_angle'):
            return
        if not self._check_code(
            self._arm.set_servo_angle(angle=[116.8, -9.0, 10.0, 107.1, 78.3, 20.0],
                                      speed=self._angle_speed,
                                      mvacc=self._angle_acc,
                                      wait=True,
                                      radius=10.0),
            'set_servo_angle'):
            return
        if not self._check_code(
            self._arm.set_servo_angle(angle=[179.0, -17.9, 17.7, 176.4, 61.3, 0.0],
                                      speed=self._angle_speed,
                                      mvacc=self._angle_acc,
                                      wait=True,
                                      radius=0.0),
            'set_servo_angle'):
            return
        time.sleep(0.5)

    # ================= RGB 계산 관련 ======================
    def compute_roi_averages(self, roi_positions, num_frames=100):
        """
        roi_positions: dict, { region_key: (x, y, w, h) }
        num_frames: 사용할 프레임 수 (여기서는 100)
        
        100프레임 동안 각 ROI의 평균 RGB (BGR) 값을 계산합니다.
        반환값은 각 ROI별 평균 값을 담은 dict입니다.
        """
        sums = {key: np.zeros(3) for key in roi_positions}
        valid_frames = 0
        for i in range(num_frames):
            ret, frame = self.cap.read()
            # if not frame:
            #     print()
            if not ret:
                continue
            for key, (x, y, w, h) in roi_positions.items():
                # 만약 w나 h가 0이면 한 픽셀 ROI로 처리
                if w == 0 or h == 0:
                    roi = frame[y:y+1, x:x+1]
                else:
                    roi = frame[y:y+h, x:x+w]
                avg = np.mean(roi, axis=(0, 1))  # BGR 순서
                sums[key] += avg
            valid_frames += 1
        if valid_frames == 0:
            return {key: None for key in roi_positions}
        averages = {key: sums[key] / valid_frames for key in sums}
        return averages

    def detect_and_classify_capsules(self, flavor):

        roi_positions = {
            "sti": (508, 233, 95, 84)
        }
        averages = self.compute_roi_averages(roi_positions, num_frames=100)

        # 1분 동안 확인
        for i in range(60):
            capsule_loc = None
            pen_flag = False
            sti_flag = False

            class_names = ['bl_bl', 'bl_st', 'bl_x', 'pen', 'st_bl', 'st_st', 'st_x', 'x_bl', 'x_st', 'x_x']
            st_loc = ['', 'B', '', '', 'A', 'A', 'A', '', 'B', '']
            bl_loc = ['A', 'A', 'A', '', 'B', '', '', 'B', '', '']

            ret, frame = self.cap.read()
            if not ret:
                print("프레임을 읽을 수 없습니다.")
                return None, None

            # YOLO 모델로 프레임 분석
            results = self.model_cap(frame, stream=True)

            for result in results:
                for box in result.boxes:
                    class_id = int(box.cls)  # 감지된 클래스 ID
                    class_name = class_names[class_id]  # 클래스 이름 가져오기
                    if class_name == 'pen':
                        pen_flag = True
                    else:
                        print("캡슐 위치", class_name)
                        if flavor == 'strawberry':
                            capsule_loc = st_loc[class_id]
                        elif flavor == 'blueberry':
                            capsule_loc = bl_loc[class_id]

            # 스티커 확인
            for location, avg in averages.items():
                if avg is None:
                    print(f"⚠️ {location} ROI에서 프레임을 가져오지 못했습니다.")
                    continue
                # avg는 BGR 순서
                avg_r, avg_g, avg_b = avg[2], avg[1], avg[0]
                print(f"📷 {location} 평균 RGB: R={avg_r:.2f}, G={avg_g:.2f}, B={avg_b:.2f}")

                if not (0 <= avg_r <= 255 and 0 <= avg_g <= 255 and 0 <= avg_b <= 255):
                # if not (170 <= avg_r <= 185 and 150 <= avg_g <= 165 and 70 <= avg_b <= 90):
                    print("❌ 스티커가 제대로 놓여있지 않습니다.")
                else:
                    print("✅ 스티커 영역 확인됨.")
                    sti_flag = True

            draw_flag = sti_flag and pen_flag

            # 음성 안내
            if i == 20 or i == 40:
                if not capsule_loc:
                    print("캡슐이 안놓여져 있습니다")
                if not sti_flag:
                    print("스티커를 제대로 놓아주세요")
                if not pen_flag:
                    print("펜을 놓아주세요")
            time.sleep(1)
            
        return capsule_loc, draw_flag

    # ================= YOLO Detection 관련 함수들 (is_collision, expand_box, detect_and_process) ======================
    def is_collision(self, box1, box2):
        x1_inter, y1_inter = max(box1[0], box2[0]), max(box1[1], box2[1])
        x2_inter, y2_inter = min(box1[2], box2[2]), min(box1[3], box2[3])
        return max(0, x2_inter - x1_inter) > 0 and max(0, y2_inter - y1_inter) > 0

    def expand_box(self, box, expansion_factor=0.15):
        x1, y1, x2, y2 = box
        width, height = x2 - x1, y2 - y1
        return [max(0, x1 - width * expansion_factor), max(0, y1 - height * expansion_factor),
                x2 + width * expansion_factor, y2 + height * expansion_factor]

    def detect_and_process(self, frame):
        results = self.model.predict(frame, conf=0.5, save=False, show=False)
        boxes = results[0].boxes.xyxy.cpu().numpy()
        classes = results[0].boxes.cls.cpu().numpy()
        class_names = results[0].names
        robot_boxes, hand_boxes = [], []
        for i, box in enumerate(boxes):
            label = class_names[int(classes[i])]
            expanded_box = self.expand_box(box, 0.2)
            if label == "robot":
                robot_boxes.append(expanded_box)
            else:
                hand_boxes.append(expanded_box)
        collision_boxes = [r_box for r_box in robot_boxes for h_box in hand_boxes if self.is_collision(r_box, h_box)]
        return results[0], bool(collision_boxes), collision_boxes

    def detect_obstacles(self):
        """
        YOLO로 프레임을 분석하여 "hand"가 감지되면 로봇을 정지시키고,
        손이 감지되지 않은 상태가 10초 이상 지속되면 동작을 재개합니다.
        """
        last_hand_time = None  # 마지막으로 손이 감지된 시간
        while not self.end_flag:
            ret, frame = self.cap.read()
            if ret:
                results = self.model.predict(frame, conf=0.5, save=False, show=False)
                boxes = results[0].boxes.xyxy.cpu().numpy()
                classes = results[0].boxes.cls.cpu().numpy()
                class_names = results[0].names
                hand_detected = False
                for i, box in enumerate(boxes):
                    label = class_names[int(classes[i])]
                    if label == "hand":
                        hand_detected = True
                        break

                if hand_detected:
                    print("⚠️ Hand detected! Stopping robot.")
                    self.stop_event.set()
                    # self.resume_event.clear()
                    last_hand_time = time.time()
                else:
                    if last_hand_time is not None:
                        elapsed = time.time() - last_hand_time
                        if elapsed >= 2:
                            print("✅ Hand not detected for 10 seconds. Resuming operation.")
                            self.stop_event.clear()
                            # self.resume_event.set()
                            last_hand_time = None
            time.sleep(0.1)
    # =============================캐리커쳐 그리기===================================        
    def draw_caricature(self, arm_coordinates):

        acc = 100

        for coordinate in arm_coordinates:
            if coordinate == ['up']:
                code = self._arm.set_position(
                z=+10,
                radius=0,
                speed=self._tcp_speed,
                mvacc=acc,
                relative=True,
                wait= True
                )

            elif coordinate == ['down']:
                code = self._arm.set_position(
                z=-10,
                radius=0,
                speed=self._tcp_speed,
                mvacc=acc,
                relative=True,
                wait=True
                )

            else:
                code = self._arm.set_position(
                *coordinate,
                speed=self._tcp_speed,
                mvacc=acc,
                radius=0.0,
                wait=False
                )
        print(' === draw_caricature finish === ')

    def run(self, order_info, arm_coordinates):
        try:
            self.alive = True
            self.stop_event.clear()
            self.motion_home()
            # capsule_loc, draw_flag = self.detect_and_classify_capsules(order_info[0])
            ## 임시
            capsule_loc = "A"
            draw_flag = True

            self.obstacle_thread = threading.Thread(target=self.detect_obstacles)
            self.obstacle_thread.start()

            if capsule_loc:
                if order_info[1]:
                    topping_map = {
                        "jollypong": "A",
                        "chocoball": "B",
                        "sunflower_seeds": "C"
                    }
                    self.order_msg_topping_pos = ''.join(sorted(topping_map.get(t, '') for t in order_info[1]))
                else:
                    self.order_msg_topping_pos = "N"
                # while True:
                self.motion_home()
                if arm_coordinates and draw_flag:
                    self.motion_pick_sequence(label='first')
                    print(arm_coordinates)
                    self.draw_caricature(arm_coordinates)
                    self.motion_pick_sequence_again(label='second')
                self.motion_grab_capsule(capsule_loc)
                self.motion_place_capsule()
                self.motion_grab_cup()
                self.motion_topping()
                self.motion_make_icecream()
                self.motion_serve()
                self.motion_trash_capsule()
                self.motion_home()
                # if not self.alive:
                #     print("⏸️ 로봇 동작 중단됨 (장애물 감지)")
                #     break
            else:
                print("1분 동안 캡슐 혹은 스티커를 제대로 놓지 않아 주문 종료.")
                self.end_flag = True
                self.alive = False
                self.stop_event.set()
                # self.cap.release()
                self.obstacle_thread.join()
                self._arm.release_error_warn_changed_callback(self._error_warn_changed_callback)
                self._arm.release_state_changed_callback(self._state_changed_callback)
                if hasattr(self._arm, 'release_count_changed_callback'):
                    self._arm.release_count_changed_callback(self._count_changed_callback)
                return
            print('icecream finish')
        except Exception as e:
            self.pprint('MainException: {}'.format(e))
        self.end_flag = True
        self.alive = False
        self.stop_event.set()
        # self.cap.release()
        self.obstacle_thread.join()
        self._arm.release_error_warn_changed_callback(self._error_warn_changed_callback)
        self._arm.release_state_changed_callback(self._state_changed_callback)
        if hasattr(self._arm, 'release_count_changed_callback'):
            self._arm.release_count_changed_callback(self._count_changed_callback)

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("--image", type=str, default="/home/addinedu/aris-repo-5/module/image/25=11_Cartoonize Effect.jpg", help="입력 이미지 경로", required=False)
    parser.add_argument("--mask_padding", type=float, default=23, help="", required=False)
    parser.add_argument("--eye_scale_factor", type=float, default=1, help="눈 확대 비율", required=False)
    parser.add_argument("--lip_scale_factor", type=float, default=1, help="입 축소 비율", required=False)
    args = parser.parse_args()

    RobotMain.pprint('xArm-Python-SDK Version:{}'.format(version.__version__))
    arm = XArmAPI('192.168.1.167', baud_checkset=False)
    
    order_info = ['strawberry', ['jollypong', 'chocoball', 'sunflower_seeds'], False]
    robot_main = RobotMain(arm, topping="N")
    # arm_coordinates = caricature(args)
    robot_main.run(order_info, [])
