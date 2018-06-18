import xml.etree.ElementTree as etree
import urllib3, re, sqlite3, os
from pprint import pprint
from inspect import getmembers

def retrieveChild(parent):
  url = plexlocation + parent.get('key')
  get = http.request('GET', url,  headers={'X-Plex-Token': plextoken})
  return etree.fromstring(get._body.decode("utf8"))

def retrieveSection(id):
  url = plexlocation + "/library/sections/" + str(id) + "/all"
  req = http.request('GET', url,  headers={'X-Plex-Token': plextoken})
  content = req._body.decode("utf8")
  return etree.fromstring(content)

def backupShows():
  print("TV SHOWS #################################################################################################################")
  print('{0:50} | {1:10} | {2:30}'.format("Name:", "Season:", "Episodes:"))
  
  ## retrieve shows
  global conn
  root = retrieveSection(plexshowsection)

  for show in root.iter('Directory'):
    title = show.get('title')
    seasonroot = retrieveChild(show)

    for season in seasonroot.iter('Directory'):
      if season.get("title") != "All episodes":
        episoderoot = retrieveChild(season)
        episodes = ""
        for episode in episoderoot.iter('Video'):     
          vc = episode.get('viewCount') or 0
          if vc:
            metaroot = retrieveChild(episode)
            meta = metaroot.find('./Video')
            regex = r"thetvdb://\d+/\d+/\d+"
            results = re.search(regex, meta.get('guid'))
            if results != None: 
              episodes += str(results.group(0)) + ","
              c.execute("INSERT OR IGNORE INTO media(id) VALUES('%s')" % str(results.group(0)))
        episodes = episodes.rstrip(",")
        conn.commit()
        if episodes != "": 
          print('{0:50} | {1:10} | {2:30}'.format(title, season.get('title'), episodes))

def backupMovies():
  print("MOVIES ###################################################################################################################")
  print('{0:50} | {1:10} | {2:30}'.format("Name:", "Watched:", "IMDB ID:"))

  ## retrieve movies
  root = retrieveSection(plexmoviesection)
  root.findall("./Video")

  for video in root.iter('Video'):
    title = video.get('title')
    vc = video.get('viewCount') or 0
    if (vc):
        metaroot = retrieveChild(video)
        meta = metaroot.find('./Video')
        regex = r"imdb://tt\d+"
        results = re.search(regex, meta.get('guid'))
        if results != None: 
          print('{0:50} | {1:10} | {2:30}'.format(title, str(vc), results.group(0)))
          c.execute("INSERT OR IGNORE INTO media(id) VALUES('%s')" % str(results.group(0)))
          conn.commit()


def main():
  global conn, c, plexlocation, plextoken, plexmoviesection, plexshowsection, http
  #TODO: find a better way then to use globals

  ## Laptop without connection, abuse vagrant to generate a network with IP
  plexlocation = os.environ['PLEXLOCATION']

  plextoken = os.environ['PLEXTOKEN']

  # at shield movies = 6, at laptop 1
  # shows at shield = 7. at laptop 4
  # TODO: create auto detect mechanism
  plexmoviesection = 6
  plexshowsection = 7

  #share one poolmanager so we cant set it up to not nuke PMS
  http = urllib3.PoolManager()
  conn = sqlite3.connect('media.db')
  
  c = conn.cursor()
  c.execute('''CREATE TABLE IF NOT EXISTS media (id text, UNIQUE (id))''')
  conn.commit()

  backupShows()
  backupMovies()

  # closing database connection (all write actions should be commited)
  conn.close()

if __name__ == "__main__":
  main()


