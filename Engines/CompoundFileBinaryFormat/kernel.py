# -*- coding:utf-8 -*-
#
# 작성자 : 김승언
# 
# 용도 : OLE 공용 라이브러리 
# 설명 : OLE 파일 분석 및 기타 동작을 위해 필요한 공용 함수를 정의한 모듈
#
# 개발 Log
# 2018.08.14    버전 0.0.1      [개발] 프로토타입 변경
#
__version__ = "0.0.1"
__author__ = "amanaksu@gmail.com"

# 내장 라이브러리 
import os
import sys
import zlib

# 서드파티 라이브러리 
import olefile

# 고유 라이브러리 
from Engines import Log, gateway
from Engines import utils

import config


class OLEKernelError(Exception):
    def __init__(self, msg):
        self.msg = msg


@gateway
def get_ole_object(fileName):
    try:
        return olefile.OleFileIO(fileName)

    except:
        _, msg, obj = sys.exc_info()
        msg = "{} ({}::{})".format(msg, obj.tb_lineno, obj.tb_frame.f_globals.get("__file__"))
        Log.error(msg)
        return None

    finally:
        pass

@gateway
def is_ole(fileName):
    try:
        return olefile.isOleFile(fileName)

    except:
        _, msg, obj = sys.exc_info()
        msg = "{} ({}::{})".format(msg, obj.tb_lineno, obj.tb_frame.f_globals.get("__file__"))
        Log.error(msg)
        return False

    finally:
        pass

@gateway
def convert_entryname(entryName):
    try:
        new_entry_name = []
        for i, name in enumerate(entryName):
            name_int = ord(name[0])
            if not (name_int > 10):
                name = "x{:02}{}".format(name_int, name[1:])
            
            new_entry_name.append(name)

        return new_entry_name

    except:
        _, msg, obj = sys.exc_info()
        msg = "{} ({}::{})".format(msg, obj.tb_lineno, obj.tb_frame.f_globals.get("__file__"))
        Log.error(msg)
        return []

    finally:
        pass

@gateway
def extract(fileName):
    try:
        # OLE 파일 인스턴스를 생성한다. 
        ole = get_ole_object(fileName)
        if not ole:
            raise OLEKernelError("Failed Get OLE Object.")

        units = []
        for ori_stream in ole.listdir():
            # ori_stream[0] : Storage
            # ori_stream[1:]: Stream
            new_stream = convert_entryname(ori_stream)
            
            # 저장할 파일 경로를 생성한다. 
            # <temp_path>//<embedding>//<fileName>
            embedded_path = os.path.join(config.temp_path, config.dir_q_monitor.get("embedding"))
            basename = "{}_{}.{}".format(os.path.basename(fileName),
                                         config.extend_seperate.join(new_stream), 
                                         config.extend)
            embedded_name = os.path.join(embedded_path, basename)
            
            # 파일을 저장한다. 
            stream = ole.openstream(ori_stream)
            bytes_data = stream.read()

            # 파일 저장이 실패한 경우
            if not utils.writefile_ex(embedded_name, bytes_data):
                Log.error("Failed write file for embedding. ({})".format(basename))
                continue

            Log.debug(embedded_name)

            # 파일이 저장된 경우
            unit = {
                        "fileName"    : embedded_name,
                        "internal_path" : new_stream
                    }
            units.append(unit)

        return units

    except OLEKernelError as e:
        Log.error(e.msg)
        return []

    except:
        _, msg, obj = sys.exc_info()
        msg = "{} ({}::{})".format(msg, obj.tb_lineno, obj.tb_frame.f_globals.get("__file__"))
        Log.error(msg)
        return []

    finally:
        pass

@gateway
def get_directories(fileName):
    ole = None
    try:
        ole = get_ole_object(fileName)
        if ole:
            return ole.direntries
        else:
            raise KeiEngineError("Failed get ole object.")

    except KeiEngineError as e:
        Log.error(e.msg)
        return []

    except:
        _, msg, obj = sys.exc_info()
        msg = "{} ({}::{})".format(msg, obj.tb_lineno, obj.tb_frame.f_globals.get("__file__"))
        Log.error(msg)
        return []

    finally:
        if ole:
            ole.close()

@gateway
def unzip(data):
    try:
        return zlib.decompress(data, -15)

    except:
        _, msg, obj = sys.exc_info()
        msg = "{} ({}::{})".format(msg, obj.tb_lineno, obj.tb_frame.f_globals.get("__file__"))
        Log.error(msg)
        return ""

    finally:
        pass  

