import xml.etree.ElementTree as etree
import urllib3, os, re
from .db import db
from .poolmanager import poolmanager


__all__ = ['Plex']

class Plex():

  def __init__(self, *args):
    self.plexlocation = os.environ['PLEXLOCATION']
    self.plextoken = os.environ['PLEXTOKEN']
    #self.http = urllib3.PoolManager()
  
  def __enter__(self):
    return self

  def retrieveChild(self, parent):
    url = self.plexlocation + parent.get('key')
    get = poolmanager.request('GET', url,  headers={'X-Plex-Token': self.plextoken})
    return etree.fromstring(get._body.decode("utf8"))

  def retrieveSection(self, id):
    url = self.plexlocation + "/library/sections/" + str(id) + "/all"
    req = poolmanager.request('GET', url,  headers={'X-Plex-Token': self.plextoken})
    content = req._body.decode("utf8")
    return etree.fromstring(content)

  def findSections(self, contentType):
    url = self.plexlocation + "/library/sections?"
    get = poolmanager.request('GET', url,  headers={'X-Plex-Token': self.plextoken})
    sectionsroot = etree.fromstring(get._body.decode("utf8"))
    agent=""
    if contentType == "show": agent="com.plexapp.agents.thetvdb"
    elif contentType == "movie": agent="com.plexapp.agents.imdb"

    results = sectionsroot.findall("./Directory/[@agent='" + agent + "']")
    sections = []
    for section in results:
      sections.append(section.get("key"))
    return sections

  def backupShows(self):
    print("TV SHOWS #################################################################################################################")
    print('{0:50} | {1:10} | {2:30}'.format("Name:", "Season:", "Episodes:"))
    
    ## retrieve shows
    sections = self.findSections("show")
    for section in sections:
      root = self.retrieveSection(section)

      for show in root.iter('Directory'):
        title = show.get('title')
        seasonroot = self.retrieveChild(show)

        for season in seasonroot.iter('Directory'):
          if season.get("title") != "All episodes":
            episoderoot = self.retrieveChild(season)
            episodes = ""
            for episode in episoderoot.iter('Video'):     
              vc = episode.get('viewCount') or 0
              if vc:
                metaroot = self.retrieveChild(episode)
                meta = metaroot.find('./Video')
                regex = r"thetvdb://\d+/\d+/\d+"
                results = re.search(regex, meta.get('guid'))
                if results != None: 
                  episodes += str(results.group(0)) + ", "
                  db.execute("INSERT OR IGNORE INTO media(id) VALUES('%s')" % str(results.group(0)))
            episodes = episodes.rstrip(", ")
            db.commit()
            if episodes != "": 
              print('{0:50} | {1:10} | {2:30}'.format(title, season.get('title'), episodes))

  def backupMovies(self):
    print("MOVIES ###################################################################################################################")
    print('{0:50} | {1:10} | {2:30}'.format("Name:", "Watched:", "IMDB ID:"))

    sections = self.findSections("movie")
    for section in sections:
      ## retrieve movies
      root = self.retrieveSection(section)
      root.findall("./Video")

      for video in root.iter('Video'):
        title = video.get('title')
        vc = video.get('viewCount') or 0
        if vc:
            metaroot = self.retrieveChild(video)
            meta = metaroot.find('./Video')
            regex = r"imdb://tt\d+"
            results = re.search(regex, meta.get('guid'))
            if results != None: 
              print('{0:50} | {1:10} | {2:30}'.format(title, str(vc), results.group(0)))
              db.execute("INSERT OR IGNORE INTO media(id) VALUES('%s')" % str(results.group(0)))
              db.commit()

  def restoreShows(self):
    for row in db.execute("SELECT * FROM media WHERE id LIKE 'thetvdb://%'"):
      self.setPlexSeen(row[0])

  def restoreMovies(self):
    for row in db.execute("SELECT * FROM media WHERE id LIKE 'imdb://%'"):
      self.setPlexSeen(row[0])

  def setPlexSeen(self, itemid):
    #for some reason this works, without adding episode  number in the url, it will also find episode 20-29 when searching for number 2
    
    if itemid[:4] =="thet":
      episodenr = itemid.split("/")[-1]
      url = self.plexlocation + "/library/all?index=" + episodenr + "&guid=com.plexapp.agents." + itemid
    else:
      url = self.plexlocation + "/library/all?guid=com.plexapp.agents." + itemid

    req = poolmanager.request('GET', url,  headers={'X-Plex-Token': self.plextoken})
    root = etree.fromstring(req._body.decode("utf8"))
    if int(root.get('size')) == 1: 
      if root.find("Video").get("viewCount") is None:
        itemkey = root.find("Video").get("ratingKey")
        seenurl = self.plexlocation + "/:/scrobble?key=" + itemkey + "&identifier=com.plexapp.plugins.library"
        seenreq = poolmanager.request('GET', seenurl,  headers={'X-Plex-Token': self.plextoken})
        if seenreq.status == 200:
          print("Updated: " + itemid)
        else:
          print("Error: " + seenreq.status + " - " + itemid)
      elif int(root.get('size')) > 1:
        print("ERROR:" + itemid)