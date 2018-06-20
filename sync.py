#!/usr/bin/env python3
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
  sections = findPlexSections("show")
  for section in sections:
    root = retrieveSection(section)

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
                episodes += str(results.group(0)) + ", "
                c.execute("INSERT OR IGNORE INTO media(id) VALUES('%s')" % str(results.group(0)))
          episodes = episodes.rstrip(", ")
          conn.commit()
          if episodes != "": 
            print('{0:50} | {1:10} | {2:30}'.format(title, season.get('title'), episodes))

def backupMovies():
  print("MOVIES ###################################################################################################################")
  print('{0:50} | {1:10} | {2:30}'.format("Name:", "Watched:", "IMDB ID:"))

  sections = findPlexSections("movie")
  for section in sections:
    ## retrieve movies
    root = retrieveSection(section)
    root.findall("./Video")

    for video in root.iter('Video'):
      title = video.get('title')
      vc = video.get('viewCount') or 0
      if vc:
          metaroot = retrieveChild(video)
          meta = metaroot.find('./Video')
          regex = r"imdb://tt\d+"
          results = re.search(regex, meta.get('guid'))
          if results != None: 
            print('{0:50} | {1:10} | {2:30}'.format(title, str(vc), results.group(0)))
            c.execute("INSERT OR IGNORE INTO media(id) VALUES('%s')" % str(results.group(0)))
            conn.commit()

def restoreShows():
  for row in c.execute("SELECT * FROM media WHERE id LIKE 'thetvdb://%'"):
    setPlexSeen(row[0])
    
def restoreMovies():
  for row in c.execute("SELECT * FROM media WHERE id LIKE 'imdb://%'"):
    setPlexSeen(row[0])

def setPlexSeen(itemid):
  #for some reason this works, without adding episode  number in the url, it will also find episode 20-29 when searching for number 2
  
  if itemid[:4] =="thet":
    episodenr = itemid.split("/")[-1]
    url = plexlocation + "/library/all?index=" + episodenr + "&guid=com.plexapp.agents." + itemid
  else:
    url = plexlocation + "/library/all?&guid=com.plexapp.agents." + itemid

  req = http.request('GET', url,  headers={'X-Plex-Token': plextoken})
  root = etree.fromstring(req._body.decode("utf8"))
  if int(root.get('size')) == 1: 
    if root.find("Video").get("viewCount") is None:
      itemkey = root.find("Video").get("ratingKey")
      seenurl = plexlocation + "/:/scrobble?key=" + itemkey + "&identifier=com.plexapp.plugins.library"
      seenreq = http.request('GET', seenurl,  headers={'X-Plex-Token': plextoken})
      if seenreq.status == 200:
        print("Updated: " + itemid)
      else:
        print("Error: " + seenreq.status + " - " + itemid)
    elif int(root.get('size')) > 1:
      print("ERROR:" + itemid)
    

def findPlexSections(contentType):
  url = plexlocation + "/library/sections?"
  get = http.request('GET', url,  headers={'X-Plex-Token': plextoken})
  sectionsroot = etree.fromstring(get._body.decode("utf8"))
  agent=""
  if contentType == "show": agent="com.plexapp.agents.thetvdb"
  elif contentType == "movie": agent="com.plexapp.agents.imdb"

  results = sectionsroot.findall("./Directory/[@agent='" + agent + "']")
  sections = []
  for section in results:
    sections.append(section.get("key"))
  return sections

def main():
  global conn, c, plexlocation, plextoken, http
  #TODO: find a better way then to use globals

  ## Laptop without connection, abuse vagrant to generate a network with IP
  plexlocation = os.environ['PLEXLOCATION']

  plextoken = os.environ['PLEXTOKEN']
  #share one poolmanager so we cant set it up to not nuke PMS
  http = urllib3.PoolManager()
  conn = sqlite3.connect('media.db')
  
  c = conn.cursor()
  c.execute('''CREATE TABLE IF NOT EXISTS media (id text, UNIQUE (id))''')
  conn.commit()

  backupShows()
  backupMovies()
  restoreShows()

  # closing database connection (all write actions should be commited)
  conn.close()

if __name__ == "__main__":
  main()


