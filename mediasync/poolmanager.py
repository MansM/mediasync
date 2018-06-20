import urllib3

class PoolManager(object):
  def __init__(self):
    self.http = urllib3.PoolManager()

  def __del__(self):
    print ("PoolManager closed")

  def request(self, method, url, headers=None):
    return self.http.request(method, url, headers=headers)    

poolmanager = PoolManager()