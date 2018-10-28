import urllib3,logging, atexit
from .Logger import logger


class PoolManager(object):
  def __init__(self):
    self.http = urllib3.PoolManager(maxsize=10)
    self.counter=0
    atexit.register(self.cleanup)

  def cleanup(self):
    logger.debug("PoolManager closed, httpcounter: " + str(self.counter))

  def request(self, method, url, body=None, headers=None):
    self.counter+=1
    return self.http.request(method, url, body=body, headers=headers)    

poolmanager = PoolManager()