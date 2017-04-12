from flask import Flask, request, Markup, url_for
from flask.ext.bootstrap import Bootstrap, WebCDN, ConditionalCDN, StaticCDN
from flask.ext.mail import Mail
from flask.ext.moment import Moment
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager


from flask.ext.pagedown import PageDown
from flask.ext.babel import Babel
from datetime import datetime

__version__ = '3.0.3.1'

import re

bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()
pagedown = PageDown()
babel = Babel()

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'

import logging

logger = logging.getLogger("init")

from config import config

class _custom_moment(object):
    @staticmethod
    def include_moment(version='2.3.1'):
        if version is not None:
            if request.is_secure:
                protocol = 'https'
            else:
                protocol = 'http'
            # js = '<script src="%s://cdnjs.cloudflare.com/ajax/libs/moment.js/%s/moment-with-langs.min.js"></script>\n' % (protocol, version)
            js = '<script src="' + url_for("static", filename="moment-with-langs.min.js") + '"></script>'
        return Markup('''%s<script>
function flask_moment_render(elem) {
    $(elem).text(eval('moment("' + $(elem).data('timestamp') + '").' + $(elem).data('format') + ';'));
    $(elem).removeClass('flask-moment');
}
function flask_moment_render_all() {
    $('.flask-moment').each(function() {
        flask_moment_render(this);
        if ($(this).data('refresh')) {
            (function(elem, interval) { setInterval(function() { flask_moment_render(elem) }, interval); })(this, $(this).data('refresh'));
        }
    })
}
$(document).ready(function() {
    flask_moment_render_all();
});
</script>''' % js)

    @staticmethod
    def include_jquery(version='1.10.1'):
        if request.is_secure:
            protocol = 'https'
        else:
            protocol = 'http'
        return Markup('<script src="%s://code.jquery.com/jquery-%s.min.js"></script>' % (protocol, version))

    @staticmethod
    def lang(language):
        return Markup('<script>\nmoment.lang("%s");\n</script>' % language)

    def __init__(self, timestamp=None):
        if timestamp is None:
            timestamp = datetime.utcnow()
        self.timestamp = timestamp

    # REBOL note, timestamp转化为datetime
    def timestamp2datetime(self, timestamp, convert_to_local=False):
        #Converts UNIX timestamp to a datetime object.
        if isinstance(timestamp, (int, float)):
            dt = datetime.utcfromtimestamp(timestamp)
            if convert_to_local:  # 是否转化为本地时间
                dt = dt + datetime.timedelta(hours=8)  # 中国默认时区
            return dt
        return timestamp

    def _timestamp_as_iso_8601(self, timestamp):
        datetime = self.timestamp2datetime(timestamp);
        return datetime.strftime('%Y-%m-%dT%H:%M:%SZ')

    def _render(self, format, refresh=False):
        t = self._timestamp_as_iso_8601(self.timestamp)
        return Markup('<span class="flask-moment" data-timestamp="%s" data-format="%s" data-refresh="%d">%s</span>' % (
            t, format, int(refresh) * 60000, t))

    def format(self, fmt, refresh=False):
        return self._render("format('%s')" % fmt, refresh)

    def fromNow(self, no_suffix=False, refresh=False):
        return self._render("fromNow(%s)" % int(no_suffix), refresh)

    def fromTime(self, timestamp, no_suffix=False, refresh=False):
        return self._render("from(moment('%s'),%s)" % (self._timestamp_as_iso_8601(timestamp), int(no_suffix)), refresh)

    def calendar(self, refresh=False):
        return self._render("calendar()", refresh)

    def valueOf(self, refresh=False):
        return self._render("valueOf()", refresh)

    def unix(self, refresh=False):
        return self._render("unix()", refresh)


def change_cdn_domestic(tar_app):
    # static = tar_app.extensions['bootstrap']['cdns']['static']
    # local = tar_app.extensions['bootstrap']['cdns']['local']

    BOOTSTRAP_VERSION = re.sub(r'^(\d+\.\d+\.\d+).*', r'\1', __version__)
    JQUERY_VERSION = '2.0.3'
    HTML5SHIV_VERSION = '3.7'
    RESPONDJS_VERSION = '1.3.0'

    local = StaticCDN('bootstrap.static', rev=True)
    static = StaticCDN()

    def change_one(tar_lib, tar_ver, fallback):
        # tar_js = ConditionalCDN('BOOTSTRAP_SERVE_LOCAL', fallback, WebCDN('//cdn.bootcss.com/' + tar_lib + '/' + tar_ver + '/'))
        tar_js = ConditionalCDN('BOOTSTRAP_SERVE_LOCAL', fallback, WebCDN('/static/'))
        tar_app.extensions['bootstrap']['cdns'][tar_lib] = tar_js

    libs = {'jquery': {'ver': JQUERY_VERSION, 'fallback': local},
            'bootstrap': {'ver': BOOTSTRAP_VERSION, 'fallback': local},
            'html5shiv': {'ver': HTML5SHIV_VERSION, 'fallback': static},
            'respond.js': {'ver': RESPONDJS_VERSION, 'fallback': static}}
    for lib, par in libs.items():
        change_one(lib, par['ver'], par['fallback'])


def create_app(config_name):
    # print(config_name)
    app = Flask(__name__)

    config[config_name].init_app(app)

    app.config.from_object(config[config_name])

    bootstrap.init_app(app)

    # REBOL note, 修改bootstrap的cdn，默认的cloudflare访问太慢
    change_cdn_domestic(app)

    mail.init_app(app)
    moment.init_app(app)

    # REBOL note, 修改moment里的cloudflare
    app.extensions['moment'] = _custom_moment

    db.init_app(app)
    login_manager.init_app(app)
    pagedown.init_app(app)

    app.config['BABEL_DEFAULT_LOCALE'] = 'zh_Hans_CN'
    # app.config['BABEL_TRANSLATION_DIRECTORIES'] = app.root_path
    # print(app.config['BABEL_TRANSLATION_DIRECTORIES'])
    babel.init_app(app)

    app.debug = True

    from .blog import blog as blog_blueprint
    app.register_blueprint(blog_blueprint)

    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint, url_prefix='/auth')

    from .api_1_0 import api as api_1_0_blueprint
    app.register_blueprint(api_1_0_blueprint, url_prefix='/api/v1.0')

    from .tools import tool as tools_blueprint
    app.register_blueprint(tools_blueprint)
    # ...

    return app
