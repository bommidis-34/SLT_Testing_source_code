#!/usr/bin/env python

#BUILT IN MODULES IMPORT
import os
import random
import sys
import warnings
from collections import OrderedDict
from datetime import datetime
import pandas as pd
import time

#USER DEFINED MODULES IMPORT
import ssh_auth as ss
import biosGrubOvr as bb
import Pre_PostTest as pp
import SysStateLogger as sl

testSuiteDict = {}
testScenarioDict = {}
commandDict = {}
#scenario_test_dict = {}
logDir = None
inputFile=None

hostname="10.145.183.71"

"""
Full Algorithm:
1. Pre-test Commands Method ( SUT & HOST )
2. CUSTOM OS ARGS Method
3. BIOS KNOBS Method
4. TEST Method & Logging
5. POST TEST Method ( SUT & HOST)

Prorities:
P1 - PreTest                  - Complete 
P2 - Test & Logging           - ETA WW4.1
P3 - Post Test
P4 - CUSTOM OS/BIOS Knobs Override
"""

""" testScenarioDict ProtoType
testScenarioDict[count]
    Goal Name : List      -----------|
    Testline Name : List  -----------|---  From WB Sheet
    Cmd_dict:
        Type: Pretest/test    -----------|
        command:              ------------ FROM CMD Sheet
        list of commands
"""

def testSuiteDict_group_parser(inputFile,groups,order,logging):
    global testSuiteDict
# Load Columns From sheet_name1: B ( Testline Name) , M ( Goal Name) , S ( time) , Parameter.customOSArgs, Parameter.custombiosargs
    wb = pd.read_excel(inputFile,sheet_name=0)
    cmd = pd.read_excel(inputFile,sheet_name=1)
    goal=list(wb['Name'])
    print("goal initial List",goal)
    count=0
    testPerGroup=0
    #print("At loop {0} , len(goal) is {1} , order {2}".format(count,len(goal),order))
    while(len(goal) > 0):
        if count not in testSuiteDict.keys():
            testSuiteDict[count]=[]
        if len(goal) < groups:
            groups = len(goal)

        testPerGroup = int(len(goal)/groups)
        
        # Pick Testlines randomly(default)
        if order == 0 :
            for val in random.sample(goal,testPerGroup):
                #print("val",val)
                testSuiteDict[count].append(str(val))
                goal.remove(str(val))
        #Pick Testlines Sequence as per import Sheet
        else :
            for val in range(0,testPerGroup):
                #print("goal initial List",goal[0])
                testSuiteDict[count].append(goal[0])
                goal.pop(0)        
        count = count+1
        groups = groups-1 
        #print("At loop {0} , len(goal) is {1}".format(count,len(goal)))
        
    f=open(logging,"w")
    print("GROUPING FULL Test Lines to Individual Groups:" , file = f)
    print("**********************************************", file = f)
    for i in testSuiteDict.keys():
        print(" Group [",i,"] ", testSuiteDict[i], "\n" , file = f)
    f.close()

#Column AN : Index 39 , is where TestLine1 starts and check till Index != Parameter.customargs

"""
 Load Columns From sheet_name1: Current Fields of Interest
 Name    ConfigName    SoftwareConfig    AllowAutomationFlg    GoalName    TestStageEstimatedTime    
 TestStep#1    TestStep#2    ...    TestStep#n    Parameter.customargs    Parameter.custombiosargs
"""

def testScenarioDict_parser(inputFile,logging):
    global testScenarioDict
    wb = pd.read_excel(inputFile,sheet_name=0)
    Testline_StartIndex=39;iterate_TS=0
    for index,row in wb.iterrows():
        Name=row['Name']
        if Name not in testScenarioDict.keys():
            testScenarioDict[Name]={'GoalName':None,'time':None,'Hwcfg':None,'IsAutomated':None,'testlines':[]}
        testScenarioDict[Name]['GoalName']=row['GoalName']
        testScenarioDict[Name]['time']=row['TestStageEstimatedTime']
        testScenarioDict[Name]['Hwcfg']=row['ConfigName']
        testScenarioDict[Name]['IsAutomated']=row['AllowAutomationFlg']
        iterate_TS=Testline_StartIndex
        while( row.index[iterate_TS] != 'Parameter.customargs'):
            testScenarioDict[Name]['testlines'].append(row.values[iterate_TS])
            iterate_TS+=1
# Remove NAN from the list of teststeps
        testScenarioDict[Name]['testlines']=[x for x in testScenarioDict[Name]['testlines'] if str(x) != 'nan']
# Print the names of the columns.
#    for name in testScenarioDict.keys():
#    for key, value in testScenarioDict[Name].items():
#        print("key,value",key,value,value[key])
#        name, time, hwcfg , auto , testline = value
#        print("{:<10} {:<10} {:<10} {:<10} {:<10}".format(name, time, hwcfg , auto , testline))
#
    f=open(logging,"a")
    print("{:<20} {:<50} {:<10} {:<10} {:<10} {:<10}".format('UNIQUENAME', 'GOALNAME', 'TIME', 'HWCONFIG', 'ISAUTOMATED' , 'TESTLINES'), file = f)
    print("Converting Testlines to a Scenario Dictionary" , file = f)
    print("**********************************************" , file = f)
    for i in testScenarioDict.keys():
        print(" Testline [",i,"] ", testScenarioDict[i], "\n", file = f)
    f.close()


"""
 Columns of Interest , Sample Example
Name                  Type    SystemRole    Command
pcie_WA_forRHF        PreTest    Target        regx /sv/*-*/global.mstr_ctl[11]=1; regx /sv/*-*/global.uncorr_err_sts=0xffffffff; regx /sv/*-*/global.corr_err_sts=0xffffffff;regx /sv/*-*/global.reg_cpltoreg_type=0xBEBC22;
Umount_Mount_old    PreTest    Target        umountsv;mountsv;killmax
for index, row in df.iterrows():
# you can take data as row[COLUMN_NAME], then append it to data like data.append({'column': row[column})
return data
"""

def commandDict_parser(inputFile,logging):
    global commandDict
    cmd = pd.read_excel(inputFile,sheet_name=1)
    for index,row in cmd.iterrows():
        #print("Index , row , Index.row", index , row.index)
        Name=row['Name']
        if Name not in commandDict.keys():
            commandDict[Name]={'Type':None,'SystemRole':None,'command':None}
        #commandDict[index]['Name']=row['Name']
        commandDict[Name]['Type']=row['Type']
        commandDict[Name]['SystemRole']=row['SystemRole']
        commandDict[Name]['command']=row['Command']
        #print(index,"Entered")
    f=open(logging,"a")
    print("Converting TestSteps to a Commands Dictionary" , file = f)
    print("**********************************************" , file = f)
    for i in commandDict.keys():
        print(" TestStep [",i,"] ", commandDict[i], "\n" , file = f)
    f.close()
    return commandDict

   
# CREATE A DICT
# testSuiteDict : Contains Group & TL'sample
# testScenarioDict : TL & it's associated Test Steps
# commandDict : Contains Test steps Command-line


# Algorithm:
# 1. Create a Run folder with Time_Date
# 2. Start Iterating over len of Groups & Create Individual Folders for Each Group
# 3. Iterate over Individual TL's & Create Folders for Each
# 
# Goal 1 : Create Folders as per Above - Done
def scenario_test_cmd_parser(dict,logdir):
    for i in dict.keys():
        print(" Group [",i,"] ", testSuiteDict[i], "\n")
        folder=os.path.join(logdir,f"Group_{i}")
        os.mkdir(folder)
        for k in testSuiteDict[i]:
            subF=os.path.join(folder,k)
            os.mkdir(subF)
            
def help():
    print("\n\n\t Hi! How may I help you!")
    print("\t This Parser has 3 Command Line arguments")
    print("\t Arg 1 : INPUT NGA import sheet .xlsx with list of TestLines & Test Steps")
    print("\t Arg 2 : Integer Value 'm' --> Grouping All TL's to 'm' Separate Groups with 'n' TL's in Each Group")
    print("\t Arg 3 : TestOrder : 0 - Pick Testlines randomly(default) , 1 - Pick Testlines Sequence as per import Sheet")
    print("\t Reference : python <parser>.py <NGAImportSheet>.xlsx <n> <order>")
    print("\n \t Example : \n \t\t python systemLevelTest.py test.xlsx 5 0 ( This is Create 5 groups with random testlines]")
    print("\n \t\t python systemLevelTest.py test.xlsx 5 1 [ This is Create 5 groups with testlines pciked in sequence] \n \n")
    sys.exit(0)


def arguments():
    global inputFile,groups,order
    if (len(sys.argv) < 4):
        help()
    if (sys.argv[1] == '-h' or sys.argv[1] == '--help'):
        help()
    if (sys.argv[1] == '-h' or sys.argv[1] == '--help'):
        help()

    inputFile=sys.argv[1]
    # Pass Value for No of testScenarioDicts to pick in a groups and remove those from the dictonary
    groups=int(sys.argv[2])
    if int(sys.argv[3]) > 1 :
        order=1
    elif int(sys.argv[3]) < 0 :
        order=0
    else:
        order=int(sys.argv[3])

def logDirectory():
    pwd=os.getcwd()
    print("PWD",pwd)
    now = datetime.now()    
    current_time = now.strftime("%Y%m%d_%H_%M_%S")
    logDir = os.path.join(pwd,"Logs")
    print("logDir:",logDir)
#os.path.isdir is returning negate value so logging in negate way
    if os.path.isdir(logDir):
#        os.mkdir(logDir)
#        print("CREATED LOGS logDir:",logDir)
        logDir = os.path.join(logDir,f"SLT_{current_time}")
        os.mkdir(logDir)
        print("CREATED SLT Time folder logDir:",logDir)
    else:
        os.mkdir(logDir)
        print("CREATED LOGS logDir:",logDir)
        logDir = os.path.join(logDir,f"SLT_{current_time}")
        os.mkdir(logDir)
        print("CREATED SLT Time folder logDir:",logDir)
    return logDir


if __name__ == "__main__":
    warnings.filterwarnings("ignore", category=UserWarning)
    arguments()
    logDir = logDirectory()
    logs = logDir + "/Full_logs.txt"
#
#STEP 1
#Goal        : Grouping All TL's to "m" Separate Groups with "n" TL's in Each Group
#Description : Total m Groups x n TL's in each Group = Total No of TL's ( as per input XML)
#Algorithm   : 1. Picked Random TL's from Total TL's ; 2 . Each Group contains Unique TL's
#
    testSuiteDict_group_parser(inputFile,groups,order,logs)
    testScenarioDict_parser(inputFile,logs)
    commandDictionary=commandDict_parser(inputFile,logs)

    # BIOS OVERRIDE , OS OVERRIDE Command Generator
    biosOVR,osOVR=bb.biosOSGrubOverride(inputFile,logDir)
    time.sleep(1)
    print("osOVR: \n",osOVR)
    # RUN Above commands on SUT
    ss.ssh_run_os(biosOVR,hostname,"biosOVR",logDir)
    time.sleep(1)

    ss.ssh_run_os(osOVR,hostname,"osOVR",logDir)
    #ss.ssh_run_os("echo 'update-grub';update-grub;sleep 1",hostname,"update-grub",logDir)
    time.sleep(1)

    # REBOOT THE STATION AND do system Checker
    ss.serialConnection("COM4",isReboot=1)
    
    # INITIAL System Logger
    sl.systemState(hostname,logDir)

    # PRE-TEST , POST-TEST Command Generator
    targetCmd,HostCmd=pp.allPrePostTests('PreTest',commandDictionary,logDir)

    # RUN Above commands on SUT
    ss.ssh_run_os(targetCmd,hostname,"PreTestTargetCmd",logDir)
    time.sleep(1)

    #FOLDER HIERARCHY
    scenario_test_cmd_parser(testSuiteDict,logDir)
    
    # TEST EXECUTION - USING SSH CLIENT
    sys.exit(0)