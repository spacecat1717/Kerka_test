import logging
import logging.config

class LoggingSettings():
    logging.config.fileConfig(fname='log.conf')
    logger_info = logging.getLogger('info')
    logger_crit = logging.getLogger('critical')
    logger_warn = logging.getLogger('warning')
    logger_error = logging.getLogger('error')