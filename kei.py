# -*- coding:utf-8 -*-
#
# 작성자 : 김승언
# 
# 용도 : 시작 모듈
# 설명 : 분석 자동 프레임워크 콘솔 시작 모듈
#
# 개발 Log
# 2018.08.06    버전 0.0.5      [개발] 프로토타입 변경
#
__version__ = "0.0.5"
__author__ = "amanaksu@gmail.com"

# 내장 라이브러리 
import argparse
import os
import sys

# 서드파티 라이브러리 

# 고유 라이브러리 
from Engines import Log
from Engines import jobs

import config



#########################################################################################################
# 시작 부분
#########################################################################################################
def parse_argument():
    """[summary]
        외부 파라미터를 전달받는다. 

        참조 라이브러리 : argparse

    Returns:
        {instance} -- [description] argparse.ArgumentParser 클래스
        {instance} -- [description] argparse.NameSpace 클래스
    """
    try:
        # parser를 생성한다. 
        parser = argparse.ArgumentParser()

        # Parameter를 정의한다. 
        parser.add_argument("--file", dest="file", required=False, type=str, default="")
        parser.add_argument("--folder", dest="folder", required=False, type=str, default="")

        # MWS 연동 Parameter
        mws = parser.add_argument_group("mws")
        mws.add_argument("--mws_tag", dest="mws_tag", required=False, type=str)
        mws.add_argument("--mws_start_time", dest="mws_start_time", required=False, type=str, help="Ex) 2018-04-01 00:00:00")
        mws.add_argument("--mws_end_time", dest="mws_end_time", required=False, type=str, help="Ex) 2018-04-01 23:59:59")
        mws.add_argument("--mws_limit", dest="mws_limit", required=False, type=int, default=2000)

        return parser, parser.parse_args()

    except:
        return None, None

    finally:
        pass

if __name__ == "__main__":
    try:
        # 외부 설정 정보 가져오기
        parser, args = parse_argument()
        if parser is None or args is None:
            raise SystemExit

        # 로그 설정
        Log.init(log_level=config.log_level, 
                 log_path=config.log_path, 
                 log_cmd=config.log_cmd)

        # 시작 로그 
        Log.info("[*] start")

        # 메인함수 시작 
        jobs.start(args)

        # 종료 로그
        Log.info("[*] done")

    except SystemExit:
        pass

    except:
        # 에러로그 저장
        _, msg, obj = sys.exc_info()
        msg = "{} ({}::{})".format(msg, obj.tb_lineno, obj.tb_frame.f_globals.get("__file__"))
        Log.error(msg)

    finally:
        pass


#########################################################################################################
# 테스트 함수
# - test_config() : config.py 파일 필수 파라미터 검증 함수 
#########################################################################################################
def test_config():
    config_file_name = "config.py"

    assert os.path.exists(config_file_name)