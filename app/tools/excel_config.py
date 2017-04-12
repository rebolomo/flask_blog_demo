__author__ = 'Administrator'
import os
import glob
import xlrd

from app import logger

# excel loader
class ExcelDataConfig():

    def __init__(self, path):
        self.conf = {}
        self.confpath = path

    # load contents in excel file
    def loadconfig(self):
        logger.info('load excel config ...')
        oldpath = os.path.abspath(os.curdir)
        os.chdir(self.confpath)
        files = glob.glob('*.xlsx')
        for filename in files:
            if filename.startswith('~'):
                continue
            self.readconf(filename)
        os.chdir(oldpath)
        logger.info('load excel config ...ok!')

    # put the content to conf
    def readconf(self, filename):
        keyname,extension = os.path.splitext(filename)
        fullpath = os.path.join(self.confpath, filename)
        content = {}
        #logger.info(fullpath)
        index_i = 0
        index_j = 0
        cur_value = None
        cur_coltype = None
        try:
            #logger.info('xlrd open '+fullpath)
            data = xlrd.open_workbook(fullpath)
            table = data.sheets()[0]
            colnames = table.row_values(1)
            #logger.info(colnames)
            coltypes = table.row_values(2)
            #logger.info(coltypes)
            #logger.info(table.nrows)
            for i in range(3,table.nrows):
                index_i = i
                record = {}
                row = table.row_values(i)
                #logger.info(row)
                if type(row[0]) == float:
                    tempid = int(row[0])
                else:
                    tempid = row[0]
                id = str(tempid)
                if id != "":
                    #logger.info(id)
                    #logger.info(table.ncols)
                    for j in range(0,table.ncols):
                        index_j = j
                        coltype = coltypes[j]
                        cur_value = row[j]
                        if cur_value != "":
                            cur_coltype = coltype
                            #logger.info(coltype)
                            if(coltype=='i'):
                                record[colnames[j]] = int(row[j])
                            elif(coltype=='n'):
                                record[colnames[j]] = float(row[j])
                            elif(coltype=='s'):
                                if type(row[j]) == float:
                                    temp = int(row[j])
                                else:
                                    temp = row[j]
                                record[colnames[j]] = str(temp)
                    #logger.info(record)
                    content[id] = record
            #logger.info(content)
            self.conf[keyname] = content
        except Exception as e:
            logger.info('Error:load file '+filename + ' ' + str(index_i+1) + ' ' + str(index_j+1) + ' ' + str(cur_value) + ' ' + str(cur_coltype))
            mylogger.throw('readconf', e)
