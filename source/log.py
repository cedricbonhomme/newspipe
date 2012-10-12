# -*- coding: utf-8 -*-


class Log(object):
    """
    """
    def __init__(self):
        """
        """
        import logging
        self.logger = logging.getLogger("pyaggr3g470r")
        hdlr = logging.FileHandler('./var/access.log')
        formater = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        hdlr.setFormatter(formater)
        self.logger.addHandler(hdlr)
        self.logger.setLevel(logging.INFO)

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.warning(message)

    def critical(self, message):
        self.logger.critical(message)