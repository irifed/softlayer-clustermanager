#!/usr/bin/env python

import shutil
from random import randint
import sys
import subprocess
import os
from asyncproc import Process

def runProcess(command):
    myProc = Process(command)
    while True:
        
        # print any new output
        out,err = myProc.readboth()
        if out != "":
            print out
        if err != "":
            print err
        
        # check to see if process has ended
        poll = myProc.wait(os.WNOHANG)
        if poll != None and out =='':
            break


        if "master: SSH address:" in out:
            masterip = out.strip().split(" ")[3]
            print "MASTER IP IS: " + masterip
    
    # print myProc.__exitstatus
    
    return masterip



#stolen from http://stackoverflow.com/questions/4417546/constantly-print-subprocess-output-while-process-is-running
# def runProcess(command):
#     process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
# 
#     # Poll process for new output until finished
#     while True:
#         nextline = process.stdout.readline()
# #         err = process.stderr.
#         if nextline == '' and process.poll() != None:
#             break
#         masterip = None
#         if "master: SSH address:" in nextline:
#             masterip = nextline.strip().split(" ")[3]
#             print "MASTER IP IS: " + masterip
#         sys.stdout.write(nextline)
#         sys.stdout.flush()
#         print "test"
# 
#     output = process.communicate()[0]
#     exitCode = process.returncode
# 
#     if (exitCode == 0):
#         return masterip
#     else:
#         print "EREOREOREOREOREO"


if __name__ == "__main__":
    
    #anewman 3895933cc65d8099c71e48a6357b7b6ba5b5668b85e1ef5f253dd6415cdf2d05 alanbaresj /home/a/Desktop/key/id_rsa hi.com wdc01 2
    
    if len(sys.argv) != 8 or sys.argv[1] == "-h":
        print "usage: <sl_username> <sl_api_key> <sl_ssh_key> <sl_private_key_path> <custom_domain> <sl_datacenter> <numworkers>"
        sys.exit(0)
        
#     print sys.argv[1]
    
    
    
    
    #set location of vagrant-cluster repo
    #cleanrepo = "/home/a/Desktop/irinastuff/cleanrepo/vagrant-cluster"
    cleanrepo = "/Users/irina/tmp/vagrant-cluster"
    
    
    #set location of directory where all vagrant folders will be saved
    #vagrantroot = "/home/a/Desktop/workspace/marketplace_stuff/vagrantdir"
    vagrantroot = "/Users/irina/tmp/vagrantdir"
    
    randomnum = randint(0,sys.maxint) 
    curdir =vagrantroot + str(randomnum)
    
    shutil.copytree(cleanrepo, curdir, symlinks=False, ignore=None)
    
    
# # SoftLayer API credentials
# sl_username: "EDIT HERE"
# sl_api_key: "EDIT HERE"
# sl_ssh_key: "EDIT HERE"
# sl_private_key_path: "EDIT HERE"
# 
# # custom domain
# sl_domain: "example.com"
# 
# # datacenter where virtual servers should be provisioned
# # datacenter = [ams01,dal01,dal05,dal06,hkg02,lon02,sea01,sjc01,sng01,wdc01]
# sl_datacenter: "sjc01"
# 
# # virtual server parameters for BDAS cluster
# # cpus = [1,2,4,8,12,16]
# # memory = [1024,2048,4096,6144,8192,12288,16384,32768,49152,65536]
# cpus: 4
# memory: 16384
# disk_capacity: 100
# network_speed: 1000

    print sys.argv


    configname = "sl_config.yml"
    
    cpus = str(4)
    memory = str(16384)
    disk_capacity = str(100)
    network_speed = str(1000)
    
    f = open(curdir + "/" + configname, 'wb')
    f.write("# SoftLayer API credentials\n")
    f.write('sl_username: "' + sys.argv[1] + '"\n')
    f.write('sl_api_key: "' + sys.argv[2] + '"\n')
    f.write('sl_ssh_key: "' + sys.argv[3] + '"\n')
    f.write('sl_private_key_path: "' + sys.argv[4] + '"\n')
    f.write("\n")
    f.write("# custom domain\n")
    f.write('sl_domain: "' + sys.argv[5] + '"\n')
    f.write("\n")
    f.write("# datacenter where virtual servers should be provisioned\n")
    f.write("# datacenter = [ams01,dal01,dal05,dal06,hkg02,lon02,sea01,sjc01,sng01,wdc01]\n")
    f.write('sl_datacenter: "' + sys.argv[6] + '"\n')
    f.write("\n")
    f.write("# virtual server parameters for BDAS cluster\n")    
    f.write("# cpus = [1,2,4,8,12,16]\n")  
    f.write("# memory = [1024,2048,4096,6144,8192,12288,16384,32768,49152,65536]\n")  
    f.write("\n")
    f.write('cpus: ' + cpus + '\n')
    f.write('memory: ' + memory + '\n')    
    f.write('disk_capacity: ' + disk_capacity + '\n')    
    f.write('network_speed: ' + network_speed + '\n')   
    
    f.close()
    
    numworkers = sys.argv[7]
    #NUM_WORKERS=3 vagrant up --provider=softlayer --no-provision && PROVIDER=softlayer vagrant provision
    #NUM_WORKERS=1 vagrant up --provider=softlayer --no-provision && PROVIDER=softlayer vagrant provision
    runcommand = "NUM_WORKERS=" + numworkers +" vagrant up --provider=softlayer --no-provision && PROVIDER=softlayer vagrant provision"
    
    os.chdir(curdir)
    print "current directory is: " + curdir
    masterip = runProcess(runcommand)
#     masterip = runProcess("kdslfj")
    
    if masterip == None:
        print "uh oh master ip == none"
    else:
        print "masterip: " + masterip
      
    #before beginning, make sure vagrant and ruby are installed and updated
    #need to respond with to keep track of: curdir, ip address of master (respond with ip address of master, so user can ssh in)
    
    
