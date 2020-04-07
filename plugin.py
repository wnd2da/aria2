# -*- coding: utf-8 -*-
#########################################################
# python
import os
import traceback
import threading
import urllib2, json
import requests

# third-party
from flask import Blueprint, request, Response, send_file, render_template, redirect, jsonify, session, send_from_directory 
from flask_login import login_user, logout_user, current_user, login_required

# sjva 공용
from framework.logger import get_logger
from framework import app, db, scheduler, path_data, socketio, path_app_root
from framework.util import Util

# 패키지
# 로그
package_name = __name__.split('.')[0]
logger = get_logger(package_name)

from .model import ModelSetting
from .logic import Logic
from .logic_normal import LogicNormal
#########################################################


#########################################################
# 플러그인 공용                                       
#########################################################
#blueprint = Blueprint(package_name, package_name, url_prefix='/%s' %  package_name, template_folder=os.path.join(os.path.dirname(__file__), 'templates'))
blueprint = Blueprint(package_name, package_name, url_prefix='/%s' %  package_name, template_folder=os.path.join(os.path.dirname(__file__), 'templates'), static_folder=os.path.join(os.path.dirname(__file__), 'static'), static_url_path='static')

menu = {
    'main' : [package_name, 'aria2'],
    'sub' : [
        ['setting', '설정'], ['gui', 'GUI'], ['log', '로그'], 
    ],
    'category' : 'tool'
}

plugin_info = {
    'version' : '0.1.0.0',
    'name' : 'aria2',
    'category_name' : 'tool',
    'developer' : 'soju6jan',
    'description' : '다운로드 프로그램인 aria2 런처 & GUI',
    'home' : 'https://github.com/soju6jan/aria2',
    'more' : '',
}

def plugin_load():
    Logic.plugin_load()

def plugin_unload():
    Logic.plugin_unload()

def process_telegram_data(data):
    pass


#########################################################
# WEB Menu 
#########################################################
@blueprint.route('/')
def home():
    return redirect('/%s/gui' % package_name)

@blueprint.route('/jsonrpc', methods=['GET', 'POST'])
def jsonrpc():
    try:
        jsonreq = json.dumps(request.json)
        #logger.debug(jsonreq)
        c = urllib2.urlopen('http://127.0.0.1:%s/jsonrpc' % ModelSetting.get('rpc_port'), jsonreq)
        data = json.loads(c.read())
        #res = requests.post('http://127.0.0.1:%s/jsonrpc' % ModelSetting.get('rpc_port'), data=jsonreq, headers={'Content-Type': 'application/json; charset=utf-8'})
        #data = res.json()
        return jsonify(data)

    except Exception as e: 
        logger.error('Exception:%s', e)
        logger.error(traceback.format_exc())  
        

@blueprint.route('/<sub>')
@login_required
def first_menu(sub): 
    arg = ModelSetting.to_dict()
    arg['package_name']  = package_name
    if sub == 'setting':
        arg['status'] = str(LogicNormal.current_process is not None)
        arg['binary_path'] = LogicNormal.get_binary()
        return render_template('%s_%s.html' % (package_name, sub), arg=arg)
    elif sub == 'main':
        return blueprint.send_static_file('main.html')
    elif sub == 'gui':
        site = "/%s/main" % (package_name)
        return render_template('iframe.html', site=site)
    elif sub == 'log':
        return render_template('log.html', package=package_name)
    #elif sub == 'aria_log':
    #    return render_template('log.html', package='aria2c')
    elif len(sub.split('.')) > 1:
        tmp = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', sub)
        if os.path.exists(tmp):
            return blueprint.send_static_file(sub)
        tmp = os.path.join(ModelSetting.get('download_path'), sub)
        #logger.debug(tmp)
        if os.path.exists(tmp):
            #logger.debug(tmp.replace(path_app_root, ''))
            return send_from_directory(ModelSetting.get('download_path'), sub)
    return render_template('sample.html', title='%s - %s' % (package_name, sub))


@blueprint.route('/flags/<sub>')
def flags(sub): 
    return blueprint.send_static_file('flags/%s' % sub)



#########################################################
# For UI 
#########################################################
@blueprint.route('/ajax/<sub>', methods=['GET', 'POST'])
@login_required
def ajax(sub):
    try:
        # 설정 저장
        if sub == 'setting_save':
            ret = ModelSetting.setting_save(request)
            return jsonify(ret)
        elif sub == 'status':
            todo = request.form['todo']
            if todo == 'true':
                if LogicNormal.current_process is None:
                    LogicNormal.run()
                    ret = 'execute'
                else: 
                    ret = 'already_execute'
            else:
                if LogicNormal.current_process is None:
                    ret = 'already_stop'
                else:
                    LogicNormal.kill()
                    ret =  'stop'
            return jsonify(ret)
        elif sub == 'version':
            binary_path = request.form['binary_path']
            def func():
                import system
                commands = [
                    [binary_path, '-v'],
                ]
                system.SystemLogicCommand.start('버전', commands)
            if binary_path == '':
                ret = False
            else:
                t = threading.Thread(target=func, args=())
                t.setDaemon(True)
                t.start()
                ret = True
            return jsonify(ret)
        elif sub == 'install':
            LogicNormal.install()
            return jsonify({})
        elif sub == 'uninstall':
            LogicNormal.uninstall()
            return jsonify({})
    except Exception as e: 
        logger.error('Exception:%s', e)
        logger.error(traceback.format_exc())  
        return jsonify('fail')   

