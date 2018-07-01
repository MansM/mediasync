#!/usr/bin/env python3
from mediasync import Plex
from mediasync import Kodi
from mediasync import Settings
from mediasync.Logger import logger
from mediasync.poolmanager import poolmanager


import yaml, logging, base64

def main():

  settings = Settings()
  
  logger.configure(settings.logfile, settings.loglevel)
  logger.info("Log started")
  
  settings.initMedia()


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

  logger.debug("log end")

if __name__ == "__main__":
  main()


