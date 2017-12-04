# Sample Python code for user authorization

import httplib2
import os
import sys

from apiclient.discovery import build
from apiclient.errors import HttpError
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import argparser, run_flow

# The CLIENT_SECRETS_FILE variable specifies the name of a file that contains
# the OAuth 2.0 information for this application, including its client_id and
# client_secret.
CLIENT_SECRETS_FILE = "client_secret.json"

# This OAuth 2.0 access scope allows for full read/write access to the
# authenticated user's account and requires requests to use an SSL connection.
YOUTUBE_READ_WRITE_SSL_SCOPE = "https://www.googleapis.com/auth/youtube.readonly"
API_SERVICE_NAME = "youtube"
API_VERSION = "v3"

# This variable defines a message to display if the CLIENT_SECRETS_FILE is
# missing.
MISSING_CLIENT_SECRETS_MESSAGE = "WARNING: Please configure OAuth 2.0"

# Authorize the request and store authorization credentials.
def get_authenticated_service(args):
  flow = flow_from_clientsecrets(CLIENT_SECRETS_FILE, scope=YOUTUBE_READ_WRITE_SSL_SCOPE,
    message=MISSING_CLIENT_SECRETS_MESSAGE)

  storage = Storage("%s-oauth2.json" % sys.argv[0])
  credentials = storage.get()

  if credentials is None or credentials.invalid:
    credentials = run_flow(flow, storage, args)

  # Trusted testers can download this discovery document from the developers page
  # and it should be in the same directory with the code.
  return build(API_SERVICE_NAME, API_VERSION,
      http=credentials.authorize(httplib2.Http()))

#args = argparser.parse_args()
#service = get_authenticated_service(args)

### END BOILERPLATE CODE

def catchChannelVideos(service, channelID):
    channels_response = service.channels().list(
            #mine=True,
            part="contentDetails",
            #forUsername="gescheit gespielt"
            #id="UCAmaelj22ggPbyck0X93FlA"
            id=channelID
        ).execute()

    for channel in channels_response["items"]:
        uploads_list_id = channel["contentDetails"]["relatedPlaylists"]["uploads"]


        # Retrieve the list of videos uploaded to the given user's channel.
        playlistitems_list_request = service.playlistItems().list(
            playlistId=uploads_list_id,
            part="snippet,status",
            maxResults=50
        )
        
        playlistitems_list_response = playlistitems_list_request.execute()
        return playlistitems_list_response

        while playlistitems_list_request:
            playlistitems_list_response = playlistitems_list_request.execute()

            # Print information about each video.
            for playlist_item in playlistitems_list_response["items"]:
                title = playlist_item["snippet"]["title"]
                video_id = playlist_item["snippet"]["resourceId"]["videoId"]
                print "%s (%s)" % (title, video_id)

            playlistitems_list_request = service.playlistItems().list_next(
            playlistitems_list_request, playlistitems_list_response)
            print # Basically a new line

#catchChannelVideos("UCAmaelj22ggPbyck0X93FlA")

def catchVideoTags(service, videoID):
    video_response = service.videos().list(part="snippet",id=videoID).execute()
    return video_response["items"][0]["snippet"]["tags"]
