
# compares them to already known videos and adds new videos as wordpress posts to the blog 
#
# Written by Lena Siess, 2017


from oauth2client.tools import argparser
import os
import time
import json
import datetime
import parser
import getyoutubevideos
import wordpress

WAIT_TIME = 600

# Initialize
if os.path.isfile("channels.json") == False:
    print "No channels.json file found!"
    quit()

channels_file = open("channels.json").read()
channels = json.loads(channels_file)
first_run = False
added_videos = 0

knownvideos = []
set(knownvideos)

if os.path.isfile("knownvideos.json") == True:
    knownvideos_file_read = open("knownvideos.json").read()
    knownvideos = json.loads(knownvideos_file_read)

# Register with the Youtube Data API
args = argparser.parse_args()
service = getyoutubevideos.get_authenticated_service(args)

# Put "get videos, compare, and post" into its own function

def handle_video(channel, videoresponse, known_channel):
    site_libraries = []
    global added_videos
    # Check for differences with known videos
    for playlist_item in videoresponse["items"]:
        # check if video is public and wether we already know it: returns 1 if videos exists, 0 if it doesnt:
        if playlist_item["status"]["privacyStatus"] == "public" and known_channel.count(playlist_item["snippet"]["resourceId"]["videoId"]) == 0:
            # video is not known to us yet

            # make a post about it
            print ">>" + str(channel['name']) + ": New Video - " + playlist_item["snippet"]["title"]
            # Login with the user who'se channel it is the video belongs to
            wp = wordpress.login(channel['user'],channel['password'])

            if site_libraries == []:
                site_libraries = wordpress.updateLibraries(wp)

            # Embed the video into the post
            post_content = playlist_item["snippet"]["description"]
            # Search the tags of the video to categorize it
            tags = getyoutubevideos.catchVideoTags(service, playlist_item["snippet"]["resourceId"]["videoId"])
            
            
            # Post it
            wordpress.post(wp, site_libraries[0], site_libraries[1], playlist_item["snippet"]["title"], post_content, playlist_item["snippet"]["publishedAt"], playlist_item["snippet"]["resourceId"]["videoId"], {'post_tag': [str(channel['name'])],'category': ['videos']})

            # add it to the known videos
            known_channel.append(playlist_item["snippet"]["resourceId"]["videoId"])

            added_videos += 1

    return known_channel


def cycle(init=False):
    global added_videos

    # Fetch videos of unknown channels and register the channels in knownvideos.json
    for channel in channels:
        added_videos = 0
        #print "Fetching Videos in list of Channel %s" % channel['name']
        videosresponse = getyoutubevideos.catchChannelVideos(service, str(channel['id']))

        channel_is_known = False
        for known_channel in knownvideos:
            #print "%s compared with %s", (str(known_channel[0]), str(channel['id']))
            if str(known_channel[0]) == str(channel['id']):
                #print "Channel already registered!"
                channel_is_known = True
                known_channel = handle_video(channel, videosresponse, known_channel)

        if channel_is_known == False:

            add_existing_videos = False
            if init == True:
                if raw_input("Unkown Channel. Add all exisiting videos to the website? [y/N]") == 'y':
                    add_existing_videos = True

            new_channel = []
            set(new_channel)
            new_channel.append(str(channel['id'])) # Add channel ID first, so we know what channel the videos belong to
            new_channel = handle_video(channel, videosresponse, new_channel)

            knownvideos.append(new_channel)
            print ">>> Added " + str(channel['name']) + " as new channel to known channels!"

        if added_videos > 0:
            print ">>> Added " + str(added_videos) + " new videos of " + str(channel['name']) + " to the website!"

    #print knownvideos

    # Save knownvideos in knownvideos.json
    knownvideos_file_write = open("knownvideos.json", 'w')
    json.dump(knownvideos, knownvideos_file_write)
    knownvideos_file_write.close()




# Here the actual main loop
print "Iniital run:"
cycle(True)


while True:
    print "Done! Now waiting " + str(WAIT_TIME) + " seconds!"
    time.sleep(WAIT_TIME)
    cycle()

