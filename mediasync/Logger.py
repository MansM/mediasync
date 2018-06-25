import logging

__all__ = ["Logger"]

class Logger(object):
    

  def configure(self, logfile=None, loglevel='INFO'):
    logging.basicConfig(filename=logfile, format='%(asctime)s %(levelname)s %(message)s', level=int(getattr(logging, loglevel )))

    #TODO: support for log rotation

  def __enter__(self):
    return self

  def debug(self, message):
    logging.debug(message)

  def info(self, message):
    logging.info(message)

  def error(self, message):
    logging.error(message)

  def warning(self, message):
    logging.warning(message)

logger = Logger()