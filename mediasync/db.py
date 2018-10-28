import sqlite3, logging, atexit, os

class DB(object):
  def __init__(self):
    dbloc = os.environ.get('MEDIASYNC_DBLOC', "media.db")
    self.conn = sqlite3.connect(dbloc)
    self.execute("CREATE TABLE IF NOT EXISTS media (id text, UNIQUE (id));")
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