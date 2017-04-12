import os
basedir = os.path.abspath(os.path.dirname(__file__))
from app.tools.excel_config import ExcelDataConfig
from app import logger

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    FLASKY_MAIL_SUBJECT_PREFIX = '[Flasky]'
    FLASKY_MAIL_SENDER = 'Flasky Admin <flasky@example.com>'
    FLASKY_ADMIN = 'rebol@126.com'#os.environ.get('FLASKY_ADMIN')
    FLASKY_POSTS_PER_PAGE = 3

    
    #### 用户管理 ####
    # 默认密码
    DEFAULT_PASSWORD_FOR_USER = '123456'

    # 管理员名称
    DEFAULT_ADMIN_NAME = 'sunwukong'

    # 验证码配置
    # 验证码位数
    VERIFICATION_CODE_LENGTH = 4

    # 翻译管理
    BABEL_DEFAULT_LOCALE = 'zh_Hans_CN'

    # API地址管理
    API_MAIN_PORT = "8001"
    API_TIMER_PORT = "8000"

    # 上传文件的存贮目录
    UPLOAD_DIR = "uploads"

    USER_BACKUP_FILE = "user.csv"

    CONF = None
    @staticmethod
    def init_app(app):
        #print(app.root_path)
        Config.UPLOAD_DIR = app.root_path + '/' + Config.UPLOAD_DIR
        conf = ExcelDataConfig(app.root_path + '/../conf/')
        conf.loadconfig()
        Config.CONF = conf.conf
        logger.info(Config.CONF['errorcode'])
        #print(Config.UPLOAD_DIR)
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_CONVERT_UNICODE = True
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:123@127.0.0.1:3307/blog?charset=utf8"
    #SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
    #    'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'data.sqlite')


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig
}
