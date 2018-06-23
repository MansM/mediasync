#!/usr/bin/env python3
from mediasync import Plex
from mediasync import Kodi
import re

def main():
  plex = Plex()
  kodi = Kodi()

  plex.backupShows()
  kodi.backupShows()
 
  # plex.restoreMovies()
  plex.restoreShows()
  kodi.restoreShows()
  # print(kodi.getShowid_byTVDBID("328687"))
  # regex = r"thetvdb://(?P<id>\d+)/(?P<season>\d+)/(?P<episode>\d+)"
  # results = re.search(regex, "thetvdb://328687/1/9")
  # print(results.group("id"))  
  # for group in results.groups():
  #   print(group)

if __name__ == "__main__":
  main()


