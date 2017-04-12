######################################################
# 工具，用于将errorcode excel文件转换成python常量
######################################################
import os
import sys
import codecs
# 导入模块关键是能够根据sys.path环境变量的值，找到具体模块的路径
sys.path.append("..")

from app.tools.excel_config import ExcelDataConfig
from app import logger

current_path = os.path.split(os.path.realpath(__file__))[0]
datapath = current_path + "/../conf"
def main():
    conf = ExcelDataConfig(datapath)
    python_file_path = current_path + '/../app/errorcode.py'
    java_file_path = current_path + '/../../yishang_android/java/WebService/WebReturnCode.java'
    filename = 'errorcode.xlsx'
    keyname = 'errorcode'
    # configid  key desc
    conf.readconf(filename)
    try:
        file_object = open(python_file_path, 'w')

        # 转成errorcode.py文件
        #logger.info(conf.conf)
        errorcodes = conf.conf[keyname]

        # 排序
        for key in sorted(errorcodes.keys()):
            p = errorcodes[key]
            logger.info(p)
            # exist_p = dbhelper.check_product_by_configid(self.db, p['configid'])
            all_the_text = p['key'] + ' = ' + p['configid'] + " #" + p['desc'] + '\n'
            # 写入基本配置
            file_object.write(all_the_text)
  
    finally:
        file_object.close()

    try:
        #file_object = open(java_file_path, 'w')
        file_object = codecs.open(java_file_path,'w','utf-8')

        # 转成errorcode.java文件
        #logger.info(conf.conf)
        errorcodes = conf.conf[keyname]

        # 排序
        output = "package WebService;    \n"
        output += "public enum WebReturnCode \n{"
        output +=   "\tOK(0)," + \
                    "\tTOKEN_ERROR(97),\n" + \
                    "\tURL_ERROR(404),\n" + \
                    "\tNORESULT(405),\n" + \
                    "\tSYSTEM_ERROR(406),\n" + \
                    "\tERROR_UNAUTHOR_OR_AUTHOR_TIMEOUT(407),\n" + \
                    "\tSERVICE_TIMEOUT(408),\n" + \
                    "\tERROR(409),\n"
        count = len(errorcodes)
        i = 0
        for key in sorted(errorcodes.keys()):
            p = errorcodes[key]
            logger.info(p)
            # exist_p = dbhelper.check_product_by_configid(self.db, p['configid'])
            
            if i == count - 1:
                output += "\t%s(%s); //%s \n" % (p['key'], p['configid'],  p['desc'] )
            else:
                output += "\t%s(%s), //%s \n" % (p['key'], p['configid'],  p['desc'] )
            i = i + 1

        output += "\tprivate int value = 0;\n"
        output += \
        "\tprivate WebReturnCode(int value) {    //    必须是private的，否则编译错误 \n" + \
            "\t\tthis.value = value;\n" + \
        "\t}\n"

        output += "}"

        # 写入基本配置
        file_object.write(output)
  
    finally:
        file_object.close()

if __name__ == "__main__":
    # 执行主进程
    main()