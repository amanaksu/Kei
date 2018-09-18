# -*- coding:utf-8 -*-
#
# 작성자 : 김승언
# 
# 용도 : malwares.com 연동 모듈
# 설명 : malwares.com API 기능 모듈
#
# 개발 Log
# 2018.09.12    버전 0.0.1      [개발] 프로토타입 변경
#
__version__ = "0.0.1"
__author__ = "amanaksu@gmail.com"

# 내장 라이브러리 
import os
import requests  
import sys

# 서드파티 라이브러리 

# 고유 라이브러리 
from Engines import Log, gateway
from Engines import utils

import config



class MWSError(Exception):
    def __init__(self, msg):
        self.msg = msg


@gateway
def get_tag_search(tag, start_time, end_time, limit):
    try:
        params = {"api_key": config.mws_key, "tag": tag, "start":start_time, "end":end_time, "limit": str(limit)}
        response = requests.get("https://public.api.malwares.com/v3/tag/search", params=params)
        json_response = response.json()
        if json_response["result_code"] == 1:
            return json_response["list"]
        else:
            raise MWSError("result: ({}) {}".format(json_response["result_code"], json_response["result_msg"]))

    except MWSError as e:
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
def get_file_download(file_hash):
    try:
        params = {"api_key": config.mws_key, "hash": file_hash}
        response = requests.get("https://{유료 URL}/v3/file/download", params=params)
        return response.content

    except:
        _, msg, obj = sys.exc_info()
        msg = "{} ({}::{})".format(msg, obj.tb_lineno, obj.tb_frame.f_globals.get("__file__"))
        Log.error(msg)
        return ""

    finally:
        pass

@gateway
def get_file_list_download(json_list):
    try:
        Log.info("try Download from malwares.com : {}".format(len(json_list)))

        mws_path = os.path.join(config.temp_path, config.mws_save_folder)
        if not utils.makedirectory(mws_path):
            raise MWSError("Failed MakeDirectory() for malwares.com")
        
        complete_list = []
        # failed_list = []
        for i, dict_data in enumerate(json_list):
            file_hash = dict_data["sha256"]
            zip_content = get_file_download(file_hash)
            if not zip_content:
                # failed_list.append(file_hash)
                Log.error("MWS Download Failed : [{}/{}] {}".format(i+1, len(json_list), file_hash))
                continue

            fullName = os.path.join(mws_path, file_hash)
            if utils.unzip(mws_path, zip_content):
                complete_list.append(fullName)
                Log.debug("MWS Download Successed : [{}/{}] {}".format(i+1, len(json_list), file_hash))
            else:
                Log.error("Failed to write or decompress(unzip). ({})".format(file_hash))
            
        return complete_list

    except MWSError as e:
        Log.error(e.msg)
        return []

    except:
        _, msg, obj = sys.exc_info()
        msg = "{} ({}::{})".format(msg, obj.tb_lineno, obj.tb_frame.f_globals.get("__file__"))
        Log.error(msg)
        return []

    finally:
        pass