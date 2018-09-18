# -*- coding:utf-8 -*-
#
# 작성자 : 김승언
# 
# 용도 : job 모듈
# 설명 : 처리 프로세스를 생성하고 Job을 가져와 처리 프로세스로 전달하는 모듈
#
# 개발 Log
# 2018.08.06    버전 0.0.5      [개발] 프로토타입 변경
# 2018.08.07    버전 0.0.6      [개발] 멀티 프로세스 생성
#

__version__ = "0.0.6"
__author__ = "amanaksu@gmail.com"

# 내장 라이브러리 
import sys

# 서드파티 라이브러리 

# 고유 라이브러리 
from Engines import Log, gateway
from Engines import mws
from Engines import utils
from Engines import consumer

import config

#########################################################################################################
# 메인함수
# - 멀티프로세스
# - job 분배
#########################################################################################################
@gateway
def get_jobs(args):
    try:
        jobs = []

        # Job을 가져온다. 

        # - 폴더/파일에 대한 Job
        if args.file or args.folder:
            jobs += utils.get_file_list(args.file, args.folder)

        # - MWS에 대한 Job
        if config.mws_flag:
            json_list = mws.get_tag_search(args.mws_tag, args.mws_start_time, args.mws_end_time, args.mws_limit)
            if not json_list == []:
                jobs += mws.get_file_list_download(json_list)

        return jobs

    except:
        _, msg, obj = sys.exc_info()
        msg = "{} ({}::{})".format(msg, obj.tb_lineno, obj.tb_frame.f_globals.get("__file__"))
        Log.error(msg)
        return []

    finally:
        pass

@gateway
def start(args):
    job_manager = None
    try:
        # # Job을 가져온다. 
        # # - 폴더/파일에 대한 Job
        # jobs = utils.get_file_list(args.file, args.folder)

        # # - MWS에 대한 Job
        # if config.mws_flag:
        #     mws_jobs_json = mws.get_tag_search(args.mws_tag, args.mws_start_time, args.mws_end_time, args.mws_limit)
        #     if not mws_jobs_json == []:
        #         jobs += mws.get_file_list_download(mws_jobs_json)

        # Job을 가져온다.
        jobs = get_jobs(args)
        total_jobs = len(jobs)
        # Log.info("Jobs: {}".format(total_jobs))

        # 멀티 프로세스를 생성/실행한다. 
        proc_num = config.proc_num
        if total_jobs < proc_num:
            proc_num = total_jobs
        
        job_manager = consumer.Consumer(proc_num=proc_num)
        for i, job in enumerate(jobs):
            # Job을 분배한다. 
            Log.info("Job: {}".format(job))
            job_manager.put(job)
        
    except:
        _, msg, obj = sys.exc_info()
        msg = "{} ({}::{})".format(msg, obj.tb_lineno, obj.tb_frame.f_globals.get("__file__"))
        Log.error(msg)

    finally:
        # 멀티 프로세스를 종료한다. 
        job_manager.stop_all_worker()