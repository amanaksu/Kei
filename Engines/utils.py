# -*- coding:utf-8 -*-
#
# 작성자 : 김승언
# 
# 용도 : 유틸 모듈
# 설명 : 공통으로 사용하는 함수 모듈
#
# 개발 Log
# 2018.08.06    버전 0.0.5      [개발] 프로토타입 변경
# 2018.08.07    버전 0.0.6      [개발] Encode/Decode 함수 추가 
# 2018.08.08    버전 0.0.7      [수정] yara_on_demand() : Yara 폴더 -> Yara 폴더 및 파일
# 2018.08.20    버전 0.0.8      [개발] deepcopy()

__version__ = "0.0.8"
__author__ = "amanaksu@gmail.com"

# 내장 라이브러리 
import codecs
import copy
import importlib
import json
import multiprocessing
import os
import shutil
import struct
import sys
import tempfile
import uuid
import yara
import zipfile
import zlib

# 서드파티 라이브러리 

# 고유 라이브러리 
from Engines import Log, gateway

import config



#########################################################################################################
# 전역 변수
#########################################################################################################
PY_MAJOR_VER = sys.version_info.major
PY_MINOR_VER = sys.version_info.minor



#########################################################################################################
# 파일 I/O
#########################################################################################################
class FileIOError(Exception):
    def __init__(self, msg):
        self.msg = msg

@gateway
def writefile(fullName, data):
    try:
        with open(fullName, "wb") as wp:
            wp.write(data)
            # wp.flush()
            # wp.truncate()
        
        return True

    except:
        _, msg, obj = sys.exc_info()
        msg = "{} ({}::{})".format(msg, obj.tb_lineno, obj.tb_frame.f_globals.get("__file__"))
        Log.error(msg)
        return False

    finally:
        pass

@gateway
def writefile_ex(fileName, data):
    """[summary]
        파일을 생성한다. 

    Arguments:
        fileName {str} -- [description] 생성할 파일명
        data {binary} -- [description] 생성할 데이터
    """
    try:
        fullName = os.path.join(config.temp_path, fileName)
        return writefile(fullName, data)

    except:
        _, msg, obj = sys.exc_info()
        msg = "{} ({}::{})".format(msg, obj.tb_lineno, obj.tb_frame.f_globals.get("__file__"))
        Log.error(msg)
        return False

    finally:
        pass

@gateway
def deletedirectory(dirName):
    """[summary]
        전체 경로의 폴더를 삭제한다. 

    Arguments:
        dirName {str} -- [description] 폴더 전체 경로
    """
    try:
        if is_dir(dirName) and is_exists(dirName):
            shutil.rmtree(dirName)
            return True
        else:
            raise FileIOError("{} is not directory or not exists.".format(dirName))
        
    except FileIOError as e:
        Log.error(e.msg)
        return False

    except:
        _, msg, obj = sys.exc_info()
        msg = "{} ({}::{})".format(msg, obj.tb_lineno, obj.tb_frame.f_globals.get("__file__"))
        Log.error(msg)
        return False

    finally:
        pass

@gateway    
def deletefile(fileName):
    """[summary]
        전체 경로의 파일을 삭제한다.

    Arguments:
        fileName {str} -- [description] 파일 전체 경로
    """
    try:
        if is_file(fileName) and is_exists(fileName):
            os.remove(fileName)
            return True
        else:
            raise FileIOError("{} is not file or not exists.".format(fileName))

    except FileIOError as e:
        Log.error(e.msg)
        return False

    except:
        _, msg, obj = sys.exc_info()
        msg = "{} ({}::{})".format(msg, obj.tb_lineno, obj.tb_frame.f_globals.get("__file__"))
        Log.error(msg)
        return False

    finally:
        pass

@gateway
def copyfile(src, dst):
    """[summary]
        파일을 복사한다. 

    Arguments:
        src {str} -- [description] 원본 파일 경로
        dst {str} -- [description] 복사할 파일 경로

    Returns:
        {bool} -- [description] 파일 복사 여부 
    """
    try:
        dirName = os.path.dirname(dst)
        if not os.path.exists(dirName):
            if not makedirectory(dirName):
                raise FileIOError("Failed MakeDirectory ({})".format(dirName))

        shutil.copyfile(src, dst)
        return True

    except FileIOError as e:
        Log.error(e.msg)
        return False

    except:
        _, msg, obj = sys.exc_info()
        msg = "{} ({}::{})".format(msg, obj.tb_lineno, obj.tb_frame.f_globals.get("__file__"))
        Log.error(msg)
        return False

    finally:
        pass   

@gateway
def movefile(src, dst):
    """[summary]
        파일을 이동시킨다. 

    Arguments:
        src {str} -- [description] 원본 파일 경로
        dst {str} -- [description] 이동할 파일 경로

    Returns:
        {bool} -- [description] 파일 이동 여부 
    """
    try:
        dirName = os.path.dirname(dst)
        if not os.path.exists(dirName):
            if not makedirectory(dirName):
                raise FileIOError("Failed MakeDirectory ({})".format(dirName))

        shutil.move(src, dst)
        return True
    
    except FileIOError as e:
        Log.error(e.msg)
        return False

    except:
        _, msg, obj = sys.exc_info()
        msg = "{} ({}::{})".format(msg, obj.tb_lineno, obj.tb_frame.f_globals.get("__file__"))
        Log.error(msg)
        return False

    finally:
        pass   

@gateway
def makedirectory(dirName):
    try:
        if not os.path.exists(dirName):
            os.mkdir(dirName)

        return True 

    except:
        _, msg, obj = sys.exc_info()
        msg = "{} ({}::{})".format(msg, obj.tb_lineno, obj.tb_frame.f_globals.get("__file__"))
        Log.error(msg)
        return False

    finally:
        pass

@gateway
def create_temp_file(temp_path, temp_data):
    try:
        with tempfile.NamedTemporaryFile(dir=temp_path, delete=True) as tmpfile:
            temp_file_name = tmpfile.name

        if writefile(temp_file_name, temp_data):
            return temp_file_name
        else:
            raise FileIOError("Failed Create Temp File. ({})".format(temp_file_name))           

    except FileIOError as e:
        Log.error(e.msg)
        return ""

    except:
        _, msg, obj = sys.exc_info()
        msg = "{} ({}::{})".format(msg, obj.tb_lineno, obj.tb_frame.f_globals.get("__file__"))
        Log.error(msg)
        return ""

    finally:
        pass


#########################################################################################################
# Binary I/O 함수
#########################################################################################################
def readData(endian, data, data_type, unit, offset, size):
    # b	    signed char	        integer	            1	(1),(3)
    # B	    unsigned char	    integer	            1	(3)
    # H	    unsigned short	    integer	            2	(3)
    # i	    int	                integer	            4	(3)
    # I	    unsigned int	    integer	            4	(3)
    # L	    unsigned long	    integer	            4	(3)
    # Q	    unsigned long long	integer	            8	(2), (3)
    # s	    char[]	            bytes	 	 
    try:
        result = struct.unpack("{}{}{}".format(endian, unit, data_type), data[offset:offset + size])[0]
        if data_type in ["s"]:
            return convert_ToUTF8(result)
        else:
            return result

    except FileIOError as e:
        Log.error(e.msg)
        return None

    except:
        _, msg, obj = sys.exc_info()
        msg = "{} ({}::{})".format(msg, obj.tb_lineno, obj.tb_frame.f_globals.get("__file__"))
        Log.error(msg)
        return None

    finally:
        pass
    
def readString(endian, data, data_type, offset, size):
    return struct.unpack("{}{}{}".format(endian, size, data_type), data[offset:offset + size])

def readNumber(endian, data, data_type, offset, size):
    return struct



#########################################################################################################
# Yara 룰 함수
#########################################################################################################
class YaraError(Exception):
    def __init__(self, msg):
        self.msg = msg

@gateway
def isPossibleYaraPython():
    """[summary]
        파이썬이 지원가능한 버전인지 확인한다. 

        * 지원 버전 : 2.7.x <= Python <= 3.5    

    Returns:
        {bool} -- [description] 지원 가능 여부 (True : 지원 가능, False : 지원불가)
    """
    try:
        return True if config.support_min_ver <= float("{}.{}".format(PY_MAJOR_VER, PY_MINOR_VER)) <= config.support_max_ver else False

    except:
        _, msg, obj = sys.exc_info()
        msg = "{} ({}::{})".format(msg, obj.tb_lineno, obj.tb_frame.f_globals.get("__file__"))
        Log.error(msg)
        return False

    finally:
        pass

@gateway
def _yara_group(yaraList):
    """[summary]
        Yara 룰 파일 목록을 List 타입에서 dict 타입으로 변환한다. 
        변환된 dict 형식으로 컴파일한다. 

    Arguments:
        yaraList {list} -- [description] Yara 룰 파일 목록
    
    Returns:
        {dict} -- [description] dict 로 변환된 Yara 룰 파일 목록
    """
    try:
        return {os.path.basename(yara_file).split(".")[0] : yara_file for yara_file in yaraList}

    except:
        _, msg, obj = sys.exc_info()
        msg = "{} ({}::{})".format(msg, obj.tb_lineno, obj.tb_frame.f_globals.get("__file__"))
        Log.error(msg)
        return {}

    finally:
        pass

@gateway
def yara_on_demand(yara_rule_path, fileName):
    """[summary]
        Yara 룰을 통해 파일을 식별한다. 

    Arguments:
        yara_rule_path {str} -- [description] Yara 파일 경로 (폴더, 파일)
        fileName {str} -- [description] Yara 룰 검사 대상 
    """
    try:
        # Yara-Python 이 가능한 버전인지 확인한다. 
        if not isPossibleYaraPython():
            # Yara-Python을 지원하지 않는 경우 
            raise YaraError("Python {}.{} is not support.".format(PY_MAJOR_VER, PY_MINOR_VER))

        # Yara-Python을 지원하는 경우 
        # 컴파일을 위한 형식(dict)으로 변환한다. 
        if is_file(yara_rule_path):
            yaraList = [yara_rule_path]
        else:
            yaraList = get_file_path_in_folder(yara_rule_path)
        groups = _yara_group(yaraList)

        # 컴파일한다. 
        rules = yara.compile(filepaths=groups)

        # 검사한다. 
        return rules.match(filepath=fileName)

    except YaraError as e:
        Log.error(e.msg)
        return []

    except:
        _, msg, obj = sys.exc_info()
        msg = "{} ({}::{})".format(msg, obj.tb_lineno, obj.tb_frame.f_globals.get("__file__"))
        Log.error(msg)
        return []

    finally:
        pass


#########################################################################################################
# DB 함수
#########################################################################################################
def save_json(result_json):
    try:
        print(result_json)
        return True
    except:
        _, msg, obj = sys.exc_info()
        msg = "{} ({}::{})".format(msg, obj.tb_lineno, obj.tb_frame.f_globals.get("__file__"))
        Log.error(msg)
        return False

    finally:
        pass


#########################################################################################################
# 문자열 Encoding/Decoding 함수
#########################################################################################################
class EncodeError(Exception):
    def __init__(self, msg):
        self.msg = msg


def slashescape(err):
    thebyte = err.object[err.start:err.end]
    repl = u"\\x" + hex(ord(thebyte))[2:]
    return (repl, err.end)

codecs.register_error("slashescape", slashescape)


@gateway
def convert_ToUTF8(thing):
    try:
        if isinstance(thing, str):
            return thing

        if PY_MAJOR_VER == 2:
            return convert_str2utf8_for_py2(thing)
        else:
            return convert_str2utf8_for_py3(thing)
    except:
        _, msg, obj = sys.exc_info()
        msg = "{} ({}::{})".format(msg, obj.tb_lineno, obj.tb_frame.f_globals.get("__file__"))
        Log.error(msg)
        return ""

    finally:
        pass

@gateway
def convert_str2utf8_for_py2(thing):
    try:
        t = type(thing)

        if t in [str]:
            return unicode(thing, "utf-8", errors="replace").encode("utf-8")

        elif t in [unicode]:
            return thing.encode("utf-8")

        elif t in [list, set, frozenset]:
            new_obj = []
            for o in thing:
                new_obj.append(convert_str2utf8_for_py2(o))
            return new_obj

        elif t in [dict]:
            new_obj = {}
            for key, value in thing.iteritems():
                new_key = cleanKey(key)
                new_val = convert_str2utf8_for_py2(value)
                new_obj[new_key] = new_val
            return new_obj

        elif t in [int, float, long, complex]:
            return thing

        if t in [uuid.UUID]:
            return str(thing)
        else:
            return repr(thing)

    except:
        _, msg, obj = sys.exc_info()
        msg = "{} ({}::{})".format(msg, obj.tb_lineno, obj.tb_frame.f_globals.get("__file__"))
        Log.error(msg)
        return ""

    finally:
        pass

def cleanKey(key):
    try:
        bad_chars = ["\0", ",", "$"]
        new_key = key
    
        if not (isinstance(key, str) or isinstance(key, unicode)):
            new_key = str(new_key)

        for c in bad_chars:
            new_key = new_key.replace(c, "_")

        return convert_str2utf8_for_py2(new_key)

    except:
        _, msg, obj = sys.exc_info()
        msg = "{} ({}::{})".format(msg, obj.tb_lineno, obj.tb_frame.f_globals.get("__file__"))
        Log.error(msg)
        return ""

    finally:
        pass

@gateway
def convert_str2utf8_for_py3(thing):
    try:
        return thing.decode("utf-8", "slashescape")

    except:
        _, msg, obj = sys.exc_info()
        msg = "{} ({}::{})".format(msg, obj.tb_lineno, obj.tb_frame.f_globals.get("__file__"))
        Log.error(msg)
        return ""
        
    finally:
        pass

@gateway
def convert_dict2json(dict_data):
    return json.dump(dict_data)

@gateway
def convert_dict2serialize(dict_data):
    return json.dumps(dict_data)

@gateway
def compress(normal_data):
    try:
        return zlib.compress(normal_data)

    except:
        _, msg, obj = sys.exc_info()
        msg = "{} ({}::{})".format(msg, obj.tb_lineno, obj.tb_frame.f_globals.get("__file__"))
        Log.error(msg)
        return ""

    finally:
        pass

@gateway
def decompress(compress_data):
    try:
        return zlib.decompress(compress_data)

    except:
        _, msg, obj = sys.exc_info()
        msg = "{} ({}::{})".format(msg, obj.tb_lineno, obj.tb_frame.f_globals.get("__file__"))
        Log.error(msg)
        return ""

    finally:
        pass

@gateway
def unzip(unzip_path, zip_data):
    z = None
    temp_file = None
    try:
        # 임시 파일을 생성한다. 
        temp_file = create_temp_file(unzip_path, zip_data)

        if temp_file:
            # 임시 파일 생성이 성공한 경우 
            # 압축을 해제한다. 
            z = zipfile.ZipFile(open(temp_file, "rb"))
            # 압축 파일내 단일 파일만 존재한다. 
            z.extractall(unzip_path)

        else:
            # 임시 파일 생성이 실패한 경우 
            raise EncodeError("Failed Temp File.")

        return True

    except EncodeError as e:
        Log.error(e.msg)
        return False

    except:
        _, msg, obj = sys.exc_info()
        msg = "{} ({}::{})".format(msg, obj.tb_lineno, obj.tb_frame.f_globals.get("__file__"))
        Log.error(msg)
        return False

    finally:
        if z:
            z.close()

        if temp_file:
            deletefile(temp_file)

#########################################################################################################
# 유틸리티 함수
#########################################################################################################
class UtilityError(Exception):
    def __init__(self, msg):
        self.msg = msg

@gateway
def deepcopy(data):
    """[summary]
        데이터를 deepcopy 한다. 

    Arguments:
        data {} -- [description] 복사할 데이터 
    """
    return copy.deepcopy(data)

@gateway
def load_module(mod_name):
    """[summary]
        Engines 하위 경로의 모듈을 동적으로 로드한다. 

    Arguments:
        mod_name {[str]} -- [description] 로드할 모듈 경로/이름
    
    Returns:
        {handle} -- [description] 로드된 모듈 핸들 
    """
    try:
        return importlib.import_module("Engines.{}".format(mod_name))

    except:
        _, msg, obj = sys.exc_info()
        msg = "{} ({}::{})".format(msg, obj.tb_lineno, obj.tb_frame.f_globals.get("__file__"))
        Log.error(msg)
        return None

    finally:
        pass

@gateway
def is_exists(filePath):
    """[summary]
        파일이 존재하는지 확인한다. 

    Arguments:
        filePath {[str]} -- [description] 파일 경로

    Returns:
        {boolean} -- [description] 존재여부
    """
    return os.path.exists(filePath)

@gateway
def is_file(filePath):
    """[summary]
        파일인지 확인한다. 

    Arguments:
        filePath {[str]} -- [description] 파일 경로
    
    Returns:
        {boolean} -- [description] 파일여부 
    """
    return os.path.isfile(filePath)

@gateway
def is_dir(dirPath):
    """[summary]
        디렉토리인지 확인한다. 

    Arguments:
        dirPath {[str]} -- [description] 디렉토리 경로
    
    Returns:
        {boolean} -- [description] 디렉토리여부 
    """
    return os.path.isdir(dirPath)

@gateway
def get_abs_file_path(rootPath, fileName):
    """[summary]
        파일의 절대 경로를 생성한다. 

    Arguments:
        rootPath {[str]]} -- [description] (optional) Root 폴더 경로
        fileName {[str]} -- [description] 파일명

    Returns:
        {str} -- [description] 파일 절대 경로 
    """
    try:
        if rootPath:
            return os.path.join(rootPath, fileName)
        else:
            return os.path.abspath(fileName)

    except:
        _, msg, obj = sys.exc_info()
        msg = "{} ({}::{})".format(msg, obj.tb_lineno, obj.tb_frame.f_globals.get("__file__"))
        Log.error(msg)
        return ""

    finally:
        pass

@gateway
def get_file_path(rootPath="", fileName=""):
    """[summary]
        파일의 절대 경로를 생성한다. 

    Keyword Arguments:
        rootPath {str} -- [description] (optional) Root 폴더 경로 (default: {""})
        fileName {str} -- [description] 파일명 (default: {""})

    Returns:
        {str} -- [description] 파일 절대 경로 
    """
    try:
        abs_file_path = get_abs_file_path(rootPath, fileName)
        if not is_exists(abs_file_path):
            raise UtilityError("Not Exists: {}".format(abs_file_path))

        if not is_file(abs_file_path):
            raise UtilityError("Not File: {}".format(abs_file_path))
            
        return abs_file_path 

    except UtilityError as e:
        Log.error(e.msg)
        return ""

    except:
        _, msg, obj = sys.exc_info()
        msg = "{} ({}::{})".format(msg, obj.tb_lineno, obj.tb_frame.f_globals.get("__file__"))
        Log.error(msg)
        return ""

    finally:
        pass

@gateway
def get_file_path_in_folder(dirName):
    """[summary]
        폴더 내 파일목록을 가져온다. 

    Arguments:
        dirName {[type]} -- [description] 폴더 경로 

    Returns:
        {list} -- [description] 폴더내 파일 목록 
    """
    try:
        fileList = []

        # 폴더내 전체 목록을 가져온다. 
        for root, dirs, files in os.walk(dirName):
            # 파일 목록 중 ".", ".." 를 제외한다. 
            files = [f for f in files if not f[0] == "."]

            # 파일 목록을 생성한다. 
            for fileName in files:
                abs_file_path = get_file_path(rootPath=root, fileName=fileName)
                if abs_file_path:
                    fileList.append(abs_file_path)
            
        return fileList

    except:
        _, msg, obj = sys.exc_info()
        msg = "{} ({}::{})".format(msg, obj.tb_lineno, obj.tb_frame.f_globals.get("__file__"))
        Log.error(msg)
        return []

    finally:
        pass

@gateway
def get_dir_list(dirName):
    try:
        dirList = []
        for name in os.listdir(dirName):
            dirList.append(os.path.join(dirName, name))
        
        return dirList

    except:
        _, msg, obj = sys.exc_info()
        msg = "{} ({}::{})".format(msg, obj.tb_lineno, obj.tb_frame.f_globals.get("__file__"))
        Log.error(msg)
        return []
    
    finally:
        pass

@gateway
def  get_file_list(fileName="", dirName=""):
    """[summary]
        절대 경로를 갖는 목록을 생성한다. 

    Arguments:
        fileName {[str]} -- [description] (optional) 파일명
        dirName {[str]} -- [description] (optional) 폴더명

    Returns:
        {list} -- [description] 파일목록
    """
    try:
        fileList = []

        # args.file 파일 목록을 추가한다. 
        if fileName:
            abs_file_path = get_file_path(fileName=fileName)
            if abs_file_path:
                fileList.append(abs_file_path)
            else:
                raise UtilityError("Not Collect File: {}".format(fileName))

        # args.folder 파일 목록을 추가한다. 
        if dirName:
            abs_file_list = get_file_path_in_folder(dirName)
            if abs_file_list:
                fileList.extend(abs_file_list)
            else:
                raise UtilityError("Not Collect Directory: {}".format(dirName))
            
        return fileList

    except UtilityError as e:
        Log.error(e.msg)
        return []

    except:
        _, msg, obj = sys.exc_info()
        msg = "{} ({}::{})".format(msg, obj.tb_lineno, obj.tb_frame.f_globals.get("__file__"))
        Log.error(msg)
        return []

    finally:
        pass