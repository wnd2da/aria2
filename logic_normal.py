# -*- coding: utf-8 -*-
#########################################################
# python
import os
import datetime
import traceback
import urllib
from datetime import datetime
import subprocess
import threading

# third-party

# sjva 공용
from framework import app, db, scheduler, path_app_root, celery, path_data
from framework.job import Job
from framework.util import Util

# 패키지
from .plugin import logger, package_name
from .model import ModelSetting

#########################################################
class LogicNormal(object):
    current_process = None

    @staticmethod
    def run():
        try:
            LogicNormal.kill()
            binary_path = LogicNormal.get_binary()
            import platform         
            if platform.system() != 'Windows':
                os.system("chmod 777 -R %s" % binary_path)

            #command = [binary_path, '--enable-rpc', '--rpc-listen-all=true', '--rpc-allow-origin-all', '-d', ModelSetting.get('download_path'), '-l', os.path.join(path_data, 'log', 'aria2c.log')]
            command = [binary_path, '--enable-rpc', '--rpc-listen-all=true', '--rpc-allow-origin-all', '-d', ModelSetting.get('download_path')]
            if ModelSetting.get('rpc_port') != '6800':
                command.append('--rpc-listen-port=%s' % ModelSetting.get('rpc_port'))
            #if ModelSetting.get('rpc_token') != '':
            #    command.append('--rpc_secret=%s' % ModelSetting.get('rpc_token'))
            if ModelSetting.get('option') != '':
                option = ModelSetting.get_list('option')
                command = command + option
            logger.debug(command)
            LogicNormal.current_process = subprocess.Popen(command)
            logger.debug('RUN............................')
        except Exception as e: 
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())
            
    @staticmethod
    def kill():
        try:
            if LogicNormal.current_process is not None and LogicNormal.current_process.poll() is None:
                import psutil
                process = psutil.Process(LogicNormal.current_process.pid)
                for proc in process.children(recursive=True):
                    proc.kill()
                process.kill()
            LogicNormal.current_process = None
        except Exception as e: 
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())

    @staticmethod
    def install():
        try:
            import framework.common.util as CommonUtil
            def func():
                import system
                LogicNormal.kill()
                commands = [['msg', u'설치 환경이 아닙니다.']]
                if CommonUtil.is_docker():
                    commands = [
                        ['msg', u'잠시만 기다려주세요.'],
                        ['apk', 'add', 'aria2'],
                        ['msg', u'설치가 완료되었습니다.']
                    ]
                elif CommonUtil.is_termux():
                    pass
                elif CommonUtil.is_linux():
                    commands = [
                        ['msg', u'잠시만 기다려주세요.'],
                        ['apt-get', '-y', 'install', 'aria2'],
                        ['msg', u'설치가 완료되었습니다.']
                    ]
                system.SystemLogicCommand.start('설치', commands)
            t = threading.Thread(target=func, args=())
            t.setDaemon(True)
            t.start()
            return True
        except Exception as e: 
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())
        return False
    

    @staticmethod
    def uninstall():
        try:
            import framework.common.util as CommonUtil
            def func():
                import system
                LogicNormal.kill()
                commands = [['msg', u'설치 환경이 아닙니다.']]
                if CommonUtil.is_docker():
                    commands = [
                        ['msg', u'잠시만 기다려주세요.'],
                        ['apk', 'del', 'aria2'],
                        ['msg', u'삭제가 완료되었습니다.']
                    ]
                elif CommonUtil.is_termux():
                    pass
                elif CommonUtil.is_linux():
                    commands = [
                        ['msg', u'잠시만 기다려주세요.'],
                        ['apt-get', '-y', 'remove', 'aria2'],
                        ['msg', u'삭제가 완료되었습니다.']
                    ]
                system.SystemLogicCommand.start('삭제', commands)
            t = threading.Thread(target=func, args=())
            t.setDaemon(True)
            t.start()
            return True
        except Exception as e: 
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())
        return False
    
    @staticmethod
    def get_binary():
        try:
            import framework.common.util as CommonUtil
            bin_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'bin')
            ret = ''
            import platform
            if CommonUtil.is_termux() and platform.platform().find('arch') != -1:
                ret = os.path.join(bin_path, 'termux', 'aria2c')
            elif CommonUtil.is_windows():
                ret = os.path.join(bin_path, 'Windows', 'aria2c.exe')
            elif CommonUtil.is_mac():
                ret = os.path.join(bin_path, 'Darwin', 'aria2c')
            elif CommonUtil.is_docker() or CommonUtil.is_linux():
                command = ['which', 'aria2c']
                log = Util.execute_command(command)
                if log:
                    ret = log[0].strip()
        except Exception as e: 
            logger.error('Exception:%s', e)
            logger.error(traceback.format_exc())

        return ret