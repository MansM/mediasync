import sqlite3

class DB(object):
  def __init__(self):
    self.conn = sqlite3.connect('media.db')

  def __del__(self):
    self.conn.commit()
    self.conn.close()
    print ("database connection closed")

  def execute(self, query):
    c = self.conn.cursor()
    return c.execute(query)

  def commit(self):
    return self.conn.commit()
    
    

db = DB()