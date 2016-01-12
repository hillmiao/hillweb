#!/usr/bin/python
"""hill -- a micro web framework"""
import threading
import re
import config

ctx = threading.local()

class Application(object):
    def __init__(self, urlmapping):
        self.urlmapping = urlmapping

    def run(self, *middleware):
        from paste import httpserver
        app = self.make_app(*middleware)
        httpserver.serve(app, host='0.0.0.0', port='8888')

    def make_app(self, *middleware):
        def wsgi(env, start_response):
            self.load(env)
            result = self.process_request()
            result = iter(result)
            status, headers = ctx.status, ctx.headers
            start_response(status, headers)
            return result

        for clz in middleware:
            wsgi = clz(wsgi)
        return wsgi

    def load(self, env):
        ctx.env = env
        ctx.status = '200 OK'
        ctx.headers = [('ContentType', 'text/html')]
        ctx.urlpath = env['PATH_INFO']
        ctx.urlmapping = self.urlmapping

    def process_request(self):
        handler, args = self.findhandler(ctx.urlpath, ctx.urlmapping)
        out = self.dohandler(handler, args)
        return out

    def findhandler(self, urlpath, urlmapping):
        for pattern, handler in urlmapping:
            out = re.compile('^' + pattern + '$').match(urlpath)
            if out:
                return handler, [x for x in out.groups()]
        return None, None

    def dohandler(self, handler, args):
        assert handler is not None, "404 Not Found"
        if '.' in handler:
            mod, meth = self.splitmodule(handler)
        else:
            mod, meth = '__main__', handler
        mod = __import__(mod, globals(), locals(), [''], -1)
        tocall = getattr(mod, meth)
        return tocall(*args)

    def splitmodule(self, s):
        l = s.split('.')
        mod = '.'.join(l[0:-1])
        meth = l[-1]
        return mod, meth

class LogMiddleware(object):
    def __init__(self, app):
        self.app = app

    def __call__(self, env, start_response):
        print 'log'
        return self.app(env, start_response)

class Template(object):
    def __init__(self, name):
        from jinja2 import Environment, PackageLoader
        self.env = Environment(loader=PackageLoader(
            'hill', 'templates', encoding='utf-8'))
        self.name = name

    def render(self, *args, **kw):
        return self.env.get_template(self.name).render(*args, **kw)

def db():
    import MySQLdb
    conn = MySQLdb.connect(config.db_ip, config.db_user,
           config.db_password, config.db_name)
    return conn

if __name__ == '__main__':
    urlmapping = [
            (r'/', 'index'),
            (r'/dream', 'search'),
            (r'/dream/(\d+)', 'dreaminfo'),
            (r'/fund', 'controllers.fund'),
            ]
    app = application(urlmapping)
    app.run(LogMiddleware)
