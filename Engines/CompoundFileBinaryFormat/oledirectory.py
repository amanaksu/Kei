# -*- coding:utf-8 -*-
#
# 작성자 : 김승언
# 
# 용도 : OLE Skeleton 모듈
# 설명 : OLE 구조 분석시 사용할 기본 Object 클래스를 정의하는 모듈
#
# 개발 Log
# 2018.08.20    버전 0.0.1      [개발] 프로토 타입 
#

__version__ = "0.0.1"
__author__ = "amanaksu@gmail.com"

# 내장 라이브러리 
import os
import sys


# 서드파티 라이브러리 


# 고유 라이브러리 
from Engines import Log, gateway


class OleDirectoryObject:
    def __init__(self, directory_object):
        self.__parse__(directory_object)

    @gateway
    def __parse__(self, obj):
        try:
            self.name       = obj.name
            self.namelength = obj.namelength
            self.createTime = obj.createTime
            self.modifyTime = obj.modifyTime
            self.color      = obj.color
            self.entry_type = obj.entry_type
            self.sid        = obj.sid
            self.sid_left   = obj.sid_left
            self.sid_right  = obj.sid_right
            self.sid_child  = obj.sid_child
            self.size       = obj.size
        
        except AttributeError:
            # obj.name 이 NoneType으로 나오는 경우
            # Directory Padding을 위해 추가된 Null 데이터.
            pass

        except:
            _, msg, obj = sys.exc_info()
            msg = "{} ({}::{})".format(msg, obj.tb_lineno, obj.tb_frame.f_globals.get("__file__"))
            Log.error(msg)

        finally:
            pass

    @gateway
    def get(self):
        try:
            return self.__dict__

        except:
            _, msg, obj = sys.exc_info()
            msg = "{} ({}::{})".format(msg, obj.tb_lineno, obj.tb_frame.f_globals.get("__file__"))
            Log.error(msg)
            return {}

        finally:
            pass