# -*- coding: utf-8 -*-
from wsgiref.simple_server import make_server
from wsgiref.util import FileWrapper
from ConfigObject import ConfigObject
from datetime import datetime
from webob import Request
from webob import Response
from webob import exc
from chut import path
from chut import env
import chut as sh
import logging
import json
import sys
import os

pkg_dir = os.path.dirname(__file__)


def fd(*path):
    return FileWrapper(open(os.path.join(*path), 'rb'))


class Application(object):

    def delete(self, filename):
        if path.isdir(filename):
            sh.rm('-Rf', filename) > 1
        for ext in ('.jpg', '.JPG'):
            f = path.join(env.photos, filename + ext)
            if path.isfile(f):
                sh.rm('-Rf', f) > 1
            f += '.metadata'
            if path.isfile(f):
                sh.rm('-Rf', f) > 1
        os.chdir(env.photos)
        sh[sys.argv[0]]('update') > 1
        os.chdir(env.build_path)

    def __call__(self, environ, start_response):
        req = Request(environ)
        resp = Response()
        filename = req.path_info.strip('/')
        lfilename = filename.lower()
        if not req.path_info.strip('/') or os.path.isdir(filename):
            if filename:
                filename = path(filename, 'index.html')
            else:
                filename = 'index.html'
            body = open(filename, 'rb').read()
            resp.body = body
        elif os.path.isfile(filename):
            if req.method.lower() == 'delete':
                sh.rm(filename + '*', shell=True)
                resp = exc.HTTPNoContent()
                return resp(environ, start_response)
            if req.path_info.endswith('.metadata'):
                cfg = ConfigObject(filename=filename)
                if req.method.lower() == 'get':
                    resp.content_type = 'application/json'
                elif req.method.lower() == 'put':
                    data = json.loads(req.body)
                    cfg.metadata.update(data)
                    cfg.write()
                metadata = dict(cfg.metadata.items())
                metadata.update(tags=cfg.metadata.tags.as_list())
                resp.body = json.dumps(metadata)
            elif req.path_info.endswith('.js'):
                resp.content_type = 'text/javascript'
            elif req.path_info.endswith('.json'):
                resp.content_type = 'application/json'
            elif req.path_info.endswith('.css'):
                resp.content_type = 'text/css'
            elif lfilename.endswith('.jpg'):
                resp.charset = None
                resp.content_type = 'image/jpeg'
            print(filename)
            if not resp.content_length:
                resp.app_iter = fd(filename)
        elif req.path_info.startswith('/delete/'):
            filename = req.path_info[8:-1]
            self.delete(filename)
            resp.status_int = 302
            resp.location = '/' + path.dirname(filename)
        else:
            resp.body = str(req.path_info)
        resp.last_modified = datetime.now()
        return resp(environ, start_response)


def serve():
    logging.basicConfig(stream=sys.stderr, level=logging.INFO)
    print('Serving %s at http://localhost:8000/ ...' % os.getcwd())
    server = make_server('', 8000, Application())
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
