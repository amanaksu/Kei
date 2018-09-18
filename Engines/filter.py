# -*- coding:utf-8 -*-
#
# 작성자 : 김승언
# 
# 용도 : 필터 모듈
# 설명 : 각종 필터링 함수 정의 
#
# 개발 Log
# 2018.08.07    버전 0.0.6      [개발] 멀티 프로세스 생성
#

__version__ = "0.0.6"
__author__ = "amanaksu@gmail.com"

# 내장 라이브러리 
import sys

# 서드파티 라이브러리 

# 고유 라이브러리 
from Engines import Log, gateway
from Engines import utils

import config



class FilterError(Exception):
    def __init__(self, msg):
        self.msg = msg

class FilterPassThru(Exception):
    pass


@gateway
def __is_filtered__(scanObject):
    """[summary]
        설정 조건에 따른 필터링을 수행한다. 

        필터링 결과는 scanObject.result에 dict 형태로 추가된다. 

        * 필터링 조건
            - 용량 (filter_size, int)
            - 포멧 (filter_format, list)

    Arguments:
        scanObject {instance} -- [description] ScanObject 인스턴스

    Returns:
        {bool} -- [description] 필터링 여부 (True : 필터 대상, False : 분석 대상)
    """
    try:
        # 파일 크기 기반으로 필터링을 수행한다. 
        size = scanObject.get_file_size()
        if __is_filtered_by_size__(size):
            raise FilterPassThru

        # 파일 포멧 기반으로 필터링을 수행한다. 
        fformat = scanObject.get_fformat()
        if __is_filtered_by_format__(fformat):
            raise FilterPassThru

        return False

    except FilterPassThru:
        scanObject.updateResult({"error" : True, "err_msg" : "filtered"})
        return True

    except:
        _, msg, obj = sys.exc_info()
        msg = "{} ({}::{})".format(msg, obj.tb_lineno, obj.tb_frame.f_globals.get("__file__"))
        Log.error(msg)
        return True

    finally:
        pass

@gateway
def __is_filtered_by_format__(fformat):
    """[summary]
        파일 포멧 기반으로 필터링한다. 

    Arguments:
        fformat {dict} -- [description] 파일 포멧

    Returns:
        {bool} -- [description] 필터링 여부 (True : 필터 대상, False : 분석 대상)
    """
    try:
        filtered_format = config.filter_format

        if fformat.file_type in filtered_format:
            raise FilterError("exception type by file_type")

        if fformat.name in filtered_format:
            raise FilterError("exception type by yara_name")

        return False

    except FilterError as e:
        Log.error(e.msg)
        return True

    except:
        _, msg, obj = sys.exc_info()
        msg = "{} ({}::{})".format(msg, obj.tb_lineno, obj.tb_frame.f_globals.get("__file__"))
        Log.error(msg)
        return True

    finally:
        pass

@gateway
def __is_filtered_by_size__(size):
    """[summary]
        파일 사이즈 기반으로 필터링한다. 

    Arguments:
        size {int} -- [description] 파일 크기 

    Returns:
        {bool} -- [description] 필터링 여부 (True : 필터 대상, False : 분석 대상)
    """
    try:
        min_size = config.filter_size_min
        max_size = config.filter_size_max
        if min_size == 0 and max_size == 0:
            return False

        if min_size <= size <= max_size:
            return False
        else:
            raise FilterError("the file size is not satisfied with the condition. ({}/{}/{}) ".format(size, min_size, max_size))

    except FilterError as e:
        Log.error(e.msg)
        return True

    except:
        _, msg, obj = sys.exc_info()
        msg = "{} ({}::{})".format(msg, obj.tb_lineno, obj.tb_frame.f_globals.get("__file__"))
        Log.error(msg)
        return True

    finally:
        pass