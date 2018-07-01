#!/usr/bin/env python3
from mediasync import Plex
from mediasync import Kodi
from mediasync import Settings
from mediasync.Logger import logger
#from mediasync.poolmanager import poolmanager


#import yaml, logging, base64

def main():

  settings = Settings()
  
  logger.configure(settings.logfile, settings.loglevel)
  settings.initMedia()
  
  logger.info("Log started")

  for plex in settings.plexes:
    plex.backupShows()
    plex.backupMovies()

  for kodi in settings.kodis:
    kodi.backupShows()
    kodi.backupMovies()

  for plex in settings.plexes:
    plex.restoreShows()
    plex.restoreMovies()

  for kodi in settings.kodis:
    kodi.restoreShows()
    kodi.restoreMovies()

  #poolmanager.http.headers["user"] = "kodi"
  # raw = bytes("%s:%s"%("kodi", str(1)), "UTF-8")
  # #print(raw)
  # auth = "Basic %s"  % base64.b64encode(raw).strip().decode("utf-8")
  # poolmanager.http.headers["Authorization"] = auth
  # r = poolmanager.request('POST', "http://10.0.1.53:8080/jsonrpc", body=None, headers={"Content-Type": "application/json", "Authorization": auth})

  # print(r.status)
  logger.debug("log end")
 
  # plex.restoreMovies()
  # plex.restoreShows()
  # kodi.restoreShows()


if __name__ == "__main__":
  main()


