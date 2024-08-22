import pandas as pd
import warnings
import sys
from collections import OrderedDict
#import logging as _log

#_log.basicConfig(filename='biosGrubOvr.txt', level=_log.INFO)
warnings.filterwarnings("ignore", category=UserWarning)

def biosKnobOverrides(inputFile,logDir):
    biosKnobList = []
    biosStr = " "
    replaceStr = " "
    cmd = pd.read_excel(inputFile,sheet_name=0)
    for index,row in cmd.iterrows():
        custKnob = row['Parameter.custombiosargs']
        if str(custKnob) != 'nan' :
            biosKnobList.append(custKnob)
    _file= logDir+"/biosGrubOvr.txt"
    f=open(_file,"w")
    print("biosKnobList: ",biosKnobList, file = f)
    
    #CONVERT list to String
    delim=" "
    biosStr=delim.join(map(str, biosKnobList))
    print("SPLIT String biosStr on delim:'{0}' and remove Duplicates".format(delim), file = f)
    print("Initial Command Before Update : ",str(biosStr), file = f)
    _list=biosStr.split("--biosstr ")
    replaceStr = list(OrderedDict.fromkeys(_list))
    biosStr="biosknob write "+ delim.join(map(str, replaceStr)).replace("="," ")
    print(" \n BIOS Knobs Override : \n ********************** \n",biosStr)
    print(" \n BIOS Knobs Override : \n ********************** \n",biosStr, file = f)
    f.close()
    return biosStr

#Example:
# --osstr [grub_parameters="35_xpressos"] --osstr [grub_parameters_override="mem=svos@100000M"] --osstr [grub_kernel="SVOS-NEXT_6.3.0_svos-next-tickless"]

def OSArgsOverrides(inputFile,logDir):
    osArgsList = []
    osStr = " "
    replaceStr = " "
    cmd = pd.read_excel(inputFile,sheet_name=0)
    for index,row in cmd.iterrows():
        custKnob = str(row['Parameter.customOSArgs'])
        if str(custKnob) != 'nan' :
            custKnob = custKnob.split("--osstr ") # Select grub_parameters_override
            custKnob = custKnob[2].replace('"','').replace('grub_parameters_override=','') 
            osArgsList.append(custKnob)
    _file= logDir+"/biosGrubOvr.txt"
    f=open(_file,"a")
    print("osArgsList",osArgsList, file = f)   
    #CONVERT list to String
    delim=" "
    osStr=delim.join(map(str, osArgsList))
    print("SPLIT String biosStr on delim:'{0}' and remove Duplicates".format(delim), file = f)
    print("Initial Command Before Update \n ",str(osStr), file = f)
    _list = osStr.split(" ")
    _list = list(OrderedDict.fromkeys(_list))
    _list.remove('')
    replaceStr = delim.join(map(str, _list))
    print("Final Command After Update \n ",str(replaceStr), file = f)
    sed=' '
    for i in _list:
        sed = sed + f"-e '/{i}/d' "
    osStr = "sed -i" + sed + "/etc/svos/params.d/35_xpressos ;echo -e '"+ replaceStr.replace(' ','\\n').replace('\\n\\n','\\n') + "' >> /etc/svos/params.d/35_xpressos; update-grub"
    print(" \n OS GRUB Knobs Override : \n ********************** \n",osStr)
    print(" \n OS GRUB Knobs Override : \n ********************** \n",osStr, file = f)
    f.close()
    return osStr

def biosOSGrubOverride(inputFile,logDir):
    biosOvr = biosKnobOverrides(inputFile,logDir)
    osOvr = OSArgsOverrides(inputFile,logDir)
    return biosOvr,osOvr

if __name__ == "__main__":
    inputFile=sys.argv[1]
    commands = biosOSGrubOverride(inputFile,'biosGrubOvr.txt')
    print(" BIOS Knobs Override : \n ********************** \n",commands[0])
    print(" OS GRUB Knobs Override : \n *********************** \n",commands[1])