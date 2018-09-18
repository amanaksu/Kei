# -*- coding:utf-8 -*-
#
# 작성자 : 김승언
# 
# 용도 : Consumer 모듈
# 설명 : 단일 프로세스 모듈
#
# 개발 Log
# 2018.08.06    버전 0.0.5      [개발] 프로토타입 변경
# 2018.08.10    버전 0.0.6      [추가] 분석 완료된 파일 삭제
#
__version__ = "0.0.6"
__author__ = "amanaksu@gmail.com"

# 내장 라이브러리 
from datetime import datetime

import sys

# 서드파티 라이브러리 

# 고유 라이브러리 
from Engines import dispatch
from Engines import Log, gateway
from Engines import skeleton
from Engines import utils

import config


class ConsumerError(Exception):
    def __init__(self, msg):
        self.msg = msg


class Consumer(skeleton.Work):
    def __init__(self, proc_num=config.proc_num):
        skeleton.Work.__init__(self, proc_num=proc_num)
    
    @gateway
    def run(self, queue, stop_flag, queue_wait):
        """[summary]
            Job 단위 분석을 수행하고 완료된 Job은 삭제된다. 

        Arguments:
            queue {instance} -- [description] 분석 Queue 인스턴스
            stop_flag {int} -- [description] 분석 종료 여부 (0 : 분석, 1 : 종료)
            queue_wait {int} -- [description] 분석 Queue가 비었을 때 재탐색까지 대기 시간
        """
        while stop_flag.value is 0 or not queue.empty():
            try:
                # job을 가져온다. 
                try:
                    job = queue.get_nowait()
                except multiprocessing.Queue.Empty:
                    time.sleep(queue_wait)
                    continue

                # 결과 구조체를 생성한다. 
                scanResult = skeleton.ScanResult()
                # 분석 함수 호출 전 시작 시간을 설정한다. 
                scanResult.updateStartTime(datetime.now())

                # 분석한다. 
                dispatch.Dispatch(scanResult, job[0])

                # 분석 결과 반환 전 완료 시간을 설정한다. 
                scanResult.updateEndTime(datetime.now())

                # View 테스트 
                # resultView(scanResult.__dict__)

            except ConsumerError as e:
                Log.error(e.msg)

            except:
                _, msg, obj = sys.exc_info()
                msg = "{} ({}::{})".format(msg, obj.tb_lineno, obj.tb_frame.f_globals.get("__file__"))
                Log.error(msg)

            finally:
                # 임시 폴더를 정리한다. 
                self.__clear__()



def resultView(dict_data, depth=0):
    for key, value in dict_data.items():
        if isinstance(value, dict):
            print("{}{}".format(depth * "    ", key))
            resultView(value, depth = depth + 1)
        elif isinstance(value, (int, str, list)):
            print("{}{} : {}".format(depth * "    ", key, value))    
        else:
            try:
                _tmp_value = value.get()
                print("{}{}".format(depth * "    ", key))
                resultView(_tmp_value, depth = depth + 1)
            except:
                print("{}{} : {}".format(depth * "    ", key, value))    
            