import urllib3

class PoolManager(object):
  def __init__(self):
    self.http = urllib3.PoolManager()

  def __del__(self):
    print ("PoolManager closed")

  def request(self, method, url, body=None, headers=None):
    return self.http.request(method, url, body=body, headers=headers)    

poolmanager = PoolManager()