import os
import logging.config
import yaml
import datetime

def setupLog(
      serviceName=None,
      default_path='./utils/config.yml',
      default_level=logging.INFO,
      env_key='LOG_CFG'
    ):
    # setup logging profile
    path = default_path
    value = os.getenv(env_key, None)
    if value:
         path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            #config = json.load(f)
            config = yaml.load(f, Loader=yaml.FullLoader)
        logcfg = config["LOGGING"]
        if (serviceName):
            svcName = os.path.splitext(os.path.basename(serviceName))[0]
            # print(" update base on service ")
            filename = "logs/" + svcName + datetime.datetime.now().strftime('-%Y%m%d.log')
            config["LOGGING"]["handlers"]["fileoutrotate"]["filename"] = filename
        logging.config.dictConfig(logcfg)
    else:
        logging.basicConfig(level=default_level)

    # print(" end setup logger")

def getLogger(serviceName=None,
      default_path='./utils/config.yml',
      default_level=logging.INFO,
      env_key='LOG_CFG'):
    path = default_path
    value = os.getenv(env_key, None)
    if value:
         path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            
            config = yaml.load(f, Loader=yaml.FullLoader)
            svcName = os.path.splitext(os.path.basename(serviceName))[0]
            logging.basicConfig(format=config["LOGGING"]["formatters"]["outfile"]["format"], filename = "logs/" + svcName + datetime.datetime.now().strftime('-%Y%m%d.log'), encoding=None, level=logging.DEBUG)
            consoleHandler = logging.StreamHandler()
            consoleHandler.setFormatter(logging.Formatter(config["LOGGING"]["formatters"]["stdout1"]["format"]))
            logging.getLogger().addHandler(consoleHandler)
            return logging

