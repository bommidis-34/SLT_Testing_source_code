import os
import sys
import ssh_auth as ss
from colorama import Fore
import subprocess
from datetime import datetime

hostTestCmdList = []
sutTestCmdList = []

# groupTLDict[key]= [UniqueName]
# Key : 0 - Value : ['GNR_SP_R1S_VV_SVOS_CONC_5', 'GNR_SP_R1S_VV_SVOS_CONC_51']

# testlineDict[key]={'GoalName':None,'time':None,'Hwcfg':None,'IsAutomated':None,'testlines':[]}
# Key : GNR_SP_R1S_VV_SVOS_CONC_5 - Value : 
#{'GoalName': 'DSA/IAX  Max Transfer , HQM/CPM , Memory( highmem_wpc ) , Lock Stress',
# 'time': 180,
# 'Hwcfg': 'SBR2S1',
# 'IsAutomated': True,
# 'testlines': ['pcie_WA_forRHF_old', 'set_hang_breaks_Mesh', 'dsa_iax_maxTransfer_withoutInterrupts', 'sc_Locks_exclude_core0_arden_dsa']}

# Command Dict :
# Key : pcie_WA_forRHF_old - Value : {'Type': 'PreTest', 'SystemRole': 'Target', 'command': 'regx /sv/*-*/global.mstr_ctl[11]=1; regx /sv/*-*/global.uncorr_err_sts=0xffffffff; regx /sv/*-*/global.corr_err_sts=0xffffffff;regx /sv/*-*/global.reg_cpltoreg_type=0xBEBC22;'}

# use zip() to iterate over all dictionary in single line
def hostprocess(command,logDir):
    now = datetime.now()    
    current_time = now.strftime("%Y%m%d_%H_%M_%S")
    _file = logDir+f"\hostProcess_{current_time}.txt"
    try:
        output = subprocess.run(command, stdout=subprocess.PIPE,stderr=subprocess.PIPE,universal_newlines=True)
        f = open(_file,"w")
        resp = ''.join(output.stdout.readlines())
        f.write(resp)
        if "No such file or directory" in resp:
            print(Fore.YELLOW + "\n Warning - command didnt execute")
            print(Fore.YELLOW + "\n Warning - command stdout - ", resp)
        else:
            print(Fore.GREEN +"\n Command executed - output - ",resp)        
    except:
        print(Fore.RED + "Oops!", sys.exc_info()[0], Fore.RED + "occurred.")
        print(Fore.RED + "Exiting the script execution...")
        sys.exit(0)
    f.close()


def multiThread(cmdList,hostname,logDir):
    Module = "multiprocessing"
    if Module not in sys.modules:
        import multiprocessing
    global hostTestCmdList,sutTestCmdList
    threads = len(cmdList)
    processes = []
    now = datetime.now()    
    current_time = now.strftime("%Y%m%d_%H_%M_%S")
    _file = logDir+f"\multiThreadPids_{current_time}.txt"
    f = open(_file, "w")
    print("Total Threads to run : {0} \n".format(threads), file = f)
    print("hostTestCmdList",hostTestCmdList, file = f)
    print("sutTestCmdList",sutTestCmdList, file = f)
    print("cmdList",cmdList, file = f)
    for cmd in cmdList:
        ind = cmdList.index(cmd) + 1
        print("cmd",cmd, file = f)
        if cmd in sutTestCmdList:
            process = multiprocessing.Process(target=ss.ssh_run_os, args=(cmd,hostname,f"cmd_{ind}",logDir,))
            processes.append(process)
            process.start()
            print("Process : {0} Started on SUT \n".format(ind), file = f)
        else:
            process = multiprocessing.Process(target=hostprocess, args=(cmd,logDir,))
            processes.append(process)
            process.start()
            print("Process : {0} Started \n".format(ind), file = f)

    # Wait for all processes to complete
    for process in processes:
        process.join()
        print("Waiting for Process : {0} to complete \n".format(process), file = f)
    f.close()

def startTest(groupTLDict,testlineDict,cmdDict,logDir,hostname,time=0):
    global hostTestCmdList,sutTestCmdList
    # Update cmdDict only to Test , by removing those test steps in testlineDict
    testlineList = []
    cmdLinesList = []
    subList = ['PreTest','PostTest']
    # for (key1,value1),(key2,value2),(key3,value3) in zip(groupTLDict.items(),testlineDict.items(),cmdDict.items()):
    #     #print(" Key : {0} - Value : {1}".format(key,value))
    #     # IF testLine Dict, value Is Automated  & cmdDict , value is Test & Target ( SUT cmd) , Separate ( HOST cmd)
    #     for val in value1:
    #         if value2['IsAutomated'] == True and value3['Type'] == "Test" and value3['SystemRole'] == "Target" :
    #             print(" Group[{0}] , UniqueName [{1}], testlines[{2}]".format(key1,val,value2
    finalCmd=""
    #Update command Dict & TLDict by removing "Pre-Test" & "Post-test"
    cmdList_Pop = []
    _file=logDir+"\Tests_Mapping.txt"
    f=open(_file,"w")
    for key,value in list(cmdDict.items()):
        for sub in subList:
            if sub in value['Type']:
                cmdList_Pop.append(key)
                cmdDict.pop(key)
    #print(cmdList_Pop)
    # Delete Pre-test & Post test from Testline Dictionary
    print("testlineDict Before : ",testlineDict, file = f)
    for key,value in list(testlineDict.items()):
        for sub in cmdList_Pop:
            if sub in value['testlines']:
                value['testlines'].remove(sub)
    print("testlineDict After : ",testlineDict, file = f)
    for key1,value1 in groupTLDict.items():
        print("Group[{0}]\n********************************************\n".format(key1), file = f)
        for name in value1:
            if testlineDict[name]['IsAutomated'] == True :
                index = int(value1.index(name)) + 1
                print("\t{0}) Name[{1}] :\n ".format(index,name), file = f)
                testlineList = testlineDict[name]['testlines']
                if time == 0 :
                    time = str(testlineDict[name]['time'])
                print("testlineList",testlineList, file = f)
                for tl in testlineList:
                    finalCmd = str(cmdDict[tl]['command']);#print("Commad Before Updating time : ", finalCmd, file = f)
                    finalCmd = finalCmd.replace("@{TestLine.TestStageEstimatedTime}",str(time))
                    cmdLinesList.append(finalCmd)
                    #print("Commad After Updating time : ", finalCmd)
                    if cmdDict[tl]['SystemRole'] == "Target" :
                        print("\t\tSUT Command Name : {0} \n\t\tCommand Line : {1} \n".format(tl,finalCmd), file = f)
                        # RUN here tests in Parallel using SSH
                        sutTestCmdList.append(finalCmd)
                    else:
                        print("\t\tHOST Command Name : {1} \n\t\tCommand Line : {2} \n".format(tl,finalCmd), file = f)
                        # RUN tests here on Host
                        hostTestCmdList.append(finalCmd)
                # Run Tests on SUT & HOST
                multiThread(cmdLinesList,hostname,logDir)
        hostTestCmdList.clear()
        sutTestCmdList.clear()
    f.close()