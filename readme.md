# mediasync

Goal is to be able to sync all watched media between different playing tools like
- plex
- kodi
- etc


## Notes for myself
- find single episode http://ip:32400/library/all?index=2&guid=com.plexapp.agents.thetvdb://266189/3/2
- find single movie http://ip:32400/library/all?guid=com.plexapp.agents.imdb://tt3397884
- mark as seen http://ip:32400/:/scrobble?key=3137&identifier=com.plexapp.plugins.library
- mark as unseen http://ip:32400/:/scrobble?key=3137&identifier=com.plexapp.plugins.library

kodi:
imdb number == thetvdbid
curl --verbose -X POST -H "Content-Type: application/json" --data-binary '{
  "jsonrpc": "2.0",
  "method": "VideoLibrary.GetEpisodes",
  "params": {
    "filter": { 
      "field": "playcount", 
      "operator": "greaterthan", 
      "value": "0"
      },
    "tvshowid": 9,
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
}' ${KODILOCATION}/jsonrpc|jq


curl --verbose -X POST -H "Content-Type: application/json" --data-binary '{
  "jsonrpc": "2.0",
  "method": "VideoLibrary.GetEpisodes",
  "params": {
    "tvshowid": 60,
    "properties": [
      "tvshowid",
      "uniqueid"
    ]
  },
  "id": "libTvShows"
}' ${KODILOCATION}/jsonrpc|jq



    "filter": {
      "field": "imdbnumber",
      "operator": "is",
      "value": 340666
      },