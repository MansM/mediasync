import urllib3, os, re, json
from .db import db
from .poolmanager import poolmanager
from .Logger import logger

__all__ = ['Kodi']

class Kodi():
  def __init__(self, location="http://127.0.0.1:8080"):
    self.kodilocation = location
    self.url = self.kodilocation + "/jsonrpc"
    self.listShow = None

  def __enter__(self):
    return self

  def kodiRequest(self, payload):
    encoded_data = json.dumps(payload).encode('utf-8')
    r = ""
    try:
      r = poolmanager.request('POST', self.url, body=encoded_data, headers={"Content-Type": "application/json"})
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

  # def getMovieIDbyIMDBNR(self):
  #   print("placeholder")

  def backupShows(self):
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
      db.execute("INSERT OR IGNORE INTO media(id) VALUES('%s')" % str(movie["imdbnumber"]))
      db.commit()
      logger.debug("insert or ignore: " + movie["imdbnumber"])

  def setSeen(self, bla):
    logger.debug('bla')

  def restoreShows(self):
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
    for row in db.execute("SELECT * FROM media WHERE id LIKE 'imdb://%'"):
      self.setSeen(row[0])