import sys,os
import json
import logging as log
import socket
from collections import OrderedDict
import datetime

# -------------------- json files inout -------------------- 
def get_local_json():
    """fetches the config.json file in the local directory
       if config_hostname.json is found it is used over the default one
    """
    config = None
    dirname = os.path.dirname(sys.argv[0])
    config_file = "./config_"+socket.gethostname()+".json"
    #print(f"checking file '{config_file}'")
    if(os.path.isfile(config_file)):
        #print("loading: ",config_file)
        config = json.load(open(config_file))
    else:
        config_file = dirname+'/'+"config.json"
        if(os.path.isfile(config_file)):
            #print("loading: %s",config_file)
            config = json.load(open(config_file))
        else:
            log.error("Fatal error 'config.json' not found")
    return config

def save_json_timestamp(fileName,data):
    fileName = "./test_db/"+ fileName + datetime.datetime.now().strftime(' %Y.%m.%d %H-%M-%S')+".json"
    jfile = open(fileName, "w")
    jfile.write(json.dumps(data, indent=4))
    jfile.close()
    return fileName

def load_json(fileName):
    return json.load(open(fileName))

# -------------------- config -------------------- 
def get_local_nodes(nodes_file):
    nodes = json.load(open(nodes_file),object_pairs_hook=OrderedDict)
    return nodes

def configure_log(logger_name):
    global_config = get_local_json()
    config = global_config["log"]
    log_level_map = {
        "Debug"     :10,
        "Info"      :20,
        "Warning"   :30,
        "Error"     :40,
        "Critical"  :50
    }
    #if(os.path.isfile(config["logfile"])):
    logfile = config["logfile"].replace("(date)",datetime.datetime.now().strftime('-%Y.%m.%d'))
    for handler in log.root.handlers[:]:
        log.root.removeHandler(handler)
    log.basicConfig(    filename=logfile,
                        level=log_level_map[config["level"]],
                        format='%(asctime)s %(name)s %(levelname)-8s %(message)s',
                        datefmt='%d %H:%M:%S'
                        )
    log.getLogger('').addHandler(log.StreamHandler())
    log.debug(f"{logger_name} started at {str(datetime.datetime.utcnow())}")
    log.debug(f"logging in file '{logfile}' logs level {config['level']}")
    #else:
    #    print("Log file not available : %s"%(config["logfile"]))
    return global_config

