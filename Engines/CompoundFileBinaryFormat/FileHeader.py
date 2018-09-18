# -*- coding:utf-8 -*-
#
# 작성자 : 김승언
# 
# 용도 : FileHeader 분석 모듈
# 설명 : OLE 파일 포멧 내 외부에서 참조하는 FileHeader Stream을 분석하는 모듈
#
# 개발 Log
# 2018.08.15    버전 0.0.1      [개발] 프로토타입 변경
#
__version__ = "0.0.1"
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

import config

#================================================================================================#
# FileHeader 구조
# - Reference : 한글문서파일형식_5.0_revision1.2 
#================================================================================================#
# 자료형            길이(바이트)        설명
#------------------------------------------------------------------------------------------------#
# BYTE array[32]    32              signature, 문서 파일은 "HWP Document File"
# DWORD             4               파일 버전, 0xMMnnPPrr 의 형태 (예: 5.0.3.0)
# DWORD             4               속성
#                                   -------------------------------------------------------------
#                                   범위            설명
#                                   -------------------------------------------------------------
#                                   bit 0           is_arch         압축여부
#                                   bit 1           is_password     암호 설정 여부
#                                   bit 2           is_distributed  배포용 문서 여부
#                                   bit 3           is_save_script  스크립트 저장 여부
#                                   bit 4           is_drm          DRM 보안 문서 여부
#                                   bit 5           is_template     XML Template 스토리지 존재 여부
#                                   bit 6           is_history      문서 이력 관리 존재 여부
#                                   bit 7           is_signature    전자 서명 정보 존재 여부
#                                   bit 8           is_certificate  공인 인증서 암호화 여부
#                                   bit 9           is_reserve_sign 전자 서명 예비 저장 여부 
#                                   bit 10          is_cert_drm     공인 인증서 DRM 보안 문서 여부
#                                   bit 11          is_ccl          CCL 문서 여부 
#                                   bit 12 ~ 31     prop_reserved   예약
#                                   -------------------------------------------------------------
# BYTE array[216]   216             예약
#================================================================================================#
class KeiEngineError(Exception):
    def __init__(self, msg):
        self.msg = msg

class KeiEngine(skeleton.EngineObject):
    def __init__(self):
        skeleton.EngineObject.__init__(self, __version__, __author__, self.__module__)

        # 데이터 타입
        # b	    signed char	        integer	            1	(1),(3)
        # B	    unsigned char	    integer	            1	(3)
        # H	    unsigned short	    integer	            2	(3)
        # i	    int	                integer	            4	(3)
        # I	    unsigned int	    integer	            4	(3)
        # L	    unsigned long	    integer	            4	(3)
        # Q	    unsigned long long	integer	            8	(2), (3)
        # s	    char[]	            bytes	 	 
        self.__structure__ = {
            "signature"     :   {"endian" : "big",    "type" : "s", "offset" : 0,   "size" : 32},
            "file_version"  :   {"endian" : "little", "type" : "L", "offset" : 32,  "size" : 4,    "method" : self._get_file_version},
            "properties"    :   {"endian" : "little", "type" : "L", "offset" : 36,  "size" : 4,    "method" : self._get_properties},
            "reserved"      :   {"endian" : "little", "type" : "s", "offset" : 40,  "size" : 216}
        }
    
    @gateway
    def _get_file_version(self, data, dict_value):
        try:
            value = self.__format__(data, dict_value)

            return {
                "value"     :   value, 
                "major"     :   (value & 0xFF000000) >> 24,  
                "minor"     :   (value & 0x00FF0000) >> 16,
                "build"     :   (value & 0x0000FF00) >> 8,
                "revision"  :   (value & 0x000000FF)
            }

        except:
            _, msg, obj = sys.exc_info()
            msg = "{} ({}::{})".format(msg, obj.tb_lineno, obj.tb_frame.f_globals.get("__file__"))
            Log.error(msg)
            return None

        finally:
            pass

    @gateway
    def _get_properties(self, data, dict_value):
        try:
            value = self.__format__(data, dict_value)

            return {
                "value"             :   value,
                "is_arch"           :   (value & 0x00000001),
                "is_password"       :   (value & 0x00000002),
                "is_distributed"    :   (value & 0x00000004),
                "is_save_script"    :   (value & 0x00000008),
                "is_drm"            :   (value & 0x00000010),
                "is_template"       :   (value & 0x00000020),
                "is_history"        :   (value & 0x00000040),
                "is_signature"      :   (value & 0x00000080),
                "is_certificate"    :   (value & 0x00000100),
                "is_reserve_sign"   :   (value & 0x00000200),
                "is_cert_drm"       :   (value & 0x00000400),
                "is_ccl"            :   (value & 0x00000800),
                "reserved"          :   (value & 0xFFFFF000)
            }

        except:
            _, msg, obj = sys.exc_info()
            msg = "{} ({}::{})".format(msg, obj.tb_lineno, obj.tb_frame.f_globals.get("__file__"))
            Log.error(msg)
            return None
            
        finally:
            pass

    @gateway
    def run(self, scanResult, scanObject):
        error = False
        err_msg = ""

        data = None
        try:
            # 분석 대상 파일의 데이터(바이너리)를 가져온다. 
            data = scanObject.get_file_data()

            # 포멧 구조에 맞춰 파일을 분석한다. 
            for key, dict_value in self.__structure__.items():
                func = dict_value.get("method", None)
                if func:
                    parsed_value = func(data, dict_value)
                else:
                    parsed_value = self.__format__(data, dict_value)

                if parsed_value:
                    setattr(self, key, parsed_value)
            
        except KeiEngineError as e:
            Log.error(e.msg)

            # 에러 상태를 업데이트한다. 
            error = True
            err_msg = e.msg

        except:
            # 에러로그를 작성한다. 
            _, msg, obj = sys.exc_info()
            msg = "{} ({}::{})".format(msg, obj.tb_lineno, obj.tb_frame.f_globals.get("__file__"))
            Log.error(msg)

            # 에러 상태를 업데이트한다. 
            error = True
            err_msg = msg
                        
        finally:
            if data:
                del(data)

            scanObject.updateResult(error, err_msg)
            
    @gateway
    def to_dict(self):
        return self.__dict__

    @gateway
    def to_json(self):
        return utils.convert_dict2json(self.to_dict())