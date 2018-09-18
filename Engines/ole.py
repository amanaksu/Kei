# -*- coding:utf-8 -*-
#
# 작성자 : 김승언
# 
# 용도 : OLE 모듈
# 설명 : OLE 파일 포맷 분석 
#
# 개발 Log
# 2018.08.08    버전 0.0.1      [개발] 프로토타입 변경
# 2018.08.16    버전 0.0.2      [수정] 리팩토링
# 2018.08.16    버전 0.0.3      [추가] Stream 디렉토리 정보 
# 2018.08.21    버전 0.0.4      [추가] Child or Embedded 처리 방식 변경 (Pre-Processing -> Dispatch)

__version__ = "0.0.4"
__author__ = "amanaksu@gmail.com"

# 내장 라이브러리 
import os
import sys

# 서드파티 라이브러리 

# 고유 라이브러리 
from Engines import Log, gateway
from Engines import skeleton
from Engines import utils

from Engines.CompoundFileBinaryFormat import kernel
from Engines.CompoundFileBinaryFormat import oledirectory

import config



class KeiEngineError(Exception):
    def __init__(self, msg):
        self.msg = msg


class KeiEngine(skeleton.EngineProcess):
    def __init__(self):
        skeleton.EngineProcess.__init__(self, __version__, __author__, self.__module__)

    @gateway
    def get_directories_info(self, scanObject):
        """[summary]
            분석 대상 파일에서 Directory 정보를 추출해 Struct 에 저장한다. 

            * 저장 경로 : scanObject.fformat.struct[<directory name>] = {"header" : instance}

        Arguments:
            scanObject {instance} -- [description] ScanObject 인스턴스

        Returns:
            {bool} -- [description] 정상 처리 여부 
        """
        try:
            # 분석 대상 파일명을 가져온다. 
            fileName = scanObject.get_file_name()

            # Directory 목록을 가져온다. 
            directories = kernel.get_directories(fileName)
            for directory in directories:
                # 개별 Directory 정보를 추출한다. 
                instance = oledirectory.OleDirectoryObject(directory)
                
                # 추출된 정보를 업데이트한다. 
                if instance:
                    try:
                        new_name = kernel.convert_entryname([instance.name])
                        # 함수 : scanObject.updateStructure()
                        # 위치 : scanObject.fformat.struct[new_name] = instance
                        scanObject.updateStructure(new_name[0], instance)

                    except AttributeError:
                        # instance는 생성되고 instance.name 이 없는 경우 
                        # - Padding을 위해 채워진 Directory 의 경우 
                        pass

                else:
                    raise KeiEngineError("{} file is not ole structure.".format(os.path.basename(fileName)))

            return True

        except KeiEngineError as e:
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
    def get_streams(self, scanObject):
        """[summary]
            분석 대상 파일에서 Stream을 추출하고 이를 <temp_path>\\<"Embedded"> 에 저장한다. 

            * 반환 결과
                [
                    {
                        "fileName" : "",
                        "internal_path" : []
                    },
                    .....
                ]

        Arguments:
            scanObject {instance} -- [description] ScanObject 인스턴스

        Returns:
            {list} -- [description] 추출된 Stream 목록
        """
        try:
            # 분석 대상 파일명을 가져온다. 
            fileName = scanObject.get_file_name()

            # 분석 대상 파일에서 Stream을 추출한다. 
            return kernel.extract(fileName)

        except:
            _, msg, obj = sys.exc_info()
            msg = "{} ({}::{})".format(msg, obj.tb_lineno, obj.tb_frame.f_globals.get("__file__"))
            Log.error(msg)
            return []

        finally:
            pass

    @gateway
    def __parse_root__(self, scanObject):
        """[summary]
            ScanObject 대상(Root 파일)을 분석한다. 

            분석 결과는 ScanObject.Children 에 저장된다. 

            * 저장형태 : 
                Children = {
                    <uuid> : {
                        "child_name" : "",
                        "internal_path" : [],
                        "priority" : <int>
                    },
                    .....
                }

        Arguments:
            scanObject {instance} -- [description] ScanObject 인스턴스
        """
        error = False
        err_msg = ""
        try:
            # 분석 대상의 Directory 정보를 저장한다. 
            if not self.get_directories_info(scanObject):
                raise KeiEngineError("Failed get directory info.")

            # 구조를 분석해 Stream을 파일로 저장한다. 
            streams = self.get_streams(scanObject)

            # 생성한 Stream을 Children에 업데이트 한다. 
            for i, stream in enumerate(streams):
                if stream.get("internal_path", [])[-1] in config.ole_reference:
                    priority = config.PRIORITY_LEVEL.get("LEVEL_HIGH", 0)
                else:
                    priority = config.PRIORITY_LEVEL.get("LEVEL_NORMAL", 0)
                
                scanObject.updateChildren(
                    stream.get("fileName", ""),
                    stream.get("internal_path", []),
                    priority
                )

        except KeiEngineError as e:
            error = True
            err_msg = e.msg
            
        except:
            # 에러 로그를 저장한다. 
            _, msg, obj = sys.exc_info()
            msg = "{} ({}::{})".format(msg, obj.tb_lineno, obj.tb_frame.f_globals.get("__file__"))
            Log.error(msg)

            # 에러 결과를 ScanObject에 업데이트할 수 있도록 상태값을 변경한다. 
            error = True
            err_msg = msg
            
        finally:
            scanObject.updateResult(error, err_msg)

    @gateway
    def __load_module__(self, scanObject):
        """[summary]
            ScanObject 대상에 맞는 엔진을 로드하고 엔진 내 정의된 클래스 (config.engine_class) 명을 반환한다. 

        Arguments:
            scanObject {instance} -- [description] ScanObject 인스턴스

        Returns:
            {str} -- [description] 모듈 내 클래스 명
        """
        error = False
        err_msg = ""
        try:
            Log.info(scanObject.get_internal_path())
            
            engine_name = scanObject.get_internal_path()[0]                
            mod = utils.load_module("{}.{}".format(config.ole_eng_path, engine_name))
            if not mod:
                # 경로내 <엔진명>.py 가 없거나 로드 실패한 경우
                raise KeiEngineError("Failed Load Module")
                
            # 엔진내 정의된 클래스명을 가져온다. 
            clsName = getattr(mod, config.engine_class) 
            # 있는 경우 
            if clsName:
                return clsName
            else:
                raise KeiEngineError("Not Found {} Engine Class.".format(config.engine_class))

        except KeiEngineError as e:
            # 에러 로그를 저장한다. 
            Log.error(e.msg)

            # 에러 결과를 ScanObject에 업데이트할 수 있도록 상태값을 변경한다. 
            error = True
            err_msg = e.msg

        except:
            # 에러 로그를 저장한다. 
            _, msg, obj = sys.exc_info()
            msg = "{} ({}::{})".format(msg, obj.tb_lineno, obj.tb_frame.f_globals.get("__file__"))
            Log.error(msg)

            # 에러 결과를 ScanObject에 업데이트할 수 있도록 상태값을 변경한다. 
            error = True
            err_msg = msg
            
        finally:
            scanObject.updateResult(error, err_msg)


    @gateway
    def __parse_child__(self, scanResult, scanObject):
        """[summary]
            ScanObject 대상(Embedded or Children) 을 분석하고 그 결과를 저장한다. 

            * 저장 경로 : ScanObject.fformat.struct[<name>] = {"body" : instance}

        Arguments:
            scanResult {instance} -- [description] ScanResult 인스턴스
            scanObject {instance} -- [description] ScanObject 인스턴스
        """
        error = False
        err_msg = ""
        try:
            # 엔진을 로드한다. 
            clsName = self.__load_module__(scanObject)
            if not clsName:
                raise KeiEngineError("Failed Load Module")

            # 분석 클래스를 초기화한다. 
            instance = clsName()
            # 분석한다. 
            instance.__run__(scanResult, scanObject)
            
            # 분석 결과를 저장한다. 
            # print(instance.to_dict())

            scanObject.updateStructure(instance.__engine__, instance)      

        except KeiEngineError as e:
            # 에러 로그를 저장한다. 
            Log.error(e.msg)

            # 에러 결과를 ScanObject에 업데이트할 수 있도록 상태값을 변경한다. 
            error = True
            err_msg = e.msg

        except:
            # 에러 로그를 저장한다. 
            _, msg, obj = sys.exc_info()
            msg = "{} ({}::{})".format(msg, obj.tb_lineno, obj.tb_frame.f_globals.get("__file__"))
            Log.error(msg)

            # 에러 결과를 ScanObject에 업데이트할 수 있도록 상태값을 변경한다. 
            error = True
            err_msg = msg

        finally:
            scanObject.updateResult(error, err_msg)

    @gateway
    def run(self, scanResult, scanObject):
        """[summary]
             ScanObject 대상을 분석한다. 

        Arguments:
             scanResult {instance} -- [description] ScanResult 인스턴스
             scanObject {instance} -- [description] ScanObject 인스턴스 
        """
        error = False
        err_msg = ""
        try:
            fileName = scanObject.get_file_name()
            
            # OLE 파일여부를 판단한다. 
            if kernel.is_ole(fileName):
                # OLE 파일인 경우
                # Root OLE 파일이거나 추출된 OLE 파일로 판단
                self.__parse_root__(scanObject)
            else:
                # OLE 파일이 아닌 경우 
                # OLE 파일에서 추출한 Embedded 파일로 판단
                self.__parse_child__(scanResult, scanObject)

        except:
            # 에러 로그를 저장한다. 
            _, msg, obj = sys.exc_info()
            msg = "{} ({}::{})".format(msg, obj.tb_lineno, obj.tb_frame.f_globals.get("__file__"))
            Log.error(msg)

            # 에러 결과를 ScanObject에 업데이트할 수 있도록 상태값을 변경한다. 
            error = True
            err_msg = msg
            
        finally:
            scanObject.updateResult(error, err_msg)



    # @gateway
    # def _get_engine(self, stream_name):
    #     """[summary]
    #         해당 분석 엔진에서 분석 클래스 Attribute를 반환한다. 

    #     Arguments:
    #         stream_name {str} -- [description] 분석 엔진명에서 사용될 Stream 명

    #     Returns:
    #         {str} -- [description] 분석 클래스 Attribute
    #     """
    #     try:
    #         # 해당 모듈을 로드한다. 
    #         mod = utils.load_module("{}.{}".format(config.ole_eng_path, stream_name))
    #         if not mod:
    #             # 경로내 <엔진명>.py 가 없거나 로드 실패한 경우
    #             raise KeiEngineError("Failed Load Module")
                
    #         # 엔진내 정의된 클래스명을 가져온다. 
    #         clsName = getattr(mod, config.engine_class) 
    #         # 있는 경우 
    #         if clsName:
    #             return clsName
    #         else:
    #             raise KeiEngineError("Not Found {} Engine Class.".format(config.engine_class))

    #     except KeiEngineError as e:
    #         Log.error(e.msg)
    #         return None

    #     except:
    #         _, msg, obj = sys.exc_info()
    #         msg = "{} ({}::{})".format(msg, obj.tb_lineno, obj.tb_frame.f_globals.get("__file__"))
    #         Log.error(msg)
    #         return None

    #     finally:
    #         pass

    # @gateway
    # def __parse__(self, scanObject, engine_name, fileName):
    #     """[summary]
    #         Stream을 분석한다. 

    #     Arguments:
    #         engine_name {str} -- [description] 엔진 파일명, OLE의 경우 Stream 명
    #         fileName {str} -- [description] 분석 대상 파일 경로

    #     Returns:
    #         {dict} -- [description] 분석된 데이터 
    #     """
    #     try:
    #         # 해당 엔진의 클래스를 가져온다. 
    #         clsName = self._get_engine(engine_name)
    #         if not clsName:
    #             raise KeiEngineError("Failed Get Engine for {}".format(engine_name))

    #         # 분석 클래스를 초기화한다. 
    #         instance = clsName()
    #         # 분석한다. 
    #         instance.__run__(scanObject, fileName)
    #         # 분석된 인스턴스를 반환한다. 
    #         return instance
            
    #     except KeiEngineError as e:
    #         Log.error(e.msg)
    #         return {}

    #     except:
    #         _, msg, obj = sys.exc_info()
    #         msg = "{} ({}::{})".format(msg, obj.tb_lineno, obj.tb_frame.f_globals.get("__file__"))
    #         Log.error(msg)
    #         return {}
            
    #     finally:
    #         pass



    # @gateway
    # def check_pre_process(self, stream):
    #     try:
    #         engine_name = stream.get("internal_path", [])[-1]
    #         return True if engine_name in config.ole_reference else False

    #     except:
    #         _, msg, obj = sys.exc_info()
    #         msg = "{} ({}::{})".format(msg, obj.tb_lineno, obj.tb_frame.f_globals.get("__file__"))
    #         Log.error(msg)
    #         return False

    #     finally:
    #         pass

    # @gateway
    # def processing(self, scanObject=None, stream=None):
    #     try:
    #         if stream:
    #             # 선분석이 필요한 Stream의 경우 
    #             fileName = stream.get("fileName", "")
    #             engine_name = stream.get("internal_path", [])[-1]
    #         else:
    #             # Root 이거나 Embedding의 경우 
    #             fileName = scanObject.get_file_name()
    #             engine_name = scanObject.get_internal_path()[-1]                

    #         parsed_data = self.__parse__(scanObject, engine_name, fileName)
    #         if parsed_data:
    #             scanObject.updateStructure(engine_name, {"body" : parsed_data})
    #             return True
    #         else:
    #             raise KeiEngineError("Failed Parse {}".format(engine_name))

    #     except KeiEngineError as e:
    #         Log.error(e.msg)
    #         return False

    #     except:
    #         _, msg, obj = sys.exc_info()
    #         msg = "{} ({}::{})".format(msg, obj.tb_lineno, obj.tb_frame.f_globals.get("__file__"))
    #         Log.error(msg)

    #         return False

    #     finally:
    #         pass

    # @gateway
    # def root(self, scanObject):
    #     error = False
    #     err_msg = ""
    #     try:
    #         # 분석 대상의 Directory 정보를 저장한다. 
    #         if not self.get_directories_info(scanObject):
    #             raise KeiEngineError("Failed get directory info.")

    #         # 구조를 분석해 Stream을 저장한다. 
    #         streams = self.get_streams(scanObject)
    #         if streams:
    #             # 구조 분석 후 Stream을 파일로 생성하고 children에 저장한 경우 
    #             for stream in streams:
    #                 # 선분석 여부를 확인한다. 
    #                 if self.check_pre_process(stream):
    #                     # 선분석 대상인 경우 
    #                     # 선분석을 수행한다. 
    #                     if not self.processing(scanObject, stream):
    #                         # 선분석이 실패한 경우 
    #                         raise KeiEngineError("Failed Pre-Processing {}".format(os.path.basename(stream.get("fileName", ""))))
    #                 else:
    #                     # 선분석 대상이 아닌 경우
    #                     # 제외된다. 
    #                     pass
    #         else:
    #             # 실패한 경우 
    #             raise KeiEngineError("Failed get streams and update children.")

    #     except KeiEngineError as e:
    #         error = True
    #         err_msg = e.msg
            
    #     except:
    #         # 에러 로그를 저장한다. 
    #         _, msg, obj = sys.exc_info()
    #         msg = "{} ({}::{})".format(msg, obj.tb_lineno, obj.tb_frame.f_globals.get("__file__"))
    #         Log.error(msg)

    #         # 에러 결과를 ScanObject에 업데이트할 수 있도록 상태값을 변경한다. 
    #         error = True
    #         err_msg = msg
            
    #     finally:
    #         scanObject.updateResult(error, err_msg)

    # @gateway
    # def embedded(self, scanObject):
    #     error = False
    #     err_msg = ""
    #     try:
    #         if not self.processing(scanObject):
    #             raise KeiEngineError("Failed Processing.")
                
    #     except KeiEngineError as e:
    #         # 에러 로그를 저장한다. 
    #         Log.error(e.msg)

    #         # 에러 결과를 ScanObject에 업데이트할 수 있도록 상태값을 변경한다. 
    #         error = True
    #         err_msg = e.msg

    #     except:
    #         # 에러 로그를 저장한다. 
    #         _, msg, obj = sys.exc_info()
    #         msg = "{} ({}::{})".format(msg, obj.tb_lineno, obj.tb_frame.f_globals.get("__file__"))
    #         Log.error(msg)

    #         # 에러 결과를 ScanObject에 업데이트할 수 있도록 상태값을 변경한다. 
    #         error = True
    #         err_msg = msg
            
    #     finally:
    #         scanObject.updateResult(error, err_msg)

    # @gateway
    # def run(self, scanObject):
    #     """[summary]
    #          ScanObject 대상을 분석한다. 

    #     Arguments:
    #          scanObject {instance} -- [description] ScanObject 인스턴스 
    #     """
    #     error = False
    #     err_msg = ""
    #     try:
    #         fileName = scanObject.get_file_name()

    #         # OLE 파일여부를 판단한다. 
    #         if kernel.is_ole(fileName):
    #             # OLE 파일인 경우 
    #             # Root OLE 파일이거나 추출된 OLE 파일로 판단.
    #             self.root(scanObject)

    #         else:
    #             # OLE 파일이 아닌 경우 
    #             # OLE 파일에서 추출한 Embedded 파일로 판단.
    #             self.embedded(scanObject)

    #     except:
    #         # 에러 로그를 저장한다. 
    #         _, msg, obj = sys.exc_info()
    #         msg = "{} ({}::{})".format(msg, obj.tb_lineno, obj.tb_frame.f_globals.get("__file__"))
    #         Log.error(msg)

    #         # 에러 결과를 ScanObject에 업데이트할 수 있도록 상태값을 변경한다. 
    #         error = True
    #         err_msg = msg
            
    #     finally:
    #         scanObject.updateResult(error, err_msg)


    # @gateway
    # def root(self, scanObject):
    #     try:
    #         fileName = scanObject.get_file_name()

    #         # 구조를 분석해 Stream을 저장한다. 
    #         # 저장 경로 : (default) <temp_path>\\<"embedded" 폴더>
    #         streams = kernel.extract(fileName)

    #         # Stream 데이터 중 선분석 Stream (struct) 과 후분석 Stream(Children) 분리한다. 
    #         # 분리 기준 : Stream 명
    #         for stream in streams:
    #             stream_name = stream.get("internal_path", [])[-1]

    #             # Stream 명이 선분석 Stream 목록에 있는지 확인한다. 
    #             if stream_name in config.ole_reference:
    #                 # 선분석 Stream 인 경우 
    #                 # 저장 위치 : scanObject.fformat["struct"]
    #                 # 함수 : scanObject.updateStructure()
    #                 engine_name = stream.get("internal_path", [])[-1]
    #                 fileName = stream.get("fileName", "")
    #                 reference = self.__parse__(scanObject, engine_name, fileName)
    #                 if reference:
    #                     scanObject.updateStructure(reference)
    #                 else:
    #                     # 예외처리시 추가 분석이 종료되므로 Error 로 직접 입력
    #                     Log.error("Failed __parse__().".format(stream_name))

    #             else:
    #                 # 후분석 Stream 인 경우 
    #                 # Children 항목에 추가한다. 
    #                 # 저장 위치 : scanObject.children
    #                 # 함수 : scanObject.updateChildren()
    #                 scanObject.updateChildren(stream.get("fileName", None), stream.get("internal_path", None))
            
    #         self.update(False, "")

    #     except:
    #         # 에러 로그를 저장한다. 
    #         _, msg, obj = sys.exc_info()
    #         msg = "{} ({}::{})".format(msg, obj.tb_lineno, obj.tb_frame.f_globals.get("__file__"))
    #         Log.error(msg)

    #         # 에러 결과를 ScanObject에 업데이트할 수 있도록 상태값을 변경한다. 
    #         self.update(True, msg)            

    #     finally:
    #         pass
    # 

    # @gateway
    # def __get_directory_info__(self, fileName):
    #     try:
    #         directory_info = {}

    #         ole = kernel.get_ole_object(fileName)
    #         if not ole:
    #             raise KeiEngineError("Failed get ole object.")

    #         for directory in ole.direntries:
    #             instance = bone.OleDirectoryObject(directory)
    #             info = instance.get()
    #             if info:
    #                 new_name = kernel.convert_entryname([instance.name])
    #                 directory_info.update({new_name[0] : {"header" : info}})

    #         return directory_info

    #     except KeiEngineError as e:
    #         Log.error(e.msg)
    #         return {}

    #     except:
    #         # 에러로그를 작성한다. 
    #         _, msg, obj = sys.exc_info()
    #         msg = "{} ({}::{})".format(msg, obj.tb_lineno, obj.tb_frame.f_globals.get("__file__"))
    #         Log.error(msg)
    #         return {}

    #     finally:
    #         pass            