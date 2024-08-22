import paramiko
import os
import sys
from colorama import Fore
import subprocess
import serial
import time

# variable decleration 
port = 22
username = ""
password = ""
_hostname = "Dummy"

"""
Reference Systems
1. HY05WVAW0058 - SUT IP : 10.145.183.71
"""
# To assign username and password according to the OS

"""
def os_auth(logDir,OS) :
    global username,password
    _file=logDir+"/"+_hostname+"_demo.txt"
    _f = open(_file, 'w')
    if (OS == "svos" or OS == "SVOS"):
        username = "root"
        password = "svos"
        print("username -", username , file = _f)
        print("password -", password, file = _f)
        return True
    elif (OS == "fedora" or OS == "FEDORA"):
        username = "root"
        password = "password"
        print("username -", username)
        print("password -", password)
        return True
    else:
        print(Fore.RED + "Invalid OS name given...")
        return False
    _f.close()

def dsa_reg_dump(logDir) :
    _file=logDir+"/"+_hostname+"_demo.txt"
    try:
        #print("DSA-00 REG Dump")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(_hostname, port, username, password)
        #stdin, stdout, stderr = ssh.exec_command('cd /root/RDK_SVOS/;. nac.env;adf_ctl status')
        stdin, stdout, stderr = ssh.exec_command('cat /sv/dsa-00')
        outlines=stdout.readlines()
        #print(outlines)
        resp=''.join(outlines)
        f = open(_file, "a")
        f.write(resp)
        if "No such file or directory" in resp:
            print(Fore.YELLOW + "\n Warning - DSA-00 Cat command didnt execute")
            print(Fore.YELLOW + "\n Warning - command stdout - ", resp)
        else:
            print(Fore.GREEN +"\n DSA-00 Cat command executed - output - ",resp)        
        print("\n Closing ssh...")
    except:
        print(Fore.RED + "Oops!", sys.exc_info()[0], Fore.RED + "occurred.")
        print(Fore.RED + "Exiting the script execution...")
        sys.exit(0)
    f.close()
    ssh.close()
"""
def ssh_run_os(command,hostname,name,logDir) :
    _file=logDir+"/"+hostname+"_"+name+".txt"
    #os_auth(logDir,"svos")
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        print("\n Starting ssh...")
        ssh.connect(hostname, 22, "root", "svos")
        print("\n Connected to host : ",hostname)
        print("\n Command Parsed : {0} ".format(command))
        #resp = []
        # SINGLE COMMAND Execution
        f = open(_file, "w")
        stdin, stdout, stderr = ssh.exec_command(command)
        outlines=stdout.readlines()
        resp = ''.join(outlines) 
        f.write(resp)               
        if "No such file or directory" in resp:
            print(Fore.YELLOW + "\n Warning - command didnt execute")
            print(Fore.YELLOW + "\n Warning - command stdout - ", resp)
        else:
            print(Fore.GREEN +"\n Command executed - output - ",resp)        
        print("\n Closing ssh...")
    except:
        print(Fore.RED + "Oops!", sys.exc_info()[0], Fore.RED + "occurred.")
        print(Fore.RED + "Exiting the script execution...")
        sys.exit(0)
    f.close()
    ssh.close()

def getBMCPECIPort(hostname,peci):
    try:
        comportlist=[]
        print("opening ssh")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname,port,username, password)
        stdin, stdout, stderr = ssh.exec_command("ipmitool raw 0x30 0x5f 0x0 0x30 0x70 0x65 0x6e 0x42 0x6d 0x63 0x31")
        print("sucessfully ran ipmitool raw command")
        cmd="wmic path Win32_SerialPort Where '{}' Get DeviceID".format("Caption LIKE '%Standard%'")
        com=subprocess.run(cmd, stdout=subprocess.PIPE, universal_newlines=True)
        comportlist.append(com.stdout)
        for i in comportlist:
            i=i.replace('\n','')
            i = i.strip()
            print("wmic command output to get serial peci port - ", i)
            comport = i.split(" ")
            print("Serial PECI comport# after parsing - ", comport[-1])
        ser = serial.Serial(port=comport[-1],baudrate=115200,bytesize=8, timeout=2, stopbits=serial.STOPBITS_ONE)
        print("Debug ser output - ", ser)
        ser.write(b'root\r\n')
        response1=ser.read(1024).decode()
        print("username response - ", response1)
        ser.write(b'0penBmc1\r\n')
        response2=ser.read(1024).decode()
        print("password response - ", response2)
        #sleep(1000)

        for i in peci:
            ser.write(i)
            pecioutput=ser.read(1024).decode()
            print("******************************************************\n")
            print("Executing OOB Serial PECI cmd -  ", i)
            print("output of oob serial peci cmd- ",pecioutput)
            print("******************************************************\n")
            if('cc:0x90 0x00000000' in pecioutput or '0x82' in pecioutput):
                print("BMC:The registers are not accessed ")
                
            else:
                print("ERROR - The registers are accessible,unexpected")
                return False

    except:
        print("occurred - ", sys.exc_info()[0])
        return False
    finally:
        print("Closing serial connection")
        #ser.close()
        ssh.close()
    return True

# import serial.tools.list_ports as port_list^M
# ports = list(port_list.comports())^M
# for p in ports:^M
#     print (p)^M
#     if "Enhanced" in str(p):^M
#         comport = str(p)[:4]^M
# print("comport:",comport)
# COM4 - USB Serial Device (COM4)
# COM9 - Prolific USB-to-Serial Comm Port (COM9)
# COM3 - Intel(R) Active Management Technology - SOL (COM3)
# COM6 - Silicon Labs Dual CP2105 USB to UART Bridge: Standard COM Port (COM6)
# COM5 - Silicon Labs Dual CP2105 USB to UART Bridge: Enhanced COM Port (COM5)
# comport: COM5

def getSerialPorts():
    import serial.tools.list_ports as port_list
    ports = list(port_list.comports())
    for p in ports:
        print (p)
        if "Enhanced" in str(p):
            comport = str(p)[:4]
        if "Prolific" in str(p):
            bmcport = str(p)[:4]
    return comport,bmcport

def getSerialPort_wmicMethod():
    comportlist=[]
    cmd="wmic path Win32_SerialPort Where '{}' Get DeviceID".format("Caption LIKE '%Enhanced%'")
    com=subprocess.run(cmd, stdout=subprocess.PIPE, universal_newlines=True)
    comportlist.append(com.stdout)
    print(comportlist)
    for i in comportlist:
        i=i.replace('\n','')
        i = i.strip()
        print("wmic command output to get serial COM port - ", i)
        comport = i.split(" ")
        print("Serial PECI comport# after parsing - ", comport[-1])
    return comport[-1]

def rebootSUT(COMPort):
    COMPort.write(b'reboot\r\n')
    for i in range(1,7):
        time.sleep(60)
        print("System in Sleep for {0} secs".format(60 * i))
    response2 = "Dummy"
    while "root@" not in response2:
        print("Debug ser output - ", COMPort)
        COMPort.write(b'root\r\n')
        response1=COMPort.read(1024).decode()
        print("username response - ", response1)
        COMPort.write(b'svos\r\n')
        response2=COMPort.read(1024).decode()
        print("password response - ", response2)
        COMPort.write(b'svos\r\n')
        response2=COMPort.read(1024).decode()
        print("password response - ", response2)
    print("Successfully Rebooted Station")

def serialConnection(serial_Port,command=None,isReboot=0):
    ser = serial.Serial(port=serial_Port,baudrate=115200,bytesize=8, timeout=2, stopbits=serial.STOPBITS_ONE)
    time.sleep(1)
    print("\n opening serial connection...")
    time.sleep(1)
    print("Debug ser output - ", ser)
    ser.write(b'root\r\n')
    response1=ser.read(1024).decode()
    print("username response - ", response1)
    ser.write(b'svos\r\n')
    response2=ser.read(1024).decode()
    print("password response - ", response2)
    ser.write(b'svos\r\n')
    response2=ser.read(1024).decode()
    print("password response - ", response2)
    if isReboot == 1:
        rebootSUT(ser)
    if command != None:
        cmd = "b'" + command + "\r\n"
        ser.write(cmd)
        response1=ser.read(1024).decode()
