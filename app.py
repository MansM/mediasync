#!/usr/bin/env python3
from mediasync import Plex
from mediasync import Kodi

def main():
  plex = Plex()
  #plex.restoreShows()
  plex.restoreMovies()
  # kodi = Kodi()
  # kodi.backupShows()

if __name__ == "__main__":
  main()


