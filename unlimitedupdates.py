
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

WAIT_TIME = 10

# Initialize
if os.path.isfile("channels.json") == False:
    print "No channels.json file found!"
    quit()

channels_file = open("channels.json").read()
channels = json.loads(channels_file)
first_run = False

knownvideos = []
set(knownvideos)

if os.path.isfile("knownvideos.json") == True:
    knownvideos_file_read = open("knownvideos.json").read()
    knownvideos = json.loads(knownvideos_file_read)

# Register with the Youtube Data API
args = argparser.parse_args()
service = getyoutubevideos.get_authenticated_service(args)

# Put "get videos, compare, and post" into its own function

def cycle(init=False):
    site_libraries = []

    # Fetch videos of unknown channels and register the channels in knownvideos.json
    for channel in channels:
        added_videos = 0
        print "Fetching Videos in list of Channel %s" % channel['name']
        videosresponse = getyoutubevideos.catchChannelVideos(service, str(channel['id']))

        channel_is_known = False
        for known_channel in knownvideos:
            #print "%s compared with %s", (str(known_channel[0]), str(channel['id']))
            if str(known_channel[0]) == str(channel['id']):
                print "Channel already registered!"
                channel_is_known = True
                
                # Check for differences with known videos
                for playlist_item in videosresponse["items"]:
                    # returns 1 if videos exists, 0 if it doesnt:
                    if known_channel.count(playlist_item["snippet"]["resourceId"]["videoId"]) == 0:
                        # video is not known to us yet

                        # make a post about it
                        print "New Video! " + playlist_item["snippet"]["title"]

                        # Login with the user who'se channel it is the video belongs to
                        wp = wordpress.login(channel['user'],channel['password'])

                        if site_libraries == []:
                            site_libraries = wordpress.updateLibraries(wp)

                        # Embed the video into the post
                        post_content = "[embed]https://www.youtube.com/watch?v=" + playlist_item["snippet"]["resourceId"]["videoId"] + "[/embed]\n" + playlist_item["snippet"]["description"]


                        # Post it
                        wordpress.post(wp, site_libraries[0], site_libraries[1], playlist_item["snippet"]["title"], post_content, playlist_item["snippet"]["publishedAt"], playlist_item["snippet"]["resourceId"]["videoId"], {'post_tag': [str(channel['name'])],'category': ['videos']})

                        # add it to the known videos
                        known_channel.append(playlist_item["snippet"]["resourceId"]["videoId"])

                        added_videos += 1

        if channel_is_known == False:

            add_existing_videos = False
            if init == True:
                if raw_input("Unkown Channel found. Do you want to add all exisiting videos to the website? [Y/n]") != 'n':
                    if raw_input("Are you absolutely sure? Type 'yes' if you are: ") == "yes":
                        add_existing_videos = True

            new_channel = []
            set(new_channel)
            new_channel.append(str(channel['id'])) # Add channel ID first, so we know what channel the videos belong to
            for playlist_item in videosresponse["items"]:
                #title = playlist_item["snippet"]["title"]
                video_id = playlist_item["snippet"]["resourceId"]["videoId"]
                #description = playlist_item["snippet"]["description"]

                new_channel.append(video_id)

                if add_existing_videos == True:
                    # Login with the user who'se channel it is the video belongs to
                    wp = wordpress.login(channel['user'],channel['password'])

                    if site_libraries == []:
                        site_libraries = wordpress.updateLibraries(wp)

                    # Embed the video into the post
                    post_content = "[embed]https://www.youtube.com/watch?v=" + playlist_item["snippet"]["resourceId"]["videoId"] + "[/embed]\n" + playlist_item["snippet"]["description"]

                    # Post it
                    wordpress.post(wp, site_libraries[0], site_libraries[1], playlist_item["snippet"]["title"], post_content, playlist_item["snippet"]["publishedAt"], playlist_item["snippet"]["resourceId"]["videoId"] ,{'post_tag': [str(channel['name'])],'category': ['videos']})

                    added_videos += 1

            knownvideos.append(new_channel)
            print ">>> Added " + str(channel['name']) + " as new channel to known channels!"

        print ">>> Added " + str(added_videos) + " new videos to the website!"

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

