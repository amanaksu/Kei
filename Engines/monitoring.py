# -*- coding:utf-8 -*-
#
# 작성자 : 김승언
# 
# 용도 : Monitoring 모듈
# 설명 : 분석 대상의 현재 상태를 모니터링하기 위한 모듈 
#
# 개발 Log
# 2018.08.14    버전 0.0.5      [개발] 프로토타입 변경
#

__version__ = "0.0.5"
__author__ = "amanaksu@gmail.com"

# 내장 라이브러리 
import os
import sys

# 서드파티 라이브러리 

# 고유 라이브러리 
from Engines import Log, gateway
from Engines import skeleton
from Engines import utils

import config


class QueueMonitorError(Exception):
    def __init__(self, msg):
        self.msg = msg

@gateway
def __waiting__(scanObject):
    """[summary]
        분석 대상 파일의 상태를 변경한다. 
        
        * 변경 시점 : dispatch.Dispatch() 내 _get_metadata() 완료 시점
        * 변경 위치 : 원본 파일 경로 -> <temp_path>\\<waiting>\\<uid>\\<fileName>
        
    Arguments:
        scanObject {instance} -- [description] ScanObject 인스턴스 
    """
    try:
        # 분석 대상 파일의 현재 경로를 가져온다. 
        # src : 원본 파일 경로
        src = scanObject.get_file_name()
        
        # 분석 대상 파일의 변경할 경로를 가져온다. 
        # 위치 : <temp_path>\\<waiting>\\<uid>\\<fileName>
        dstDir1 = os.path.join(config.temp_path, config.dir_q_monitor.get("waiting"))
        if not utils.is_exists(dstDir1):
            utils.makedirectory(dstDir1)

        dstDir2 = os.path.join(dstDir1, scanObject.get_uid())
        if not os.path.exists(dstDir2):
            utils.makedirectory(dstDir2)

        dst = os.path.join(dstDir2, os.path.basename(src))

        # 테스트
        # - 파일명 내에 한글이고 띄어쓰기가 있는 경우
        dst = dst.replace(" ", "_")
        dst = dst.replace("\\", "\\\\")

        # 파일을 복사한다. 
        if not utils.copyfile(src, dst):
            raise QueueMonitorError("Failed change status to wait. ({})".format(scanObject.get_uid()))

        Log.debug("[ORI -> WAIT] {}".format(os.path.basename(src)))

        # 복사에 성공하면 분석 대상 파일의 경로를 변경한다. 
        scanObject.update_file_name(dst)

    except QueueMonitorError as e:
        Log.error(e.msg)

    except:
        _, msg, obj = sys.exc_info()
        msg = "{} ({}::{})".format(msg, obj.tb_lineno, obj.tb_frame.f_globals.get("__file__"))
        Log.error(msg)
        

    finally:
        pass

@gateway
def __analyzing__(scanObject):
    """[summary]
        분석 대상 파일의 상태를 변경한다. 

        * 변경 시점 : _run_module() 실행시 Skeleton.EngineProcess.__run__() 시점
        * 변경 위치 : <waiting> -> <temp_path>\\<analyzing>\\<uid>\\<fileName>

    Arguments:
        scanObject {instance} -- [description] ScanObject 인스턴스 
    
    KeyArgument:
        fileName {str} -- [description] 분석 대상 파일 (optional), 주로 분석 엔진에서 선분석시 요청됨.
    """
    try:
        # 분석 대상 파일의 현재 경로를 가져온다. 
        ori_fileName = scanObject.get_file_name()
        srcDir, fileName = os.path.split(ori_fileName)
                
        # 분석 대상 파일의 변경할 경로를 가져온다. 
        dstDir = os.path.join(config.temp_path, config.dir_q_monitor.get("analyzing"))
        if not utils.is_exists(dstDir):
            utils.makedirectory(dstDir)

        # 원본 파일을 이동 시킨다. 
        # srcDir : <temp_path>\\<waiting>\\<uid> 또는 <temp_path>\\<embedding>
        # dstDir : <temp_path>\\<analyzing>
        if not utils.movefile(srcDir, dstDir):
            raise QueueMonitorError("Failed change status to analyzing. ({})".format(scanObject.get_uid()))

        Log.debug("[WAIT -> ANLZ] {}".format(fileName))

        # 복사에 성공하면 분석 대상 파일의 경로를 변경한다. 
        dst_fileName1 = os.path.join(dstDir, scanObject.get_uid())
        dst_fileName = os.path.join(dst_fileName1, fileName)
        
        scanObject.update_file_name(dst_fileName)

    except QueueMonitorError as e:
        Log.error(e.msg)

    except:
        _, msg, obj = sys.exc_info()
        msg = "{} ({}::{})".format(msg, obj.tb_lineno, obj.tb_frame.f_globals.get("__file__"))
        Log.error(msg)
        
    finally:
        pass

@gateway
def __except__(scanObject):
    """[summary]
        분석 대상 파일의 상태를 변경한다. 

        * 변경 시점 : dispatch.Dispatch() 내 DispatchPassThru 예외가 발생한 시점.
        * 변경 위치 : <waiting> -> <temp_path>\\<except>\\<uid>\\<fileName>

    Arguments:
        scanObject {instance} -- [description] ScanObject 인스턴스 
    """
    try:
        # 분석 대상 파일의 현재 경로를 가져온다. 
        ori_fileName = scanObject.get_file_name()
        srcDir, fileName = os.path.split(ori_fileName)
                
        # 분석 대상 파일의 변경할 경로를 가져온다. 
        dstDir = os.path.join(config.temp_path, config.dir_q_monitor.get("except"))
        if not utils.is_exists(dstDir):
            utils.makedirectory(dstDir)

        # 원본 파일을 이동 시킨다. 
        # srcDir : <temp_path>\\<waiting>\\<uid>
        # dstDir : <temp_path>\\<analyzing>
        if not utils.movefile(srcDir, dstDir):
            raise QueueMonitorError("Failed change status to except. ({})".format(scanObject.get_uid()))

        Log.debug("[ANLZ -> EXPT] {}".format(fileName))

        # 복사에 성공하면 분석 대상 파일의 경로를 변경한다. 
        dst_fileName1 = os.path.join(dstDir, scanObject.get_uid())
        dst_fileName = os.path.join(dst_fileName1, fileName)

        scanObject.update_file_name(dst_fileName)

    except QueueMonitorError as e:
        Log.error(e.msg)

    except:
        _, msg, obj = sys.exc_info()
        msg = "{} ({}::{})".format(msg, obj.tb_lineno, obj.tb_frame.f_globals.get("__file__"))
        Log.error(msg)
        
    finally:
        pass        

@gateway
def __error__(scanObject):
    """[summary]
        분석 대상 파일의 상태를 변경한다. 

        * 변경 시점 : dispatch.Dispatch() 내 DispatchModuleError 예외가 발생한 시점.
        * 변경 위치 : <analyzing> -> <temp_path>\\<error>\\<uid>\\<fileName>

    Arguments:
        scanObject {instance} -- [description] ScanObject 인스턴스 
    """
    try:
        # 분석 대상 파일의 현재 경로를 가져온다. 
        ori_fileName = scanObject.get_file_name()
        srcDir, fileName = os.path.split(ori_fileName)
                
        # 분석 대상 파일의 변경할 경로를 가져온다. 
        dstDir = os.path.join(config.temp_path, config.dir_q_monitor.get("error"))
        if not utils.is_exists(dstDir):
            utils.makedirectory(dstDir)

        # 원본 파일을 이동 시킨다. 
        # srcDir : <temp_path>\\<waiting>\\<uid>
        # dstDir : <temp_path>\\<analyzing>
        if not utils.movefile(srcDir, dstDir):
            raise QueueMonitorError("Failed change status to error. ({})".format(scanObject.get_uid()))

        Log.debug("[ANLZ -> ERR] {}".format(fileName))

        # 복사에 성공하면 분석 대상 파일의 경로를 변경한다. 
        dst_fileName1 = os.path.join(dstDir, scanObject.get_uid())
        dst_fileName = os.path.join(dst_fileName1, fileName)

        scanObject.update_file_name(dst_fileName)

    except QueueMonitorError as e:
        Log.error(e.msg)
        
    except:
        _, msg, obj = sys.exc_info()
        msg = "{} ({}::{})".format(msg, obj.tb_lineno, obj.tb_frame.f_globals.get("__file__"))
        Log.error(msg)
        
    finally:
        pass        

@gateway
def __complete__(scanObject):
    """[summary]
        분석 대상 파일의 상태를 변경한다. 

        * 변경 시점 : dispatch.Dispatch() 내 분석 완료 시점
        * 변경 위치 : <analyzing> -> <temp_path>\\<complete>\\<uid>\\<fileName>

    Arguments:
        scanObject {instance} -- [description] ScanObject 인스턴스 
    """
    try:
        # 분석 대상 파일의 현재 경로를 가져온다. 
        ori_fileName = scanObject.get_file_name()
        srcDir, fileName = os.path.split(ori_fileName)
                
        # 분석 대상 파일의 변경할 경로를 가져온다. 
        dstDir = os.path.join(config.temp_path, config.dir_q_monitor.get("complete"))
        if not utils.is_exists(dstDir):
            utils.makedirectory(dstDir)

        # 원본 파일을 이동 시킨다. 
        # srcDir : <temp_path>\\<waiting>\\<uid>
        # dstDir : <temp_path>\\<analyzing>
        if not utils.movefile(srcDir, dstDir):
            raise QueueMonitorError("Failed change status to complete. ({})".format(scanObject.get_uid()))

        Log.debug("[ANLZ -> CMPT] {}".format(fileName))

        # 복사에 성공하면 분석 대상 파일의 경로를 변경한다. 
        dst_fileName1 = os.path.join(dstDir, scanObject.get_uid())
        dst_fileName = os.path.join(dst_fileName1, fileName)

        scanObject.update_file_name(dst_fileName)

    except QueueMonitorError as e:
        Log.error(e.msg)
        
    except:
        _, msg, obj = sys.exc_info()
        msg = "{} ({}::{})".format(msg, obj.tb_lineno, obj.tb_frame.f_globals.get("__file__"))
        Log.error(msg)
        
    finally:
        pass  