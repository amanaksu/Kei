# -*- coding:utf-8 -*-
#
# 작성자 : 김승언
# 
# 용도 : Consumer 모듈
# 설명 : 단일 프로세스 모듈
#
# 개발 Log
# 2018.08.06    버전 0.0.5      [개발] 프로토타입 변경
# 2018.08.07    버전 0.0.6      [개발] 멀티프로세스용 Work 클래스 추가 
# 2018.08.13    버전 0.0.7      [수정] 동작 큐잉을 위해 ScanObject 의 uniqID 생성 로직을 이동함.(dispatch._get_metadata())
# 2018.08.21    버전 0.0.8      [개발] FormatObject 구현 

__version__ = "0.0.8"
__author__ = "amanaksu@gmail.com"

# 내장 라이브러리 
import hashlib
import logging
import multiprocessing
import os
import sys
import time
import uuid

# 서드파티 라이브러리 

# 고유 라이브러리 
from Engines import Log
from Engines import monitoring
from Engines import utils

import config

#########################################################################################################
# 분석 큐잉
#########################################################################################################




#########################################################################################################
# 멀티프로세스 동작 단위 클래스
#########################################################################################################
class WorkError(Exception):
    def __init__(self, msg):
        self.msg = msg


class Work:
    def __init__(self, proc_num=config.proc_num, 
                       queue_wait=config.queue_wait, 
                       queue_size=config.queue_size):
        
        if self.__queuing__():
            self.proc_num = proc_num
            self.queue_wait = queue_wait
            self.stop_flag = multiprocessing.Value("i", 0, lock=False)
            self.tasks_queue = multiprocessing.Queue(queue_size)
            self.process = []
            for i in range(self.proc_num):
                p = multiprocessing.Process(target=self.__run__,                                        # 프로세스 함수 
                                            name="Work{}".format(i),                                    # 프로세스 이름 
                                            args=(self.tasks_queue, self.stop_flag, self.queue_wait))   # 프로세스 Parameter
                p.start()
                self.process.append(p)            

    def __del__(self):
        self.stop_all_worker()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def is_full(self):
        return self.tasks_queue.full()

    def is_empty(self):
        return self.tasks_queue.empty()

    def put_nowait(self, *args):
        self.tasks_queue.put_nowait(args)

    def put(self, *args):
        self.tasks_queue.put(args)

    def stop_all_worker(self):
        self.stop_flag.value = 1
        for p in self.process:
            p.join()

    def __queuing__(self):
        """[summary]
            큐잉용 모니터링시 사용할 폴더를 생성한다. 
        
        Returns:
            {bool} -- [desciption] 큐잉용 폴더 생성 여부 
        """
        try:
            if config.queue_monitor:
                for name, dirPath in config.dir_q_monitor.items():
                    dirName = os.path.join(config.temp_path, dirPath)
                    if not utils.makedirectory(dirName):
                        raise WorkError("Failed Create {} for Monitoring.".format(name))

            return True

        except WorkError as e:
            Log.error(e.msg)
            return False

        except:
            _, msg, obj = sys.exc_info()
            msg = "{} ({}::{})".format(msg, obj.tb_lineno, obj.tb_frame.f_globals.get("__file__"))
            Log.error(msg)
            return False

        finally:
            pass

    def __clear__(self):
        """[summary]
            임시 폴더를 정리한다. 

            * clear_temp : 임시 폴더 정리 여부
            * clear_q_monitor : 임시 폴더 내 분석 모니터링용 폴더 정리 여부 
        """
        try:
            if config.clear_temp:
                fileList = utils.get_dir_list(config.temp_path)
                
                for fileName in fileList:
                    if not config.clear_q_monitor:
                        if os.path.basename(fileName) in config.dir_q_monitor.keys():
                            continue

                    if utils.is_file(fileName):
                        utils.deletefile(fileName)
                    else:
                        utils.deletedirectory(fileName)

        except:
            _, msg, obj = sys.exc_info()
            msg = "{} ({}::{})".format(msg, obj.tb_lineno, obj.tb_frame.f_globals.get("__file__"))
            Log.error(msg)

        finally:
            pass

    def __run__(self, tasks_queue, stop_flag, queue_wait):
        """[summary]
            사용자가 작성할 run() 함수의 Wrapper

        Arguments:
            tasks_queue {instnace} -- [description] 작업 큐
            stop_flag {instance} -- [description] 프로세스 종료여부 Flag
            queue_wait {int} -- [description] 다음 Queue 확인까지 대기 시간
        """
        try:
            # 전처리 
            # Log 초기화 
            Log.init(log_name="work",
                     log_level=config.log_level, 
                     log_path=config.log_path, 
                     log_cmd=config.log_cmd)
            
            # 처리 
            self.run(tasks_queue, stop_flag, queue_wait)

            # 후처리 

        except:
            _, msg, obj = sys.exc_info()
            msg = "{} ({}::{})".format(msg, obj.tb_lineno, obj.tb_frame.f_globals.get("__file__"))
            Log.error(msg)

        finally:
            pass

    def run(self, tasks_queue, stop_flag, queue_wait):
        """[summary]
            사용자가 작성해야 할 부분

        Arguments:
            tasks_queue {[instnace]]} -- [description] 작업 큐
            stop_flag {[instance]} -- [description] 프로세스 종료여부 Flag
            queue_wait {[int]} -- [description] 다음 Queue 확인까지 대기 시간
        """
        pass

#########################################################################################################
# 분석 엔진 부모 클래스 
# - 프로세스 생성을 제외한 동작은 분석 엔진 부모 프로세스 같음
#########################################################################################################
class EngineObject:
    def __init__(self, version, author, moduleName):
        self.__version__ = version
        self.__author__ = author
        self.__engine__ = moduleName
        self.__moduleName__ = self.__class__.__name__

    def get_engine_info(self):
        """[summary]
            엔진 정보를 반환한다. 

            * version   : 엔진 버전
            * author    : 엔진 개발자
            * module    : 엔진 이름
        """
        try:
            return {
                "version"   :   self.__version__,
                "author"    :   self.__author__,
                "module"    :   self.__engine__
            }

        except:
            _, msg, obj = sys.exc_info()
            msg = "{} ({}::{})".format(msg, obj.tb_lineno, obj.tb_frame.f_globals.get("__file__"))
            Log.error(msg)
            return {}

        finally:
            pass

    def update(self, err, err_msg):        
        self.result.updateResultObject(err, err_msg)

    def __format__(self, data, dict_value):
        # 데이터 타입
        # b	    signed char	        integer	            1	(1),(3)
        # B	    unsigned char	    integer	            1	(3)
        # H	    unsigned short	    integer	            2	(3)
        # i	    int	                integer	            4	(3)
        # I	    unsigned int	    integer	            4	(3)
        # L	    unsigned long	    integer	            4	(3)
        # Q	    unsigned long long	integer	            8	(2), (3)
        # s	    char[]	            bytes	 	 
        try:
            endian = "<" if dict_value.get("endian") is "little" else ">"
            offset = dict_value.get("offset", None)
            size = dict_value.get("size", None)
            data_type = dict_value.get("type", None)

            if data_type in ["H"]:  
                unit = int(size / 2)
            elif data_type in ["i", "I", "L"]:
                unit = int(size / 4)
            elif data_type in ["Q"]:
                unit = int(size / 8)
            else:
                unit = size

            return utils.readData(endian, data, data_type, unit, offset, size)

        except:
            _, msg, obj = sys.exc_info()
            msg = "{} ({}::{})".format(msg, obj.tb_lineno, obj.tb_frame.f_globals.get("__file__"))
            Log.error(msg)
            return None

        finally:
            pass

    def __run__(self, scanResult, scanObject):
        """[summary]
            분석 엔진 run() 의 Wrapper

        Arguments:
            scanResult {instance} -- [description] ScanResult 인스턴스
            scanObject {instance} -- [description] ScanObject 인스턴스
        """
        error = False
        err_msg = ""
        try:
            # Log 초기화 
            Log.init(log_name=self.__engine__.split(".")[-1],
                     log_level=config.log_level, 
                     log_path=config.log_path, 
                     log_cmd=config.log_cmd)

            # Log.info("{} : {}".format(self.__engine__, scanObject.get_file_name()))
            Log.info(self.__engine__)

            # 전처리 
            # 호출 모듈명을 저장한다. 
            scanObject.updateScanModule(self.__engine__)

            # 상태를 변경한다. 
            # monitoring.__analyzing__(scanObject)

            # 분석
            self.run(scanResult, scanObject)

            # 후처리            

        except:
            # 에러로그를 작성한다. 
            _, msg, obj = sys.exc_info()
            msg = "{} ({}::{})".format(msg, obj.tb_lineno, obj.tb_frame.f_globals.get("__file__"))
            Log.error(msg)

            # 에러 상태를 업데이트한다. 
            error = True
            err_msg = msg

        finally:
            scanObject.updateResult(error, err_msg)

    def run(self, fileName):
        """[summary]
            상속받은 클래스에서 구현할 부분

        Arguments:
            fileName {str} -- [description] 분석 대상 파일명
        """
        pass

#########################################################################################################
# 분석 엔진 부모 프로세스
#########################################################################################################
class EngineProcess:
    def __init__(self, version, author, moduleName):
        self.__version__ = version
        self.__author__ = author
        self.__engine__ = moduleName
        self.__moduleName__ = self.__class__.__name__   

        self.task_queue = multiprocessing.JoinableQueue()
        manager = multiprocessing.Manager()
        self.result_queue = manager.Queue()

        self.__process__ = multiprocessing.Process(target=self.__run__, args=(self.task_queue, self.result_queue,))

    def get_engine_info(self):
        """[summary]
            엔진 정보를 반환한다. 

            * version   : 엔진 버전
            * author    : 엔진 개발자
            * module    : 엔진 이름
        """
        try:
            return {
                "version"   :   self.__version__,
                "author"    :   self.__author__,
                "module"    :   self.__engine__
            }

        except:
            _, msg, obj = sys.exc_info()
            msg = "{} ({}::{})".format(msg, obj.tb_lineno, obj.tb_frame.f_globals.get("__file__"))
            Log.error(msg)
            return {}

        finally:
            pass

    def start(self):
        self.__process__.start()

    def close(self):
        self.__process__.terminate()

    def join(self):
        self.__process__.join()

    def put_task(self, task):
        self.task_queue.put(task)

    def get_result(self):
        serialized_data = utils.decompress(self.result_queue.get())
        # return serialized_data
        return type("ScanObject", (object,), serialized_data)

    def __run__(self, task_queue, result_queue):
        error = False
        err_msg = ""
        try:
            # Log 초기화 
            Log.init(log_name=self.__engine__.split(".")[1],
                     log_level=config.log_level, 
                     log_path=config.log_path, 
                     log_cmd=config.log_cmd)

            # 전처리 
            # Job을 가져온다. 
            scanResult, scanObject = task_queue.get()
            
            # 호출 모듈명을 저장한다. 
            scanObject.updateScanModule(self.__engine__)

            # 상태를 변경한다. 
            monitoring.__analyzing__(scanObject)

            # 분석
            self.run(scanResult, scanObject)

        except:
            # 에러로그를 작성한다. 
            _, msg, obj = sys.exc_info()
            msg = "{} ({}::{})".format(msg, obj.tb_lineno, obj.tb_frame.f_globals.get("__file__"))
            Log.error(msg)
            
            # 에러 상태를 업데이트한다. 
            error = True
            err_msg = msg
            
        finally:
            # 후처리
            # 분석 결과를 저장한다.             
            scanObject.updateResult(error, err_msg)

            # 분석 결과를 반환한다. 
            dict_data = scanObject.to_dict()
            serialized_data = utils.convert_dict2serialize(dict_data)
            result_queue.put(utils.compress(serialized_data))

    def run(self, scanResult, scanObject):
        """[summary]
            상속받은 클래스에서 구현할 부분

        Arguments:
            scanObject {instance} -- [description] ScanObject 인스턴스 
        """
        pass


#########################################################################################################
# 파일/분석/결과 정보 클래스 
#########################################################################################################
class FileObject(object):
    def __init__(self, fileName):
        # TODO : 인코딩
        # - 샘플 : 120604 전북도당 통합진보당 규약(6월 2주차).hwp_
        # - 에러 : Could not open file 
        self.__ori_name__ = utils.convert_ToUTF8(fileName)
        self.__name__ = self.__ori_name__
        self.__size__ = self.__get_size__()
        self.__sha256__ = self.__get_sha256__()

    def __get_size__(self):
        return os.path.getsize(self.__name__)

    def __binary__(self):
        try:
            with open(self.__name__, "rb") as fp:
                data = fp.read()

            return data

        except:
            _, msg, obj = sys.exc_info()
            msg = "{} ({}::{})".format(msg, obj.tb_lineno, obj.tb_frame.f_globals.get("__file__"))
            raise SystemError(msg)

        finally:
            pass

    def __get_sha256__(self):
        sha256 = hashlib.sha256()
        sha256.update(self.__binary__())
        return sha256.hexdigest().upper()

    def update_file_name(self, new_fileName):
        self.__name__ = utils.convert_ToUTF8(new_fileName)

    def get_ori_file_name(self):
        return self.__ori_name__

    def get_file_name(self):
        return self.__name__

    def get_file_size(self):
        return self.__size__

    def get_file_data(self):
        return self.__binary__()

    def get_file_sha256(self):
        return self.__sha256__

class ResultObject(object):
    def __init__(self):
        self.error = False
        self.err_msg = ""

    def updateResultObject(self, err, err_msg):
        # Error 상태 확인
        if self.error:
            # 기존 Error 상태가 True 인 경우
            # 별도 처리를 하지 않음
            pass

        else:
            # 기존 Error 상태가 False 인 경우
            if not isinstance(err, bool):
                raise TypeError("error must be boolean type. (input type:{})".format(str(type(err))))

            if not isinstance(err_msg, str):
                raise TypeError("err_msg must be str type. (input type:{})".format(str(type(err_msg))))

            self.error = err
            self.err_msg = err_msg

    def get(self):
        dict_data = self.__dict__
        for key, value in self.__dict__.items():
            if hasattr(value, "get"):
                dict_data[key] = getattr(value, "get")()
                
        return dict_data




class FormatObjectError:
    def __init__(self, msg):
        self.msg = msg

class FormatObject:
    def __init__(self, meta):
        self.author = ""
        self.last_updated = ""
        self.description = ""
        self.product = ""
        self.scan_module = ""
        self.file_type = ""
        self.name = ""
        
        self.struct = {}

        self.__parse__(meta)

    def __parse__(self, meta):
        for key, value in meta.items():
            setattr(self, key, value)

    def update(self, key, value):
        if getattr(self, key):
            setattr(self, key, value)
        else:
            raise AttributeError("{} is not exists in FormatObject.".format(key))

    def updateStruct(self, key, value):
        if isinstance(value, dict):
            tmp_dict = self.struct.get(key, {})
            for sub_key, sub_value in value.items():
                tmp_dict.update({sub_key : sub_value})
            self.struct[key] = tmp_dict
        else:
            self.struct.update({key : value})

    def get(self, dict_data={}):
        if not dict_data:
            dict_data = self.__dict__
        
        result_data = utils.deepcopy(dict_data)
        for key, value in dict_data.items():
            if isinstance(value, dict):
                ret_value = self.get(dict_data=value)
                result_data[key] = ret_value

            elif hasattr(value, "get"):
                ret_value = getattr(value, "get")()
                if isinstance(value, dict):
                    ret_value = self.get(dict_data=value)

                result_data[key] = ret_value

        return result_data
    
class ScanObject(FileObject):
    def __init__(self, fileName="", uniqID="", depth=0, parentID="", parentName="", fformat=None, internal_path=""):
        # 파일 기본 정보를 생성한다. 
        FileObject.__init__(self, fileName)

        self.uniqID = uniqID if uniqID else str(uuid.uuid4())   # 식별 고유값
        self.depth = depth                                      # Recursive 확인
        self.parentID = parentID                                # Parent 고유값
        self.parentName = parentName                            # Parent 파일명
        self.fformat = fformat                                  # 포멧 정보, FormatObject 인스턴스
        self.internal_path = internal_path                      # 내부 세부 경로

        self.scan_module = []                                   # 처리한 엔진명
        self.children = {}                                      # 임베딩 파일 정보 

        self.result = ResultObject()                            # 처리 결과, 분석 엔진에서만 접근 (error, err_msg)

    def get_fformat(self):
        """[summary]
            파일 포멧 정보를 반환한다. 
        
        Returns:
            {dict} -- [description] 파일 포멧 정보
        """
        return self.fformat

    def updatefformat(self, fformat):
        """[summary]
            파일 포멧 정보를 저장한다. 

            * 저장형식 : instance

        Arguments:
            fformat {instance} -- [description] 파일 포멧 정보
        """
        if isinstance(fformat, FormatObject):
            self.fformat = fformat
        else:
            raise TypeError("fformat's member type must be instance by FormatObject. (type: {})".format(str(type(fformat))))            

    def get_scan_module(self):
        """[summary]
            호출된 모듈 목록을 반환한다.

        Returns:
            {list} -- [description] 호출된 모듈 목록
        """
        return self.scan_module

    def updateScanModule(self, scanModule):
        """[summary]
            분석 엔진 이름을 순서대로 저장한다. 

        Arguments:
            scanModule {str} -- [description] 분석 엔진명
        """
        if isinstance(scanModule, str):
            self.scan_module.append(scanModule)
        else:
            raise TypeError("scan module name's type must be string or utf-8. (type: {})".format(str(type(scanModule))))

    def get_children(self):
        """[summary]
            저장된 임베딩 파일 목록을 반환한다. 

        Returns:
            {dict} -- [description] 임베딩 파일 목록
        """
        return self.children

    def get_child_name_by_id(self, uniqID):
        """[summary]
            저장되어 있는 임베딩 파일 목록 중 uniqID 에 해당하는 파일명을 반환한다. 

        Arguments:
            uniqID {str} -- [description] 임베딩 파일의 고유값
        
        Returns:
            {str} -- [description] uniqID 의 임베딩 파일명
        """
        return self.get_children().get(uniqID, {}).get("child_name", "")

    def get_child_internal_path_by_id(self, uniqID):
        """[summary]
            저장되어 있는 임베딩 파일 목록 중 uniqID 에 해당하는 파일의 내부 경로를 반환한다. 

        Arguments:
            uniqID {str} -- [description] 임베딩 파일의 고유값
        
        Returns:
            {list} -- [description] uniqID 의 임베딩 파일 내부 경로 목록
        """
        return self.get_children().get(uniqID, {}).get("internal_path", [])     

    def get_children_by_priority(self, children, level):
        """[summary]
            Children 에서 특정 우선 순위를 갖는 Child를 반환한다. 
        Arguments:
            children {dict} -- [description] 전체 Children 목록
            level {int} -- [description] 우선순위 레벨
        """
        result = {}
        for uniqID, child in children.items():
            if child.get("priority", 0) == level:
                result.update({uniqID : child})
        return result

    def updateChildren(self, fileName, internal_path=[], priority=config.default_priority):
        """[summary]
            임베딩된 데이터가 있을 경우 저장되는 데이터
            - uniqID
            - 추출된 파일의 파일명
            - 내부 구조
            - 분석 우선순위
            
            * 저장형식 : dict

        Arguments:
            fileName {str} -- [description] 저장할 파일명
        
        Keyword Arguments:
            internal_path {list} -- [description] 내부 경로, depth에 따라 split해서 저장됨 (default: {[]})
        """
        fileName = utils.convert_ToUTF8(fileName)
        if not isinstance(fileName, str):
            raise TypeError("child's fileName type must be string or utf-8. (type: {})".format(str(type(fileName))))
        
        if not isinstance(internal_path, list):
            raise TypeError("child's internal path type must be list. (type: {})".format(str(type(internal_path))))

        new_internal_path = []
        for _path in internal_path:
            new_path = utils.convert_ToUTF8(_path)
            new_internal_path.append(new_path)

        self.children.update({str(uuid.uuid4()) : {
            "child_name" : fileName,
            "internal_path" : new_internal_path,
            "priority" : priority
        }})

    def get_structure(self):
        return self.fformat.struct

    def updateStructure(self, key, value):
        self.fformat.updateStruct(key, value)

    def get_result(self):
        """[summary]
            분석 결과를 반환한다. 

        Returns:
            {dict} -- [description] 분석 결과
        """
        return self.result  

    def updateResult(self, err, err_msg):
        """[summary]
            분석 결과 에러정보를 업데이트 한다. 

        Arguments:
            err {bool} -- [description] 에러 여부 
            err_msg {str} -- [description] 에러 정보
        """
        if not isinstance(self.result, ResultObject):
            raise ValueError
        self.result.updateResultObject(err, err_msg)

    def get_uid(self):
        """[summary]
            파일 고유값을 반환한다. 

        Returns:
            {str} -- [description] 파일 고유값
        """
        return self.uniqID

    def get_parentID(self):
        """[summary]
            부모 파일의 uniqID 를 반환한다. 
        
        Returns:
            {str} -- [description] 부모 파일의 uniqID
        """
        return self.parentID

    def get_internal_path(self):
        """[summary]
            내부 경로를 반환한다. 

        Returns:
            {list} -- [description] 내부 경로
        """
        return self.internal_path

    def to_dict(self):
        result = self.__dict__
        for key, value in self.__dict__.items():
            if isinstance(value, (FormatObject, ResultObject)):
                result[key] = value.get()
                
        return result

class ScanResult:
    def __init__(self, rootUID=""):
        self.rootUID = rootUID      # self.files 에 첫번째 저장되는 파일의 uniqID로 설정한다. 
        self.files = {}             # {uniqID : <scanObject> }
        self.startTime = 0          # ScanResult 초기화 후 설정된다. 
        self.endTime = 0            # 분석 완료 후 설정된다. 
        self.result = {             # 분석 완료에 대한 로그를 저장한다. 
            "error"     :   False,
            "err_msg"   :  ""
        }            

    def updateRootUID(self, rootUID):
        """[summary]
            rootUID 값을 수정한다. 

        Arguments:
            rootUID {[type]} -- [description] 파일을 식별하기 위한 고유값
        """
        self.rootUID = rootUID

    def updateFiles(self, scanObject):
        """[summary]
            분석된 파일 정보를 저장한다. 

            * 저장 형식 : dict  {uniqID(str) : scanObject(instance)}

        Arguments:
            scanObject {[type]} -- [description] 파일 분석 정보 
        """
        if isinstance(scanObject, ScanObject):
            self.files.update({scanObject.get_uid() : scanObject})
        else:
            raise TypeError("input type is not collect. (type: {})".format(str(type(scanObject))))
            
    def updateStartTime(self, startTime):
        """[summary]
            분석 시작 시간을 저장한다. 

        Arguments:
            startTime {datetime} -- [description] 분석 시작 시간
        """
        self.startTime = startTime
    
    def updateEndTime(self, endTime):
        """[summary]
            분석 종료 시간을 저장한다. 
        Arguments:
            endTime {datetime} -- [description] 분석 종료 시간 
        """
        self.endTime = endTime

    def updateResult(self, error, uniqID, err_msg):
        """[summary]
            분석 결과 로그를 저장한다. 

        Arguments:
            error {bool} -- [description] 분석 결과 에러 여부 
            uniqID {str} -- [description] 에러가 발생한 ScanObject의 uniqID
            err_msg {str} -- [description] 에러한 발생한 로그 정보
        """
        old_error = self.result.get("error", False)
        if old_error is True:
            error = True

        self.result = {"error" : error, uniqID : err_msg}

    def get_rootUID(self):
        """[summary]
            ScanResult 에 저장된 RootID를 반환한다. 
        
        Returns:
            {str} -- [description] Root 파일의 uniqID
        """
        return self.rootUID

    def get_root_type(self):
        rootObject = self.files.get(self.rootUID, None)
        if rootObject:
            return rootObject.get_fformat()
        else:
            return None

    def get_files(self):
        """[summary]
            파일 목록을 반환한다. 

        Returns:
            {list} -- [description] 파일 목록 (임베딩 파일 포함)
        """
        return self.files