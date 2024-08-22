import os
import ssh_auth as ss

osOVR='echo -e "mem=svos@100000M\\npcie_ports=compat" >> /etc/svos/params.d/35_xpressos && sleep 2 && update-grub'
osGrub=["sed -i -e '/mem=svos@100000M/d' -e '/pcie_ports=compat/d' /etc/svos/params.d/35_xpressos", "echo -e 'mem=svos@100000M\\npcie_ports=compat' >> /etc/svos/params.d/35_xpressos", 'sleep 1;update-grub']
pwd=os.getcwd()
hostname="10.145.183.71"
#ss.ssh_run_os(osOVR,hostname,"osOVR",pwd)
ss.ssh_run_os(" apt install dos2unix  --fix-missing;dos2unix /usr/local/python/graniterapids/pm/pmx/content/cpu_rapl.py",hostname,"unix",pwd)
