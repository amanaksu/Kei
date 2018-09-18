# -*- coding:utf-8 -*-
#
# 작성자 : 김승언
# 
# 용도 : 로그 모듈
# 설명 : 프레임워크 동작 과정에 대해 파일/화면에 출력하는 모듈
#
# 개발 Log
# 2018.08.06    버전 0.0.5      [개발] 프로토타입 변경
#
__version__ = "0.0.5"
__author__ = "amanaksu@gmail.com"

# 내장 라이브러리 
from datetime import datetime, timedelta
from logging import getLogger, handlers, Formatter

import inspect
import logging
import os
import sys

# 서드파티 라이브러리 

# 고유 라이브러리 


#########################################################################################################
# 전역 변수
#########################################################################################################
LOG_FORMATTER = "%(asctime)s [%(levelname)-8s] %(message)s"
TIME_FORMATTER = "%Y%m%dT%H%M%S"

#########################################################################################################
# 로그용 클래스
#########################################################################################################
class Log:
    __log_level_map__ = {
        "debug"		:	logging.DEBUG,
        "info"		:	logging.INFO,
        "warn"		:	logging.WARN,
        "error"		:	logging.ERROR,
        "critical"	:	logging.CRITICAL
    }

    __logger__ = None

    @staticmethod
    def init(log_name="", log_level="info", log_path="", log_cmd=False):
        Log.__logger__ = getLogger(log_name)
        Log.__logger__.setLevel(Log.__log_level_map__.get(log_level, "warn"))
        formatter = Formatter(LOG_FORMATTER)
        

        # 로그 핸들러 등록
        if log_cmd:
            # 화면 핸들러 생성
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)

            # 화면 핸들러 등록
            Log.__logger__.addHandler(console_handler)

        else:
            # 파일 핸들러 전처리 
            if not os.path.exists(log_path):
                # 로그 저장 폴더가 없는 경우 
                # 생성한다. 
                os.mkdir(log_path)

            if log_name:
                log_file_name = "{}_{}.log".format(datetime.now().strftime(TIME_FORMATTER), log_name)
            else:
                log_file_name = "{}.log".format(datetime.now().strftime(TIME_FORMATTER))

            log_path = os.path.join(log_path, log_file_name)

            # 파일 핸들러 생성
            file_handler = handlers.TimedRotatingFileHandler(log_path, when="D", interval=1)
            file_handler.setFormatter(formatter)

            # 파일 핸들러 등록 
            Log.__logger__.addHandler(file_handler)
        
    @staticmethod
    def debug(msg="", mod_name="", func_name=""):
        """[summary]
            Debug 로그 정보를 출력한다. 

        Keyword Arguments:
            msg {str} -- [description] 출력할 로그 메시지 (default: {""})
            mod_name {str} -- [description] 출력할 모듈명 (default: {""})
            func_name {str} -- [description] 출력할 함수명 (default: {""})
        """
        if not mod_name:
            mod_name = inspect.getmodule(inspect.stack()[1][0]).__name__

        if not func_name:
            func_name = sys._getframe(1).f_code.co_name
        
        if func_name[0] != ".":
            func_name = "." + func_name
        
        if func_name[-2:] != "()":
            func_name = func_name + "()"

        Log.__logger__.debug("{}{}:{}".format(mod_name, func_name, msg))

    @staticmethod
    def info(msg="", mod_name="", func_name=""):
        """[summary]
            Info 로그 정보를 출력한다. 

        Keyword Arguments:
            msg {str} -- [description] 출력할 로그 메시지 (default: {""})
            mod_name {str} -- [description] 출력할 모듈명 (default: {""})
            func_name {str} -- [description] 출력할 함수명 (default: {""})
        """
        if not mod_name:
            mod_name = inspect.getmodule(inspect.stack()[1][0]).__name__

        if not func_name:
            func_name = sys._getframe(1).f_code.co_name
        
        if func_name[0] != ".":
            func_name = "." + func_name
        
        if func_name[-2:] != "()":
            func_name = func_name + "()"
            
        Log.__logger__.info("{}{}:{}".format(mod_name, func_name, msg))

    @staticmethod
    def warn(msg="", mod_name="", func_name=""):
        """[summary]
            Warn 로그 정보를 출력한다. 

        Keyword Arguments:
            msg {str} -- [description] 출력할 로그 메시지 (default: {""})
            mod_name {str} -- [description] 출력할 모듈명 (default: {""})
            func_name {str} -- [description] 출력할 함수명 (default: {""})
        """
        if not mod_name:
            mod_name = inspect.getmodule(inspect.stack()[1][0]).__name__

        if not func_name:
            func_name = sys._getframe(1).f_code.co_name
        
        if func_name[0] != ".":
            func_name = "." + func_name

        if func_name[-2:] != "()":
            func_name = func_name + "()"
        
        Log.__logger__.warn("{}{}:{}".format(mod_name, func_name, msg))

    @staticmethod
    def error(msg="", mod_name="", func_name=""):
        """[summary]
            Error 로그 정보를 출력한다. 

        Keyword Arguments:
            msg {str} -- [description] 출력할 로그 메시지 (default: {""})
            mod_name {str} -- [description] 출력할 모듈명 (default: {""})
            func_name {str} -- [description] 출력할 함수명 (default: {""})
        """
        if not mod_name:
            mod_name = inspect.getmodule(inspect.stack()[1][0]).__name__

        if not func_name:
            func_name = sys._getframe(1).f_code.co_name
        
        if func_name[0] != ".":
            func_name = "." + func_name
        
        if func_name[-2:] != "()":
            func_name = func_name + "()"

        Log.__logger__.error("{}{}:{}".format(mod_name, func_name, msg))

    @staticmethod
    def critical(msg="", mod_name="", func_name=""):
        """[summary]
            Critical 로그 정보를 출력한다. 

        Keyword Arguments:
            msg {str} -- [description] 출력할 로그 메시지 (default: {""})
            mod_name {str} -- [description] 출력할 모듈명 (default: {""})
            func_name {str} -- [description] 출력할 함수명 (default: {""})
        """
        if not mod_name:
            mod_name = inspect.getmodule(inspect.stack()[1][0]).__name__

        if not func_name:
            func_name = sys._getframe(1).f_code.co_name
        
        if func_name[0] != ".":
            func_name = "." + func_name

        if func_name[-2:] != "()":
            func_name = func_name + "()"

        Log.__logger__.critical("{}{}:{}".format(mod_name, func_name, msg))



######################################################################
# 함수 입출력 로그용 데코레이터
######################################################################
def gateway(f):
    def wrap(*args, **kwargs):
        # 함수 시작
        Log.debug("start", mod_name=f.__module__, func_name=f.__name__)
        start_time = datetime.now()

        # 함수 처리 
        ret = f(*args, **kwargs)

        # 함수 종료
        end_time = datetime.now()
        elasped_time = (end_time - start_time).total_seconds()
        Log.debug("end (Elasped Time: {}s)".format(elasped_time), mod_name=f.__module__, func_name=f.__name__)
        
        return ret
    return wrap