import urllib3, os, re, json, base64, sys
from .db import db
from .poolmanager import poolmanager
from .Logger import logger

__all__ = ['Kodi']

class Kodi():
  def __init__(self, location="http://127.0.0.1:8080", username=None, password=None):
    logger.info("New kodi instance at " + location)
    self.kodilocation = location
    self.url = self.kodilocation + "/jsonrpc"
    self.listShow = None
    self.listMovies = None
    self.username = username
    self.password = password

    if self.username != None and self.password != None:
      raw = bytes("%s:%s"%(str(self.username), str(self.password)), "UTF-8")
      auth = "Basic %s"  % base64.b64encode(raw).strip().decode("utf-8")
      poolmanager.http.headers["Authorization"] = auth
      r = poolmanager.request('POST', "http://10.0.1.53:8080/jsonrpc", body=None, headers={"Content-Type": "application/json", "Authorization": auth})
      if r.status == 401:
        logger.error("invalid credentials/kodi")
        sys.exit("invalid kodi credentials")
    else:
      r = poolmanager.request('POST', self.url, body=None, headers={"Content-Type": "application/json"})
      if r.status == 401:
        logger.error("invalid credentials/kodi")
        quit("invalid kodi credentials")


  def __enter__(self):
    return self

  def kodiRequest(self, payload):
    encoded_data = json.dumps(payload).encode('utf-8')
    r = ""
    try:
      if self.username != None and self.password != None:
        raw = bytes("%s:%s"%(str(self.username), str(self.password)), "UTF-8")
        auth = "Basic %s"  % base64.b64encode(raw).strip().decode("utf-8")
        poolmanager.http.headers["Authorization"] = auth
        r = poolmanager.request('POST', "http://10.0.1.53:8080/jsonrpc", body=encoded_data, headers={"Content-Type": "application/json", "Authorization": auth})
        if r.status == 401:
          logger.error("invalid credentials/kodi")
          sys.exit("invalid kodi credentials")
      else:
        r = poolmanager.request('POST', self.url, body=encoded_data, headers={"Content-Type": "application/json"})
        if r.status == 401:
          logger.error("invalid credentials/kodi")
          quit("invalid kodi credentials")
      return json.loads(r._body.decode("utf8"))
    except (urllib3.exceptions.ProtocolError):
      return None
    
  def getShowid_byTVDBID(self, id):
    if self.listShow == None:
      payload = {
        "jsonrpc": "2.0",
        "method": "VideoLibrary.GetTVShows",
        "params": {
          "properties": [
            "imdbnumber",
            "mpaa",
            "uniqueid"
          ],
          "sort": {
            "order": "ascending",
            "method": "label"
          }
        },
        "id": "libTvShows"
      }
      self.listShow = self.kodiRequest(payload)["result"]["tvshows"]
    for show in self.listShow:
      if show["imdbnumber"] == id:
        return show["tvshowid"]

  def getEpisodeid(self, thetvdbid):
    regex = r"thetvdb://(?P<id>\d+)/(?P<season>\d+)/(?P<episode>\d+)"
    results = re.search(regex, thetvdbid)
    if self.getShowid_byTVDBID(results.group("id")):
      payload = {
        "jsonrpc": "2.0",
        "method": "VideoLibrary.GetEpisodes",
        "params": {
          "tvshowid": self.getShowid_byTVDBID(results.group("id")),
          "filter": {
            "and" : [{
              "field": "season",
              "operator": "is",
              "value": results.group("season")
            },
            {
              "field": "episode",
              "operator": "is",
              "value": results.group("episode")
            }
            ]
          },
          "properties": [
            "tvshowid",
            "uniqueid"
          ]
        },
        "id": "libTvShows"
        }
      returnvalues=[]
      for episode in self.kodiRequest(payload)["result"]["episodes"]:
        returnvalues.append(episode["episodeid"])
      return returnvalues

  def getMovieIDbyIMDBNR(self, imdbnr):
    #print("placeholder")
    if self.listMovies == None:
      payload = {
        "jsonrpc": "2.0",
        "method": "VideoLibrary.GetMovies",
        "params": {
          "properties": [
            "title",
            "imdbnumber",
            "playcount"
          ]
        },
        "id": "libMovies"
      }
      self.listMovies = self.kodiRequest(payload)["result"]["movies"]
    
    returnvalues = []
    for movie in self.listMovies:
      #print(movie)
      #print(imdbnr)
      if movie["imdbnumber"] == imdbnr[7:]:
        returnvalues.append(movie["movieid"])
        # print(movie)
    
    return returnvalues

  def backupShows(self):
    print("backing up kodi shows")
    payload = {
      "jsonrpc": "2.0",
      "method": "VideoLibrary.GetTVShows",
      "params": {
        "properties": [
          "imdbnumber",
          "uniqueid"
        ]
      },
      "id": "libTvShows"
    }
    results = self.kodiRequest(payload)

    if "tvshows" in results["result"]:
      for show in results["result"]["tvshows"]:
        #TODO: fix this in the query to kodi, but couldnt get it to work
        if show["imdbnumber"] != "":
          episodes_payload = {
            "jsonrpc": "2.0",
            "method": "VideoLibrary.GetEpisodes",
            "params": {
              "filter": { 
                "field": "playcount", 
                "operator": "greaterthan", 
                "value": "0"
                },
              "tvshowid": show["tvshowid"],
              "properties": [
                "season",
                "episode",
                "file",
                "tvshowid",
                "uniqueid",
                "playcount"
              ]
            },
            "id": "libTvShows"
          }
          e_results = self.kodiRequest(episodes_payload)
          if "episodes" in e_results["result"]:
            for episode in e_results["result"]["episodes"]:
              db.execute("INSERT OR IGNORE INTO media(id) VALUES('thetvdb://%s/%d/%d')" % (show["imdbnumber"], episode["season"], episode["episode"]))
              db.commit()
    else:
      logger.error("no tv shows")

  def backupMovies(self):
    print("backing up kodi movies")
    payload = {
      "jsonrpc": "2.0",
      "method": "VideoLibrary.GetMovies",
      "params": {
        "filter": {
          "field": "playcount",
          "operator": "greaterthan",
          "value": "0"
        },
        "properties": [
          "title",
          "imdbnumber",
          "playcount"
        ]
      },
      "id": "libMovies"
    }
    m_results = self.kodiRequest(payload)
    for movie in m_results["result"]["movies"]:
      db.execute("INSERT OR IGNORE INTO media(id) VALUES('imdb://%s')" % str(movie["imdbnumber"]))
      db.commit()
      logger.debug("insert or ignore: " + movie["imdbnumber"])

  def setSeen(self, bla):
    logger.debug('bla')

  def restoreShows(self):
    print("restoring up kodi shows")
    for row in db.execute("SELECT * FROM media WHERE id LIKE 'thetvdb://%'"):
      episodeids = self.getEpisodeid(row[0])
      if episodeids != None:
        for epi_id in episodeids:
          payload = {
              "jsonrpc": "2.0",
              "method": "VideoLibrary.SetEpisodeDetails",
              "params": {
                "episodeid": epi_id,
                "playcount": 1
              }
          }
          self.kodiRequest(payload)

  def restoreMovies(self):
    print("restoring up kodi movies")
    for row in db.execute("SELECT * FROM media WHERE id LIKE 'imdb://%'"):
      for id in self.getMovieIDbyIMDBNR(row[0]):
        payload = {
          "jsonrpc": "2.0",
          "method": "VideoLibrary.SetMovieDetails",
          "params": {
            "movieid": id,
            "playcount": 1
          }
        }
        self.kodiRequest(payload)
    
  