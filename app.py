#!/usr/bin/env python3
from mediasync import Plex
from mediasync import Kodi
from mediasync import Settings
from mediasync.Logger import logger

import yaml, logging

def main():

  settings = Settings()
  
  logger.configure(settings.logfile, settings.loglevel)
  settings.initMedia()
  
  logger.info("Log started")

  for plex in settings.plexes:
    plex.backupShows()

  for kodi in settings.kodis:
    kodi.backupShows()
    kodi.backupMovies()

  for plex in settings.plexes:
    plex.restoreShows()
    plex.restoreMovies()

  for kodi in settings.kodis:
    kodi.restoreShows()

  

  logger.debug("log end")
 
  # plex.restoreMovies()
  # plex.restoreShows()
  # kodi.restoreShows()


if __name__ == "__main__":
  main()


