import yaml, logging
from mediasync import Kodi
from mediasync import Plex

__all__ = ['Settings']

class Settings():

  def __init__(self):
    self.plexes, self.kodis = [], []
    try:
      settingsfile = open("settings.yaml", 'r').read()
    except:
      exit("No Settings file available")
    
    self.settings = yaml.safe_load(settingsfile)

    try: self.loglevel = self.settings["log"]["level"]
    except: self.loglevel = "INFO"

    try: self.logfile = self.settings["log"]["file"]
    except: self.logfile = "output.log"


  def initMedia(self):
    try:
      for plexinstance in self.settings["plex"]:
        self.plexes.append(Plex(plexinstance["location"], plexinstance["token"]))
        #logging.info("Added plex instance: " + plexinstance["location"])
    except: pass

    try:
      for kodiinstance in self.settings["kodi"]:
        if "username" in kodiinstance and "password" in kodiinstance:
          self.kodis.append(Kodi(kodiinstance["location"], kodiinstance["username"], kodiinstance["password"]))
        else: self.kodis.append(Kodi(kodiinstance["location"]))
    except Exception as e: 
      print("blah" + str(e))
      pass

    

settings = Settings()