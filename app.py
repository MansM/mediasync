#!/usr/bin/env python3
from mediasync import Plex
from mediasync import Kodi
import yaml, logging

def main():

  settingsfile = open("settings.yaml", 'r').read()
  settings = yaml.safe_load(settingsfile)

  try: loglevel = settings["log"]["level"]
  except: loglevel = "INFO"
  
  logging.basicConfig(filename=settings["log"]["file"], format='%(asctime)s %(message)s', level=int(getattr(logging, loglevel )))
  logging.info("Log started")
  logging.debug("first debug")

  plexes, kodis = [], []

  for plexinstance in settings["plex"]:
    plexes.append(Plex(plexinstance["location"], plexinstance["token"]))

  for kodiinstance in settings["kodi"]:
    kodis.append(Kodi(kodiinstance["location"]))

  for plex in plexes:
    plex.backupShows()

  for kodi in kodis:
    kodi.backupShows()

  logging.debug("log end")
  # plex = Plex()
  # kodi = Kodi()

  # plex.backupShows()
  # kodi.backupShows()
 
  # # plex.restoreMovies()
  # plex.restoreShows()
  # kodi.restoreShows()
  # print(kodi.getShowid_byTVDBID("328687"))
  # regex = r"thetvdb://(?P<id>\d+)/(?P<season>\d+)/(?P<episode>\d+)"
  # results = re.search(regex, "thetvdb://328687/1/9")
  # print(results.group("id"))  
  # for group in results.groups():
  #   print(group)

if __name__ == "__main__":
  main()


