import os
import ssh_auth as ssh

def isUnlocked():
    import namednodes as nn
    nn.sv.get_all()
    #Do unlock to load PCUDATA
    if itp.islocked() == True:
        itp.unlock()
        nn.sv.refresh()
    else:
        nn.sv.refresh()

def ltssmDump(LogDir):
    import pysvtools.pciedebug.ltssm as ltssm
    _file=LogDir+"/ltssmDump.txt"
    itp.log(_file)
    ltssm.sls()
    itp.nolog()

def memoryDIMMDump(LogDir):
    import graniterapids.mc.gnrDimmInfo as di
    _file=LogDir+"/dimminfo.txt"
    itp.log(_file)
    di.dimminfo()
    itp.nolog()

def regdumps(LogDir):
    import namednodes as nn
    nn.sv.get_all()
    _file=LogDir+"/allMCAErrors.txt"
    itp.log(_file)
    import graniterapids.ras.pysvtools.mca_tools.gnr_mca_tools as mca
    mca.get_all_mca_status_valid()
    
    import pysvtools.server_ip_debug as sip
    sip.cha.errors.show_mca_status()
    
    import pysvtools.server_ip_debug as sip
    sip.punit.errors.show_mca_status()
    
    import graniterapids.ras.ras_master.mca_master as mm
    mm.mca.mca_table()
    
    import graniterapids.core.debug as cd
    cd.mca_dump_gnr()
    itp.nolog()
    _file=LogDir+"/Ubox1st2ndError.txt"
    itp.log(_file)
    from pysvtools import server_ip_debug as sip
    import importlib
    importlib.reload(sip);
    sip.ubox.watch_windows.mca_error_source.show(source='reg')
    importlib.reload(sip);
    sip.ubox.watch_windows.ubox_quiesce_status.show(source='reg')
    itp.nolog()

def systemState(hostname,LogDir):
    logs=os.path.join(LogDir,"systemState")
    import ipccli
    itp = ipccli.baseaccess()
    os.mkdir(logs)
    #os.chdir(logs)
    isUnlocked()
    ltssmDump(logs)
    memoryDIMMDump(logs)
    ssh.ssh_run_os("svosinfo",hostname,"svosinfo",logs)
    ssh.ssh_run_os("svosdimminfo",hostname,"svosdimminfo",logs)
    ssh.ssh_run_os("cat /sv/memoryTargets",hostname,"memTargets",logs)
    ssh.ssh_run_os("racepointbeach -l",hostname,"racepointbeach",logs)
    regdumps(logs)

# if __name__ == "__main__":
#     pwd=os.getcwd()
#     isUnlocked()
#     ltssmDump(pwd)
#     memoryDIMMDump(pwd)