# required imports and code exection for basic functionning

import sys
if 'threading' in sys.modules:
    raise Exception('threading module loaded before patching!')
import conf
import logging

if not (conf.WEBSERVER_DEBUG or conf.ON_HEROKU):
    import gevent.monkey
    gevent.monkey.patch_thread()




def set_logging(log_path, log_level=logging.INFO,
                log_format='%(asctime)s %(levelname)s %(message)s'):
    logger = logging.getLogger('pyaggr3g470r')
    formater = logging.Formatter(log_format)
    handler = logging.FileHandler(log_path)
    handler.setFormatter(formater)
    logger.addHandler(handler)
    logger.setLevel(log_level)

set_logging(conf.LOG_PATH)
