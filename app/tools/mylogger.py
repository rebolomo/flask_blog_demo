__author__ = 'Administrator'

######################################################
# 打印辅助类
#-内部调用
######################################################

#-*- coding:utf-8 -*-
import traceback
import logging
import logging.handlers
import sys
import os

# flag 
FILE_LOGGING_IS_OPEN = False

# UDP host and port
# UDP_HOST = "192.168.8.46"
# UDP_HOST = "124.202.133.46"
UDP_HOST = "124.202.133.6" #"115.182.97.207"
UDP_PORT = 10088 #10086

def addconsole():
    # Handler to print INFO and high level tag log to sys.stderr
    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    # Format it
    formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s [%(funcName)s: %(filename)s,%(lineno)d] %(message)s')
    console.setFormatter(formatter)
    # add handler to logger
    logging.getLogger('').addHandler(console)

class GameLogger():
    def __init__(self, filename):
        # log path
        realpath = os.path.split(os.path.realpath(__file__))[0]
        filenamefull = realpath + '/../../log/' + str(filename)
        print(filenamefull)
        logging.basicConfig(level=logging.DEBUG,
                            format='%(asctime)s %(process)d %(filename)s[line:%(lineno)d] '
                                   '%(name)-12s %(levelname)-8s %(message)s',
                            datefmt='%m-%d %H:%M:%S ',
                            filename=filenamefull,
                            filemode='w+')
        rfilehdl = logging.handlers.RotatingFileHandler(filenamefull, maxBytes=10*1024*1024, backupCount=5)
        rfilehdl.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s %(process)d %(filename)s[line:%(lineno)d] '
                                      '%(name)-12s %(levelname)-8s %(message)s')
        rfilehdl.setFormatter(formatter)

        self.logger = logging.getLogger(filename)

        if FILE_LOGGING_IS_OPEN is True:
            self.logger.addHandler(rfilehdl)

errorfile = GameLogger('error.log')
errorlogger = logging.getLogger('error')
def throw(callname, e):
    msg = '%s error %s \n' % (callname,e)
    exstr = traceback.format_exc()
    msg += '%s' % (exstr)
    #print msg
    errorlogger.error(msg)
    # TODO: raise exeption in production mode, avoid crash
    # raise e

# Output the log to udp in utf-8
class DatagramPlainHandler(logging.handlers.DatagramHandler):
    def makePickle(self, record):
        msg = record.getMessage()
        msgencoded = msg.encode('utf-8')
        #print(msgencoded)
        return msgencoded


def create_plainudp_logger(host=UDP_HOST, port=UDP_PORT):
    """ here is example:
            login_logger = logging.getLogger("udp.login")
            logstr = 'RoleLevelUp|40000001|4525536|3|30005|1430300491|2015-04-29 17:41:31|5|b char is delete!'
            login_logger.error(logstr)
    """

    datag_hdl = DatagramPlainHandler(host, port)

    formatter = logging.Formatter('%(message)s')
    datag_hdl.setFormatter(formatter)

    udp_logger = logging.getLogger("udp")
    udp_logger.setLevel(logging.NOTSET)
    udp_logger.addHandler(datag_hdl)

