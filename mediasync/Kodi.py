import urllib3, os, re, json
from .db import db
from .poolmanager import poolmanager

__all__ = ['Kodi']

class Kodi():
  def __init__(self):
    self.kodilocation = os.environ['KODILOCATION']
    self.url = self.kodilocation + "/jsonrpc"
    self.listShow = None

  def __enter__(self):
    return self

  def kodiRequest(self, payload):
    encoded_data = json.dumps(payload).encode('utf-8')
    r = poolmanager.request('POST', self.url, body=encoded_data, headers={"Content-Type": "application/json"})
    return json.loads(r._body.decode("utf8"))

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
          print('{0:50} | {1:10} | {2:30}'.format(show["label"], str(show["imdbnumber"]), str(show["tvshowid"])))
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
              #print("thetvdb://" + str(show["imdbnumber"]) + "/" + str(episode["season"]) + "/" + str(episode["episode"]))
              db.execute("INSERT OR IGNORE INTO media(id) VALUES('thetvdb://%s/%d/%d')" % (show["imdbnumber"], episode["season"], episode["episode"]))
              db.commit()
            #print(show["tvshowid"] + " - " )
    else:
      print("ERROR no tv shows")