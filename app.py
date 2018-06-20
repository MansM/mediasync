#!/usr/bin/env python3
import xml.etree.ElementTree as etree
import urllib3, re, sqlite3, os
from mediasync import Plex
from pprint import pprint
from inspect import getmembers

def main():
  plex = Plex()
  plex.backupShows()

if __name__ == "__main__":
  main()


