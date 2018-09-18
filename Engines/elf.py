# -*- coding:utf-8 -*-
#
# 작성자 : 김승언
# 
# 용도 : ELF 모듈
# 설명 : ELF 파일 포맷 분석 
#
# 개발 Log
# 2018.09.12    버전 0.0.1      [개발] 프로토타입 변경

__version__ = "0.0.1"
__author__ = "amanaksu@gmail.com"

# 내장 라이브러리 
import os
import sys

# 서드파티 라이브러리 
from elftools.elf.elffile import ELFFile

# 고유 라이브러리 
from Engines import Log, gateway
from Engines import skeleton
from Engines import utils

import config

class KeiEngineError(Exception):
    def __init__(self, msg):
        self.msg = msg


class KeiEngine(skeleton.EngineProcess):
    def __init__(self):
        skeleton.EngineProcess.__init__(self, __version__, __author__, self.__module__)

    def run(self, scanResult, scanObject):
        """[summary]
             ScanObject 대상을 분석한다. 

        Arguments:
             scanResult {instance} -- [description] ScanResult 인스턴스
             scanObject {instance} -- [description] ScanObject 인스턴스 
        """
        error = False
        err_msg = ""

        fp = None
        try:
            fileName = scanObject.get_file_name()
            
            fp = open(fileName, "rb")
            elffile = ELFFile(fp)
            for sect in elffile.iter_sections():
                scanObject.updateStructure(sect.name, sect.header)  

        except:
            # 에러 로그를 저장한다. 
            _, msg, obj = sys.exc_info()
            msg = "{} ({}::{})".format(msg, obj.tb_lineno, obj.tb_frame.f_globals.get("__file__"))
            Log.error(msg)

            # 에러 결과를 ScanObject에 업데이트할 수 있도록 상태값을 변경한다. 
            error = True
            err_msg = msg
            
        finally:
            if fp:
                fp.close()

            scanObject.updateResult(error, err_msg)