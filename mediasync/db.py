import sqlite3, logging, atexit

class DB(object):
  def __init__(self):
    self.conn = sqlite3.connect('media.db')
    atexit.register(self.cleanup)

  # def __del__(self):
    

  def cleanup(self):
    self.conn.commit()
    self.conn.close()
    logging.info("database connection closed")

  def execute(self, query):
    c = self.conn.cursor()
    return c.execute(query)

  def commit(self):
    return self.conn.commit()
    
    

db = DB()