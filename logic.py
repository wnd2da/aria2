# -*- coding: utf-8 -*-
#########################################################
# python
import os
import traceback
import time
import threading

# third-party

# sjva 공용
from framework import db, scheduler, path_data
from framework.job import Job
from framework.util import Util

# 패키지
from .plugin import logger, package_name
from .model import ModelSetting
from .logic_normal import LogicNormal
#########################################################

class Logic(object): 
    db_default = {
        'db_version' : '1',
        'download_path' : os.path.join(path_data, package_name),
        'auto_start' : 'False',
        'rpc_port' : '6800', 
        'rpc_token' : '',
        'option' : '--bt-tracker=udp://93.158.213.92:1337/announce,udp://62.210.97.59:1337/announce,udp://151.80.120.115:2710/announce,udp://208.83.20.20:6969/announce,udp://185.181.60.67:80/announce,udp://194.182.165.153:6969/announce,udp://5.206.3.65:6969/announce,udp://37.235.174.46:2710/announce,udp://89.234.156.205:451/announce,udp://92.223.105.178:6969/announce,udp://207.241.231.226:6969/announce,udp://207.241.226.111:6969/announce,udp://51.15.40.114:80/announce,udp://91.149.192.31:6969/announce\n--seed-time=0'
    }

    @staticmethod
    def db_init():
        try:
            for key, value in Logic.db_default.items():
                if db.session.query(ModelSetting).filter_by(key=key).count() == 0:
                    db.session.add(ModelSetting(key, value))
            db.session.commit()
            Logic.migration()
        except Exception as e: 
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())
        
    @staticmethod
    def plugin_load():
        try:
            logger.debug('%s plugin_load', package_name)   
            import platform         
            if platform.system() != 'Windows':
                custom = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bin')    
                os.system("chmod 777 -R %s" % custom)

            Logic.db_init()
            if ModelSetting.get_bool('auto_start'):
                Logic.scheduler_start()
            # 편의를 위해 json 파일 생성
            from plugin import plugin_info
            Util.save_from_dict_to_json(plugin_info, os.path.join(os.path.dirname(__file__), 'info.json'))
        except Exception as e: 
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())
    
    @staticmethod
    def plugin_unload():
        try:
            LogicNormal.kill()
        except Exception as e: 
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())
    
    @staticmethod
    def scheduler_start():
        try:
            LogicNormal.run()
        except Exception as e: 
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())
    
    @staticmethod
    def scheduler_stop():
        try:
            LogicNormal.kill()
        except Exception as e: 
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())
           
    @staticmethod
    def migration():
        try:
            pass
        except Exception as e:
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())