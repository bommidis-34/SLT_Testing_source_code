import pandas as pd
import warnings
import sys
from collections import OrderedDict

warnings.filterwarnings("ignore", category=UserWarning)

def allPrePostTests(TestType,preDict,logDir):
# Command for Host , Command for SUT
    sut_cmd=" "
    host_cmd=" "
    #TestType :
    #    'PreTest' and 'PostTest'
    for key,value in preDict.items():
        if value['Type'] == TestType and value['SystemRole'] == 'Target' :
            sut_cmd = sut_cmd + value['command'] + ";"
        if value['Type'] == TestType and value['SystemRole'] == 'Host' :
            host_cmd = host_cmd + value['command'] + ";"
# Remove Duplicates
# Convert String to List
    #print("Initial Command Before Update \n ",sut_cmd)
    _list=sut_cmd.split(";")
    res = list(OrderedDict.fromkeys(_list))
    #REMOVE umountsv , mountsv from middle of the list
    if res.count("umountsv") > 0:
        res.remove("umountsv")
        res.remove("mountsv")
        #ADD umountsv , mountsv to the end of the list
        res.append("umountsv")
        res.append("mountsv")
    delim=";"
    sut_cmd=delim.join(map(str, res)).replace(";;",";")
    #print("Final Command After Update \n ",sut_cmd)
    #ssh_auth.ssh_run_os(logs_folder,sut_cmd,hostname,logDir)
    #ssh_auth.ssh_run_os(logs_folder,"cat /sv/dsa-00;killmax;sleep 10;cat /sv/iax-00",hostname,logDir)
    _file= logDir+f"/all_{TestType}_Command.txt"
    f = open(_file,"w")
    print(" Target/SUT {0} Command : \n ******************************* \n".format(TestType),sut_cmd, file = f)
    print(" HOST {0} Command : \n ******************************* \n".format(TestType),host_cmd, file = f)
    f.close()
    return sut_cmd,host_cmd