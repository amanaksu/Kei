# -*- coding:utf-8 -*-
#
# 작성자 : 김승언
# 
# 용도 : 초기화 모듈
# 설명 : 전역으로 사용하는 모듈/함수 초기화 모듈 (데코레이터, 화면출력, 로그)
#
# 개발 Log
# 2018.08.06    버전 0.0.5      [개발] 프로토타입 변경
#
__version__ = "0.0.5"
__author__ = "amanaksu@gmail.com"

# 내장 라이브러리 

# 서드파티 라이브러리 

# 고유 라이브러리 
from Engines.log import Log, gateway
from Engines import utils
from Engines import dispatch

