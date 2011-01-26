#!/usr/bin/python
# 
# install.py
# 
# Copyright (C) 2010 Antoine Mercadal <antoine.mercadal@inframonde.eu>
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
# 
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import os, sys, getopt
import threading, time
import ConfigParser
import uuid

MSG_ARCHIPEL_SERVER_HEADER = """\
###############################################################################
#                                                                             #
#                            Archipel Server                                  #
#                                                                             #
###############################################################################

Welcome to the installation script of ArchipelServer. 
Note that you must be root in order to install this software. Please answer the 
following questions.

"""


class Spinner(threading.Thread):
    
    def __init__(self, delay=0.2):
        threading.Thread.__init__(self);
        self.sequence = ["#   ", "##  ", "### ", "####", " ###", "  ##", "   #", "    " ];
        self.on = True;
        self.delay = delay
        self.start()
    
    
    def run(self):
        i = 0
        while self.on:
            sys.stdout.write("\033[33m [%s]\033[0m\r" % self.sequence[i])
            sys.stdout.flush()
            i += 1;
            if i >= len(self.sequence):
                i = 0;
            time.sleep(self.delay)
    
    
    def stop(self):
        self.on = False;
    



def ask(message, answers=None, default=None):
    question = " * " + message
    if answers and default:
        question += " ["
        for a in answers:
            a = a
            if default and a in (default): a = "\033[32m" + a + "\033[0m"
            question += a + "/"
        question = question[:-1]
        question += "]"
        
    if not answers and default:
        question += " [\033[32m" + default + "\033[0m]"
        
    question += " : "
    
    resp = raw_input(question)
    
    if default:
        if resp == "": resp = default;
    
    if answers and default:
        if not resp in answers and len(answers) > 0:
            resp = ask("\033[33mYou must select of the following answer\033[0m", answers, default);
    
    return resp


def ask_bool(message, default="y"):
    if ask(message, ["y", "n"], default) == "y":
        return True
    return False



### tests / init / Utils

def test_python_version():
    version = sys.version_info
    if not version[0] == 2 or (version[0] == 2 and not version[1] in (5,6,7)):
        print "\033[31m\n * ERROR: You need to use python 2.5 to 2.7 \033[0m\n"
        sys.exit(1)


def test_cmd(cmd):
    if os.system("which %s > /dev/null 2>&1" % cmd) != 0:
        return False
    return True


def test_cmd_or_die(cmd, warn=False):
    if not test_cmd(cmd):
        if not warn:
            print "\033[31m\n * ERROR: You need %s\033[0m\n" % cmd
            sys.exit(1)
        else:
            print "\033[33m   - WARNING: You'll need %s to use certains features.\033[0m" % cmd


def test_basic_cmds():
    test_cmd_or_die("git")
    test_cmd_or_die("cp")
    test_cmd_or_die("mkdir")
    test_cmd_or_die("mv")
    test_cmd_or_die("echo")
    test_cmd_or_die("chmod")
    test_cmd_or_die("chown")


def test_user_root():
    import getpass
    if not getpass.getuser() == "root":
        print "\033[31m\n * ERROR: You need to be root\033[0m\n"
        sys.exit(1)


def test_install_archipelserver():
    test_basic_cmds()
    test_cmd_or_die("openssl", warn=True)
    test_cmd_or_die("chkconfig", warn=True)


def clear():
    os.system("clear")




### install server

def install_archipelserver():
    clear()
    print MSG_ARCHIPEL_SERVER_HEADER
    
    print " Testing environment"
    test_install_archipelserver()
    print ""
    
    inst_eggs               = None
    inst_bin                = None
    inst_data               = None
    inst_init               = None
    inst_start              = None
    inst_conf               = None
    inst_cert               = None
    inst_configure          = None
    inst_working_folders    = None
    inst_log_folder         = None
    vm_working_folders      = { "drives":   "/vm/drives", 
                                "iso":      "/vm/iso", 
                                "repo":     "/vm/repo",
                                "tmp":      "/vm/tmp",
                                "vmcasts":  "/vm/vmcasts"}
    
    test_cmd_or_die("easy_install")
    inst_eggs = ask_bool("Would you like to install needed python eggs ?")
    
    
    if ask_bool("Would you like to install Archipel binary ?"):
        inst_bin    = ask("Where do you want to install ArchipelServer ?", None, "/usr/bin")
    
    if ask_bool("Would you like to install Archipel default configuration ?"):
        inst_conf   = ask("Where do you want to install configuration ?", None, "/etc/archipel")
    
    if ask_bool("Would you like to create Archipel data folder ?"):
        inst_data   = ask("Where do you want to ArchipelServer stores its datas ?", None, "/var/lib/archipel")
    
    if ask_bool("Would you like to create Archipel log folder ?"):
        inst_log_folder = ask("Where do you want to store the log files ?", None, "/var/log/archipel")
    
    if ask_bool("Would you like to configure Archipel working folders (store all virtualization info) ?"):
        inst_working_folders = True;
        vm_working_folders["drives"]   = ask("Where do you want to store drives ?", None, vm_working_folders["drives"])
        vm_working_folders["iso"]      = ask("Where do you want to shared isos ?", None, vm_working_folders["iso"])
        vm_working_folders["tmp"]      = ask("Where do you want to store tmp files ?", None, vm_working_folders["tmp"])
        vm_working_folders["repo"]     = ask("Where do you want to vmcasts repository ?", None, vm_working_folders["repo"])
        vm_working_folders["vmcasts"]  = ask("Where do you want to downloaded vmcasts ?", None, vm_working_folders["vmcasts"])
    
    if ask_bool("Would you like to install the init script ?"):
        inst_init   = ask("Where do you want to install init script ?", None, "/etc/init.d")
        if test_cmd("chkconfig"):
            inst_start  = ask_bool("Would you like to start archipel with the system ?")
    
    if test_cmd("openssl"):
        if inst_conf: 
            inst_cert = ask_bool("Would you like to generate the VNC certificates ?")
    
    inst_configure  = ask_bool("Would you like to configure Archipel server ?")
    
    
    print ""
    print " Installation information"
    if inst_eggs:               print "   - install eggs         : %s" % str(inst_eggs)
    if inst_bin:                print "   - binary folder        : %s" % inst_bin
    if inst_data:               print "   - data folder          : %s" % inst_data
    if inst_log_folder:         print "   - log folder           : %s" % inst_log_folder
    if inst_working_folders:    
        print "   - working folders      : "
        for name, folder in vm_working_folders.items():
            print "        - folder for %s: %s" % (name, folder)
    if inst_conf:               print "   - configuration folder : %s" % inst_conf
    if inst_init:               print "   - install init script  : %s" % inst_init
    if inst_start:              print "   - start with system    : %s" % inst_start
    if inst_configure:          print "   - configure            : %s" % str(inst_configure)
    print ""
    
    if not ask("Do you confirm ?", ["y", "n"], "y"):
        print " \033[33m* Installation canceled by user\033[0m"
        sys.exit(0)
    
    if inst_eggs:                   server_install_python_eggs()
    if inst_bin:                    server_install_binary(inst_bin)
    if inst_conf:                   server_install_conf_folder(inst_conf)
    if inst_data:                   server_install_data_folder(inst_data)
    if inst_log_folder:             server_install_log_folder(inst_log_folder)
    if inst_working_folders:        server_install_working_folders(vm_working_folders)
    if inst_init:                   server_install_init_script(inst_init)
    if inst_init and inst_start:    server_install_init_start()    
    if inst_cert:                   server_install_vnc_certificate(inst_conf)
    if inst_configure:              server_configure("./ArchipelServer/conf/archipel.conf.template", inst_bin, inst_data, inst_conf, vm_working_folders, inst_log_folder)
    
    print "\033[32m"
    print " Installation is now complete.\n"
    print "\033[0m"
    
    ask_bool("Continue ?")


def server_install_python_eggs():
    print " * Installing needed python eggs";
    test_cmd_or_die("svn")
    print "\n\033[35m*******************************************************************************"
    ret = os.system("easy_install xmpppy")
    if ret != 0:
        print "\033[31mUnable to get xmpppy egg\033[0m"
        sys.exit(1)
    ret = os.system("easy_install sqlobject")
    if ret != 0:
        print "\033[31mUnable to get sqlobject egg\033[0m"
        sys.exit(1)
    ret = os.system("easy_install apscheduler")
    if ret != 0:
        print "\033[31mUnable to get apscheduler egg\033[0m"
        sys.exit(1)
    print "*******************************************************************************\033[0m"
    print "\033[32m * Needed eggs installed\033[0m"


def server_install_binary(inst_bin):
    if not os.path.exists(inst_bin):
        print " - creating folder %s" % inst_bin
        s = Spinner()
        os.system("mkdir -p '%s'" % inst_bin)
        s.stop()
    
    print " - installation ArchipelServer binary to %s" % inst_bin
    s = Spinner()
    os.system("cp -a ./ArchipelServer '%s'" %  inst_bin)
    os.system("chmod -R 700 '%s/ArchipelServer'" %  inst_bin)
    os.system("chown root:root '%s/ArchipelServer'" % inst_bin)
    s.stop()


def server_install_conf_folder(inst_conf):
    if not os.path.exists(inst_conf):
        s = Spinner()
        print " - creating folder %s" % inst_conf
        os.system("mkdir -p '%s'" % inst_conf)
        s.stop()
    print " - installing configuration in %s" % inst_conf
    s = Spinner()
    os.system("cp -a ./ArchipelServer/conf/archipel.conf '%s'" % inst_conf)
    os.system("chmod -R 700 '%s'" % inst_conf)
    os.system("chown root:root '%s'" % inst_conf)
    s.stop()


def server_install_data_folder(inst_data):
    if not os.path.exists(inst_data):
       print " - creating folder %s" %  inst_data
       s = Spinner()
       os.system("mkdir -p '%s'" % inst_data)
       s.stop()


def server_install_log_folder(folder):
    if not os.path.exists(folder):
        print " - creating log folder  %s" % folder
        s = Spinner()
        os.system("mkdir -p '%s'" % folder)
        s.stop()


def server_install_working_folders(folders):
    for name, folder in folders.items():
        print " - creating working %s folder at %s" %  (name, folder)
        s = Spinner()
        os.system("mkdir -p '%s'" % folder)
        s.stop()


def server_install_init_script(inst_init):
    if not os.path.exists(inst_init):
        print " - creating folder  %s" % inst_init
        s = Spinner()
        os.system("mkdir -p '%s'" % inst_init)
        s.stop()
    print " - installing init script to  %s" % inst_init
    s = Spinner()
    os.system("cp -a ./ArchipelServer/archipel '%s'" % inst_init)
    os.system("chmod -R 700 '%s/archipel'" % inst_init)
    os.system("chown root:root '%s/archipel'" % inst_init)
    s.stop()


def server_install_init_start():
    print " - setting archipel to be started with system"
    s = Spinner()
    os.system("chkconfig --level 345 archipel on")
    s.stop()


def server_install_vnc_certificate(inst_conf):
    print " - generating the certificates for VNC"
    print "\n\033[35m*******************************************************************************"
    os.system("openssl req -new -x509 -days 365 -nodes -out '%s/vnc.pem' -keyout '%s/vnc.pem'" % (inst_conf, inst_conf))
    print "*******************************************************************************\033[0m"


def server_configure(confpath, general_exec_dir, general_var_dir, general_etc_dir, vm_working_folders, log_folder):
    os.system("cp %s %s.working" %  (confpath, confpath))
    conf = ConfigParser.ConfigParser()
    conf.readfp(open("%s.working" % confpath))
    configuration = [
                {"domain": "GLOBAL",                "key": "general_exec_dir",                          "name": "General execution directory",          "type": "text", "default": "%s/ArchipelServer" % general_exec_dir},
                {"domain": "GLOBAL",                "key": "machine_ip",                                "name": "Hypervisor IP",                        "type": "text", "default": "auto"},
                {"domain": "GLOBAL",                "key": "libvirt_uri",                               "name": "Libvirt URI",                          "type": "text", "default": "qemu:///system"},
                {"domain": "GLOBAL",                "key": "xmpp_pubsub_server",                        "name": "PubSub Server",                        "type": "text", "default": "pubsub.xmppserver"},
                {"domain": "GLOBAL",                "key": "archipel_root_admin",                       "name": "Archipel admin account",               "type": "text", "default": "admin@xmppserver"},
                {"domain": "MODULES",               "key": "hypervisor_health",                         "name": "Use module hypervisor health",         "type": "bool", "default": "y"},
                {"domain": "MODULES",               "key": "hypervisor_network",                        "name": "Use module hypervisor network",        "type": "bool", "default": "y"},
                {"domain": "MODULES",               "key": "vm_media_management",                       "name": "Use module media management",          "type": "bool", "default": "y"},
                {"domain": "MODULES",               "key": "geolocalization",                           "name": "Use module geolocalization",           "type": "bool", "default": "y"},
                {"domain": "MODULES",               "key": "vmcasting",                                 "name": "Use module VMCasting",                 "type": "bool", "default": "y"},
                {"domain": "MODULES",               "key": "snapshoting",                               "name": "Use module snapshoting",               "type": "bool", "default": "y"},
                {"domain": "MODULES",               "key": "oom_killer",                                "name": "Use module OOM",                       "type": "bool", "default": "y"},
                {"domain": "MODULES",               "key": "actions_scheduler",                         "name": "Use module scheduler",                 "type": "bool", "default": "y"},
                {"domain": "MODULES",               "key": "xmppserver",                                "name": "Use module XMPPServer",                "type": "bool", "default": "y"},
                {"domain": "MODULES",               "key": "iphone_appnotification",                    "name": "Use module iPhone Notification",       "type": "bool", "default": "n"},
                {"domain": "HYPERVISOR",            "key": "hypervisor_xmpp_jid",                       "name": "Hypervisor XMPP JID",                  "type": "text", "default": "hypervisor@xmppserver"},
                {"domain": "HYPERVISOR",            "key": "hypervisor_xmpp_password",                  "name": "Hypervisor XMPP password",             "type": "text", "default": "password"},
                {"domain": "HYPERVISOR",            "key": "hypervisor_name",                           "name": "Hypervisor name",                      "type": "text", "default": "auto"},
                {"domain": "HYPERVISOR",            "key": "hypervisor_database_path",                  "name": "Hypervisor database path",             "type": "text", "default": "%s/hypervisor.sqlite3" % general_var_dir},
                {"domain": "HYPERVISOR",            "key": "hypervisor_permissions_database_path",      "name": "Hypervisor permissions database path", "type": "text", "default": "%s/hypervisor-permissions.sqlite3" % general_var_dir},
                {"domain": "HYPERVISOR",            "key": "name_generation_file",                      "name": "path for virtual machine names list",  "type": "text", "default": "%s/ArchipelServer/names.txt" % general_exec_dir},
                {"domain": "VIRTUALMACHINE",        "key": "vm_base_path",                              "name": "Virtual machines base path",           "type": "text", "default": vm_working_folders["drives"]},
                {"domain": "VIRTUALMACHINE",        "key": "xmpp_password_size",                        "name": "Virtual machines XMPP password size",  "type": "text", "default": "32"},
                {"domain": "VIRTUALMACHINE",        "key": "vnc_certificate_file",                      "name": "Virtual machines VNC certificate",     "type": "text", "default": "%s/vnc.pem" % general_etc_dir},
                {"domain": "VIRTUALMACHINE",        "key": "vnc_only_ssl",                              "name": "Use only SSL connection for VNC",      "type": "bool", "default": "n"},
                {"domain": "LOGGING",               "key": "logging_level",                             "name": "Logging level",                        "type": "text", "default": "info"},
                {"domain": "LOGGING",               "key": "logging_file_path",                         "name": "Log file",                             "type": "text", "default": "%s/archipel.log" % log_folder},
                {"domain": "HEALTH",                "key": "health_database_path",                      "name": "Health database path",                 "type": "text", "default": "%s/health.sqlite3" % general_var_dir,                   "dep_module_key": "hypervisor_health"},
                {"domain": "HEALTH",                "key": "health_collection_interval",                "name": "Collection interval",                  "type": "text", "default": "5",                                                     "dep_module_key": "hypervisor_health"},
                {"domain": "HEALTH",                "key": "max_rows_before_purge",                     "name": "Max rows before purge",                "type": "text", "default": "50000",                                                 "dep_module_key": "hypervisor_health"},
                {"domain": "HEALTH",                "key": "max_cached_rows",                           "name": "Max cached rows",                      "type": "text", "default": "200",                                                   "dep_module_key": "hypervisor_health"},
                {"domain": "MEDIAS",                "key": "iso_base_path",                             "name": "Path of common ISO",                  "type": "text", "default": vm_working_folders["iso"],                                "dep_module_key": "vm_media_management"},
                {"domain": "GEOLOCALIZATION",       "key": "localization_mode",                         "name": "Geolocalization mode (manual/auto)",   "type": "text", "default": "auto",                                                  "dep_module_key": "geolocalization"},
                {"domain": "GEOLOCALIZATION",       "key": "localization_latitude",                     "name": "Latitude (manual mode)",               "type": "text", "default": "0.0",                                                   "dep_module_key": "geolocalization"},
                {"domain": "GEOLOCALIZATION",       "key": "localization_longitude",                    "name": "Longitude (manual mode)",              "type": "text", "default": "0.0",                                                   "dep_module_key": "geolocalization"},
                {"domain": "GEOLOCALIZATION",       "key": "localization_service_url",                  "name": "Service URL (auto mode)",              "type": "text", "default": "ipinfodb.com",                                          "dep_module_key": "geolocalization"},
                {"domain": "GEOLOCALIZATION",       "key": "localization_service_request",              "name": "Service request (auto mode)",          "type": "text", "default": "/ip_query.php",                                         "dep_module_key": "geolocalization"},
                {"domain": "GEOLOCALIZATION",       "key": "localization_service_method",               "name": "Service request method (auto mode)",   "type": "text", "default": "GET",                                                   "dep_module_key": "geolocalization"},
                {"domain": "GEOLOCALIZATION",       "key": "localization_service_response_root_node",   "name": "XML root node (auto mode)",            "type": "text", "default": "Response",                                              "dep_module_key": "geolocalization"},
                {"domain": "VMCASTING",             "key": "repository_path",                           "name": "Repo path",                            "type": "text", "default": vm_working_folders["repo"],                              "dep_module_key": "vmcasting"},
                {"domain": "VMCASTING",             "key": "temp_path",                                 "name": "Temp path",                            "type": "text", "default": vm_working_folders["tmp"],                               "dep_module_key": "vmcasting"},
                {"domain": "VMCASTING",             "key": "own_vmcast_name",                           "name": "Name",                                 "type": "text", "default": "Local VM Cast of $HOSTNAME",                            "dep_module_key": "vmcasting"},
                {"domain": "VMCASTING",             "key": "own_vmcast_description",                    "name": "Description",                          "type": "text", "default": "This is the vmcast feed of the hypervisor $HOSTNAME",   "dep_module_key": "vmcasting"},
                {"domain": "VMCASTING",             "key": "own_vmcast_uuid",                           "name": "UUID",                                 "type": "text", "default":  str(uuid.uuid1()),                                      "dep_module_key": "vmcasting"},
                {"domain": "VMCASTING",             "key": "own_vmcast_url",                            "name": "Public URL",                           "type": "text", "default":  "http://127.0.0.1/vmcasts/",                            "dep_module_key": "vmcasting"},
                {"domain": "VMCASTING",             "key": "own_vmcast_file_name",                      "name": "Index file",                           "type": "text", "default": "rss.xml",                                               "dep_module_key": "vmcasting"},
                {"domain": "VMCASTING",             "key": "own_vmcast_lang",                           "name": "Language",                             "type": "text", "default": "en-us",                                                 "dep_module_key": "vmcasting"},
                {"domain": "VMCASTING",             "key": "own_vmcast_path",                           "name": "Physical path",                        "type": "text", "default": vm_working_folders["vmcasts"],                           "dep_module_key": "vmcasting"},
                {"domain": "VMCASTING",             "key": "own_vmcast_refresh_interval",               "name": "Refresh interval",                     "type": "text", "default": "60",                                                    "dep_module_key": "vmcasting"},
                {"domain": "VMCASTING",             "key": "disks_extensions",                          "name": "Supported disks extensions",           "type": "text", "default": ".qcow2;.qcow;.img;.iso",                                "dep_module_key": "vmcasting"},
                {"domain": "VMCASTING",             "key": "vmcasting_database_path",                   "name": "Vmcasting database path",              "type": "text", "default": "%s/vmcasting.sqlite3" % general_var_dir,                "dep_module_key": "vmcasting"},
                {"domain": "IPHONENOTIFICATION",    "key": "credentials_key",                           "name": "PushApp Credentials",                  "type": "text", "default": "",                                                      "dep_module_key": "iphone_appnotification"},
                {"domain": "OOMKILLER",             "key": "database",                                  "name": "OOM database path",                    "type": "text", "default": "%s/oom.sqlite3" % general_var_dir,                      "dep_module_key": "oom_killer"},
                {"domain": "SCHEDULER",             "key": "database",                                  "name": "Scheduler database path",              "type": "text", "default": "%s/scheduler.sqlite3" % general_var_dir,                "dep_module_key": "actions_scheduler"},
                {"domain": "XMPPSERVER",            "key": "exec_path",                                 "name": "XMPP server control tool path",        "type": "text", "default": "/sbin/ejabberdctl",                                     "dep_module_key": "xmppserver"},
                {"domain": "XMPPSERVER",            "key": "exec_user",                                 "name": "XMPP server running user",             "type": "text", "default": "ejabberd",                                              "dep_module_key": "xmppserver"}]
    
    
    for token in configuration:
        if token.has_key("dep_module_key") and not conf.getboolean("MODULES", token["dep_module_key"]):
            continue
    
        if token["type"] == "bool":
            resp = ask_bool("[\033[33m%s\033[0m] %s" % (token["domain"], token["name"]), token["default"])
            conf.set(token["domain"], token["key"], str(resp))
        elif token["type"] == "text":
            resp = ask("[\033[33m%s\033[0m] %s" % (token["domain"], token["name"]), None, token["default"])
            conf.set(token["domain"], token["key"], resp)
    
    configfile = open("%s/archipel.conf" % general_etc_dir, "wb")
    conf.write(configfile)
    configfile.close()
    
    os.system("rm %s.working" % confpath)




### Main

def main():
    try:
        clear()
        
        print MSG_ARCHIPEL_SERVER_HEADER
        
        test_python_version()
        
        test_user_root()
                
        print " "
        
        confirm = ask("Do you confirm ?", ["y", "n"], "y")
        if confirm == "n":
            print " \033[33m* Installation canceled by user\033[0m"
            sys.exit(0)
        
        install_archipelserver()
        
        clear()
        print MSG_ARCHIPEL_END;
    except KeyboardInterrupt:
        print "\n\n\033[33m * Installation canceled by user\033[0m\n"




if __name__ == "__main__":
    main()




