# -*- coding:utf-8 -*-
#
# 작성자 : 김승언
# 
# 용도 : Dispatch 모듈
# 설명 : 분석 모듈 
#
# 개발 Log
# 2018.08.06    버전 0.0.5      [개발] 프로토타입 변경
# 2018.08.14    버전 0.0.6      [개발] 분석 큐 모니터링 로직 추가 
# 2018.08.15    버전 0.0.7      [수정] _get_fformat() : Root 파일 내 임베딩 파일의 fformat 결과 반환값 변경
#

__version__ = "0.0.7"
__author__ = "amanaksu@gmail.com"

# 내장 라이브러리 
import os
import sys

# 서드파티 라이브러리 

# 고유 라이브러리 
from Engines import Log, gateway
from Engines import monitoring
from Engines import skeleton
from Engines import utils
from Engines.filter import __is_filtered__

import config


class DispatchPassThru(Exception):
    pass

class DispatchErrorPassThru(Exception):
    pass

class DispatchError(Exception):
    def __init__(self, msg):
        self.msg = msg

class DispatchDebug(Exception):
    def __init__(self, msg):
        self.msg = msg

class DispatchModuleError(Exception):
    def __init__(self, msg):
        self.msg = msg


@gateway
def _get_metadata(job, uniqID="", depth=0, parentID="", parentName="", internal_path=[]):
    """[summary]
        ScanObject 인스턴스를 생성한다. 
        
        동작 큐잉를 위해 uniqID 생성 로직을 skeleton.ScanObject 에서 _get_metadata()로 옮김
        
    Arguments:
        job {str}} -- [description] 분석 대상 파일명
        uniqID {str} -- [description] 분석 대상 고유값 (default: {""})
        depth {int} -- [description] 재귀처리시 분석 depth (default: {0})
        parentID {str} -- [description] 분석 대상 파일의 Parent 고유값 (default: {""})
        parentName {str} -- [description] 분석 대상 파일명 (default: {""})
        internal_path {list} -- [description] 내부 경로 (default: {[]})
    
    Returns:
        {instance} -- [description] ScanObject 인스턴스 
    """
    try:
        return skeleton.ScanObject(fileName=job, 
                                   uniqID=uniqID,
                                   depth=depth, 
                                   parentID=parentID, 
                                   parentName=parentName,
                                   internal_path=internal_path)

    except:
        _, msg, obj = sys.exc_info()
        msg = "{} ({}::{})".format(msg, obj.tb_lineno, obj.tb_frame.f_globals.get("__file__"))
        Log.error(msg)
        return None

    finally:
        pass

@gateway
def _rule_match(scanResult, job, matchRules):
    try:
        matchRules = matchRules[0]
        # Log.debug("Type: {}".format(matchRules))

        if hasattr(matchRules, "meta") and hasattr(matchRules, "rule"):
            meta = matchRules.meta
            meta.update({"name" : matchRules.rule})
            return skeleton.FormatObject(meta)
        else:
            # Yara 룰 내 정보가 부족한 것으로 판단한다. 
            raise DispatchError("the rules are wrong. (detect: {})".format(matchRules))

    except DispatchError as e:
        Log.error(e.msg)
        return None

    except:
        _, msg, obj = sys.exc_info()
        msg = "{} ({}::{})".format(msg, obj.tb_lineno, obj.tb_frame.f_globals.get("__file__"))
        Log.error(msg)
        return {}

    finally:
        pass

@gateway
def _rule_mismatch(scanResult, job, matchRules):
    try:
        # Root 파일 타입을 상속받는 경우
        # 임베딩 데이터의 경우 일부 상속받음
        if config.inherit_root:
            root_type = scanResult.get_root_type()

            # Root 파일 타입이 있는 데이터의 경우 
            if root_type:
                # 상속시 deepcopy를 통해 Root의 struct를 함께 상속받는 경우
                # Embedded 경우 다른 Embedded 분석 정보를 참조하기 위해 ScanObject.fformat.struct 에 접근해서 얻을 수 있음
                # return root_type
                
                # 상속시 Root의 struct는 상속받지 않는 경우 
                # deepcopy를 통해 새로운 인스턴스를 생성하고 그중 struct 데이터를 초기화함
                # Embedded 경우 다른 Embedded 분석 정보를 참조하기 위해 ScanResult 에 접근해서 얻을 수 있음
                copy_root_type = utils.deepcopy(root_type)
                copy_root_type.update("struct", {})
                return copy_root_type
                
            else:
                # Root 파일 타입이 없는 최초 데이터의 경우 
                # 대상 파일이 아님.
                raise DispatchDebug("this file is not target.")   

        # Root 파일 타입을 상속받지 않는 경우 
        else:
            # Yara 룰로 매칭되지 않음.
            # 대상 파일이 아님.
            raise DispatchDebug("this file is not target.") 

    except DispatchDebug as e:
        Log.debug(e.msg)
        return None

    except:
        _, msg, obj = sys.exc_info()
        msg = "{} ({}::{})".format(msg, obj.tb_lineno, obj.tb_frame.f_globals.get("__file__"))
        Log.error(msg)
        return {}

    finally:
        pass

@gateway
def _rule_overmatch(scanResult, job, matchRules):
    try:
        # Yara 룰이 중복된 것으로 판단한다. 
        tmp = [_match.rule for _match in matchRules]
        raise DispatchError("the rules are wrong. (detect: {})".format(", ".join(tmp)))

    except DispatchError as e:
        Log.error(e.msg)
        return None

    except:
        _, msg, obj = sys.exc_info()
        msg = "{} ({}::{})".format(msg, obj.tb_lineno, obj.tb_frame.f_globals.get("__file__"))
        Log.error(msg)
        return {}

    finally:
        pass

@gateway
def _get_fformat(scanResult, job):
    """[summary]
        Yara 룰을 바탕으로 파일 포멧 정보를 반환한다. 

        * 반환값 : instance

    Arguments:
        scanResult {instance} -- [description] ScanResult 인스턴스
        job {str} -- [description] 분석 대상 

    Returns:
        {instance} -- [description] FormatObject 클래스 인스턴스
    """
    try:
        # Yara Rule 기반 파일 포멧을 탐지한다. 
        matchRules = utils.yara_on_demand(config.format_rules, job)

        # 탐지된 파일 포멧이 없는 경우
        if len(matchRules) == 0:
            return _rule_mismatch(scanResult, job, matchRules)
           
        # 탐지된 파일 포멧이 1개인 경우 
        elif len(matchRules) == 1:
            return _rule_match(scanResult, job, matchRules)
           
        # 탐지된 파일 포멧이 2개 이상인 경우 
        else:
            return _rule_overmatch(scanResult, job, matchRules)
       
    except:
        _, msg, obj = sys.exc_info()
        msg = "{} ({}::{})".format(msg, obj.tb_lineno, obj.tb_frame.f_globals.get("__file__"))
        Log.error(msg)
        return {}

    finally:
        pass

@gateway
def _get_engine(fformat):
    """[summary]
        분석 대상의 종류에 따른 엔진을 호출한다. 
        분석 완료 정보는 ScanObject에 저장되지만 명시적 Return은 수행하지 않는다. 

        * 엔진 처리 우선순위 : scan_module -> file_type -> name
            단, 설정 파일에 있는 엔진 항목만 적용받는다. 

        * 엔진은 <엔진명>.py 로 정의한다. 
    
    Arguments:
        fformat {dict} -- [description] 포멧 정보 
    """
    try:
        # 우선 순위에 따라 엔진명을 가져온다. 
        for name in config.priority_eng:
            mod_name = getattr(fformat, name)
            
            Log.debug("{}:{}".format(name, mod_name))

            # 해당 엔진명을 키로하는 엔진 경로가 없는 경우 
            if not mod_name:
                continue

            # 엔진 경로내 <엔진명>.py 가 없거나 로드 실패한 경우
            # 엔진 경로는 Engines. 이하 하위 경로만 해당됨.
            mod = utils.load_module(mod_name)
            if not mod:
                continue

            # 엔진내 정의된 클래스명을 가져온다. 
            clsName = getattr(mod, config.engine_class) 
            # 있는 경우 
            if clsName:
                return clsName
            
        return None

    except:
        _, msg, obj = sys.exc_info()
        msg = "{} ({}::{})".format(msg, obj.tb_lineno, obj.tb_frame.f_globals.get("__file__"))
        Log.error(msg)
        return None

    finally:
        pass

@gateway
def _run_module(scanResult, scanObject):
    """[summary]
        엔진을 호출해 분석한다. 

    Arguments:
        scanResult {instance} -- [description] ScanResult 클래스 인스턴스
                                    (ScanObject 대상을 분석할 때 사전 분석 대상의 정보를 참조해야 하는 경우를 위함)
        scanObject {instance} -- [description] ScanObject 클래스 인스턴스 
    """
    process = None
    try:
        # 엔진을 로드한 후 분석 클래스명을 가져온다. 
        fformat = scanObject.get_fformat()
        clsName = _get_engine(fformat)
        if not clsName:
            raise DispatchError("this file is not target or failed to load module.")

        # 분석 프로세스를 생성한다. 
        process = clsName()
        # 분석 프로세스를 실행한다. 
        process.start()
        # 분석 대상을 분석 큐에 넣는다. 
        process.put_task((scanResult, scanObject))
        # 분석이 완료될 때까지 기다린다. 
        process.join()
        # 분석이 완료되면 분석 결과를 반환한다. 

        return True, process.get_result()
         
    except DispatchError as e:
        # 모듈 에러
        # 에러로그를 남긴다. 
        Log.error(e.msg)
        return False, scanObject

    except:
        # 모듈 에러
        # 에러로그를 남긴다. 
        _, msg, obj = sys.exc_info()
        msg = "{} ({}::{})".format(msg, obj.tb_lineno, obj.tb_frame.f_globals.get("__file__"))
        Log.error(msg)
        return False, scanObject

    finally:
        if process:
            process.close()

@gateway
def _recursive(scanResult, scanObject, depth):
    """[summary]
        Dispatch 함수를 재귀호출한다. 

    Arguments:
        scanResult {instance} -- [description] ScanResult 인스턴스
        scanObject {instance} -- [description] ScanObject 인스턴스
        depth {int} -- [description] 재귀호출을 조절하기 위한 Depth
    """
    try:
        # 임베딩 파일이 있는 경우 
        # 임베딩 파일 목록을 가져온다. 
        children = scanObject.get_children()
        # 우선순위 레벨을 가져온다. 
        # priority_level = [10000, 1000, 100, 0]
        priority_level = sorted(config.PRIORITY_LEVEL.values())[::-1]

        # 우선순위별로 처리한다. 
        for level in priority_level:
            # 우선순위에 따라 Children 목록을 가져온다. 
            new_children = scanObject.get_children_by_priority(children, level)

            # 순서대로 Dispatch를 호출한다. 
            for uniqID, child in new_children.items():
                child_name = child.get("child_name", "")
                parentID = scanObject.get_uid()
                parentName = scanObject.get_ori_file_name()
                internal_path = child.get("internal_path", [])

                Dispatch(scanResult, 
                            child_name,
                            uniqID=uniqID,
                            depth = depth + 1,
                            parentID=parentID,
                            parentName=parentName,
                            internal_path=internal_path)

    except:
        # 에러로그를 남긴다. 
        _, msg, obj = sys.exc_info()
        msg = "{} ({}::{})".format(msg, obj.tb_lineno, obj.tb_frame.f_globals.get("__file__"))
        Log.error(msg)

    finally:
        pass

@gateway
def Dispatch(scanResult, job, uniqID="", depth=0, parentID="", parentName="", internal_path=[]):
    """[summary]
        job을 처리한다. 

    Arguments:
        scanResult {instance} -- [description] 결과 저장 클래스 인스턴스
        job {str} -- [description] 분석 대상 파일명
    
    Keyword Arguments:
        uniqID {str} -- [description] 분석 대상 파일 고유값 (default: {""})
        depth {int} -- [description] 분석 Depth (default: {0})
        parentID {str} -- [description] 분석 대상 파일의 부모 파일 고유값 (default: {""})
        parentName {str} -- [description] 분석 대상 파일의 부모 파일명 (default: {""})
        internal_path {list} -- [description] 분석 대상 파일의 내부 경로 (default: {[]})
    """
    scanObject = None
    try:
        # (Recursive 상) 이전 Dispatch 처리과정에서 예외가 발생한 경우
        if scanResult.result.get("error"):
            # Dispatch() 를 종료한다. 
            raise DispatchErrorPassThru

        # 분석 Depth를 확인한다. 
        elif depth > config.depth:
            # 초과한 경우
            # 로그 작성 후 종료한다. 
            Log.debug("exceeded analytical depth.")
        else:
            # 미만인 경우 
            Log.info("Job: {}".format(job))

            # 전처리를 수행한다. 
            # - ScanObject를 생성한다. 
            scanObject = _get_metadata(job, uniqID, depth, parentID, parentName, internal_path)
            if not scanObject:
                raise DispatchError("Failed in the allocation of ScanObject.")

            # 상태를 변경한다. 
            # 상태 : [ORI] -> [WAIT]
            monitoring.__waiting__(scanObject)

            # - 포멧을 확인한다. 
            fformat = _get_fformat(scanResult, scanObject.get_file_name())
            if not fformat:
                # 분석 대상이 아님.
                raise DispatchPassThru

            if not (fformat.scan_module or fformat.file_type or fformat.name):
                raise DispatchError("engine is not set. check yara rules.")

            scanObject.updatefformat(fformat)

            # 필터링 한다. 
            # - True : 필터링 대상
            # - False : 분석 대상 
            if __is_filtered__(scanObject):
                raise DispatchPassThru


            # 분석을 수행한다. 
            # 상태 : [WAIT] -> [ANLZ]]
            bRet, scanObject = _run_module(scanResult, scanObject)
            if not bRet:
                raise DispatchError("Failed _run_module().")

            # TEST
            print(scanObject)                

            # 후처리를 수행한다.
            # - 분석 결과를 ScanResult 에 저장한다. 
            scanResult.updateFiles(scanObject)

            # 최초 분석시 
            if not scanResult.get_rootUID():
                # rootUID를 업데이트한다. 
                scanResult.updateRootUID(scanObject.get_uid())

            # - 분석 중 오류가 발생한 경우 에러로그를 생성하고 추가 분석을 종료한다. 
            if scanObject.result.error:
                raise DispatchError("No further analysis is made.")

            # 분석 성공한 파일
            # 처리 대상을 분석 완료 폴더로 이동시키고 파일명을 예외 폴더 내 파일 경로로 변경한다. 
            # 상태 : [ANLZ] -> [CMPT]
            monitoring.__complete__(scanObject)

            # Recursive 처리여부를 확인한다. 
            if config.recursive:
                # Recursive 처리시
                _recursive(scanResult, scanObject, depth)
            
    except DispatchErrorPassThru:
        # 이전 Recursived Dispatch에서 예외처리된 경우
        pass

    except DispatchPassThru:
        # 필터에 의해 예외된 파일
        # 처리 대상을 예외 폴더로 이동시키고 파일명을 예외 폴더 내 파일 경로로 변경한다. 
        # 상태 : [ANLZ] -> [EXPT]
        monitoring.__except__(scanObject)

    except DispatchModuleError as e:
        # 분석 실패 파일
        # 에러로그를 남긴다. 
        Log.error(e.msg)

        # ScanResult 에 에러로그를 업데이트한다. 
        uniqID = scanObject.get_uid()
        result = scanObject.get_result()
        err_msg = result.get("err_msg", "")
        scanResult.updateResult(True, uniqID, err_msg)

        # 처리 대상을 에러 폴더로 이동시키고 파일명을 에러 폴더 내 파일 경로로 변경한다. 
        # 상태 : [ANLZ] -> [ERR]
        monitoring.__error__(scanObject)

    except DispatchError as e:
        # 모듈 에러
        # 에러로그를 남긴다. 
        Log.error(e.msg)

        # 외부 요인에 의한 분석 실패 
        # 처리 대상을 에러 폴더로 이동시키고 파일명을 에러 폴더 내 파일 경로로 변경한다. 
        # 상태 : [ANLZ] -> [ERR]
        monitoring.__error__(scanObject)

    except:
        # 알수없는 모듈 에러 
        # 에러로그를 남긴다. 
        _, msg, obj = sys.exc_info()
        msg = "{} ({}::{})".format(msg, obj.tb_lineno, obj.tb_frame.f_globals.get("__file__"))
        Log.error(msg)

        # 외부 요인에 의한 분석 실패 
        # 처리 대상을 에러 폴더로 이동시키고 파일명을 에러 폴더 내 파일 경로로 변경한다. 
        # 상태 : [ANLZ] -> [ERR]
        monitoring.__error__(scanObject)

    finally:
        pass